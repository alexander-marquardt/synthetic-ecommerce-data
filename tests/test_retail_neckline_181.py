"""Neckline on every top, dress and knit, boat and slash in depth, with neighbours (gen#181).

"womens boat neck top" must filter or boost the stored neckline and bury the other neck types.
That could not be shown while two tops were boat and one slash. The floors and the expected
words are written out here, not read from the rows module, so dropping rows fails this file.

The counts are taken over :func:`scale.templates`: every row is a template, and a derived style
only adds to them, so a floor met here is met by the ceiling build. A product is a style (its
colors times its sizes are its SKUs), so a floor counts products, not SKUs.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import kit  # noqa: E402
import kit_garments  # noqa: E402
import scale  # noqa: E402

#: The types the issue names: a top, a dress, a knit (and the near-miss types it lists).
CARRIERS = {
    "Top",
    "Dress",
    "Tea Dress",
    "Blouse",
    "Jumper",
    "Cardigan",
    "Knitted Top",
    "T-Shirt",
    "Shirt",
    "Bodysuit",
    "Co-ord Set",
    "Polo Shirt",
}
#: Every value a neckline takes.
VALUES = {
    "boat",
    "slash",
    "crew",
    "round",
    "v-neck",
    "high",
    "collared",
    "square",
    "halter",
    "cowl",
    "tie-neck",
}
#: The common necklines the policy must find neighbours for, at least this many products each.
COMMON = {"crew": 120, "round": 120, "v-neck": 120, "high": 120, "collared": 120}
#: The rarer ones the kit now draws.
RARER = {"square": 30, "halter": 20, "cowl": 20}
#: A title phrase that states a neckline -> the stored value.
PHRASES = {
    "boat neck": "boat", "slash neck": "slash", "v neck": "v-neck", "v-neck": "v-neck",
    "crew neck": "crew", "scoop neck": "round", "square neck": "square", "halter neck": "halter",
    "cowl neck": "cowl", "roll neck": "high", "turtle neck": "high", "funnel neck": "high",
    "high neck": "high", "tie neck": "tie-neck",
}  # fmt: skip
#: A drawing key -> the values it may show: a slash neck is drawn as a boat, and the crew drawing
#: stands for a round neck and for the collar of the shirts drawn beneath it (authored before this).
SHOWS = {
    "crew": {"crew", "round", "collared"},
    "scoop": {"round"},
    "v_neck": {"v-neck"},
    "roll_neck": {"high"},
    "square": {"square"},
    "halter": {"halter"},
    "cowl": {"cowl"},
    "boat": {"boat", "slash"},
    "collar": {"collared"},
}


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def real(templates) -> list[dict]:
    """The styles that are not a text-match decoy: a decoy copies a style's neckline, and a floor
    counts the products a shopper means, not the look-alikes."""
    return [r for r in templates if r["product_id"] not in scale.TEXT_EXEMPT]


@pytest.fixture(scope="module")
def carriers(real) -> list[dict]:
    return [r for r in real if r["product_type"] in CARRIERS]


def _products(recs, **want) -> int:
    return len({r["product_id"] for r in recs if all(r.get(k) == v for k, v in want.items())})


def test_forty_tops_are_boat_or_slash_with_both_in_depth(real):
    tops = [r for r in real if r["product_type"] == "Top"]
    boat, slash = _products(tops, neckline="boat"), _products(tops, neckline="slash")
    assert boat + slash >= 40, (boat, slash)
    assert boat >= 15 and slash >= 15, (boat, slash)


@pytest.mark.parametrize(("value", "floor"), sorted({**COMMON, **RARER}.items()))
def test_each_neighbouring_neckline_has_products_to_bury(carriers, value, floor):
    n = _products(carriers, neckline=value)
    assert n >= floor, f"{value}: {n} products"


@pytest.mark.parametrize("ptype", ["Bodysuit", "Co-ord Set", "Dress"])
def test_near_miss_types_carry_a_boat_or_slash_neckline(carriers, ptype):
    n = len(
        {
            r["product_id"]
            for r in carriers
            if r["product_type"] == ptype and r.get("neckline") in ("boat", "slash")
        }
    )
    assert n >= 3, f"{ptype}: {n}"


def test_every_top_dress_and_knit_states_a_neckline_from_the_vocabulary(carriers):
    # A men's shirt or a sports tee is not a neckline shopper's item; the rest all state one.
    bare = [
        r["product_id"]
        for r in carriers
        if r.get("neckline") not in VALUES
        and not (r["product_type"] == "T-Shirt" and r["category_path"][1:2] == ["Sportswear"])
    ]
    assert not bare, bare[:20]


def test_a_title_that_names_a_neckline_states_that_neckline(carriers, templates):
    wrong = []
    for r in carriers:
        title = re.sub(r"[^a-z0-9- ]", " ", r["title"].lower())
        said = {v for p, v in PHRASES.items() if re.search(rf"\b{re.escape(p)}\b", title)}
        if said and r.get("neckline") not in said:
            wrong.append((r["product_id"], r["title"], r.get("neckline")))
    assert not wrong, wrong[:20]


def test_the_picture_shows_the_stated_neckline(carriers):
    wrong = []
    for r in carriers:
        key = ((r.get("drawing") or {}).get("params") or {}).get("neckline")
        shape = r.get("drawing", {}).get("shape")
        if (
            key
            and shape in ("top", "dress", "bodysuit", "cardigan")
            and (r.get("neckline") not in SHOWS.get(key, set()))
        ):
            wrong.append((r["product_id"], key, r.get("neckline")))
    assert not wrong, wrong[:20]


def test_the_title_names_the_neckline_on_some_boat_and_slash_tops_only(real):
    tops = [
        r for r in real if r["product_type"] == "Top" and r.get("neckline") in ("boat", "slash")
    ]
    named = [r for r in tops if re.search(r"\b(boat|slash) neck\b", r["title"].lower())]
    unnamed = [r for r in tops if r not in named]
    assert len(named) >= 20, len(named)
    assert len(unnamed) >= 15, len(unnamed)
    for r in unnamed:  # the stored attribute carries it; the words do not say boat or slash
        assert not re.search(r"\b(boat|slash)", r["description"].lower()), r["product_id"]


def test_neckline_word_decoys_are_true_to_their_attribute(templates):
    """A boat print, a slash pocket, slashed sleeves: the word is in the title, not the neck."""
    decoys = [
        r
        for r in templates
        if r["product_type"] in ("Top", "Dress")
        and re.search(r"\b(boat|slash)", r["title"].lower())
        and not re.search(r"\b(boat|slash) neck\b", r["title"].lower())
        and r.get("neckline") not in ("boat", "slash")
    ]
    assert len(decoys) >= 5, [d["title"] for d in decoys]
    for r in decoys:
        assert r.get("neckline") in VALUES, r["product_id"]


def test_titles_stay_unique_across_the_neckline_rows(templates):
    titles = Counter(
        (r["title"], r["product_type"]) for r in templates if r["product_id"].startswith("BRD-NK")
    )
    assert titles
    assert [t for t, n in titles.items() if n > 1] == []


def test_the_kit_draws_a_halter_and_a_cowl_and_a_dress_neckline():
    assert {"halter", "cowl"} <= set(kit_garments.NECKLINES)
    plain = kit.dress("#abc", None, None)
    drawn = {
        n: kit.dress("#abc", None, None, neckline=n) for n in ("crew", "v_neck", "halter", "cowl")
    }
    assert all(d != plain for d in drawn.values())
    assert len({tuple(d) for d in drawn.values()}) == len(drawn)


def test_building_the_templates_leaves_the_authored_samples_untouched():
    """The completed necklines are copies: the authored samples are shared with the image release,
    and a drawing edited in place there changed the images that release writes. A fresh interpreter,
    so an earlier build in this process cannot have made the edit already."""
    code = (
        "import copy, scale\n"
        "from build_preview4 import samples\n"
        "before = copy.deepcopy(samples())\n"
        "scale.templates()\n"
        "assert samples() == before, 'an authored sample was edited in place'\n"
    )
    run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         check=False, cwd=RETAIL)  # fmt: skip
    assert run.returncode == 0, run.stderr[-600:]
