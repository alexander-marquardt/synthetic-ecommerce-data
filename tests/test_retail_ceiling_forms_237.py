"""A derived ceiling light keeps only what its own form has (gen#237).

The derivation copies a pendant's attribute set across the other ceiling forms, so a flush fitting
listed a ``drop_length`` it cannot have, and a title read "Linen Dome Chandelier Light" (the
pendant's shade word beside the new form word). Only a form that hangs (pendant, chandelier)
carries ``drop_length``, and a title names one form.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import lighting_rows  # noqa: E402
import scale  # noqa: E402

#: The forms that hang from a cord, chain or rod: written here, not read from the source.
HANGING = {"Pendant", "Chandelier"}
FORMS = ("Pendant", "Chandelier", "Semi-Flush", "Flush", "Spotlight Bar")
#: A word that belongs to one form's title ("Dome" and "Cluster" are a pendant's).
FORM_QUALIFIERS = ("Dome", "Cluster")
FORM_WORDS = re.compile("|".join(rf"\b{re.escape(w)}\b" for w in FORMS), flags=re.IGNORECASE)
QUALIFIERS = re.compile("|".join(rf"\b{w}\b" for w in FORM_QUALIFIERS), flags=re.IGNORECASE)

#: (template, a form it never has) pairs: the pendant templates, derived to every other form.
PENDANTS = ("BRD-LTCPND", "BRD-LTCPN3")
OTHER_FORMS = ("Flush", "Semi-Flush", "Spotlight Bar", "Chandelier")


def _template(pid: str) -> dict:
    return next(t for t in scale.templates() if t["product_id"] == pid)


def _derive(pid: str, form: str) -> dict:
    tpl = _template(pid)
    return scale.derive(
        tpl, "BRD-TEST", "Ashcombe", tpl["brand"], {"fixture_type": form},
        [tpl["color_options"][0]["color"]], {tpl["brand"]: "own"}, random.Random(0),
    )  # fmt: skip


def _attrs(rec: dict) -> dict[str, object]:
    return {a["key"]: a["value"] for a in rec["attributes"]}


def _joined_words(rec: dict) -> list[str]:
    """What a title names beyond the style's own form: a second form word ("Flush Pendant"),
    or a pendant's shade or arrangement word on another form ("Dome Chandelier")."""
    title = rec["title"]
    forms = [m.group(0).lower() for m in FORM_WORDS.finditer(title)]
    extra = forms[1:]
    if _attrs(rec)["fixture_type"] != "Pendant":
        extra += [m.group(0).lower() for m in QUALIFIERS.finditer(title)]
    return extra


@pytest.mark.parametrize("pid", PENDANTS)
@pytest.mark.parametrize("form", ("Flush", "Semi-Flush", "Spotlight Bar"))
def test_a_derived_form_that_does_not_hang_has_no_drop_length(pid: str, form: str) -> None:
    rec = _derive(pid, form)
    assert _attrs(rec)["fixture_type"] == form
    assert "drop_length" not in _attrs(rec), rec["title"]


@pytest.mark.parametrize("pid", PENDANTS)
def test_a_derived_chandelier_keeps_the_drop_it_hangs_by(pid: str) -> None:
    assert "drop_length" in _attrs(_derive(pid, "Chandelier"))


@pytest.mark.parametrize("pid", PENDANTS)
@pytest.mark.parametrize("form", OTHER_FORMS)
def test_a_derived_title_names_one_form(pid: str, form: str) -> None:
    rec = _derive(pid, form)
    assert _joined_words(rec) == [], rec["title"]
    assert form.lower() in rec["title"].lower()


def test_a_pendant_keeps_its_own_qualifier() -> None:
    """A derived pendant of a pendant template keeps "Dome": it is that form's own word."""
    rec = _derive("BRD-LTCPND", "Pendant")
    assert "Dome" in rec["title"]
    assert _joined_words(rec) == []


@pytest.fixture(scope="module")
def derived_ceiling_lights() -> list[dict]:
    built = scale.build(10**6)
    return [r for r in built.records if r["product_type"] == "Ceiling Light"]


def test_the_ceiling_derives_every_form_to_check(derived_ceiling_lights: list[dict]) -> None:
    forms = {_attrs(r)["fixture_type"] for r in derived_ceiling_lights}
    assert forms >= set(FORMS)
    assert len(derived_ceiling_lights) > 100


