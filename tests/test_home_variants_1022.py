"""The rug, wall light and bench variants WANDS needs (gen#1022, slice 7).

Kitchen mats, doormats and kids' rugs are new values of the ``rug`` shape: two forms
(``doormat``, ``kitchen_mat``) and a ``motif`` for a kids' rug, its default ``none`` drawing
today's rug byte for byte. Vanity lighting and benches are types of their own, built from
``wall_light``'s parts and the dining-chair bench's seat, because one ``drawings.PROPORTIONS`` row
cannot hold both a tall sconce and a wide vanity bar, nor a chair and a bench. Each keeps slice 1's
promises: each param value draws a picture of its own, the drawn count is the stated count, a
value outside the table is refused naming the param, a White piece reads white (gen#226), each
type names one orientation (#849), and each draws through ``drawings.render`` in both finishes at
the width, height and depth a product states.
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data import drawings
from synthetic_ecommerce_data.domains.retail import (
    kit,
    kit_home_variants,
    kit_softfurn,
    orientation,
)
from test_retail_furniture_drawings_226 import BASE, _lum, _rgb, _structure_luminances

TYPES = ("vanity_light", "bench")
WOOD = kit.Fill("solid", "#8a5a3a", "#333333", "#f2d14b")
BRAND = "Harbour & Pine"
#: sha256 (first 16 hex) of each rug the generator's rows draw, recorded on main before this slice.
RUG_BEFORE = {
    ("rectangle", "flat"): "a06958515b410b10",
    ("rectangle", "shag"): "3759839dddb923d3",
    ("rectangle", "short"): "1bd4fae585ee18cd",
    ("round", "flat"): "27fba68a6bc8bad0",
    ("round", "shag"): "1f4d7a2f9e6ed5d3",
    ("round", "short"): "81436c8797dd4837",
    ("runner", "flat"): "61f04561dde82dc8",
    ("runner", "shag"): "4328745f65f9d6ac",
    ("runner", "short"): "de237fd33e859fc2",
}


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, WOOD, params=params or None)


def _count(svg: str, cls: str) -> int:
    return len(re.findall(rf'class="{cls}"', svg))


def _table(shape: str) -> dict[str, tuple[str, ...]]:
    return kit_softfurn.RUG_PARAMS if shape == "rug" else kit_home_variants.PARAMS.get(shape, {})


def test_the_two_types_are_registered_with_their_param_tables() -> None:
    kit.register_all()
    assert set(kit_home_variants.PARAMS) == set(TYPES)
    assert set(TYPES) <= set(kit.SHAPES)
    for shape in TYPES:
        # A bench is furniture and a vanity light a light fitting: level (#1095).
        assert orientation.of(shape) == "level", shape


@pytest.mark.parametrize("shape", TYPES)
def test_each_type_draws_a_well_formed_svg_with_a_body(shape: str) -> None:
    svg = _svg(shape)
    assert ET.fromstring(svg).tag.endswith("svg")
    assert len(re.findall(r"<(?:rect|path|circle|ellipse)\b", svg)) >= 8, shape
    assert WOOD.base in svg, f"{shape} does not paint the record's color"


@pytest.mark.parametrize(
    ("shape", "key"),
    [(s, k) for s in (*TYPES, "rug") for k in _table(s)],
)
def test_every_value_of_a_param_draws_a_picture_of_its_own(shape: str, key: str) -> None:
    values = _table(shape)[key]
    assert len(values) >= 2, (shape, key)
    pictures = {_svg(shape, **{key: v}) for v in values}
    for svg in pictures:
        ET.fromstring(svg)  # every variant is a well-formed document, not only the default
    assert len(pictures) == len(values), (shape, key)


@pytest.mark.parametrize("form", kit_softfurn.RUG_PARAMS["form"])
def test_every_rug_form_draws_each_pile_and_motif_apart(form: str) -> None:
    for key in ("pile", "motif"):
        values = kit_softfurn.RUG_PARAMS[key]
        assert len({_svg("rug", form=form, **{key: v}) for v in values}) == len(values), (form, key)


@pytest.mark.parametrize("shape", (*TYPES, "rug"))
def test_a_value_outside_the_table_is_refused(shape: str) -> None:
    for key in _table(shape):
        with pytest.raises(ValueError, match=key):
            _svg(shape, **{key: "seventeen"})


def test_each_rug_the_generator_draws_is_the_picture_it_was() -> None:
    """``motif`` defaults to ``none`` and the old forms draw as before: no rug product changes."""
    for (form, pile), digest in RUG_BEFORE.items():
        svg = _svg("rug", form=form, pile=pile)
        assert hashlib.sha256(svg.encode()).hexdigest()[:16] == digest, (form, pile)
        assert svg == _svg("rug", form=form, pile=pile, motif="none"), (form, pile)


def test_a_kids_rug_draws_its_motif_and_a_plain_rug_none() -> None:
    for motif in kit_softfurn.RUG_PARAMS["motif"]:
        drawn = _count(_svg("rug", motif=motif), "motif")
        assert (drawn > 0) == (motif != "none"), motif


def test_a_doormat_shows_its_bristles_and_a_kitchen_mat_its_bevel() -> None:
    assert _count(_svg("rug", form="doormat"), "bristle") > 0
    assert _count(_svg("rug", form="kitchen_mat"), "bevel") == 1
    for form in ("rectangle", "round", "runner"):
        assert _count(_svg("rug", form=form), "bristle") == 0, form
        assert _count(_svg("rug", form=form), "bevel") == 0, form


def test_the_drawn_count_is_the_stated_count() -> None:
    for value in kit_home_variants.PARAMS["vanity_light"]["lights"]:
        assert _count(_svg("vanity_light", lights=value), "shade") == int(value), value
    assert _count(_svg("bench", storage="drawers"), "drawer") == kit_home_variants.BENCH_DRAWERS


def test_a_bench_draws_its_back_and_its_storage_only_when_it_says_so() -> None:
    assert _count(_svg("bench", back="yes"), "back") == 1
    assert _count(_svg("bench", back="no"), "back") == 0
    assert _count(_svg("bench", storage="shelf"), "shelf") == 1
    assert _count(_svg("bench", storage="none"), "shelf") == 0
    assert _count(_svg("bench", storage="none"), "drawer") == 0


@pytest.mark.parametrize(
    ("shape", "params"),
    [("vanity_light", {}), ("bench", {}), ("rug", {"form": "kitchen_mat"})],
)
def test_a_white_piece_reads_white(shape: str, params: dict[str, str]) -> None:
    """At least 80% of the body's painted area keeps 80% of White's own lightness."""
    white = _lum(_rgb(BASE))
    fill = kit.Fill("solid", BASE, "#333333", "#f2d14b")
    lums = _structure_luminances(kit.render(shape, fill, params=params or None))
    assert lums, shape
    light = sum(1 for v in lums if v >= 0.8 * white) / len(lums)
    assert light >= 0.8, (shape, light)


@pytest.mark.parametrize(
    ("shape", "params", "size"),
    [
        ("rug", {"form": "doormat", "pile": "flat"}, {"width": 30, "depth": 18}),
        ("rug", {"form": "kitchen_mat"}, {"width": 39, "depth": 20}),
        ("rug", {"form": "rectangle", "motif": "road"}, {"width": 60, "depth": 40}),
        ("vanity_light", {"lights": "4"}, {"width": 32, "height": 8, "depth": 7}),
        ("bench", {"back": "yes", "storage": "shelf"}, {"width": 60, "height": 34, "depth": 16}),
    ],
)
def test_each_variant_draws_through_render_in_both_finishes(
    shape: str, params: dict[str, str], size: dict[str, float]
) -> None:
    """The public call draws each variant at the dimensions a product states, in either finish."""
    spec = {"color": "#8a5a3a", **size, **params}
    for finish in drawings.FINISHES:
        svg = drawings.render(shape, spec, finish, product_id=f"fixture-{shape}-7", brand=BRAND)
        ET.fromstring(svg)
        assert "#8a5a3a" in svg, (shape, finish)
