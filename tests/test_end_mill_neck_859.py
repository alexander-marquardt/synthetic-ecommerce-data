"""An end mill states ``Neck Length`` only when it has a reduced neck, at a standard reach (#859).

A reduced neck is a long-reach tool's: the body behind the flutes is ground below the
cutting diameter for a stated length. A catalog prints that length on those tools only, in
a standard size and in the unit of the tool's other lengths. It used to be on every end
mill the sparsity draw kept, as ``length of cut * uniform(1.05, 1.4)`` in four decimals:
6,124 distinct values on 6,735 end mills in the served catalog.

The end-mill types are built alone here, which builds the same lines the whole build makes
for them (:func:`generate`). ``clean`` turns the unit defects off, so a value is spelled as
the builder spelled it; ``built`` is the default build, defects and all.
"""

from __future__ import annotations

import re

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import series
from synthetic_ecommerce_data.domains.industrial.generate import generate

END_MILLS = ("end_mill_square", "end_mill_ball")
NECK = "Neck Length"

#: Every reach the builder may state, in inches.
STANDARD_IN = [float(size) for size in series.NECK_LENGTHS_IN]
STANDARD_MM_IN = [mm / series.MM_PER_INCH for mm in series.NECK_LENGTHS_MM]


def _tools(catalog) -> list[tuple[str, str, list[dict]]]:
    """Each line's type, product id and its SKUs' attributes, the line's merged in (a zero-axis
    variant's specs sit on its product)."""
    out = []
    for line in catalog.lines:
        own = {a.name: a for a in line.attributes}
        skus = [{**own, **{a.name: a for a in sku.attributes}} for sku in line.children]
        out.append((line.type_key, line.product_id, skus))
    return out


def _geometry(attrs: dict) -> series.ToolGeometry | None:
    """The tool the SKU publishes, when it publishes every length the rule reads."""
    names = ("Milling Dia.", "Length of Cut", "Overall Length", "Shank Dia.")
    if any(attrs.get(name) is None or attrs[name].value_num is None for name in names):
        return None
    dia, loc, oal, shank = (attrs[name].value_num for name in names)
    system = "mm" if attrs["Length of Cut"].value.endswith("mm") else "in"
    return series.ToolGeometry(system, dia, loc, oal, shank, "")


@pytest.fixture(scope="module")
def clean():
    return _tools(generate(GeneratorConfig(defect_scale=0.0), types=END_MILLS))


@pytest.fixture(scope="module")
def built():
    return _tools(generate(GeneratorConfig(), types=END_MILLS))


def test_only_a_reduced_neck_lines_tools_state_a_neck_and_each_that_fits_does(clean) -> None:
    """The line is the mark: a reduced-neck line states the neck on every tool a reach fits,
    and a line that is not one states it on none. On a line of several lengths the neck is the
    next reach past the length of cut, and it (or its absence) follows that axis alone, so it is
    no third choice on the product page (#850)."""
    skus = [attrs for _, _, line in clean for attrs in line]
    marked_lines = reach_lines = 0
    for _, product_id, line in clean:
        stating = [NECK in attrs for attrs in line]
        if not any(stating):
            continue
        marked_lines += 1
        cuts: dict[str, set[str]] = {}
        for attrs in line:
            cuts.setdefault(attrs["Milling Dia."].value, set()).add(attrs["Length of Cut"].value)
        if any(len(lengths) > 1 for lengths in cuts.values()):
            reach_lines += 1
            by_cut: dict[str, set[str | None]] = {}
            for attrs in line:
                neck = attrs.get(NECK)
                by_cut.setdefault(attrs["Length of Cut"].value, set()).add(neck and neck.value)
                geom = _geometry(attrs)
                if neck is not None and geom is not None:
                    assert neck.value_num == pytest.approx(series.neck_lengths(geom)[0])
            assert all(len(necks) == 1 for necks in by_cut.values()), (product_id, by_cut)
            continue
        for attrs, states in zip(line, stating, strict=True):
            geom = _geometry(attrs)
            if geom is None:
                continue
            fits = bool(series.neck_lengths(geom))
            assert states == fits, (product_id, attrs["Milling Dia."].value)
    with_neck = sum(NECK in attrs for attrs in skus)
    assert marked_lines and reach_lines and with_neck
    # Near the census's 0.2727 of end mills, and well under every tool.
    assert 0.18 < with_neck / len(skus) < 0.36, (with_neck, len(skus))
    for key in END_MILLS:
        typed = [attrs for type_key, _, line in clean if type_key == key for attrs in line]
        assert any(NECK in attrs for attrs in typed), key


def test_a_stated_neck_is_a_standard_reach_the_tool_fits_in_its_length_of_cuts_unit(clean) -> None:
    for _, product_id, line in clean:
        for attrs in line:
            neck = attrs.get(NECK)
            if neck is None:
                continue
            loc = attrs["Length of Cut"].value
            unit = "mm" if loc.endswith("mm") else '"'
            assert neck.value.endswith(unit), (product_id, neck.value, loc)
            assert not re.search(r"\.\d{3,}", neck.value), (product_id, neck.value)
            standard = STANDARD_MM_IN if unit == "mm" else STANDARD_IN
            assert any(abs(neck.value_num - size) < 1e-6 for size in standard), neck.value
            dia = attrs["Milling Dia."].value_num
            most = series.REDUCED_NECK_MAX_DIA_MM / series.MM_PER_INCH if unit == "mm" else 0.5
            assert dia <= most + 1e-9, (product_id, attrs["Milling Dia."].value)
            assert attrs["Length of Cut"].value_num < neck.value_num <= 10 * dia + 1e-9, (
                product_id,
                loc,
                neck.value,
            )
            geom = _geometry(attrs)
            if geom is not None:
                grip = geom.overall_length_in - series.NECK_GRIP_SHANKS * geom.shank_dia_in
                assert neck.value_num <= grip + 1e-9, (product_id, neck.value)
                assert any(abs(neck.value_num - s) < 1e-6 for s in series.neck_lengths(geom)), (
                    product_id,
                    attrs["Milling Dia."].value,
                    loc,
                    neck.value,
                )


def test_tools_of_one_diameter_are_sold_at_several_reaches(clean) -> None:
    """The tool's own draw picks among the sizes that fit, not the shortest every time."""
    reaches: dict[str, set[str]] = {}
    for _, _, line in clean:
        for attrs in line:
            if NECK in attrs:
                reaches.setdefault(attrs["Milling Dia."].value, set()).add(attrs[NECK].value)
    assert max(len(values) for values in reaches.values()) >= 4, reaches


def test_a_neck_is_at_least_the_length_of_cut_and_shorter_than_the_tool(clean) -> None:
    checked = 0
    for _, product_id, line in clean:
        for attrs in line:
            neck = attrs.get(NECK)
            oal = attrs.get("Overall Length")
            if neck is None or oal is None:
                continue
            loc = attrs["Length of Cut"].value_num
            assert loc <= neck.value_num < oal.value_num, (product_id, loc, neck.value, oal.value)
            checked += 1
    assert checked > 100


def test_a_build_states_a_few_dozen_necks_not_thousands(clean, built) -> None:
    def distinct(tools) -> set[str]:
        return {attrs[NECK].value for _, _, line in tools for attrs in line if NECK in attrs}

    assert len(distinct(clean)) <= len(STANDARD_IN) + len(STANDARD_MM_IN)
    # The unit defects respell a few in the other system, as they do every length.
    assert len(distinct(built)) < 50, sorted(distinct(built))
