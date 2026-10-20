"""Mutant rows for the golden-pin machinery (#50): each plants one defect and one test must red.

The rule that picks a pinned SKU, the anchor rule and its once-only check live in
``scripts/golden_pins.py``; the fixture they write is read by ``tests/test_sku_drawings.py`` and
``tests/test_catalog_titles.py``. A row for the fixture builds its text from the committed fixture,
so a regeneration edits nothing here.
"""

from __future__ import annotations

import golden_pins
from mutation_row import Row

PREFIX = "golden pins"

_TEST = "tests/test_golden_pins_50.py::"
_LENS = (
    "tests/test_sku_drawings.py::"
    "test_every_lens_enlarges_at_least_the_measured_floor_and_is_handle_less_only_when_it_must_be"
)
_TITLES = (
    "tests/test_catalog_titles.py::test_the_cap_cut_this_replaced_really_did_land_inside_words"
)


def _script(name: str, old: str, new: str, test: str, prop: str) -> Row:
    return Row(name, "golden_pins.py", old, new, _TEST + test, prop, "scripts")


def _fixture(name: str, old: str, new: str, test: str, prop: str) -> Row:
    return Row(name, "golden_pins.json", old, new, test, prop, "tests/data")


def rows() -> list[Row]:
    pins = golden_pins.load()
    floor = pins["lens"]["min_enlargement"]
    mid_word = pins["titles"]["mid_word"]
    screw = pins["lens"]["skus"]["screw"]
    return [
        _script(
            "a pinned SKU need not be drawn under the handle-less lens",
            "        if rule.handle_less and not handle_less:\n            continue\n",
            "",
            "test_a_pinned_sku_is_the_first_in_catalog_order_that_the_rule_fits",
            "a lens pin is a SKU the handle-less lens serves",
        ),
        _script(
            "a pinned SKU need not carry the rule's attribute",
            "            if not any("
            'a["key"] == key and a["value"] == value for a in variant["attributes"]'
            "):\n"
            "                continue\n",
            "            pass\n",
            "test_the_drill_rule_reads_the_size_and_the_lens",
            "a pin rule is the whole statement, not its product type",
        ),
        _script(
            "a rule that no SKU fits pins nothing instead of being refused",
            "    raise PinRuleError("
            'f"no SKU satisfies the pin rule {rule.key!r}: {rule.statement}")\n',
            "    return None\n",
            "test_a_rule_that_no_sku_fits_is_refused_naming_the_rule_not_met_by_a_weaker_sku",
            "a rule nothing fits is refused by name",
        ),
        _script(
            "the anchor is the first line, not the first with more than one variant",
            '        if len(parent["variants"]) > 1:\n',
            '        if len(parent["variants"]) >= 1:\n',
            "test_the_anchor_is_the_first_line_with_more_than_one_variant",
            "the mutation anchor is the first multi-variant line",
        ),
        _script(
            "an anchor text that occurs twice is accepted",
            "        if found != 1:\n",
            "        if found < 1:\n",
            "test_an_anchor_text_that_occurs_twice_or_not_at_all_is_refused",
            "each anchor text occurs exactly once",
        ),
        _fixture(
            "the lens floor is pinned below the measured minimum",
            f'"min_enlargement": {floor}',
            f'"min_enlargement": {round(floor - 0.05, 2)}',
            _LENS,
            "the fixture's lens floor is the catalog's measured minimum",
        ),
        _fixture(
            "the screw pin is a SKU the rule does not pick",
            f'"screw": "{screw}"',
            f'"screw": "{screw[:-1]}{(int(screw[-1]) + 1) % 10}"',
            _LENS,
            "the fixture's pinned SKUs are the rules' picks",
        ),
        _fixture(
            "the mid-word count is one short",
            f'"mid_word": {mid_word}',
            f'"mid_word": {mid_word - 1}',
            _TITLES,
            "the fixture's title counts are the measured ones",
        ),
    ]
