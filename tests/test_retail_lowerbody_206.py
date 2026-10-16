"""Lower-body types (gen#206): leggings, joggers, shorts, cycling shorts, tracksuits, skirts.

:mod:`lowerbody_rows` holds the styles and :mod:`kit_lowerbody` draws them. These checks hold
what the issue asked for: every type has its range (six styles, three brands), each style
draws as its own lower-body shape, each key attribute (the size keys too) is a structured
entry in the export, every mark a record states is the mark the drawing shows, a color is a
plain color word, and the styles reach the scaled build.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402
import export  # noqa: E402
import image_release  # noqa: E402
import kit  # noqa: E402
import kit_lowerbody  # noqa: E402
import lowerbody_rows  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402
import variants  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: The tracksuits are a type spec (gen#351); the other five types are still in lowerbody_rows.
ROWS = (*lowerbody_rows.ROWS, *type_registry.specs()["tracksuit"].rows)
LOWER_DOCS = [*lowerbody_rows.docs(), *type_registry.specs()["tracksuit"].docs()]
LOWER_IDS = scale.LOWER_IDS | type_registry.ids_of(type_registry.specs()["tracksuit"])

#: Each type and every attribute a shopper filters or searches it on (the issue's table),
#: the color and the size keys of its SKUs included. ``garment_length`` is the length the
#: shopper reads ("7/8", "Mini"); ``inside_leg`` and ``fit_length`` are the SKU axes.
KEYS = {
    "Leggings": {"garment_length", "rise", "fabric", "leg_fit", "pockets", "pattern",
                 "maternity", "lining", "color", "size"},
    "Joggers": {"leg_fit", "cuff", "fabric", "rise", "pockets", "cargo_pockets", "waist_type",
                "color", "size", "inside_leg"},
    "Shorts": {"garment_length", "shorts_style", "rise", "fabric", "waist_type", "pockets",
               "color", "size"},
    "Cycling Shorts": {"garment_length", "rise", "leg_fit", "padding", "pockets", "color",
                       "size"},
    "Tracksuit": {"piece_count", "top_style", "leg_fit", "fabric", "audience", "color", "size",
                  "sold_as"},
    "Skirt": {"garment_length", "skirt_shape", "fabric", "waist_type", "lining", "pattern",
              "color", "size", "fit_length"},
}  # fmt: skip

#: The shape name each skirt record states for the ``shape`` it draws.
SHAPE_NAMES = {"a_line": "A-Line", "pleated": "Pleated", "pencil": "Pencil", "wrap": "Wrap",
               "tiered": "Tiered", "tennis": "Tennis"}  # fmt: skip

#: Every marked group the lower-body drawings count.
MARKS = ("pocket", "cargo-pocket", "belt-loop", "piece", "tier", "pad")


def _attr(row: lowerbody_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(row: lowerbody_rows.Row) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _drawn(row: lowerbody_rows.Row, cls: str) -> int:
    return len(re.findall(rf'<g class="{cls}"', _svg(row)))


def _stated(row: lowerbody_rows.Row) -> dict[str, int]:
    """How many of each mark the record says its drawing shows: two pockets when it has
    pockets, two cargo pockets, four belt loops when the waist is belted, one group per piece
    or tier, one pad when it is padded."""
    pieces, tiers = _attr(row, "piece_count"), _attr(row, "tiers")
    return {
        "pocket": 2 if _attr(row, "pockets") == ["Yes"] else 0,
        "cargo-pocket": 2 if "Yes" in _attr(row, "cargo_pockets") or "Cargo" in _attr(
            row, "shorts_style") else 0,
        "belt-loop": 4 if "Belted" in _attr(row, "waist_type") else 0,
        "piece": int(pieces[0]) if pieces else 0,
        "tier": int(tiers[0]) if tiers else 0,
        "pad": 1 if _attr(row, "padding") == ["Padded"] else 0,
    }  # fmt: skip


def test_every_type_has_six_styles_from_three_brands() -> None:
    styles: dict[str, list[lowerbody_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if n[0] < 6 or n[1] < 3} == {}


def test_every_style_draws_as_its_own_lower_body_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_lowerbody.SHAPES} == {}
    one_to_one = {r.product_type: r.shape for r in ROWS}
    assert len(set(one_to_one.values())) == len(KEYS)


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if KEYS[ptype] - keys:
            missing[row.code] = sorted(KEYS[ptype] - keys)
    assert missing == {}


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_the_drawing_shows_every_mark_its_record_states(row: lowerbody_rows.Row) -> None:
    """Pockets, cargo pockets, belt loops, pieces, tiers and a pad: the drawing has exactly
    the marked groups the record states, and none it does not."""
    assert {cls: _drawn(row, cls) for cls in MARKS} == _stated(row)


def test_the_drawn_count_test_reads_every_mark_above_zero_and_at_zero() -> None:
    """Each mark is stated by some record and absent from another, so a style that drew all
    of them (or none) could not pass the drawn-count test above."""
    on = {cls for r in ROWS for cls, n in _stated(r).items() if n}
    off = {cls for r in ROWS for cls, n in _stated(r).items() if not n}
    assert on == set(MARKS) == off
    assert {n for r in ROWS for n in [_stated(r)["piece"]]} == {0, 2, 3}


def test_belted_shorts_and_only_they_draw_belt_loops() -> None:
    belted = {r.code for r in ROWS if "Belted" in _attr(r, "waist_type")}
    assert belted == {r.code for r in ROWS if r.shape == "shorts" and _drawn(r, "belt-loop")}
    assert {_attr(r, "shorts_style")[0] for r in ROWS if r.code in belted} == {
        "Chino",
        "Cargo",
        "Tailored",
        "Bermuda",
    }


def test_a_legging_s_length_and_rise_are_the_ones_it_draws() -> None:
    for row in (r for r in ROWS if r.product_type == "Leggings"):
        p = dict(row.params)
        length = {"full": "Full Length", "7_8": "7/8", "cropped": "Cropped"}[p["length"]]
        assert _attr(row, "garment_length") == [length], row.code
        assert dict(row.facts)["rise"].lower() == p["rise"], row.code
    lengths = {_attr(r, "garment_length")[0] for r in ROWS if r.product_type == "Leggings"}
    assert lengths == {"Full Length", "7/8", "Cropped"}


def test_a_jogger_states_the_cuff_and_the_fit_it_draws() -> None:
    for row in (r for r in ROWS if r.product_type == "Joggers"):
        p = dict(row.params)
        cuff = {"elastic": "Elasticated", "open": "Open Hem"}[p["cuff"]]
        assert _attr(row, "cuff") == [cuff], row.code
        assert _attr(row, "leg_fit") == [p["fit"].title()], row.code
        assert dict(row.facts)["rise"].lower() == p["rise"], row.code
    assert {dict(r.params)["fit"] for r in ROWS if r.product_type == "Joggers"} == {
        "slim",
        "regular",
        "relaxed",
        "oversized",
    }


def test_a_skirt_states_the_shape_and_the_length_it_draws() -> None:
    skirts = [r for r in ROWS if r.product_type == "Skirt"]
    for row in skirts:
        p = dict(row.params)
        assert _attr(row, "skirt_shape") == [SHAPE_NAMES[p["shape"]]], row.code
        assert _attr(row, "garment_length") == [p["hem"].title()], row.code
    assert {dict(r.params)["shape"] for r in skirts} == set(kit_lowerbody.SKIRT_SHAPES)
    assert {_attr(r, "garment_length")[0] for r in skirts} == {"Mini", "Midi", "Maxi"}


def _built(build):
    """What ``build()`` returns, or the error it raises (so a collision fails on an assertion)."""
    try:
        return build()
    except TypeError as err:
        return {"collision": str(err)}


def test_drawing_takes_a_param_named_shape_beside_the_shape_it_draws() -> None:
    navy = variants.cw("Navy", "#1f2a44")
    out = _built(lambda: variants.drawing("skirt", navy, None, shape="pleated", hem="midi"))
    assert out.get("shape") == "skirt", out
    assert out.get("params") == {"shape": "pleated", "hem": "midi"}, out


def test_a_skirt_row_builds_its_document_without_stripping_its_shape_param() -> None:
    from breadth_rows import Row

    for row in (r for r in lowerbody_rows.ROWS if r.product_type == "Skirt"):
        out = _built(lambda row=row: Row.doc(row))
        assert out.get("drawing", {}).get("params") == dict(row.params), (row.code, out)
        assert out["drawing"]["shape"] == "skirt", row.code


def test_a_tracksuit_is_sold_as_a_set_or_either_piece_in_each_size() -> None:
    for row in (r for r in ROWS if r.product_type == "Tracksuit"):
        skus = row.skus()
        assert {s["sold_as"] for s in skus} == {"Set", "Jacket Only", "Bottoms Only"}
        by = {s["sold_as"]: s["price"] for s in skus if s["color"] == skus[0]["color"]
              and s["size"] == skus[0]["size"]}  # fmt: skip
        assert by["Set"] > by["Jacket Only"] > by["Bottoms Only"], row.code
        pieces = int(_attr(row, "piece_count")[0])
        assert pieces == int(dict(row.params)["pieces"]), row.code


def test_the_tracksuits_cover_every_audience() -> None:
    audiences = {
        e["value"]
        for r in ROWS
        if r.product_type == "Tracksuit"
        for e in export.standard_document(r.doc())["attributes"]
        if e["key"] == "audience"
    }
    assert audiences == {"Womens", "Mens", "Boys", "Girls"}


def test_the_leg_and_skirt_lengths_state_the_size_range_they_serve() -> None:
    for row in (r for r in ROWS if r.product_type in ("Joggers", "Skirt")):
        assert row.doc()["size_range"] == ["regular", "petite", "tall"], row.code


def test_the_maternity_and_lined_leggings_state_it() -> None:
    legs = [r for r in ROWS if r.product_type == "Leggings"]
    assert {r.code for r in legs if _attr(r, "maternity") == ["Yes"]} == {"LGGMAT"}
    assert {r.code for r in legs if _attr(r, "lining") == ["Fleece"]} == {"LGGFLC"}
    assert {_attr(r, "fabric")[0] for r in legs} >= {"Cotton Blend", "Knitted", "Faux Leather"}


#: Words the lower-body rows once put in ``fabric`` that a shopper does not name as a fabric
#: (a use, a fit, a pocket style) or that spell another fabric's name again (gen#258).
NOT_FABRICS = {"Sports", "Compression", "Cargo", "Leather-Look", "Leather Look"}


def test_no_lower_body_fabric_is_a_use_a_fit_or_another_name_for_a_fabric() -> None:
    """``Faux Leather`` is the one name (the bags and purses use it); ``Leather-Look`` was the
    same fabric on a skirt, so one filter split it. A sports leggings' knit, a cargo jogger's
    twill and a cycling short's compression fit are stated as what they are."""
    fabrics = {a[2] for r in ROWS for a in r.attrs if a[0] == "fabric"}
    assert fabrics & NOT_FABRICS == set()
    skirt = next(r for r in ROWS if r.code == "SKTPNC")
    assert _attr(skirt, "fabric") == ["Faux Leather"]
    assert skirt.title == "Faux Leather Pencil Skirt"
    assert {r.code: _attr(r, "fabric") for r in ROWS if r.code in {"JGGCRG", "JGGWCR"}} == {
        "JGGCRG": ["Twill"], "JGGWCR": ["Twill"]}


