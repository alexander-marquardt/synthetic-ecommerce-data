"""Two beauty products of different lines draw different packs, and a product keeps one (gen#748).

A foundation, a face cream, a moisturiser, a bath salt and a perfume each drew one pack, so a page
of separate products read as a grouping failure. These tests read what the release draws: a SKU's
image with its colors and words taken out is the picture a line owns.
"""

from __future__ import annotations

import copy
import itertools
import re

import pytest

from synthetic_ecommerce_data.domains.retail import (
    export,
    image_release,
    kit,
    kit_home,
    kit_packs,
    lipstick_looks,
    pack_looks,
    scale,
    shades,
    sheet_extent,
)
from synthetic_ecommerce_data.domains.retail.line_grammar_families.beauty import (
    LEADS,
    NUMBERS,
    SUBS,
)

TEMPLATES = {
    "Foundation": "BEA-FNDFTH",
    "Face Cream": "PLT-FCDAYC",
    "Moisturiser": "BEA-TNTMST",
    "Bath Salts": "BRD-BSLLAV",
    "Perfume": "BRD-PERJAS",
}
RECORDS = {r["product_id"]: r for r in scale.templates()}
KINDS = sorted(TEMPLATES)


def _product(kind: str, line: str | None = "Renew 2", title: str = "A Pack") -> dict:
    """A copy of ``kind``'s template on ``line``, under ``title``."""
    rec = copy.deepcopy(RECORDS[TEMPLATES[kind]])
    rec["product_line"], rec["title"] = line, title
    return rec


def _outline(rec: dict, sku: dict) -> str:
    """What ``sku``'s image draws, with its colors, its words, its size and its ids gone."""
    svg = image_release.render(rec, sku, styled=False).decode().replace(rec["product_id"], "ID")
    svg = re.sub(r"<(text|title)\b.*?</\1>", "", svg, flags=re.S)
    svg = re.sub(r'<g class="pack"[^>]*>|(?<=/>)</g>', "", svg)
    return re.sub(r'#[0-9a-fA-F]{3,8}\b', "", svg)


def _spec(rec: dict) -> dict:
    return export.drawing_spec(rec, rec["skus"][0]).get("params", {})


@pytest.mark.parametrize("kind", KINDS)
def test_two_lines_of_a_kind_draw_two_outlines(kind: str) -> None:
    one, other = _product(kind, "Renew 2"), _product(kind, "Radiance Pro 7")
    assert _outline(one, one["skus"][0]) != _outline(other, other["skus"][0])


@pytest.mark.parametrize("kind", KINDS)
def test_two_titles_with_no_model_draw_two_outlines(kind: str) -> None:
    one, other = _product(kind, None, "Rose Veil"), _product(kind, None, "Night Harbor")
    assert _outline(one, one["skus"][0]) != _outline(other, other["skus"][0])


@pytest.mark.parametrize("kind", KINDS)
def test_every_model_of_the_grammar_has_a_look_of_its_own(kind: str) -> None:
    subs = ("", *(f"{s} " for s in SUBS))
    lines = [f"{a} {b}{n}" for a, b, n in itertools.product(LEADS, subs, NUMBERS)]
    assert len({str(_spec(_product(kind, line))) for line in lines}) == len(lines)


def test_a_foundations_shades_share_one_pack() -> None:
    rec = _product("Foundation")
    assert len(rec["skus"]) == 40
    assert len({_outline(rec, s) for s in rec["skus"]}) == 1
    top = f'fill="{_spec(rec)["top_color"]}"'
    assert all(top in image_release.render(rec, s).decode() for s in rec["skus"])


def test_a_foundations_top_is_no_shade_of_its_range() -> None:
    rec = _product("Foundation")
    range_of_shades = {c["hex"].lower() for c in rec["color_options"]}
    assert rec["product_type"] in shades.SOLD_BY_SHADE
    assert range_of_shades and not range_of_shades & {c.lower() for c in pack_looks.CASE_COLORS}


def test_a_kind_outside_the_table_has_no_look() -> None:
    rec = copy.deepcopy(next(r for r in RECORDS.values() if r["product_type"] == "Hand Wash"))
    assert rec["drawing"]["shape"] == "bottle"
    assert pack_looks.params(rec) == {}


def test_a_kind_drawn_as_another_shape_has_no_look() -> None:
    rec = _product("Foundation")
    rec["drawing"]["shape"] = "lipstick"
    assert pack_looks.params(rec) == {}


def test_the_kinds_are_the_families_of_their_shapes() -> None:
    assert sorted(pack_looks.KINDS) == KINDS
    assert set(pack_looks.KINDS.values()) == set(kit_packs.FAMILIES)
    assert set(pack_looks.BASES) == set(KINDS)


@pytest.mark.parametrize("kind", KINDS)
def test_a_look_names_every_choice_from_the_kinds_family(kind: str) -> None:
    choices = pack_looks.choices(kind)
    look = pack_looks.params(_product(kind))
    assert set(look) == set(choices)
    assert all(look[name] in options for name, options in choices.items())


@pytest.mark.parametrize("kind", KINDS)
def test_the_kinds_looks_have_room_for_every_place(kind: str) -> None:
    room = 1
    for options in pack_looks.choices(kind).values():
        room *= len(options)
    assert lipstick_looks.MODELS < pack_looks.PRIME < room


