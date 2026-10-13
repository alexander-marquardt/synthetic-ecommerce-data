"""Underwear and nightwear types (gen#208): knickers, tights, vests, slips, shapewear,
dressing gowns and boxers.

:mod:`underwear_rows` holds the styles and :mod:`kit_underwear` draws them. These checks hold
what the issue asked for: every type has its range (three styles, three brands), each style
draws as its own shape, each key attribute the issue lists is a structured entry in the
export, a count the record states is the count the drawing shows, and the styles reach the
scaled build.
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

import export  # noqa: E402
import kit  # noqa: E402
import kit_underwear  # noqa: E402
import scale  # noqa: E402
import underwear_rows  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = underwear_rows.ROWS

#: Each type and every key attribute the issue lists for it (its table), by the export key.
#: Size, colour and pack count are pinned as well as the drawn attributes: a table that left
#: the size keys out let a missing size through on the household review. Size is ``size``
#: everywhere but boxers, which sell by ``waist``. Pattern is a colorway (the colour value
#: names it), so the colour key carries it. Audience is on every record.
KEYS = {
    "Knickers": {"cut", "fabric", "pack_size", "size", "color", "audience"},
    "Tights": {"denier", "finish", "size", "pack_size", "color", "control_top", "audience"},
    "Vest": {"audience", "style", "fabric", "pack_size", "size", "color"},
    "Slip": {"length", "fabric", "strap", "size", "color", "audience"},
    "Shapewear": {"control_level", "shapewear_type", "seamless", "size", "color", "audience"},
    "Dressing Gown": {"fabric", "length", "hood", "belt", "audience", "size", "color"},
    "Boxers": {"fit", "fabric", "pack_size", "waist", "color", "audience"},
}  # fmt: skip

#: The keys a SKU states (the variant axes), so a size or a pack count is per SKU.
VARIANT_KEYS = {
    "Knickers": {"color", "size", "pack_size"},
    "Tights": {"color", "size", "pack_size"},
    "Vest": {"color", "size", "pack_size"},
    "Slip": {"color", "size"},
    "Shapewear": {"color", "size"},
    "Dressing Gown": {"color", "size"},
    "Boxers": {"color", "waist", "pack_size"},
}  # fmt: skip


def _attr(row: underwear_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(row: underwear_rows.Row) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _marks(row: underwear_rows.Row) -> dict[str, int]:
    """The marked groups the drawing holds, by class."""
    return dict(collections.Counter(re.findall(r'<g class="([a-z-]+)"', _svg(row))))


def _expected(row: underwear_rows.Row) -> dict[str, int]:
    """The marks the record's attributes say the drawing must hold."""
    p = dict(row.params)
    one = lambda key, yes: _attr(row, key) == [yes]  # noqa: E731
    out: dict[str, int] = {}
    if row.shape == "knickers":
        out = {"waistband": 1, "leg-opening": 2}
    elif row.shape == "tights":
        out = {"leg": 2, "waistband": 1}
        if one("control_top", "Yes"):
            out["control-panel"] = 1
    elif row.shape == "vest":
        out = {"sleeve": 2} if one("style", "Thermal") else {"strap": 2}
    elif row.shape == "slip":
        out = {"strap": 2}
    elif row.shape == "shapewear":
        kind = _attr(row, "shapewear_type")[0]
        if kind in ("Bodysuit", "Bra-Friendly Bodysuit"):
            out["strap"] = 2
        if kind == "Shorts":
            out["waistband"] = 1
        elif kind == "High-Waisted Brief":
            out.update({"waistband": 1, "leg-opening": 2})
        if one("seamless", "No"):
            out["seam-panel"] = 2
        bands = {"Light": 0, "Medium": 1, "Firm": 2}[_attr(row, "control_level")[0]]
        if bands:
            out["control-band"] = bands
    elif row.shape == "dressing_gown":
        out = {"sleeve": 2, "belt": 1} if one("belt", "Yes") else {"sleeve": 2}
        if one("hood", "Yes"):
            out["hood"] = 1
    elif row.shape == "boxers":
        out = {"leg": 2, "fly": 1, "waistband": 1}
    if p.get("trim") == "lace":
        out["lace-trim"] = 1
    return out


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[underwear_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS) == set(underwear_rows.TYPES)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_underwear_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_underwear.SHAPES} == {}
    assert {r.product_type: r.shape for r in ROWS if r.product_type == "Vest"} == {"Vest": "vest"}


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


@pytest.mark.parametrize("ptype", sorted(VARIANT_KEYS))
def test_every_sku_states_its_size_colour_and_pack(ptype: str) -> None:
    short = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        for v in doc["variants"]:
            got = {e["key"] for e in v["attributes"]}
            if VARIANT_KEYS[ptype] - got:
                short[row.code] = sorted(VARIANT_KEYS[ptype] - got)
    assert short == {}


def test_a_pack_states_its_unit_count_and_a_bigger_pack_costs_less_per_unit() -> None:
    bad = {}
    for row in (r for r in ROWS if getattr(r, "packs", ())):
        by_unit: dict[tuple, dict[int, float]] = collections.defaultdict(dict)
        for s in row.skus():
            label = "Single" if s["units_per_pack"] == 1 else f"{s['units_per_pack']} pack"
            if s["pack_size"] != label:
                bad[row.code] = (s["pack_size"], s["units_per_pack"])
            by_unit[(s["color"], s.get("size", s.get("waist")))][s["units_per_pack"]] = (
                s["price"] / s["units_per_pack"]
            )
        for per in by_unit.values():
            units = [per[n] for n in sorted(per)]
            if any(b > a for a, b in zip(units, units[1:], strict=False)):
                bad[row.code] = per
    assert bad == {}


def test_tights_are_stocked_in_every_denier_the_issue_lists() -> None:
    assert {int(a) for r in ROWS if r.product_type == "Tights" for a in _attr(r, "denier")} >= {
        10, 15, 20, 40, 60, 100
    }  # fmt: skip


def test_patterned_colorways_exist() -> None:
    names = {c[0] for r in ROWS for c in r.colors}
    assert any(re.search(r"Polka Dot|Stripe|Leopard", n) for n in names)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_the_drawing_shows_the_marks_its_record_states(row: underwear_rows.Row) -> None:
    """Straps, sleeves, legs, a hood, a belt, control bands and panels, a lace trim: the
    drawing holds one marked group per piece the record's attributes state, and no other."""
    assert _marks(row) == _expected(row)


def test_every_counted_mark_is_drawn_both_present_and_absent_across_the_range() -> None:
    """Each optional mark is present on some record and absent from another, so the
    drawn-count test reads a real difference and not a constant."""
    optional = {"control-panel", "lace-trim", "seam-panel", "control-band", "hood", "sleeve"}
    seen_with = {m for r in ROWS for m in _marks(r)}
    absent_somewhere = {m for m in optional if any(m not in _marks(r) for r in ROWS)}
    assert optional <= seen_with
    assert optional == absent_somewhere


def test_no_underwear_drawing_prints_a_size_or_a_pack_count() -> None:
    """A style's sizes and packs share one image, so a printed one would be wrong for most."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        if words:
            printed[row.code] = words
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_underwear_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.UNDERWEAR_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
