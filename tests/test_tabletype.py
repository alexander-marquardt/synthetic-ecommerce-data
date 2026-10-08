"""The table-driven type declaration itself (#101): what a table may not say,
what its price ladder orders, and which lengths its drawing is given.

The table here is made up and belongs to no product: these gates are about
:mod:`synthetic_ecommerce_data.catalog.tabletype`, not about a type.
"""

from __future__ import annotations

import dataclasses
import importlib
import math
import pkgutil

import pytest

from synthetic_ecommerce_data.catalog import price, tabletype, typespec
from synthetic_ecommerce_data.catalog.config import GeneratorConfig
from synthetic_ecommerce_data.catalog.generate import Generator
from synthetic_ecommerce_data.catalog.tabletype import TableType, Variant
from synthetic_ecommerce_data.drawing.model import Figure

MM = 25.4


def _draw(values) -> Figure:
    fig = Figure(size_in=values["Diameter"])
    fig.rect(0.0, 0.0, values["Diameter"], values["Width"])
    return fig


TABLE = TableType(
    "made_up",
    category=("Fasteners", "Pins", "Made Up"),
    item="Made Up Pin",
    standards_family="fastener",
    standard="ISO 0000",
    columns=("Diameter", "Width"),
    rows=((2.0, 5.0), (4.0, 9.0), (8.0, 20.0)),
    variants=(Variant("Steel", "Plain", 1.0), Variant("Brass", "Plain", 3.0)),
    packs=(10, 100),
    base_price=2.0,
    size_slope=1.0,
    pack_slope=0.5,
    draw=_draw,
    extent=(1.0, 1.0),
    share=0.001,
    default_lines=1,
    default_skus=1,
    series="MU",
)


def _usd(table: TableType, size_mm: float, material: str, pack: int) -> float:
    """The declared price at the standard tier, before it is shown."""
    model = table.price
    return model.anchor * math.exp(
        price.structure(model, size_mm / MM, material, "standard", pack=float(pack))
    )


def test_a_sound_table_has_no_problems():
    assert tabletype.problems(TABLE) == []


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"rows": ((2.0, 5.0), (4.0,))}, "a row misses a column"),
        ({"rows": ((4.0, 9.0), (2.0, 5.0))}, "the sizes do not rise down the table"),
        ({"rows": ((2.0, 5.0), (2.0, 9.0))}, "the sizes do not rise down the table"),
        (
            {"variants": (Variant("Steel", "Plain", 1.0), Variant("Steel", "Zinc Plated", 2.0))},
            "a material is listed twice",
        ),
        (
            {"variants": (Variant("Brass", "Plain", 3.0), Variant("Steel", "Plain", 1.0))},
            "the factors do not rise from 1.0",
        ),
        ({"packs": (100, 10)}, "the packs do not rise"),
        ({"size_slope": 0.0}, "size_slope is not positive: a larger size must cost more"),
        (
            {"pack_slope": 1.0},
            "pack_slope is not between 0 and 1: a piece must cost less",
        ),
        (
            {"pack_slope": 0.0},
            "pack_slope is not between 0 and 1: a piece must cost less",
        ),
        ({"base_price": 0.0}, "base_price is not positive"),
        ({"unit": "cm"}, "unit is neither mm nor in"),
    ],
)
def test_a_table_that_would_break_an_order_is_refused(change, message):
    wrong = dataclasses.replace(TABLE, **change)
    assert tabletype.problems(wrong) == [message]
    with pytest.raises(ValueError, match="made_up"):
        tabletype.spec(wrong)


def test_the_base_price_is_the_first_row_in_the_first_material_and_pack():
    assert _usd(TABLE, 2.0, "Steel", 10) == pytest.approx(2.0)


def test_a_larger_size_costs_more_by_the_declared_slope():
    assert _usd(TABLE, 4.0, "Steel", 10) == pytest.approx(4.0)
    assert _usd(TABLE, 8.0, "Steel", 10) == pytest.approx(8.0)


def test_a_material_costs_the_tables_own_factor_not_the_shared_one():
    """Brass is 3.0 in this table, whatever the shared ladder says of brass."""
    assert _usd(TABLE, 2.0, "Brass", 10) == pytest.approx(6.0)


def test_a_bigger_pack_costs_more_in_total_and_less_a_piece():
    small, large = _usd(TABLE, 2.0, "Steel", 10), _usd(TABLE, 2.0, "Steel", 100)
    assert large == pytest.approx(2.0 * 10**0.5)
    assert small < large
    assert small / 10 > large / 100


def test_the_price_claims_no_measurement_and_adds_no_noise():
    model = TABLE.price
    assert model.measured is False
    assert (model.group_sigma, model.sku_sigma, model.size_sigma) == (0.0, 0.0, 0.0)
    assert dict(model.endings) == {"other": 1.0}
    assert "made_up" not in price.CENSUS


def test_a_record_with_every_column_is_drawn_from_its_own_values():
    values, source = tabletype.lengths(TABLE, {"Diameter": "4mm", "Width": "11mm"})
    assert source == "record"
    assert values == pytest.approx({"Diameter": 4 / MM, "Width": 11 / MM})


