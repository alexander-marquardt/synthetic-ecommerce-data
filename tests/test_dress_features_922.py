"""A dress drawing shows the construction and the pattern its title names (gen#922).

The "Petite Pinstripe Wrap Midi Dress" was drawn as the plain strap dress: no wrap front, no
pinstripe. :mod:`dress_features` reads each construction or pattern word off a dress title and
draws it on the dress. These tests read the SKU's release image (``image_release.render``), the
file a shopper sees, so a word the release cannot draw fails here.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    dress_features,
    image_release,
    kit,
    scale,
)
from synthetic_ecommerce_data.domains.retail.kit import Fill

#: The row the issue names, and the words its image must draw: written here, not read from the
#: module, so loosening the vocabulary does not loosen the test.
REPORTED = ("PLT-DPT105", "Petite Pinstripe Wrap Midi Dress", ("wrap", "pinstripe"))
#: Every construction or pattern word a generated dress title carries today, with a row that
#: names it. The vocabulary must cover each one, so a word cannot fall out of it unnoticed.
NAMED_TODAY = {
    "wrap": "PLT-DPT105",
    "pinstripe": "PLT-DPT105",
    "tiered": "PLT-SDMAXI",
    "smocked": "PLT-FPSMOK",
    "ruched": "BRD-WDBC006",
    "belted": "PLT-DPT117",
    "button front": "PLT-DRS3",
    "pinafore": "BRD-KDD015",
    "pleated": "PLT-DPT101",
    "seamed": "PLT-DPT097",
    "slashed hem": "BRD-NKXDSLSD",
    "broderie": "BRD-NWD2",
    "roses": "PLT-DBLR06",
    "boat print": "BRD-NKXDBOAD",
    "print": "PLT-LEMDRS",
}

_MARK = re.compile(r'data-feature="([a-z_]+)"')


def _look(rec: dict) -> tuple[str, str]:
    """The release image of the row's first SKU: its fill pattern and its SVG."""
    sku = rec["skus"][0]
    return image_release.colorway_drawing(rec, sku)["pattern"], image_release.render(
        rec, sku
    ).decode()


@pytest.fixture(scope="module")
def dresses() -> list[dict]:
    return [d for d in scale.templates(baseline=False) if dress_features.is_dress(d)]


def test_every_construction_and_pattern_word_of_a_dress_title_is_drawn(dresses) -> None:
    unshown = dress_features.unshown(dresses, _look)
    assert not unshown, "dress titles name words their images do not draw:\n" + "\n".join(
        f"  {word}: {len(rows)} rows, e.g. {', '.join(rows[:3])}"
        for word, rows in sorted(unshown.items())
    )


def test_the_reported_dress_draws_its_wrap_and_pinstripe(dresses) -> None:
    code, title, words = REPORTED
    rec = next(d for d in dresses if d["product_id"] == code)
    assert rec["title"] == title
    for styled in (True, False):
        svg = image_release.render(rec, rec["skus"][0], styled=styled).decode()
        assert set(words) <= set(_MARK.findall(svg)), (styled, _MARK.findall(svg))


def test_the_check_names_every_word_it_misses_not_only_the_first() -> None:
    rec = {"product_id": "X", "title": "Pinstripe Tiered Wrap Dress", "product_type": "Dress",
           "category_path": ["Womens", "Dresses"]}  # fmt: skip
    # Drawn with another feature: a mark that is not the word's does not count as drawing it.
    fill = Fill("solid", "#223344", "#333333", "#f2d14b")
    belted = "".join(kit.dress("#223344", fill, None, features="belted"))
    got = dress_features.unshown([rec], lambda _rec: ("solid", belted))
    assert got == {"pinstripe": ["X"], "tiered": ["X"], "wrap": ["X"]}


def test_a_shirt_dress_marks_its_own_belt_and_button_front() -> None:
    rec = {"product_id": "X", "title": "Belted Button Front Shirt Dress", "product_type": "Dress",
           "category_path": ["Womens", "Dresses"]}  # fmt: skip
    svg = kit.render("shirt_dress", Fill("solid", "#223344", "#333333", "#f2d14b"))
    assert dress_features.unshown([rec], lambda _rec: ("solid", svg)) == {}


@pytest.mark.parametrize("word", sorted(NAMED_TODAY))
def test_the_vocabulary_reads_each_word_a_dress_title_carries(word, dresses) -> None:
    title = next(d["title"] for d in dresses if d["product_id"] == NAMED_TODAY[word])
    assert word in dress_features.words_of(title), title


@pytest.mark.parametrize("shape", sorted(dress_features.DRAWN))
def test_each_feature_draws_a_mark_the_plain_shape_lacks(shape) -> None:
    fill = Fill("solid", "#2a3a5c", "#333333", "#f2d14b")
    plain = kit.render(shape, fill)
    missing = []
    for feature in sorted(dress_features.DRAWN[shape]):
        svg = kit.render(shape, fill, params={"features": feature})
        if svg == plain or feature not in _MARK.findall(svg):
            missing.append(feature)
    assert not missing, f"{shape} draws nothing for {missing}"


def test_a_wrap_front_is_its_own_v_and_draws_no_neckline_cut() -> None:
    fill = Fill("solid", "#c2b8a3", "#333333", "#f2d14b")
    cut = kit.DRESS_NECKS["v_neck"][1]
    assert cut in "".join(kit.dress("#c2b8a3", fill, None, neckline="v_neck"))
    assert cut not in "".join(kit.dress("#c2b8a3", fill, None, neckline="v_neck", features="wrap"))


def test_a_mark_on_a_dark_fill_is_drawn_light_not_in_the_kit_ink() -> None:
    def marks(base: str) -> str:
        drawn = "".join(kit.dress(base, Fill("solid", base, "#333333", "#f2d14b"), None,
                                  features="belted wrap"))  # fmt: skip
        return "".join(re.findall(r'<g data-feature="[a-z_]+">.*?</g>', drawn))

    assert f'stroke="{kit.INK}"' in marks("#c2b8a3")
    assert f'stroke="{kit.INK}"' not in marks("#2f2f35")


def test_a_shape_refuses_a_feature_it_cannot_draw() -> None:
    with pytest.raises(ValueError, match="shirt_dress draws no"):
        dress_features.draw(
            "shirt_dress", "wrap", "#ffffff", Fill("solid", "#ffffff", "#333333", "#f2d14b")
        )
