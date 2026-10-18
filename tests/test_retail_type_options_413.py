"""A type spec declares its own SKU options: the attribute key, label and unit (gen#413, slice 1).

The central table of ``export.py`` held a line for every quantity a type's SKUs vary by, so each
new quantity edited a shared file. A quantity only spec types carry is now declared by the spec
that carries it (``TypeSpec.options``); ``export.SHARED_OPTIONS`` keeps the options the types not
yet moved into specs share, and ``export.OPTIONS`` is the two together. A key declared twice with
different meanings fails here and at import. Moving a declaration never changes what is
generated: the byte-identical build diff of the pull request shows it.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import type_registry  # noqa: E402
from type_registry import Option, SpecError  # noqa: E402

#: The options only spec types carry, by the spec that declares each: spec key -> options.
MOVED = {
    "parasol": [Option("canopy_m", "canopy_diameter", "Canopy diameter", "MTR")],
    "garden_furniture_set": [Option("seats", "seats", "Seats", "C62")],
    "analog_watch": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "digital_watch": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "fitness_band": [Option("case_mm", "case_diameter", "Case diameter", "MMT")],
    "dolls_house": [Option("house_style", "style", "Style")],
    "tracksuit": [Option("sold_as", "sold_as", "Sold as")],
    "body_mist": [Option("fragrance", "fragrance", "Fragrance")],
    "sun_cream": [Option("spf", "spf", "SPF")],
    "garden_hose": [Option("length_m", "item_length", "Item length", "MTR")],
    "baseball_glove": [Option("glove_size_in", "glove_size", "Glove size", "INH")],
    "batting_helmet": [Option("head_cm", "head_circumference", "Head circumference", "CMT")],
    "swim_armbands": [Option("max_load_kg", "max_load_kg", "Maximum load", "KGM")],
    "football": [Option("ball_size", "ball_size", "Ball size", "C62")],
    "badminton_set": [Option("players", "players", "Players", "C62")],
    "resistance_band": [Option("resistance", "resistance_level", "Resistance level")],
    "camping_lantern": [Option("brightness_lm", "brightness", "Brightness (lm)")],
    "tennis_racket": [Option("grip", "grip_size", "Grip size")],
}
MOVED_OPTIONS = sorted({o.option for opts in MOVED.values() for o in opts})


def _spec(key: str, *options: Option):
    return replace(type_registry.specs()[key], options=tuple(options))


def test_each_moved_option_is_declared_by_the_spec_that_carries_it() -> None:
    declared = {k: list(type_registry.specs()[k].options) for k in MOVED}
    assert declared == MOVED


def test_the_central_table_holds_no_option_a_spec_declares() -> None:
    assert [o for o in MOVED_OPTIONS if o in export.SHARED_OPTIONS] == []


def test_the_export_table_still_states_every_moved_option_as_before() -> None:
    got = {o.option: export.OPTIONS[o.option] for opts in MOVED.values() for o in opts}
    want = {o.option: (o.key, o.name, o.unit) for opts in MOVED.values() for o in opts}
    assert got == want


def test_the_merged_table_is_the_shared_table_and_every_declaration() -> None:
    table, problems = type_registry.option_table(export.SHARED_OPTIONS)
    assert problems == []
    assert table == export.OPTIONS
    assert set(table) == set(export.SHARED_OPTIONS) | set(MOVED_OPTIONS)


def test_the_central_table_is_not_a_second_home_for_a_declared_key() -> None:
    names: dict[str, set[str]] = {}
    for key, name, _unit in export.OPTIONS.values():
        names.setdefault(key, set()).add(name)
    assert {k: n for k, n in names.items() if len(n) > 1} == {}


@pytest.mark.parametrize(
    ("label", "options", "mentions"),
    [
        ("redeclares-a-shared-option", [Option("size", "size", "Size")], "size"),
        ("same-option-new-key", [Option("spf", "sun_factor", "SPF")], "spf"),
        ("same-option-new-unit", [Option("spf", "spf", "SPF", "C62")], "spf"),
        ("one-key-two-names", [Option("sun_factor", "item_length", "Length")], "item_length"),
    ],
)
def test_a_key_declared_twice_with_different_meanings_is_a_problem(
    label: str, options: list[Option], mentions: str
) -> None:
    spec = _spec("kite", *options)
    table, problems = type_registry.option_table(
        export.SHARED_OPTIONS, [spec, type_registry.specs()["sun_cream"]]
    )
    assert any(mentions in p for p in problems), (label, problems)


def test_two_specs_may_declare_one_option_the_same_way() -> None:
    same = Option("spf", "spf", "SPF")
    specs = [_spec("kite", same), type_registry.specs()["sun_cream"]]
    _, problems = type_registry.option_table(export.SHARED_OPTIONS, specs)
    assert problems == []


def test_one_key_may_carry_two_units_under_one_name() -> None:
    metres = Option("hose_m", "item_length", "Item length", "MTR")
    _, problems = type_registry.option_table(export.SHARED_OPTIONS, [_spec("kite", metres)])
    assert problems == []


def test_a_spec_that_names_an_option_twice_is_refused() -> None:
    twice = _spec("kite", Option("spf", "spf", "SPF"), Option("spf", "spf", "SPF"))
    with pytest.raises(SpecError, match="spf"):
        type_registry.validate(twice)