def test_no_derived_style_that_does_not_hang_has_a_drop_length(
    derived_ceiling_lights: list[dict],
) -> None:
    """Guard: no ceiling light whose ``fixture_type`` is not pendant or chandelier carries
    ``drop_length``. Metric: how many of the derived styles do, in the message."""
    wrong = [
        (r["product_id"], r["title"])
        for r in derived_ceiling_lights
        if _attrs(r)["fixture_type"] not in HANGING and "drop_length" in _attrs(r)
    ]
    assert not wrong, f"{len(wrong)} of {len(derived_ceiling_lights)}: {wrong[:5]}"


def test_no_derived_ceiling_title_joins_two_form_words(
    derived_ceiling_lights: list[dict],
) -> None:
    wrong = [
        (r["product_id"], r["title"])
        for r in derived_ceiling_lights
        if _joined_words(r)
    ]
    assert not wrong, f"{len(wrong)} of {len(derived_ceiling_lights)}: {wrong[:5]}"


def test_every_authored_ceiling_light_has_a_drop_length_only_if_it_hangs() -> None:
    for row in lighting_rows.CEILING_LIGHTS:
        keys = {a[0] for a in row.attrs}
        form = next(a[2] for a in row.attrs if a[0] == "fixture_type")
        assert "drop_length" not in keys or form in HANGING, row.code


# --- the reverse of #237 (gen#401): a form that hangs carries a drop_length ----------------------

#: Every ceiling-light template: each one is derived to both hanging forms.
CEILING_TEMPLATES = tuple(
    t["product_id"] for t in scale.templates() if t["product_type"] == "Ceiling Light"
)
HANGING_FORMS_TO_DERIVE = ("Pendant", "Chandelier")


def _drop(rec: dict) -> dict:
    drops = [a for a in rec["attributes"] if a["key"] == "drop_length"]
    assert len(drops) == 1, f"{rec['title']}: {len(drops)} drop_length entries"
    return drops[0]


@pytest.mark.parametrize("pid", CEILING_TEMPLATES)
@pytest.mark.parametrize("form", HANGING_FORMS_TO_DERIVE)
def test_a_hanging_form_derived_from_any_template_carries_a_drop_length(
    pid: str, form: str
) -> None:
    """One assertion per (template, hanging form): a pendant or chandelier derived from a flush,
    semi-flush or spotlight template has a ``drop_length``, in centimetres as the authored ones."""
    rec = _derive(pid, form)
    assert _attrs(rec)["fixture_type"] == form
    drop = _drop(rec)
    assert drop["unit_code"] == "CMT", rec["title"]
    assert float(drop["value"]) > 0, rec["title"]
    assert drop["value_canonical"] == float(drop["value"]) * 10, rec["title"]


@pytest.mark.parametrize("pid", CEILING_TEMPLATES)
def test_a_derived_hanging_drop_sits_among_the_templates_own_keys(pid: str) -> None:
    """The added entry follows the fixture's size, ahead of its shade, as the authored ones do."""
    keys = [a["key"] for a in _derive(pid, "Chandelier")["attributes"]]
    assert "drop_length" in keys, f"{pid}: a derived Chandelier has no drop_length: {keys}"
    assert keys.index("drop_length") < keys.index("shade_material"), keys


def test_every_derived_hanging_style_has_a_drop_length(
    derived_ceiling_lights: list[dict],
) -> None:
    """Guard: the converse of the one above. Metric: how many hanging styles lack one."""
    wrong = [
        (r["product_id"], r["title"])
        for r in derived_ceiling_lights
        if _attrs(r)["fixture_type"] in HANGING and "drop_length" not in _attrs(r)
    ]
    assert not wrong, f"{len(wrong)} of {len(derived_ceiling_lights)}: {wrong[:5]}"


def test_every_authored_hanging_ceiling_light_has_a_drop_length() -> None:
    lacking = [
        row.code
        for row in lighting_rows.CEILING_LIGHTS
        if next(a[2] for a in row.attrs if a[0] == "fixture_type") in HANGING
        and "drop_length" not in {a[0] for a in row.attrs}
    ]
    assert not lacking, lacking
