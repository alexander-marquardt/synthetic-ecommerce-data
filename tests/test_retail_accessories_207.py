"""Bags, umbrellas and jewelry (gen#207): handbag, backpack, tote bag, purse, umbrella,
necklace, bracelet and ring.

:mod:`accessory_rows` holds the styles and :mod:`kit_accessories` draws them. These checks
hold what the issue asked for: every type has its range (three styles, three brands), each
style draws as its own shape, each key attribute the issue lists is a structured entry in the
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

import accessory_rows  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_accessories  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = accessory_rows.ROWS

#: Each type and the key attributes every one of its styles states (the issue's table; the
#: ones only some styles have are in ``CONDITIONAL``). A key is an attribute of the style or
#: of its SKUs: the size keys (``size``, ``capacity_l``/``capacity``, ``canopy_diameter``,
#: ``item_length``, ``size_uk``/``size_us``) are pinned as well as the descriptive ones.
KEYS = {
    "Handbag": {"bag_style", "material", "closure", "color"},
    "Backpack": {"use", "capacity", "material", "pocket_count", "waterproof", "color"},
    "Tote Bag": {"size", "material", "closure", "pocket", "color"},
    "Purse": {"purse_type", "material", "closure", "rfid_blocking", "color"},
    "Umbrella": {"umbrella_type", "canopy_diameter", "automatic_open", "windproof",
                 "uv_protection", "ribs", "color"},
    "Necklace": {"necklace_type", "metal", "item_length", "color"},
    "Bracelet": {"bracelet_type", "metal", "size", "color"},
    "Ring": {"ring_type", "metal", "size_uk", "size_us", "color"},
}  # fmt: skip


def _attr(row: accessory_rows.ARow, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _keys(row: accessory_rows.ARow) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def _conditional(row: accessory_rows.ARow) -> set[str]:
    """The keys the issue lists that a style states only when it has the thing."""
    want: set[str] = set()
    if row.product_type == "Handbag":
        if dict(row.params)["style"] != "clutch":
            want.add("size")  # a clutch is one size
        if dict(row.params)["style"] in ("shoulder", "crossbody", "bucket"):
            want.add("strap")
    if row.product_type == "Backpack" and "laptop" in dict(row.params)["use"]:
        want.add("laptop_size")
    if row.product_type in ("Necklace", "Bracelet", "Ring") and dict(row.params).get("stone"):
        want.add("stone")
    if any(c[1] != "solid" for c in row.colors):
        want.add("pattern")
    return want


#: The marked group each counted shape draws, the attribute that states the count, and what
#: the drawing must show when the record states none (a plain ring draws no band; a necklace
#: that is not layered draws its one chain).
COUNTED = {
    "backpack": ("pocket", "pocket_count", 1),
    "tote_bag": ("pocket", "pocket", 0),
    "purse": ("slot", "card_slots", 0),
    "umbrella": ("rib", "ribs", 0),
    "necklace": ("chain", "layers", 1),
    "bracelet": ("charm", "charms", 0),
    "ring": ("band", "piece_count", 0),
}


def _svg(row: accessory_rows.ARow) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _stated(row: accessory_rows.ARow) -> int:
    """The count the record states for its counted shape, as the drawing must show it."""
    _, key, default = COUNTED[row.shape]
    got = _attr(row, key)
    if not got:
        return default
    return {"Yes": 1, "No": 0}.get(got[0]) if row.shape == "tote_bag" else int(got[0])


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[accessory_rows.ARow]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_accessory_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_accessories.SHAPES} == {}
    assert len({r.shape for r in ROWS}) == len(KEYS)


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        want = KEYS[ptype] | _conditional(row)
        if want - _keys(row):
            missing[row.code] = sorted(want - _keys(row))
    assert missing == {}


def test_the_size_keys_are_on_the_skus_not_only_the_style() -> None:
    """Each type's size axis is a value every SKU states, so a size filter can narrow it."""
    axis = {"Backpack": "capacity_l", "Umbrella": "canopy_cm", "Necklace": "length_cm",
            "Bracelet": "size", "Ring": "size_uk"}  # fmt: skip
    bad = {}
    for row in ROWS:
        key = axis.get(row.product_type)
        if key and not all(key in s for s in row.skus()):
            bad[row.code] = key
    assert bad == {}


@pytest.mark.parametrize("row", [r for r in ROWS if r.shape in COUNTED], ids=lambda r: r.code)
def test_the_drawing_shows_the_count_its_record_states(row: accessory_rows.ARow) -> None:
    """Pockets, card slots, umbrella ribs, necklace layers, charms and stacked bands: the
    drawing has one marked group per piece the record states."""
    cls = COUNTED[row.shape][0]
    drawn = len(re.findall(rf'<g class="{cls}"', _svg(row)))
    assert drawn == _stated(row)


def test_the_counted_shapes_cover_a_count_above_one_for_every_mark() -> None:
    """The drawn-count test reads a real count for each mark, not only a zero or a one."""
    big = {COUNTED[r.shape][0] for r in ROWS if r.shape in COUNTED and _stated(r) > 1}
    assert big == {cls for cls, _, _ in COUNTED.values()}


def test_a_handbag_draws_no_counted_mark() -> None:
    """The handbag counts nothing: its style, flap and strap are shapes, not counts."""
    assert "handbag" not in COUNTED
    assert all('<g class="pocket"' not in _svg(r) for r in ROWS if r.shape == "handbag")


def test_no_accessory_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed size would be wrong for all but one."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d\s*(cm|mm|l|L|in|ltr|litre)\b", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_accessory_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.ACCESSORY_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []


@pytest.mark.timeout(300)
def test_every_brand_has_exactly_one_owner_across_templates_and_derived_styles() -> None:
    """``OWNERS.setdefault`` hides a clash, and a derived style takes ``third_party`` for a
    brand the base does not own, so the owner is read off the built records. Scoped to the
    brands these rows sell: other families' clashes are not this change's."""
    records = scale.build(100_000).records
    owners: dict[str, set[str]] = collections.defaultdict(set)
    for rec in [*scale.templates(), *records]:
        if "brand_owner" in rec:
            owners[rec["brand"]].add(rec["brand_owner"])
    mine = {r.brand for r in ROWS}
    assert mine <= set(owners)
    assert {b: sorted(o) for b, o in owners.items() if b in mine and len(o) != 1} == {}


def test_the_jute_tote_description_names_the_closure_it_states() -> None:
    row = next(r for r in ROWS if r.code == "TTBJUT")
    assert "zip" in row.description.lower() and "magnetic" not in row.description.lower()
    assert all(c[1] == "solid" for c in row.colors), "no style-level pattern: a SKU is solid"


def test_every_polka_dot_umbrella_sku_is_polka_dot() -> None:
    row = next(r for r in ROWS if r.code == "UMBPOL")
    assert [c[1] for c in row.colors] == ["polka"] * len(row.colors)
