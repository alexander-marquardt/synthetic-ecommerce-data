"""Review plants for the table-type mechanism (#101): the paths no gate reached.

Three planted defects in ``catalog/tabletype.py`` left every table test green
(``tests/review_104_r1_mutants.py.txt``): an inch table read as millimetres,
an inch table published in the metric style, and a material ladder whose
cheapest factor is not 1.0. Both shipped types are metric, so the ``unit="in"``
branch had no caller. These pass on the mechanism as written and red on each
of those three.
"""

from __future__ import annotations

import dataclasses
import math

import pytest

from synthetic_industrial_products.catalog import price, tabletype
from synthetic_industrial_products.catalog.config import GeneratorConfig
from synthetic_industrial_products.catalog.generate import Generator
from synthetic_industrial_products.catalog.tabletype import TableType, Variant
from synthetic_industrial_products.drawing.model import Figure

MM = 25.4
#: A registered key, borrowed for its random stream and brands only: the
#: table below is made up and belongs to no product.
BORROWED_KEY = "cotter_pins"


def _draw(values) -> Figure:
    fig = Figure(size_in=values["Diameter"])
    fig.rect(0.0, 0.0, values["Diameter"], values["Width"])
    return fig


INCH = TableType(
    "made_up_inch",
    category=("Fasteners", "Pins", "Made Up"),
    item="Made Up Pin",
    standards_family="fastener",
    standard="ASME 0000",
    columns=("Diameter", "Width"),
    rows=((0.25, 0.5), (0.5, 1.0), (1.0, 2.5)),
    variants=(Variant("Steel", "Plain", 1.0), Variant("Brass", "Plain", 3.0)),
    packs=(10, 100),
    base_price=2.0,
    size_slope=1.0,
    pack_slope=0.5,
    draw=_draw,
    extent=(1.0, 2.5),
    share=0.001,
    default_lines=1,
    default_skus=1,
    series="MU",
    unit="in",
)


def _usd(table: TableType, size_in: float) -> float:
    model = table.price
    return model.anchor * math.exp(
        price.structure(model, size_in, "Steel", "standard", pack=float(table.packs[0]))
    )


def test_an_inch_tables_rows_are_inches():
    assert INCH.inches(INCH.rows[2]) == {"Diameter": 1.0, "Width": 2.5}
    assert INCH.price.anchor_key == 0.25


def test_an_inch_tables_base_price_is_its_first_row_and_rises_by_the_slope():
    assert _usd(INCH, 0.25) == pytest.approx(2.0)
    assert _usd(INCH, 1.0) == pytest.approx(8.0)


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
        INCH, variants=(Variant("Steel", "Plain", 2.0), Variant("Brass", "Plain", 3.0))
    )
    assert tabletype.problems(dear) == ["the factors do not rise from 1.0"]
