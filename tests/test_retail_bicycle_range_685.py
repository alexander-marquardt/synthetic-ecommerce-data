"""The bicycle range is built by code from a small table of axes (gen#685, gen#718).

The maintainer's ask: about 20 bicycles, built algorithmically, with the decoys still working, and
then ten brands. :mod:`type_specs.bicycle` crosses each kind's trims (gears, wheel, frame material
and brake) with the brands that sell the kind and the model year: for each trim every third
brand, in turn, still sells last year's model. Each product keeps the shape the four authored bikes
had: four colors times three frame sizes (a kids' bike: three wheel sizes) as its SKUs. Its title,
series and model number come from :mod:`bicycle_model_numbers`, and its price follows from its
parts.
"""

from __future__ import annotations

from collections import defaultdict

from synthetic_ecommerce_data.domains.retail import bicycle_model_numbers as bmn
from synthetic_ecommerce_data.domains.retail.type_specs import bicycle

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


def test_the_spec_holds_a_bike_per_trim_each_brand_sells_with_distinct_model_numbers():
    rows = bicycle.SPEC.rows
    sold = {brand: set(series) for brand, series in bmn.SERIES.items()}
    trims = {kind.name: len(kind.trims) for kind in bicycle.KINDS}
    assert len(rows) == sum(trims[k] for kinds in sold.values() for k in kinds)
    assert len(rows) == 41
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


def test_the_build_refuses_a_repeated_bike(monkeypatch):
    """A table that would build the same bike twice raises instead of shipping two of it."""
    monkeypatch.setattr(bicycle, "KINDS", (bicycle.KINDS[0], bicycle.KINDS[0]))
    try:
        bicycle.build()
    except ValueError as err:
        assert "repeats" in str(err)
    else:
        raise AssertionError("a repeated trim built twice")


def test_ten_brands_sell_the_range_and_each_kind_has_at_least_three():
    rows = bicycle.SPEC.rows
    brands = {r.brand for r in rows}
    assert len(brands) == 10
    assert brands == set(bmn.SCHEMES) == set(bmn.SERIES)
    for kind in bmn.KINDS:
        assert len({r.brand for r in rows if _axes(r)[1] == kind}) >= 3, kind


def test_each_brand_sells_exactly_the_kinds_it_has_a_series_for():
    rows = bicycle.SPEC.rows
    for brand, series in bmn.SERIES.items():
        assert {_axes(r)[1] for r in rows if r.brand == brand} == set(series), brand


def test_a_specialist_sells_one_kind_and_the_house_brands_sell_all_four():
    sold = {brand: set(series) for brand, series in bmn.SERIES.items()}
    assert sold["Wattlebrook"] == {"Electric"}
    assert sold["Gorsecliff"] == {"Mountain"}
    for brand in ("Wrenfield", "Harbour & Pine", "Larkmoor"):
        assert sold[brand] == set(bmn.KINDS), brand


def test_each_house_brand_keeps_the_bikes_it_had():
    """A new brand moves no model number of the three that sold the range: a served product keeps
    its id, so a catalog load adds the new bikes and removes none."""
    rows = {_attrs(r)["model_number"] for r in bicycle.SPEC.rows}
    assert {"RD28-18-25", "HP26RD2818", "LMRD-262818", "KD-01-25", "LMKD-2601"} <= rows
    assert {"HP25RD2822", "HP26MT2621", "EB26-08-26", "HP26KD01", "LMEB-252608"} <= rows


def test_each_kind_is_on_sale_in_both_model_years():
    rows = bicycle.SPEC.rows
    for kind in bmn.KINDS:
        years = {_axes(r)[4] for r in rows if _axes(r)[1] == kind}
        assert years == {bmn.MODEL_YEAR, bmn.MODEL_YEAR - 1}, kind


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
