"""A style's description names the closure and the pattern its attributes say (gen#250).

``attribute_text.disagreements`` reads every record: a closure word in the title or description
must be the ``closure`` attribute (or a closure it lists as an allowance), and a style with a
``pattern`` attribute sells only that pattern in its color options, its drawing and its text. The
metric is the number of rows that disagree; it is held at zero on the templates and on the ceiling
build, and the check itself is held against hand-made rows so it cannot go quiet.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import attribute_text  # noqa: E402
import scale  # noqa: E402
from retail_figures import committed  # noqa: E402

#: The ceiling build, as ``test_retail_scale.py`` builds it.
CEILING_SKUS = committed()["ceiling"]["skus"] * 2
#: The rows the check must read, so a check that sees none cannot pass: the templates hold 31
#: styles with a closure attribute that names a closure word and 66 with a pattern attribute.
MIN_CLOSURE_ROWS = 25
MIN_PATTERN_ROWS = 60


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(CEILING_SKUS).records


def _rec(
    title: str = "A Style",
    description: str = "A style.",
    closure: str | None = None,
    pattern: str | None = None,
    sold: tuple[str, ...] = ("solid",),
    drawn: str | None = None,
) -> dict[str, Any]:
    attrs = [
        {"key": k, "name": k.title(), "value": v}
        for k, v in (("closure", closure), ("pattern", pattern))
        if v is not None
    ]
    rec: dict[str, Any] = {
        "product_id": "T-1",
        "title": title,
        "description": description,
        "attributes": attrs,
        "color_options": [{"color": "Red", "hex": "#b3202e", "pattern": p} for p in sold],
    }
    if drawn is not None:
        rec["drawing"] = {"pattern": drawn}
    return rec


def test_no_template_row_disagrees_with_its_attributes(templates):
    bad = attribute_text.disagreements(templates)
    assert not bad, f"{len(bad)} rows disagree: {bad}"


def test_no_row_of_the_ceiling_build_disagrees_with_its_attributes(ceiling):
    bad = attribute_text.disagreements(ceiling)
    assert not bad, f"{len(bad)} of {len(ceiling)} rows disagree: {bad[:20]}"


def test_the_check_reads_enough_rows_to_mean_something(templates):
    closure = [
        r
        for r in templates
        if any(a["key"] == "closure" for a in r["attributes"])
        and attribute_text._named(f"{r['title']} {r['description']}", attribute_text.FAMILIES)
    ]
    pattern = [r for r in templates if any(a["key"] == "pattern" for a in r["attributes"])]
    assert len(closure) >= MIN_CLOSURE_ROWS, len(closure)
    assert len(pattern) >= MIN_PATTERN_ROWS, len(pattern)


def test_every_allowance_is_used_by_a_real_row(ceiling):
    """A stale allowance would let a defect through; each (closure, family) must still occur."""
    seen = set()
    for r in ceiling:
        text = attribute_text.NOT_A_CLOSURE.sub(" ", f"{r['title']} {r['description']}")
        named = attribute_text._named(text, attribute_text.FAMILIES)
        for a in r["attributes"]:
            if a["key"] == "closure":
                seen |= {(a["value"].lower(), f) for f in named}
    stale = [(v, f) for v, fams in attribute_text.ALSO.items() for f in fams if (v, f) not in seen]
    assert not stale, stale


def test_every_pattern_value_in_the_catalog_is_mapped(templates):
    values = {
        a["value"].lower() for r in templates for a in r["attributes"] if a["key"] == "pattern"
    }
    assert values <= set(attribute_text.PATTERN_KIND), values - set(attribute_text.PATTERN_KIND)


# ---- the check against hand-made rows ------------------------------------------------------


def test_a_tote_that_says_magnetic_fastening_over_a_zip_closure_disagrees():
    rec = _rec("Jute Tote", "A woven jute tote with a magnetic fastening.", closure="Zip")
    assert attribute_text.closure_lines(rec) == ["closure Zip but the text names ['magnetic']"]


def test_a_tote_that_says_zip_over_a_zip_closure_agrees():
    rec = _rec("Jute Tote", "A woven jute tote with a zip fastening.", closure="Zip")
    assert attribute_text.closure_lines(rec) == []


def test_a_zipped_pocket_is_not_the_closure():
    rec = _rec(
        description="A bag with a magnetic flap and a zipped inner pocket.", closure="Magnetic"
    )
    assert attribute_text.closure_lines(rec) == []
    rec = _rec(description="A bag with a magnetic flap and a zip top pocket.", closure="Zip")
    assert attribute_text.closure_lines(rec) == ["closure Zip but the text names ['magnetic']"]


def test_a_zipped_pocket_over_a_flap_closure_agrees():
    rec = _rec(
        description="A canvas bag with a front flap and a zipped back pocket.", closure="Flap"
    )
    assert attribute_text.closure_lines(rec) == []


def test_a_closure_word_over_an_unlisted_closure_disagrees():
    rec = _rec(description="Trainers with a buckled strap.", closure="Lace-Up")
    assert attribute_text.closure_lines(rec) == ["closure Lace-Up but the text names ['buckle']"]


def test_a_listed_allowance_agrees_and_the_rest_do_not():
    ok = _rec(description="Shoes with a buckled ankle strap.", closure="Ankle Strap")
    assert attribute_text.closure_lines(ok) == []
    bad = _rec(description="Shoes with a magnetic ankle strap.", closure="Ankle Strap")
    assert attribute_text.closure_lines(bad) == [
        "closure Ankle Strap but the text names ['magnetic']"
    ]


def test_a_text_without_a_closure_word_agrees_whatever_the_closure():
    assert attribute_text.closure_lines(_rec(description="A bag.", closure="Zip")) == []


def test_a_polka_dot_style_that_sells_a_gingham_color_disagrees():
    rec = _rec(
        "Polka Dot Umbrella",
        "A polka dot umbrella.",
        pattern="Polka Dot",
        sold=("polka", "gingham"),
    )
    assert attribute_text.pattern_lines(rec) == [
        "pattern Polka Dot but color options sell ['gingham']"
    ]


def test_a_style_that_draws_another_pattern_disagrees():
    rec = _rec(pattern="Striped", sold=("stripe",), drawn="solid")
    assert attribute_text.pattern_lines(rec) == ["pattern Striped but the drawing is solid"]


def test_a_style_whose_text_names_another_pattern_disagrees():
    rec = _rec("Polka Dot Umbrella", "A striped umbrella.", pattern="Polka Dot", sold=("polka",))
    assert attribute_text.pattern_lines(rec) == ["pattern Polka Dot but the text names ['stripe']"]


def test_a_gingham_check_agrees_and_a_matching_style_agrees():
    gingham = _rec(
        "Gingham Shade",
        "A cotton gingham check shade.",
        pattern="Gingham",
        sold=("gingham", "gingham"),
        drawn="gingham",
    )
    assert attribute_text.pattern_lines(gingham) == []
    plain = _rec(pattern="Plain", sold=("solid",), drawn="solid")
    assert attribute_text.pattern_lines(plain) == []


def test_an_unmapped_pattern_value_is_reported_not_skipped():
    rec = _rec(pattern="Paisley")
    assert attribute_text.pattern_lines(rec) == ["pattern Paisley is not in PATTERN_KIND"]


def test_disagreements_names_the_row():
    closure = _rec(description="A bag with a magnetic flap.", closure="Zip")
    pattern = _rec(pattern="Striped", sold=("stripe",), drawn="solid")
    pattern["product_id"] = "T-2"
    assert attribute_text.disagreements([copy.deepcopy(closure), pattern]) == [
        "T-1: closure Zip but the text names ['magnetic']",
        "T-2: pattern Striped but the drawing is solid",
    ]
