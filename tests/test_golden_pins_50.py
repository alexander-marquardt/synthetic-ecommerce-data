"""A regeneration of ``golden-catalog/`` restates every hand-pinned figure with one command (#50).

Part 1 of #48 restated 16 tests and their prose by hand, one measurement script at a time. The pins
now live in ``tests/data/golden_pins.json``, written by ``scripts/measure_pins.py`` from rules
(``scripts/golden_pins.py``), and the tests read them. These tests hold the machinery:

* a pinned SKU is the first in catalog order that a stated rule fits, and a rule nothing fits is a
  refusal that names it, never a weaker SKU;
* the mutation bed's golden anchor is the first line with more than one variant, and each text a
  planted row quotes occurs exactly once;
* the fixture carries every pin and is the committed catalog's;
* no test, mutant row or prose restates a pinned figure by hand.

The consumers (``test_sku_drawings``, ``test_catalog_titles``) hold the lens and title figures to a
fresh measurement.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
GOLDEN = REPO / "golden-catalog"

sys.path.insert(0, str(SCRIPTS))
import golden_pins  # noqa: E402  (scripts/ is not a package)
import measure_pins  # noqa: E402


def _refusal(call) -> str | None:
    """The message ``call`` was refused with, or ``None`` when it was not refused."""
    try:
        call()
    except golden_pins.PinRuleError as error:
        return str(error)
    return None


def _candidate(sku: str, product_type: str, size: str | None, handle_less: bool):
    attributes = [] if size is None else [{"key": "size", "value": size}]
    return {"product_type": product_type}, {"sku": sku, "attributes": attributes}, handle_less


RULES = {rule.key: rule for rule in golden_pins.SKU_RULES}


def test_a_pinned_sku_is_the_first_in_catalog_order_that_the_rule_fits() -> None:
    candidates = [
        _candidate("1", "washer_flat", None, True),
        _candidate("2", "screw_socket_head", None, False),
        _candidate("3", "screw_socket_head", None, True),
        _candidate("4", "screw_socket_head", None, True),
    ]
    assert golden_pins.pick_sku(RULES["screw"], candidates) == "3"


def test_the_drill_rule_reads_the_size_and_the_lens() -> None:
    candidates = [
        _candidate("1", "drill_jobber", "1/16", True),
        _candidate("2", "drill_jobber", "5/64", False),
        _candidate("3", "drill_jobber", "5/64", True),
    ]
    assert golden_pins.pick_sku(RULES["drill"], candidates) == "3"
    # The hairline drill ignores the lens: it is the first 1/16" jobber drill, drawn how it may be.
    assert golden_pins.pick_sku(RULES["hairline_drill"], candidates) == "1"


def test_a_rule_that_no_sku_fits_is_refused_naming_the_rule_not_met_by_a_weaker_sku() -> None:
    rule = RULES["drill"]
    only_weaker = [
        _candidate("1", "drill_jobber", "1/16", True),
        _candidate("2", "drill_jobber", "5/64", False),
        _candidate("3", "screw_socket_head", None, True),
    ]
    message = _refusal(lambda: golden_pins.pick_sku(rule, only_weaker))
    assert message is not None, "a drill the rule does not fit was pinned"
    assert rule.statement in message and repr(rule.key) in message, message


def test_the_anchor_is_the_first_line_with_more_than_one_variant() -> None:
    lines = [
        json.dumps(
            {
                "product_id": "A-1",
                "product_type": "t",
                "variant_count": 1,
                "variants": [{"sku": "11", "order_multiple": 1}],
            }
        ),
        json.dumps(
            {
                "product_id": "B-2",
                "product_type": "t",
                "variant_count": 2,
                "variants": [
                    {"sku": "21", "order_multiple": 1},
                    {"sku": "22", "order_multiple": 1},
                ],
            }
        ),
        json.dumps(
            {
                "product_id": "C-3",
                "product_type": "t",
                "variant_count": 2,
                "variants": [
                    {"sku": "31", "order_multiple": 1},
                    {"sku": "32", "order_multiple": 1},
                ],
            }
        ),
    ]
    anchor = golden_pins.find_anchor(lines)
    assert (anchor.get("product_id"), anchor.get("first_sku"), anchor.get("second_sku")) == (
        "B-2",
        "21",
        "22",
    )
    assert _refusal(lambda: golden_pins.find_anchor(lines[:1])) is not None


def _texts(anchor: dict) -> dict[str, str]:
    """A two-file catalog in which each anchor text occurs exactly once."""
    needles = golden_pins.anchor_needles(anchor)
    return {
        name: "\n".join(text for file, text in needles if file == name)
        for name in ("flat.jsonl", "nested.jsonl")
    }


def test_an_anchor_text_that_occurs_twice_or_not_at_all_is_refused() -> None:
    anchor = {
        "rule": "the first line",
        "product_id": "B-2",
        "product_type": "t",
        "variant_count": 2,
        "first_sku": "21",
        "second_sku": "22",
        "order_multiple": 1,
    }
    texts = _texts(anchor)
    assert len(golden_pins.anchor_needles(anchor)) == 4
    assert _refusal(lambda: golden_pins.check_anchor(anchor, texts)) is None
    name, needle = golden_pins.anchor_needles(anchor)[0]
    twice = {**texts, name: texts[name] + "\n" + needle}
    assert "2 times" in (_refusal(lambda: golden_pins.check_anchor(anchor, twice)) or "")
    absent = {**texts, name: texts[name].replace(needle, "")}
    assert "0 times" in (_refusal(lambda: golden_pins.check_anchor(anchor, absent)) or "")


def test_the_script_fails_naming_the_rule_and_writes_nothing_when_a_measure_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "golden_pins.json"

    def refuse() -> dict:
        raise golden_pins.PinRuleError("no SKU satisfies the pin rule 'drill': the planted rule")

    monkeypatch.setattr(golden_pins, "MEASURES", {"lens": refuse})
    monkeypatch.setattr(golden_pins, "PINS_PATH", out)
    status = measure_pins.main([])
    assert status != 0
    assert "the planted rule" in capsys.readouterr().err
    assert not out.exists()


def test_the_script_writes_the_measured_pins_and_check_compares_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "golden_pins.json"
    monkeypatch.setattr(golden_pins, "MEASURES", {"x": lambda: {"n": 1}})
    monkeypatch.setattr(golden_pins, "PINS_PATH", out)
    assert measure_pins.main([]) == 0
    assert out.exists(), "the script wrote no fixture"
    assert json.loads(out.read_text("utf-8")) == {"x": {"n": 1}}
    assert measure_pins.main(["--check"]) == 0
    monkeypatch.setattr(golden_pins, "MEASURES", {"x": lambda: {"n": 2}})
    assert measure_pins.main(["--check"]) != 0
    assert golden_pins.REGENERATE in capsys.readouterr().err


# --- the committed fixture ---------------------------------------------------------------------


def test_the_fixture_carries_every_pin() -> None:
    pins = golden_pins.load()
    assert sorted(pins) == ["anchor", "lens", "titles"], (
        f"tests/data/golden_pins.json holds no pins; run {golden_pins.REGENERATE}"
    )
    assert sorted(pins["lens"]["skus"]) == sorted(rule.key for rule in golden_pins.SKU_RULES)
    assert sorted(pins["titles"]) == ["documents", "mid_word", "over_cap"]
    assert pins["lens"]["min_enlargement"] > 1


def test_the_fixture_anchor_is_the_committed_catalogs() -> None:
    pinned = golden_pins.load().get("anchor")
    assert pinned, f"no anchor is pinned; run {golden_pins.REGENERATE}"
    assert pinned == golden_pins.measure_anchor(GOLDEN)


# --- no test, mutant row or prose restates a pin by hand ---------------------------------------

#: Where a pin used to be typed: an id, the file and a pattern that matches a typed pin.
HAND_PINS = {
    "lens-skus": ("tests/test_sku_drawings.py", r'"\d{10}"'),
    "lens-floor": ("tests/test_sku_drawings.py", r"^CATALOG_MIN_ENLARGEMENT = \d"),
    "title-counts": ("tests/test_catalog_titles.py", r"\b(?:over_cap|mid_word) == \d"),
    "mutation-skus": ("scripts/mutation_check.py", r'"sku": "\d{10}"'),
}


@pytest.mark.parametrize("pin", HAND_PINS)
def test_no_hand_typed_pin_is_left(pin: str) -> None:
    path, pattern = HAND_PINS[pin]
    text = (REPO / path).read_text("utf-8")
    found = [m.group(0) for m in re.finditer(pattern, text, re.MULTILINE)]
    assert found == [], (
        f"{path} types a pin by hand ({found[:3]}); read tests/data/golden_pins.json"
    )


PROSE = {
    "readme": "README.md",
    "drawings-doc": "docs/drawings.md",
    "naming-docstring": "src/synthetic_ecommerce_data/core/naming.py",
}


def test_the_prose_patterns_name_each_pinned_figure() -> None:
    pins = {
        "lens": {"min_enlargement": 2.12, "skus": {}},
        "titles": {"documents": 10548, "over_cap": 114, "mid_word": 73},
    }
    patterns = golden_pins.prose_patterns(pins)
    planted = {
        "lens.min_enlargement": "pinned at the catalog's measured x2.12",
        "titles.mid_word": "which lands mid-word: **73 of the default catalog's 10,548 titles**",
    }
    for figure, text in planted.items():
        assert figure in patterns and re.search(patterns[figure], text), figure


@pytest.mark.parametrize("doc", PROSE)
def test_no_prose_restates_a_pinned_figure(doc: str) -> None:
    path = PROSE[doc]
    patterns = golden_pins.prose_patterns(golden_pins.load())
    assert patterns, "the fixture carries no figure to look for"
    text = (REPO / path).read_text("utf-8")
    quoted = sorted(
        f"{figure} ({m.group(0)!r}, line {text.count(chr(10), 0, m.start()) + 1})"
        for figure, pattern in patterns.items()
        for m in re.finditer(pattern, text)
    )
    assert quoted == [], (
        f"{path} restates a pinned figure; name tests/data/golden_pins.json: {quoted}"
    )


# --- the mutation bed's golden rows ------------------------------------------------------------


def test_the_golden_rows_quote_the_fixture_anchor_and_each_text_occurs_once() -> None:
    import mutation_rows_golden_anchors_50 as rows_file

    anchor = golden_pins.load().get("anchor")
    assert anchor, f"no anchor is pinned; run {golden_pins.REGENERATE}"
    rows = rows_file.rows()
    assert len(rows) == 5, [row.name for row in rows]
    for row in rows:
        assert row.root == "golden-catalog" and row.old != row.new, row.name
        assert anchor["first_sku"] in row.old or anchor["product_id"] in row.old, row.name
        text = (GOLDEN / row.file).read_text("utf-8")
        assert text.count(row.old) == 1, f"{row.name}: {text.count(row.old)} occurrences"
