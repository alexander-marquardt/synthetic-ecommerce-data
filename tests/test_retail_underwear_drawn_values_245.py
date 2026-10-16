"""Underwear drawn values (gen#245): a different cut, slip length or denier is a different drawing.

``test_retail_underwear_208.py`` counts the marked groups a record states (straps, legs, a hood,
a belt, bands). It cannot see a drawing param that changes the outline or the opacity rather than
a count, so two hand mutants survived it: a thong drawn as a brief
(``underwear_rows.CUTS["Thong"] = "brief"``) and every slip hung at the same length
(``kit_underwear.SLIP_HEM`` all 322). These checks render each distinct value of a drawn
attribute and assert the renders are as many as the values.

The metric is :func:`_identical_values`: the values of one attribute whose drawings are the same.
:data:`KNOWN_SAME` is the whole list of them, each with the reason it is right; any other pair
is a value the shopper is told about and the picture does not show.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import kit  # noqa: E402
import underwear_rows  # noqa: E402

ROWS = underwear_rows.ROWS

#: (product type, the attribute a shopper reads, the drawing param it is drawn through).
DRAWN = [
    ("Knickers", "cut", "cut"),
    ("Tights", "denier", "denier"),
    ("Tights", "finish", "finish"),
    ("Tights", "control_top", "control"),
    ("Vest", "style", "style"),
    ("Slip", "length", "length"),
    ("Shapewear", "shapewear_type", "type"),
    ("Shapewear", "seamless", "seamless"),
    ("Shapewear", "control_level", "control"),
    ("Dressing Gown", "length", "length"),
    ("Dressing Gown", "hood", "hood"),
    ("Boxers", "fit", "fit"),
]  # fmt: skip

#: The values that share a drawing, by (type, attribute), and why.
KNOWN_SAME = {
    # A full brief is the brief cut with full back coverage: one outline, two names.
    ("Knickers", "cut"): [{"Briefs", "Full Briefs"}],
    # Sheer and opaque are the denier (the opacity) and patterned is the colorway's print, so
    # only a fleece lining adds a mark of its own.
    ("Tights", "finish"): [{"Opaque", "Patterned", "Sheer"}],
}  # fmt: skip


def _attr(row: underwear_rows.Row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _baseline(rows: list[underwear_rows.Row]) -> dict[str, str]:
    """The most common value of every param in a type, so a value is compared on its own."""
    seen: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for row in rows:
        for key, value in row.params:
            seen[key][value] += 1
    return {key: counts.most_common(1)[0][0] for key, counts in seen.items()}


def _renders(ptype: str, attr: str, param: str) -> dict[str, str]:
    """Each distinct value of ``attr`` drawn through its param, the other params held fixed."""
    rows = [r for r in ROWS if r.product_type == ptype]
    base = _baseline(rows)
    fill = kit.Fill("solid", "#123456", "#654321")
    out: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        params = {**base, param: dict(row.params)[param]}
        out[_attr(row, attr)].add(kit.render(row.shape, fill, params=params))
    assert {v: len(s) for v, s in out.items() if len(s) != 1} == {}, "one value, two drawings"
    return {value: next(iter(svgs)) for value, svgs in out.items()}


def _identical_values(ptype: str, attr: str, param: str) -> list[set[str]]:
    """The groups of values of one attribute that draw the same (the metric)."""
    by_svg: dict[str, set[str]] = collections.defaultdict(set)
    for value, svg in _renders(ptype, attr, param).items():
        by_svg[svg].add(value)
    return sorted((g for g in by_svg.values() if len(g) > 1), key=sorted)


def _lowest_y(svg: str) -> float:
    """The lowest point (the largest y) any path of the drawing reaches."""
    ys = []
    for d in re.findall(r'\sd="([^"]*)"', svg):
        nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
        ys += nums[1::2]
    return max(ys)


@pytest.mark.parametrize("case", DRAWN, ids=lambda c: f"{c[0]}-{c[1]}")
def test_each_value_of_a_drawn_attribute_draws_differently(case: tuple[str, str, str]) -> None:
    ptype, attr, param = case
    assert _identical_values(ptype, attr, param) == KNOWN_SAME.get((ptype, attr), [])


def test_the_values_that_share_a_drawing_are_values_the_rows_use() -> None:
    """A stale entry in KNOWN_SAME would hide a new identical pair behind its name."""
    used = {(p, a): {_attr(r, a) for r in ROWS if r.product_type == p} for p, a, _ in DRAWN}
    stale = [
        (key, sorted(group - used[key]))
        for key, groups in KNOWN_SAME.items()
        for group in groups
        if group - used[key]
    ]
    assert stale == []


@pytest.mark.parametrize(
    ("ptype", "order"),
    [("Slip", ["Mini", "Midi", "Full"]), ("Dressing Gown", ["Short", "Knee", "Full"])],
    ids=["Slip", "Dressing Gown"],
)
def test_a_longer_garment_hangs_lower(ptype: str, order: list[str]) -> None:
    """Two lengths that flare differently still draw as two renders, so the metric alone would
    pass a slip whose every length reaches the same hem; the hem itself must step down."""
    renders = _renders(ptype, "length", "length")
    assert set(renders) == set(order)
    hems = [_lowest_y(renders[v]) for v in order]
    assert hems == sorted(set(hems)), dict(zip(order, hems, strict=True))


def test_a_higher_denier_is_drawn_more_opaque() -> None:
    renders = _renders("Tights", "denier", "denier")
    ops = {}
    for denier, svg in renders.items():
        found = re.search(r'<g opacity="([\d.]+)"', svg)
        assert found, f"a {denier} denier drawing states no opacity"
        ops[int(denier)] = float(found.group(1))
    ordered = [ops[d] for d in sorted(ops)]
    assert ordered == sorted(set(ordered)), ops