@pytest.mark.parametrize("kind", KINDS)
def test_each_model_lands_on_its_own_place(kind: str) -> None:
    base, start = pack_looks.BASES[kind]
    places = {pow(base, start + n, pack_looks.PRIME) for n in range(lipstick_looks.MODELS)}
    assert len(places) == lipstick_looks.MODELS


def test_a_kind_reads_its_own_base() -> None:
    a, b = pack_looks.place("Foundation", "Renew 2"), pack_looks.place("Perfume", "Renew 2")
    assert a != b


FILL = kit.Fill("solid", "#e3bfa0", "#333333")
LOOK = {"top_color": "#123456", "emblem": "dot", "trim": "#654321"}


def _drawn(shape: str, label: str | None = "Word", **look: str) -> str:
    return kit.render(shape, FILL, label, params=LOOK | look)


@pytest.mark.parametrize(
    ("shape", "form", "top"),
    [(s, f, t) for s, fam in kit_packs.FAMILIES.items() for f in fam.forms for t in fam.tops],
)
def test_every_pack_fits_the_sheet_and_prints_its_label(shape: str, form: str, top: str) -> None:
    svg = _drawn(shape, form=form, top=top)
    assert sheet_extent.overrun(svg, 400.0) == 0
    assert ">Word<" in svg
    assert 'fill="#123456"' in svg


@pytest.mark.parametrize("shape", sorted(kit_packs.FAMILIES))
def test_each_form_and_each_top_draws_an_outline_of_its_own(shape: str) -> None:
    family = kit_packs.FAMILIES[shape]
    form, top = next(iter(family.forms)), next(iter(family.tops))
    assert len({_drawn(shape, form=f, top=top) for f in family.forms}) == len(family.forms) >= 6
    assert len({_drawn(shape, form=form, top=t) for t in family.tops}) == len(family.tops) >= 6


@pytest.mark.parametrize("top", sorted(kit_packs.NECK_TOPS))
def test_every_neck_top_draws_its_color_and_the_trim_where_it_has_one(top: str) -> None:
    drawn = "".join(kit_packs.NECK_TOPS[top](94, 24, "#123456", "#654321"))
    assert 'fill="#123456"' in drawn
    assert ('fill="#654321"' in drawn) == (top in ("tall", "ball", "pump", "dropper"))


@pytest.mark.parametrize("top", sorted(kit_packs.LIDS))
def test_every_lid_draws_its_color_and_the_trim_where_it_has_one(top: str) -> None:
    drawn = "".join(kit_packs.LIDS[top](198, 92, "#123456", "#654321"))
    assert 'fill="#123456"' in drawn
    assert ('fill="#654321"' in drawn) == (top in ("smooth", "dome", "knob"))


def test_the_emblem_and_its_trim_are_drawn_at_the_forms_mark() -> None:
    form = kit_packs.BOTTLES["square"]
    svg = _drawn("bottle", form="square", top="block")
    assert f'<circle cx="{form.mark[0]}" cy="{form.mark[1]}" r="10" fill="#654321"' in svg
    assert "<circle" not in _drawn("bottle", form="square", top="block", emblem="none")


def test_a_flacon_stands_on_its_collar_and_prints_its_stamp() -> None:
    svg = _drawn("fragrance", form="block", top="block")
    assert '<rect x="184" y="104" width="32" height="24"' in svg
    assert '<rect x="170" y="48"' in svg  # the top sits above the collar
    assert "EAU DE PARFUM" in svg
    assert "EAU DE PARFUM" in _drawn("fragrance", None, form="block", top="block")
    assert _drawn("fragrance", None, form="block", top="block").count("<text") == 1


def test_a_bottle_prints_no_stamp_and_its_top_sits_on_its_mouth() -> None:
    svg = _drawn("bottle", form="shouldered", top="block")
    assert "EAU DE PARFUM" not in svg
    assert '<rect x="176" y="36" width="48" height="58"' in svg


def test_a_top_is_no_wider_than_its_form_can_carry() -> None:
    slim = kit_packs.JARS["tall"]
    assert slim.panel[2] * 0.62 < kit_packs.FAMILIES["jar"].half
    assert f'width="{2 * slim.panel[2] * 0.62 + 16:g}"' in _drawn("jar", form="tall", top="smooth")


@pytest.mark.parametrize("shape", sorted(kit_packs.FAMILIES))
def test_a_shape_with_no_look_draws_as_it_did(shape: str) -> None:
    plain = {
        "bottle": kit.bottle,
        "jar": kit.jar,
        "moisturiser_jar": kit_home.moisturiser_jar,
        "fragrance": kit_home.fragrance,
    }[shape]
    assert kit.SHAPES[shape] is not plain
    assert kit.SHAPES[shape]("#abcdef", FILL, "Word") == plain("#abcdef", FILL, "Word")


def test_a_jar_of_either_shape_draws_a_jar_under_a_lid() -> None:
    for shape in ("jar", "moisturiser_jar"):
        assert kit_packs.FAMILIES[shape].forms is kit_packs.JARS
        assert kit_packs.FAMILIES[shape].tops is kit_packs.LIDS
