"""The bicycle range is built by code from a small table of axes (gen#685).

The maintainer's ask: about 20 bicycles, built algorithmically, with the decoys still working.
:mod:`type_specs.bicycle` crosses the brands, each kind's trims (gears, wheel, frame material and
brake) and the model year: every brand sells every trim, and for each trim one brand, in turn,
still sells last year's model. Each product keeps the shape the four authored bikes had: four
colors times three frame sizes (a kids' bike: three wheel sizes) as its SKUs. Its title, series and
model number come from :mod:`bicycle_model_numbers`, and its price follows from its parts.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import bicycle_model_numbers as bmn  # noqa: E402
from type_specs import bicycle  # noqa: E402

#: The rank of a part, cheaper first: a bike whose parts all rank at least as high, and one higher,
#: costs more.
MATERIAL = {"Steel": 0, "Aluminum": 1, "Carbon": 2}
BRAKE = {"Coaster": 0, "Rim": 1, "Disc": 2}


def _attrs(row) -> dict[str, str]:
    return {a[0]: a[2] for a in row.attrs}


def _axes(row) -> tuple:
    a = _attrs(row)
    wheel = int(a["wheel_size"]) if "wheel_size" in a else None
    return (row.brand, a["bike_type"], int(a["gears"]), wheel, int(a["model_year"]))


def test_the_spec_holds_about_twenty_bikes_with_distinct_model_numbers():
    rows = bicycle.SPEC.rows
    assert 18 <= len(rows) <= 22, len(rows)
    codes = [_attrs(r)["model_number"] for r in rows]
    assert len(set(codes)) == len(rows)
    assert len({r.code for r in rows}) == len(rows)


def test_every_code_decodes_to_its_brand_kind_wheel_gears_and_year():
    for row in bicycle.SPEC.rows:
        brand, kind, gears, wheel, year = _axes(row)
        got = bmn.decode(_attrs(row)["model_number"])
        assert got == {"brand": brand, "kind": kind, "wheel": wheel, "gears": gears, "year": year}
        assert row.product_line == bmn.series_for(brand, kind)
        assert row.title.startswith(f"{brand} {row.product_line} {_attrs(row)['model_number']} ")


def test_no_two_bikes_share_brand_kind_gears_wheel_and_year():
    axes = [_axes(r) for r in bicycle.SPEC.rows]
    assert len(set(axes)) == len(axes)


def test_the_build_is_deterministic_and_is_the_spec():
    assert bicycle.build() == bicycle.build() == bicycle.SPEC.rows


def test_every_brand_sells_every_kind_in_both_model_years():
    rows = bicycle.SPEC.rows
    brands = {r.brand for r in rows}
    assert brands == set(bmn.SCHEMES)
    for brand in brands:
        assert {_axes(r)[1] for r in rows if r.brand == brand} == set(bmn.KINDS), brand
    assert {_axes(r)[4] for r in rows} == {bmn.MODEL_YEAR, bmn.MODEL_YEAR - 1}


def test_each_bike_keeps_four_colors_times_three_sizes():
    for row in bicycle.SPEC.rows:
        kids = _attrs(row)["bike_type"] == "Kids"
        assert row.size_key == ("wheel_size_in" if kids else "frame_cm"), row.code
        assert len(row.colors) == 4 and len(row.sizes) == 3, row.code
        assert len(row.skus()) == 12, row.code


def test_the_price_follows_the_parts():
    """Brand does not price a bike; last year's model costs less than this year's of the same trim,
    and within a kind and year a bike whose parts dominate another's costs more."""
    rows = bicycle.SPEC.rows
    trims: dict[tuple, dict[int, set[float]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        a = _attrs(row)
        _, kind, gears, wheel, year = _axes(row)
        trims[(kind, gears, wheel, a["frame_material"], a["brake_type"])][year].add(row.price)
    carried = [t for t in trims.values() if len(t) == 2]
    assert carried, "no trim is sold in two model years"
    for by_year in trims.values():
        assert all(len(prices) == 1 for prices in by_year.values()), by_year
    for by_year in carried:
        assert max(by_year[bmn.MODEL_YEAR - 1]) < min(by_year[bmn.MODEL_YEAR])

    def parts(row) -> tuple[int, int, int]:
        a = _attrs(row)
        return (MATERIAL[a["frame_material"]], BRAKE[a["brake_type"]], int(a["gears"]))

    pairs = 0
    for one in rows:
        for other in rows:
            same = _axes(one)[1] == _axes(other)[1] and _axes(one)[4] == _axes(other)[4]
            p, q = parts(one), parts(other)
            if same and p != q and all(x >= y for x, y in zip(p, q, strict=True)):
                pairs += 1
                assert one.price > other.price, (one.title, other.title)
    assert pairs, "no two bikes of a kind and year where one's parts dominate"