def test_a_missing_column_takes_the_nearest_rows_proportion():
    """3.9 mm is nearest the 4 mm row, whose width is 9/4 of its size."""
    values, source = tabletype.lengths(TABLE, {"Diameter": "3.9mm"})
    assert source == "partial"
    assert values == pytest.approx({"Diameter": 3.9 / MM, "Width": 3.9 * 9 / 4 / MM})


def test_a_record_with_no_readable_size_is_drawn_as_the_middle_row():
    values, source = tabletype.lengths(TABLE, {"Width": "11mm", "Diameter": "about four"})
    assert source == "nominal"
    assert values == pytest.approx({"Diameter": 4 / MM, "Width": 9 / MM})


def test_the_spec_carries_the_tables_figure_and_claims_only_its_standard():
    spec = tabletype.spec(TABLE)
    assert spec.may_claim == frozenset({"ISO 0000"})
    assert spec.key_attributes == ("Diameter",)
    drawn = spec.figure({"Diameter": "8mm", "Width": "20mm"})
    assert drawn.source == "record"
    x0, y0, x1, y1 = drawn.figure.bounds()
    assert (x1 - x0, y1 - y0) == pytest.approx((8 / MM, 20 / MM))


# --- an inch table (no shipped type is one, so the made-up table is) ----------

INCH = dataclasses.replace(
    TABLE,
    key="made_up_inch",
    standard="ASME 0000",
    rows=((0.25, 0.5), (0.5, 1.0), (1.0, 2.5)),
    extent=(1.0, 2.5),
    unit="in",
)
#: A registered key, borrowed for its random stream and brands only.
BORROWED_KEY = "cotter_pins"


def test_an_inch_tables_rows_are_inches():
    assert INCH.inches(INCH.rows[2]) == {"Diameter": 1.0, "Width": 2.5}
    assert INCH.price.anchor_key == 0.25


def test_an_inch_tables_base_price_is_its_first_row_and_rises_by_the_slope():
    assert _usd(INCH, 0.25 * MM, "Steel", 10) == pytest.approx(2.0)
    assert _usd(INCH, 1.0 * MM, "Steel", 10) == pytest.approx(8.0)


def test_an_inch_table_is_built_in_inches_with_every_row_of_a_run_on_the_table():
    """The line a table's ``make`` drafts, before the shared post-pass."""
    draft = tabletype._make(INCH)(
        Generator(GeneratorConfig(), BORROWED_KEY), BORROWED_KEY, INCH.category
    )
    assert len(draft.children) in (1, 2, 3)
    for child in draft.children:
        assert child.system == "in"
        assert [a.name for a in child.attrs] == ["Diameter", "Width"]
        entries = [entry for a in child.attrs for entry in a.as_entries()]
        assert [entry["unit_code"] for entry in entries] == ["INH", "INH"]
        built = tuple(round(entry["value_canonical"] / MM, 4) for entry in entries)
        assert built in INCH.rows, built


def test_a_ladder_whose_cheapest_material_is_not_the_base_is_refused():
    """``base_price`` is the first material's price, so its factor is 1.0."""
    dear = dataclasses.replace(
        TABLE, variants=(Variant("Steel", "Plain", 2.0), Variant("Brass", "Plain", 3.0))
    )
    assert tabletype.problems(dear) == ["the factors do not rise from 1.0"]


# --- the registered table types are found, not listed --------------------------


def _modules_stating_a_table() -> set[str]:
    """The type modules holding a ``TableType``, read off the modules
    themselves: a second route to the set ``tabletype.tables()`` records."""
    root = importlib.import_module(typespec.TYPES_PACKAGE)
    found = set()
    for info in pkgutil.walk_packages(root.__path__, prefix=f"{typespec.TYPES_PACKAGE}."):
        if info.ispkg:
            continue
        module = importlib.import_module(info.name)
        if any(isinstance(value, TableType) for value in vars(module).values()):
            found.add(info.name.rsplit(".", 1)[1])
    return found


def test_every_module_that_states_a_table_is_a_recorded_table_type():
    """What ``NOT_MEASURED`` (test_price) and the distinct-spec floor
    (test_catalog_brands_voice) read, so a new table type edits neither."""
    stated = _modules_stating_a_table()
    assert {"cotter_pins", "retaining_rings_external"} <= stated
    recorded = tabletype.tables()
    assert set(recorded) == stated
    for key, table in recorded.items():
        assert table.key == key
        assert typespec.discover()[key].price == table.price


def test_a_table_no_type_module_declares_is_not_a_recorded_table_type():
    """The made-up tables of this module went through ``spec`` too."""
    tabletype.spec(TABLE)
    tabletype.spec(INCH)
    assert {"made_up", "made_up_inch"} & set(tabletype.tables()) == set()


def test_a_table_type_whose_make_is_wrapped_is_still_a_recorded_table_type():
    """A type that adds per-line attributes wraps the ``make`` its spec was
    handed (turnbuckles: the end fitting). The record is kept by type key, so
    the wrapping does not hide it from the gates that read ``tables()``."""
    turnbuckles = importlib.import_module(f"{typespec.TYPES_PACKAGE}.fasteners.turnbuckles")
    assert turnbuckles.SPEC.make is not tabletype.spec(turnbuckles.TABLE).make
    assert tabletype.tables().get("turnbuckles") is turnbuckles.TABLE
