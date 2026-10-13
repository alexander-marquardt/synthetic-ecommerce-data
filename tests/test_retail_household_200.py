"""Household types (gen#200): cookware, kitchen bins, storage, laundry baskets, mops, airers.

:mod:`household_rows` holds the styles and :mod:`kit_household` draws them. These checks
hold what the issue asked for: every type has its range (three styles, three brands), each
style draws as its own household shape, each key attribute is a structured entry in the
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
import household_rows  # noqa: E402
import kit  # noqa: E402
import kit_household  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = household_rows.ROWS

#: Each type and the key attributes a shopper filters or searches it on (the issue's table).
KEYS = {
    "Saucepan": {"material", "lid", "hob_type", "oven_safe", "set_or_single", "diameter",
                 "capacity"},
    "Frying Pan": {"pan_type", "material", "coating", "induction_safe", "oven_safe", "diameter"},
    "Casserole Dish": {"material", "shape", "oven_safe", "hob_safe", "capacity"},
    "Kitchen Bin": {"bin_type", "capacity", "compartments", "material"},
    "Storage Box": {"storage_type", "material", "lid", "transparent", "stackable", "capacity"},
    "Laundry Basket": {"laundry_basket_type", "capacity", "compartments", "material"},
    "Clothes Airer": {"airer_type", "drying_length", "tiers"},
    # A flat or sponge mop has no bucket, so only the bucket styles state a capacity.
    "Mop and Bucket": {"mop_type", "refill_heads"},
}  # fmt: skip

#: A saucepan set sells by its pieces (``piece_count``), so it has no diameter or capacity.
SET_EXEMPT = {"diameter", "capacity"}

#: The marked group each counted shape draws once per counted piece, and the attribute
#: that states the count. A single-compartment bin or basket is one undivided body, so it
#: draws no compartment mark; a single saucepan has no ``piece_count`` and draws one pan.
COUNTED = {
    "saucepan": ("pan", "piece_count"),
    "kitchen_bin": ("lid-segment", "compartments"),
    "laundry_basket": ("compartment", "compartments"),
    "clothes_airer": ("tier", "tiers"),
}


def _attr(row: household_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _svg(row: household_rows.Row) -> str:
    return kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))


def _stated(row: household_rows.Row) -> int:
    """The count the record states for its counted shape, as the drawing must show it."""
    cls, key = COUNTED[row.shape]
    got = _attr(row, key)
    n = int(got[0]) if got else 1
    return n if cls in ("pan", "tier") or n > 1 else 0


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[household_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_household_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_household.SHAPES} == {}


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        want = KEYS[ptype] - (SET_EXEMPT if "Set" in _attr(row, "set_or_single") else set())
        if want - keys:
            missing[row.code] = sorted(want - keys)
    assert missing == {}


def test_a_single_saucepans_capacity_rises_with_its_diameter() -> None:
    singles = [
        r for r in ROWS if r.product_type == "Saucepan" and "Single" in _attr(r, "set_or_single")
    ]
    assert singles
    bad = {}
    for row in singles:
        pairs = sorted(
            {(float(s["diameter_cm"]), float(s.get("capacity_l", "nan"))) for s in row.skus()}
        )
        caps = [c for _, c in pairs]
        if len(pairs) < 2 or not all(a < b for a, b in zip(caps, caps[1:], strict=False)):
            bad[row.code] = pairs
    assert bad == {}


def test_a_set_of_saucepans_states_its_piece_count() -> None:
    sets = [r for r in ROWS if r.product_type == "Saucepan" and int(dict(r.params)["count"]) > 1]
    assert sets
    assert {r.code: _attr(r, "piece_count") for r in sets
            if _attr(r, "piece_count") != [dict(r.params)["count"]]} == {}  # fmt: skip


@pytest.mark.parametrize("row", [r for r in ROWS if r.shape in COUNTED], ids=lambda r: r.code)
def test_the_drawing_shows_the_count_its_record_states(row: household_rows.Row) -> None:
    """Pans in a set, a recycling bin's lids, a hamper's openings and an airer's racks: the
    drawing has one marked group per piece the record states."""
    cls = COUNTED[row.shape][0]
    drawn = len(re.findall(rf'<g class="{cls}"', _svg(row)))
    assert drawn == _stated(row)


def test_the_counted_shapes_cover_a_count_above_one_for_every_mark() -> None:
    """The drawn-count test reads a real count for each mark, not only the single ones."""
    big = {COUNTED[r.shape][0] for r in ROWS if r.shape in COUNTED and _stated(r) > 1}
    assert big == {cls for cls, _ in COUNTED.values()}


def test_no_household_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed size would be wrong for all but one."""
    printed = {}
    for row in ROWS:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d\s*(cm|mm|l|L|m|ltr|litre)\b", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_household_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.HOUSEHOLD_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