def test_a_cycling_short_is_compression_fit_not_a_compression_fabric() -> None:
    shorts = [r for r in ROWS if r.product_type == "Cycling Shorts"]
    assert shorts
    for row in shorts:
        assert _attr(row, "leg_fit") == ["Compression"], row.code
        assert _attr(row, "fabric") == [], row.code


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_color_is_a_plain_color_word(row: lowerbody_rows.Row) -> None:
    assert [c[0] for c in row.colors if not colorwords.is_plain(c[0])] == []
    assert [s["color"] for s in row.skus() if not colorwords.is_plain(s["color"])] == []


def test_no_lower_body_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed size would be wrong for all but one."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d|\b(XS|S|M|L|XL)\b", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_lower_body_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in LOWER_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []


def test_no_sku_key_shares_a_name_with_a_drawing_param() -> None:
    """A SKU's own value of a drawing param key replaces the drawing's (``export.drawing_spec``),
    so a SKU field named like a param would redraw the style from its size axis. A skirt's hem
    param is ``hem`` and its SKUs carry ``fit_length``."""
    for rec in LOWER_DOCS:
        params = set(rec["drawing"].get("params") or {})
        for sku in rec["skus"]:
            assert not params & set(sku), (rec["product_id"], params & set(sku))


def test_every_length_a_lower_body_row_can_carry_is_drawable() -> None:
    """Each SKU of each row, with the SKU's own values laid over the drawing as the image
    release does, draws without error, and a skirt's SKU draws what its row draws whatever
    leg length the SKU carries."""
    for rec in LOWER_DOCS:
        for sku in rec["skus"]:
            svg = image_release.render(rec, sku)
            if rec["drawing"]["shape"] == "skirt":
                bare = {k: v for k, v in sku.items() if k != "fit_length"}
                assert svg == image_release.render(rec, bare), (rec["product_id"], sku["sku"])
