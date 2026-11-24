"""Measure every product type's picture for fill and flatness, worst first (gen#1129).

    uv run python scripts/picture_fill_1129.py --out .agent/fill-1129 [--skus 500000]

For each (product type, shape) of the build, one SKU of the type's most common pack is drawn
through ``image_release.render``, and so are its largest and smallest packs when it has more
than one. Each drawing is measured with gen#1111's method (``sheet_cover``'s grid, read here on
the measuring side only, so arcs and ``<use>`` copies count):

* **whole**: the share of the served 400 x 400 image that ``<g class="product">`` paints;
* **area**: the share of ``house_styles.TURN_AREA`` the plain-sheet drawing paints, its
  ground shadow not counted (the floor #1111 holds produce to);
* **flat**: one solid color paints most of the figure, or it carries no highlight and no
  shadow (a gradient, a translucent overlay, a white gloss stroke, or a ``_shade``/``_tint``
  tone of another of its colors);
* **empty**: the area share is under 35%;
* **drawn to scale**: a SKU attribute naming a dimension (``diameter_cm``) is a drawing param
  that the kit's own code reads; for an industrial type, a length the SKU publishes that its
  figure draws to (made longer, the figure changes). A drawn-to-scale industrial type is out of
  scope for a redraw (the maintainer, 2026-11-21);
* **render cost**: the seconds each served render takes, and the wall time to re-render a
  catalogue of ``--catalogue-skus`` on ``--vcpus`` workers at that rate.

The industrial rows (slice 2) draw one SKU per industrial type of the default build through
``core.drawing.draw_product``, as served, and measure its 200 x 300 sheet the same way.

It writes ``types.md`` and ``kits.md`` (the two tables, worst first), ``rows.json`` (every
render's numbers), and ``worst40.html`` and ``worst40.svg`` (the worst 40 in-scope types' served
pictures). It changes no drawing: docs/retail-prototype/picture-fill-1129.md.
"""

from __future__ import annotations

import argparse
import collections
import copy
import html
import inspect
import json
import math
import os
import re
import statistics
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from synthetic_ecommerce_data.core import domain
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing import sheet as core_sheet
from synthetic_ecommerce_data.core.drawing import svg as core_svg
from synthetic_ecommerce_data.domains.retail import export, kit, scale, sheet_cover
from synthetic_ecommerce_data.domains.retail import image_release as ir
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.sheet_extent import (
    _ARGS,
    _DEFINITIONS,
    _NUMBER,
    IDENTITY,
    NS,
    Box,
    Matrix,
    _apply,
    _mul,
    _transform,
)

#: The whole served image, and the grid step #1111's measurements use.
IMAGE: Box = (0.0, 0.0, 400.0, 400.0)
STEP = 4.0
#: A drawing whose area share is under this is empty (gen#1129, step 2).
EMPTY_FLOOR = 0.35
#: One solid color painting more than this share of the figure makes it flat.
FLAT_SHARE = 0.5
#: A tone (a shade or tint of another of the figure's colors) counts as shading from this share.
TONE_SHARE = 0.02
#: A tone's base color is this far from grey (channel spread), so two greys are two parts.
CHROMA = 24
#: Points per flattened arc.
ARC_STEPS = 16
XLINK = "{http://www.w3.org/1999/xlink}href"
#: The drawing-spec keys that size a SKU's pack, and the params that name one.
PACK_FIELDS = ("size_scale", "pack_scale", "pack_count", "printed_count")
PACK_PARAMS = ("pack_size", "pack", "count")
#: A SKU attribute that names a dimension a drawing could be drawn to.
DIMENSION = re.compile(r"length|width|height|depth|diameter|radius|thickness|_(mm|cm|in|m)$")
#: A SKU value that is a length (a pizza's ``"12 inch"``): the drawing may be drawn to it.
LENGTH = re.compile(r"\s*\d+(\.\d+)?\s*(mm|cm|m|in|inch|inches|ft|\")\s*", re.IGNORECASE)
#: A pack's amount in one unit per kind, so ``"1L"`` is more than ``"500ml"``.
UNITS = {"ml": 1, "cl": 10, "l": 1000, "pint": 568, "pints": 568, "g": 1, "kg": 1000}
#: An industrial sheet (``core.drawing.sheet``): the whole image, the strip above the brand
#: plate the figure is drawn in, and the area inside its margins that a type's largest extent
#: fills (``sheet.type_scale``), the industrial counterpart of ``TURN_AREA``.
SHEET: Box = (0.0, 0.0, float(core_svg.WIDTH), float(core_svg.HEIGHT))
SHEET_FIGURE: Box = (0.0, 0.0, float(core_svg.WIDTH), core_sheet.FIGURE_HEIGHT)
SHEET_AREA: Box = (
    core_sheet.MARGIN,
    core_sheet.MARGIN,
    core_svg.WIDTH - core_sheet.MARGIN,
    core_sheet.FIGURE_HEIGHT - core_sheet.MARGIN,
)
#: How much longer a published length is made to see whether a figure draws to it.
LONGER = 1.5
#: The in-scope note on a drawn-to-scale industrial type (the maintainer, 2026-11-21).
OUT_OF_SCOPE = "out of scope (maintainer 11-21): drawn to scale"
#: The industrial kinds the maintainer names as getting a realistic drawing (2026-11-21: "others
#: such as hammers, screwdrivers, electric drill, etc. would get realistic drawings"): in scope
#: even where their code draws to a length, with the note saying so.
NAMED_REALISTIC = ("hammer_", "screwdriver", "electric_drill")
NAMED_NOTE = "yes (maintainer 11-21 names it realistic; its code draws to scale)"


def in_scope(type_key: str, scaled: list[str]) -> tuple[bool, str]:
    """Whether an industrial type is in scope for a redraw, and its table note."""
    if any(type_key.startswith(k) for k in NAMED_REALISTIC):
        return True, NAMED_NOTE if scaled else "yes"
    return (False, OUT_OF_SCOPE) if scaled else (True, "yes")


# --- reading the SVG -----------------------------------------------------------------------


def _arc_points(
    x1: float,
    y1: float,
    rx: float,
    ry: float,
    phi: float,
    large: int,
    sweep: int,
    x2: float,
    y2: float,
) -> list[tuple[float, float]]:
    """The SVG endpoint arc from (x1, y1) to (x2, y2) as points (SVG 1.1 appendix F.6)."""
    if rx == 0 or ry == 0 or (x1, y1) == (x2, y2):
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    c, s = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    xp, yp = c * dx + s * dy, -s * dx + c * dy
    grow = xp**2 / rx**2 + yp**2 / ry**2
    if grow > 1:
        rx, ry = rx * math.sqrt(grow), ry * math.sqrt(grow)
    num = rx**2 * ry**2 - rx**2 * yp**2 - ry**2 * xp**2
    den = rx**2 * yp**2 + ry**2 * xp**2
    k = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = k * rx * yp / ry, -k * ry * xp / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2

    def angle(ux: float, uy: float, vx: float, vy: float) -> float:
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    ux, uy = (xp - cxp) / rx, (yp - cyp) / ry
    start = angle(1, 0, ux, uy)
    turn = angle(ux, uy, (-xp - cxp) / rx, (-yp - cyp) / ry)
    if not sweep and turn > 0:
        turn -= 2 * math.pi
    elif sweep and turn < 0:
        turn += 2 * math.pi
    out = []
    for i in range(1, ARC_STEPS + 1):
        t = start + turn * i / ARC_STEPS
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + ex * c - ey * s, cy + ex * s + ey * c))
    return out


def flatten_arcs(d: str) -> str:
    """A path's ``d`` with every arc (``A``/``a``) as absolute lines, for ``sheet_cover``."""
    if not re.search(r"[Aa]", d):
        return d
    out: list[str] = []
    cur = start = (0.0, 0.0)
    for cmd, body in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        up, rel = cmd.upper(), cmd.islower()
        nums = [float(x) for x in _NUMBER.findall(body)]
        if up == "Z":
            out.append("Z")
            cur = start
            continue
        width = 7 if up == "A" else _ARGS[up]
        for i in range(0, len(nums), width):
            n = nums[i : i + width]
            ox, oy = cur if rel else (0.0, 0.0)
            if up == "A":
                end = (n[5] + ox, n[6] + oy)
                pts = _arc_points(*cur, n[0], n[1], n[2], int(n[3]), int(n[4]), *end)
                out += [f"L{x:.3f},{y:.3f}" for x, y in pts]
            elif up == "H":
                end = (n[0] + ox, cur[1])
                out.append(f"L{end[0]:.3f},{end[1]:.3f}")
            elif up == "V":
                end = (cur[0], n[0] + oy)
                out.append(f"L{end[0]:.3f},{end[1]:.3f}")
            else:
                pts = [(n[j] + ox, n[j + 1] + oy) for j in range(0, len(n), 2)]
                end = pts[-1]
                head = "L" if up == "M" and i else up
                out.append(head + " ".join(f"{x:.3f},{y:.3f}" for x, y in pts))
                if up == "M" and not i:
                    start = end
            cur = end
    return " ".join(out)


def inline_uses(root: ET.Element) -> None:
    """Replace each ``<use>`` by a copy of what it names, so a pack's copies count."""
    named = {el.get("id"): el for el in root.iter() if el.get("id")}
    for _ in range(4):  # a copy may hold a use of its own
        uses = [(p, u) for p in root.iter() for u in p if u.tag == NS + "use"]
        if not uses:
            return
        for parent, use in uses:
            ref = (use.get("href") or use.get(XLINK) or "").lstrip("#")
            at = list(parent).index(use)
            parent.remove(use)
            if ref not in named:
                continue
            g = ET.Element(NS + "g")
            moved = f"{use.get('transform') or ''} translate({use.get('x', 0)} {use.get('y', 0)})"
            g.set("transform", moved.strip())
            for key in ("class", "fill", "opacity"):
                if use.get(key) is not None:
                    g.set(key, use.get(key))
            body = copy.deepcopy(named[ref])
            body.attrib.pop("id", None)
            g.append(body)
            parent.insert(at, g)


def _polygons(el: ET.Element, tag: str) -> list[list[tuple[float, float]]]:
    if tag == "path":
        return sheet_cover._subpaths(flatten_arcs(el.get("d", "")))
    if tag in ("polygon", "polyline"):
        nums = [float(x) for x in _NUMBER.findall(el.get("points", ""))]
        return [list(zip(nums[::2], nums[1::2], strict=True))] if len(nums) >= 6 else []
    return sheet_cover._polygons(el, tag)


def _rgb(color: str) -> tuple[int, int, int] | None:
    color = color.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", color):
        color = "#" + "".join(ch * 2 for ch in color[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", color):
        return {"white": (255, 255, 255), "black": (0, 0, 0)}.get(color)
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def _luma(rgb: tuple[int, int, int]) -> float:
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255


def tone(color: str, of: str) -> str | None:
    """``"shade"`` when ``color`` is ``of`` mixed toward black (``kit._shade``), ``"tint"``
    when toward white (``kit._tint``), else None. ``of`` must be a color, not a grey."""
    a, b = _rgb(color), _rgb(of)
    if a is None or b is None or a == b or max(b) - min(b) < CHROMA:
        return None  # a grey lid on a white label is two parts, not a shade of one
    for kind, (x, y) in (
        ("shade", (a, b)),
        ("tint", (tuple(255 - v for v in a), tuple(255 - v for v in b))),
    ):
        ratios = [p / q for p, q in zip(x, y, strict=True) if q >= 24]
        if len(ratios) == 3 and max(ratios) - min(ratios) <= 0.08 and 0.3 <= ratios[0] <= 0.95:
            return kind
    return None


@dataclass(frozen=True)
class Measure:
    """What :func:`measure` reads off one drawing."""

    cover: float  #: the share of the box the figure paints
    solid: float  #: the largest share of the figure one solid color paints
    highlight: bool
    shadow: bool

    @property
    def flat(self) -> bool:
        return self.solid > FLAT_SHARE or not (self.highlight or self.shadow)


class _Paint:
    """The figure's color at each grid point, painted in document order."""

    def __init__(self, box: tuple[float, float, float, float]) -> None:
        self.grid = sheet_cover._Grid(box, STEP)
        self.label = np.zeros(self.grid.x.shape, dtype=int)  # 0: unpainted
        self.keys: dict[object, int] = {None: 0}
        self.highlight = self.shadow = False
        #: A fill of this color is paper, not figure (an industrial sheet's cut-outs).
        self.erase: str | None = None

    def intern(self, key: object) -> int:
        return self.keys.setdefault(key, len(self.keys))

    def lay(self, inside: np.ndarray, fill: str, alpha: float, gradients: set[str]) -> None:
        if self.erase is not None and alpha >= 1 and fill.lower() == self.erase:
            self.label[inside] = 0  # a hole cut in the paper's color, or the lens's white
            return
        ref = re.fullmatch(r"url\(#([^)]+)\)", fill)
        if ref is not None:
            gradient = ref.group(1) in gradients
            self.highlight |= gradient
            self.shadow |= gradient
            self.label[inside] = self.intern(("gradient" if gradient else "pattern", fill))
            return
        if alpha >= 1:
            self.label[inside] = self.intern(fill.lower())
            return
        rgb = _rgb(fill)
        if rgb is not None and _luma(rgb) >= 0.7:
            self.highlight = True
        elif rgb is not None and _luma(rgb) <= 0.3:
            self.shadow = True
        under = self.label[inside]
        self.label[inside] = [self.intern(("over", k, fill, alpha)) for k in under.tolist()]

    def measure(self) -> Measure:
        painted = self.label > 0
        total = int(painted.sum())
        if not total:
            return Measure(0.0, 0.0, self.highlight, self.shadow)
        names = {v: k for k, v in self.keys.items()}
        counts = collections.Counter(self.label[painted].tolist())
        solid = {names[k]: n for k, n in counts.items() if isinstance(names[k], str)}
        highlight, shadow = self.highlight, self.shadow
        toned = [
            (a, b)
            for a in solid
            for b in solid
            if solid[a] / total >= TONE_SHARE and solid[b] / total >= TONE_SHARE
        ]
        for a, b in toned:
            kind = tone(a, b)
            if kind == "shade":
                shadow = True
            elif kind == "tint":
                highlight = True
        top = max(solid.values(), default=0)
        return Measure(float(painted.mean()), top / total, highlight, shadow)


def _light_stroke(el: ET.Element) -> bool:
    rgb = _rgb(el.get("stroke", "none"))
    alpha = float(el.get("stroke-opacity", el.get("opacity", 1.0)))
    return rgb is not None and _luma(rgb) >= 0.9 and alpha < 1


def _walk(
    el: ET.Element,
    m: Matrix,
    paint: _Paint,
    named: dict[str, ET.Element],
    gradients: set[str],
    skip: set[str],
    fill: str | None,
    alpha: float,
) -> None:
    tag = el.tag.removeprefix(NS)
    if tag in _DEFINITIONS or skip & set((el.get("class") or "").split()):
        return
    alpha *= float(el.get("opacity", 1.0))
    if alpha <= 0:
        return
    here = _mul(m, _transform(el.get("transform")))
    fill = el.get("fill", fill)
    shapes = ("path", "rect", "circle", "ellipse", "polygon", "polyline")
    if tag in shapes and _light_stroke(el):
        paint.highlight = True
    if tag in shapes and fill != "none":
        own = alpha * float(el.get("fill-opacity", 1.0))
        polys = [[_apply(here, p) for p in poly] for poly in _polygons(el, tag)]
        inside = paint.grid.fill(polys)
        ref = re.fullmatch(r"url\(#([^)]+)\)", el.get("clip-path") or "")
        if ref is not None and ref.group(1) in named:
            clip = np.zeros(inside.shape, dtype=bool)
            for child in named[ref.group(1)]:
                cut = _polygons(child, child.tag.removeprefix(NS))
                clip |= paint.grid.fill([[_apply(here, p) for p in poly] for poly in cut])
            inside &= clip
        if own > 0 and inside.any():
            paint.lay(inside, fill, own, gradients)
    for child in el:
        _walk(child, here, paint, named, gradients, skip, fill, alpha)


def measure(
    svg: str | bytes,
    box: Box = IMAGE,
    skip: tuple[str, ...] = ("ground",),
    only: str | None = None,
    erase_paper: bool = False,
) -> Measure:
    """The cover, solid share and shading of an SVG's figure over ``box``: every filled shape,
    or with ``only`` those inside the group of that class (``"product"`` on a served image).
    The paper (a top-level rect the size of the sheet) is not the figure; with ``erase_paper``,
    a fill of the paper's color is not either (it cuts a hole, as an industrial sheet does)."""
    root = ET.fromstring(svg)
    inline_uses(root)
    sizes = {("400", "400"), (root.get("width"), root.get("height"))}
    paper = None
    for el in list(root):
        if el.tag == NS + "rect" and (el.get("width"), el.get("height")) in sizes:
            paper = paper or (el.get("fill") or "").lower()
            root.remove(el)
    named = {el.get("id", ""): el for el in root.iter()}
    gradients = {k for k, el in named.items() if el.tag.removeprefix(NS).endswith("Gradient")}
    tops = [root]
    if only is not None:
        tops = [el for el in root.iter() if only in (el.get("class") or "").split()][:1]
    paint = _Paint(box)
    paint.erase = paper if erase_paper else None
    for top in tops:
        _walk(top, IDENTITY, paint, named, gradients, set(skip), None, 1.0)
    return paint.measure()


# --- choosing the SKUs ---------------------------------------------------------------------


def pack_key(spec: dict) -> tuple:
    """What sizes the pack a SKU's drawing shows: its size rung, pack scale and count."""
    params = spec.get("params") or {}
    return tuple((k, spec[k]) for k in PACK_FIELDS if k in spec) + tuple(
        (k, params[k]) for k in PACK_PARAMS if k in params
    )


def _amount(value: object) -> float:
    """A pack value as a number: ``"6 x 330ml"`` is 1980, ``"1L"`` 1000, ``"4 pack"`` 4."""
    text = str(value).strip().lower()
    found = re.fullmatch(r"(?:(\d+)\s*x\s*)?(\d+(?:\.\d+)?)\s*([a-z]*).*", text)
    if found is None:
        return 1.0
    times, number, unit = found.groups()
    return int(times or 1) * float(number) * UNITS.get(unit, 1)


def pack_size(key: tuple) -> float:
    """A pack key's size: the product of its amounts (size rung, scale, count, pack size)."""
    return math.prod(_amount(value) for _, value in key)


def chosen_packs(keys: list[tuple]) -> list[tuple[str, tuple]]:
    """``(role, key)`` for the most common pack, then the largest and the smallest when they
    differ from it (a type with one pack gives one)."""
    counts = collections.Counter(keys)
    common = max(counts, key=lambda k: (counts[k], -keys.index(k)))
    out = [("common", common)]
    if len(counts) > 1:
        for role, pick in (("largest", max), ("smallest", min)):
            key = pick(counts, key=lambda k: (pack_size(k), -keys.index(k)))
            if all(key != k for _, k in out):
                out.append((role, key))
    return out


def scaled_keys(params: dict[str, set[str]], source: str) -> list[str]:
    """The SKU params the kit's code reads that are a dimension (drawn to scale): the key names
    one (``diameter_cm``), or its values are lengths (a pizza's ``pack_size``, ``"12 inch"``)."""
    return sorted(
        k
        for k, values in params.items()
        if (DIMENSION.search(k) or any(LENGTH.fullmatch(str(v)) for v in values))
        and re.search(rf"\b{k}\b", source)
    )


# --- the tables ----------------------------------------------------------------------------


def _pct(x: float) -> str:
    return f"{x:.0%}"


def _yes(x: bool) -> str:
    return "yes" if x else "no"


def _scope(row: dict) -> str:
    if row.get("note"):
        return row["note"]
    return "yes" if row["in_scope"] else (OUT_OF_SCOPE if row["scale"] else "no")


def type_rows(renders: list[dict], served: dict[tuple[str, str], int]) -> list[dict]:
    """One row per (kit, product type, shape), from its most common pack, worst area first."""
    by = collections.defaultdict(list)
    for r in renders:
        by[(r["kit"], r["type"], r["shape"])].append(r)
    rows = []
    for (kit_name, ptype, shape), rs in by.items():
        common = next(r for r in rs if r["role"] == "common")
        areas = [r["area"] for r in rs]
        rows.append(
            {
                "kit": kit_name,
                "type": ptype,
                "shape": shape,
                "skus": served[(ptype, shape)],
                "whole": common["whole"],
                "area": common["area"],
                "area_min": min(areas),
                "area_max": max(areas),
                "flat": common["flat"],
                "empty": common["empty"],
                "scale": common["scale"],
                "in_scope": common["in_scope"],
                "sku": common["sku"],
                "domain": common.get("domain", "retail"),
                "note": common.get("note", ""),
            }
        )
    return sorted(rows, key=lambda r: (r["area"], r["whole"], r["kit"], r["type"]))


def kit_rows(types: list[dict]) -> list[dict]:
    """One row per kit over its type rows: medians, and yes when most of its types are. A kit
    that holds in-scope types and drawn-to-scale ones is split in two by them (gen#1129)."""
    kinds = collections.defaultdict(set)
    for r in types:
        kinds[r["kit"]].add(r["in_scope"])
    by = collections.defaultdict(list)
    for r in types:
        name = r["kit"]
        if len(kinds[name]) > 1:
            name += " (in scope)" if r["in_scope"] else " (drawn to scale)"
        by[name].append(r)
    rows = []
    for kit_name, rs in by.items():
        worst = min(rs, key=lambda r: r["area"])
        rows.append(
            {
                "kit": kit_name,
                "types": len({r["type"] for r in rs}),
                "skus": sum(r["skus"] for r in rs),
                "whole": statistics.median(r["whole"] for r in rs),
                "area": statistics.median(r["area"] for r in rs),
                "flat": sum(r["flat"] for r in rs) * 2 > len(rs),
                "empty": statistics.median(r["area"] for r in rs) < EMPTY_FLOOR,
                "scale": any(r["scale"] for r in rs),
                "in_scope": any(r["in_scope"] for r in rs),
                "domain": rs[0].get("domain", "retail"),
                "worst": f"{worst['type']} ({worst['shape']}) {_pct(worst['area'])}",
            }
        )
    return sorted(rows, key=lambda r: (r["area"], r["whole"], r["kit"]))


def type_table(rows: list[dict]) -> str:
    head = (
        "| # | kit | product type | shape | SKUs served | whole % | area % | area range "
        "| flat | empty | drawn to scale | in scope |"
    )
    lines = [head, "|" + "---|" * 12]
    for i, r in enumerate(rows, 1):
        span = f"{_pct(r['area_min'])}-{_pct(r['area_max'])}"
        lines.append(
            f"| {i} | `{r['kit']}` | {r['type']} | {r['shape']} | {r['skus']:,} "
            f"| {_pct(r['whole'])} | {_pct(r['area'])} | {span} | {_yes(r['flat'])} "
            f"| {_yes(r['empty'])} | {_yes(bool(r['scale']))} | {_scope(r)} |"
        )
    return "\n".join(lines) + "\n"


def kit_table(rows: list[dict], unserved: list[str]) -> str:
    head = (
        "| # | kit | product types | SKUs served | whole % | area % | flat | empty "
        "| drawn to scale | in scope | worst type |"
    )
    lines = [head, "|" + "---|" * 11]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | `{r['kit']}` | {r['types']} | {r['skus']:,} | {_pct(r['whole'])} "
            f"| {_pct(r['area'])} | {_yes(r['flat'])} | {_yes(r['empty'])} "
            f"| {_yes(r['scale'])} | {_scope(r)} | {r['worst']} |"
        )
    if unserved:
        lines += [
            "",
            "Kit modules that draw no served type's shape: "
            + ", ".join(f"`{k}`" for k in unserved),
        ]
    return "\n".join(lines) + "\n"


def cost(seconds: list[float], skus: int, vcpus: int) -> dict:
    """Render seconds per SKU (median, p95, mean) and the wall time to re-render ``skus`` SKUs
    on ``vcpus`` workers at the mean rate."""
    ordered = sorted(seconds)
    p95 = ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]
    mean = statistics.fmean(ordered)
    return {
        "median_s": statistics.median(ordered),
        "p95_s": p95,
        "mean_s": mean,
        "skus": skus,
        "vcpus": vcpus,
        "wall_s": mean * skus / vcpus,
    }


def _caption(i: int, r: dict) -> str:
    return (
        f"{i}. {r['type']} ({r['kit']}, {r['shape']}) area {_pct(r['area'])}, "
        f"whole {_pct(r['whole'])}, {r['sku']}"
    )


def worst(rows: list[dict], count: int = 40) -> list[dict]:
    """The ``count`` worst in-scope type rows: a drawn-to-scale type gets no redraw."""
    return [r for r in rows if r["in_scope"]][:count]


def contact_sheet(rows: list[dict], svgs: dict[str, bytes], count: int = 40) -> str:
    cells = []
    for i, r in enumerate(worst(rows, count), 1):
        caption = _caption(i, r)
        cells.append(
            f"<figure>{svgs[r['sku']].decode()}<figcaption>{html.escape(caption)}"
            "</figcaption></figure>"
        )
    style = (
        "body{font:12px sans-serif}main{display:grid;grid-template-columns:repeat(5,220px);"
        "gap:8px}figure{margin:0}svg{width:220px;height:220px;border:1px solid #ccc}"
    )
    return (
        f"<!doctype html><meta charset=utf-8><title>Worst {count} pictures (gen#1129)</title>"
        f"<style>{style}</style><main>{''.join(cells)}</main>\n"
    )


_ID = re.compile(r'\bid="([^"]+)"')


def _own_ids(svg: str, prefix: str) -> str:
    """``svg`` with each id (and every reference to it) prefixed, so cells' ids stay apart."""
    for name in sorted(set(_ID.findall(svg)), key=len, reverse=True):
        svg = re.sub(
            rf'(\bid="|url\(#|href="#){re.escape(name)}(?=[")])', rf"\g<1>{prefix}{name}", svg
        )
    return svg


def _placed(svg: str, x: float, y: float, size: float) -> str:
    """``svg`` as a nested ``<svg>`` at ``(x, y)``, ``size`` square (its viewBox kept)."""
    start = svg.index("<svg")
    end = svg.index(">", start)
    head = re.sub(r'\s(?:x|y|width|height)="[^"]*"', "", svg[start:end])
    return f'{svg[:start]}{head} x="{x}" y="{y}" width="{size}" height="{size}"{svg[end:]}'


def contact_svg(rows: list[dict], svgs: dict[str, bytes], count: int = 40, cols: int = 5) -> str:
    """The worst ``count`` in-scope pictures as one SVG (for a PNG on the issue): each in a
    200 x 200 cell, its own sheet scaled to fit, with its caption under it."""
    cell, cap = 200, 30
    picked = worst(rows, count)
    out = []
    for i, r in enumerate(picked):
        x, y = (i % cols) * cell, (i // cols) * (cell + cap)
        body = re.sub(r"<\?xml[^>]*>", "", svgs[r["sku"]].decode())
        body = _own_ids(body, f"c{i}-")
        out.append(_placed(body, x, y, cell))
        lines = (
            f"{i + 1}. {r['type']} ({r['kit'].removeprefix('industrial/')})",
            f"area {_pct(r['area'])}, whole {_pct(r['whole'])}, {r['shape']}",
        )
        for n, text in enumerate(lines):
            out.append(
                f'<text x="{x + 4}" y="{y + cell + 11 + 11 * n}" font-family="sans-serif" '
                f'font-size="9">{html.escape(text[:40])}</text>'
            )
    rows_n = math.ceil(len(picked) / cols) or 1
    w, h = cols * cell, rows_n * (cell + cap)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" '
        f'fill="#ffffff"/>{"".join(out)}</svg>\n'
    )


# --- the sweep -----------------------------------------------------------------------------


def _kit_of(shape_fn: object) -> tuple[str, str]:
    """A shape's kit module: its name and source."""
    fn = getattr(shape_fn, "func", shape_fn)
    module = sys.modules.get(getattr(fn, "__module__", ""), None)
    name = getattr(fn, "__module__", "?").rsplit(".", 1)[-1]
    try:
        return name, inspect.getsource(module) if module else ""
    except (OSError, TypeError):
        return name, ""


def sweep(recs: list[dict]) -> tuple[list[dict], dict, dict[str, bytes], set[str]]:
    """Render and measure the chosen SKUs of every (type, shape); return the render rows,
    the SKUs served per (type, shape), the served SVG of each render and the kits drawn."""
    shapes = kit.shapes()
    groups: dict[tuple[str, str], list[tuple[dict, dict, tuple]]] = collections.defaultdict(list)
    params: dict[tuple[str, str], dict[str, set[str]]] = collections.defaultdict(
        lambda: collections.defaultdict(set)
    )
    served: dict[tuple[str, str], int] = collections.Counter()
    for rec in recs:
        unit = (rec["product_type"], rec["drawing"]["shape"])
        served[unit] += rec["sku_count"]
        for sku in rec["skus"]:
            spec = export.drawing_spec(rec, sku)
            groups[unit].append((rec, sku, pack_key(spec)))
            for key, value in (spec.get("params") or {}).items():
                params[unit][key].add(str(value))
    renders, svgs, kits = [], {}, set()
    for (ptype, shape), members in sorted(groups.items()):
        kit_name, source = _kit_of(shapes[shape])
        kits.add(kit_name)
        scaled = scaled_keys(params[(ptype, shape)], source)
        keys = [k for _, _, k in members]
        for role, key in chosen_packs(keys):
            rec, sku, _ = members[keys.index(key)]
            t0 = time.perf_counter()
            served_svg = ir.render(rec, sku)
            seconds = time.perf_counter() - t0
            whole = measure(served_svg, IMAGE, only="product")
            plain = measure(ir.render(rec, sku, styled=False), TURN_AREA)
            svgs[sku["sku"]] = served_svg
            renders.append(
                {
                    "kit": kit_name,
                    "type": ptype,
                    "shape": shape,
                    "role": role,
                    "pack": dict(key),
                    "product_id": rec["product_id"],
                    "sku": sku["sku"],
                    "whole": round(whole.cover, 4),
                    "area": round(plain.cover, 4),
                    "solid": round(plain.solid, 4),
                    "highlight": plain.highlight,
                    "shadow": plain.shadow,
                    "flat": plain.flat,
                    "empty": plain.cover < EMPTY_FLOOR,
                    "scale": scaled,
                    "in_scope": True,
                    "seconds": seconds,
                }
            )
    return renders, served, svgs, kits


# --- the industrial rows (slice 2) ----------------------------------------------------------


def sheet_measures(svg: str | bytes) -> tuple[float, Measure]:
    """An industrial sheet's whole share (the figure over the 200 x 300 image, the brand plate
    under :data:`SHEET_FIGURE` not counted) and its measure over :data:`SHEET_AREA`. A fill in
    the paper's color is a hole, not paint (a cut-out, the magnifier's lens)."""
    figure = measure(svg, SHEET_FIGURE, erase_paper=True)
    share = (SHEET_FIGURE[3] - SHEET_FIGURE[1]) / (SHEET[3] - SHEET[1])
    return figure.cover * share, measure(svg, SHEET_AREA, erase_paper=True)


def lengthened(value: str) -> str | None:
    """A published length made :data:`LONGER` times longer, in inches; None for a value that is
    not one length (a list of sizes, a thread, a count)."""
    try:
        inches = parse_length(value).inches
    except (DimensionParseError, ValueError, TypeError):
        return None
    return f"{inches * LONGER:.4f} in"


def _drawing(fn, record: dict) -> tuple[str, str] | None:
    try:
        drawn = fn(dict(record))
    except Exception:  # noqa: BLE001  (a refused value draws nothing, so it is not drawn to)
        return None
    figure = getattr(drawn, "figure", drawn)
    return repr((figure.size_in, figure.shapes)), getattr(drawn, "source", "")


def drawn_to_scale(fn, record: dict) -> list[str]:
    """The lengths ``record`` publishes that the figure function ``fn`` draws to: made longer,
    the figure it draws changes, with its source unchanged (a value it refuses and replaces by a
    nominal one is not drawn to). This reads the kit code by running it, so a ``Dim`` of a spec
    and a geometry reader count alike; a size rung alone (``size_rungs``) is not drawn to scale,
    since its scale is symbolic."""
    base = _drawing(fn, record)
    if base is None:
        return []
    out = []
    for name, value in record.items():
        longer = lengthened(value)
        if longer is None:
            continue
        other = _drawing(fn, {**record, name: longer})
        if other is not None and other[1] == base[1] and other[0] != base[0]:
            out.append(name)
    return sorted(out)


def figure_kit(fn, type_key: str) -> tuple[str, str]:
    """An industrial figure function's kit (``industrial/<module>``) and its shape: the
    function's name, or the type's own key when the function is a type module's ``figure``."""
    inner = getattr(fn, "func", fn)
    module = getattr(inner, "__module__", "?").rsplit(".", 1)[-1]
    name = getattr(inner, "__name__", "?")
    return f"industrial/{module}", type_key if name in ("figure", "_figure", "<lambda>") else name


def industrial_sweep(catalog) -> tuple[list[dict], dict, dict[str, bytes], set[str]]:
    """:func:`sweep` for the industrial build: one SKU per type of its most common
    ``Units per Pack``, plus its largest and smallest on a pack type, each drawn with its
    product's siblings (its size rung and angle are the product's) as ``emit`` serves it."""
    from synthetic_ecommerce_data.core.drawing import draw_product  # noqa: PLC0415
    from synthetic_ecommerce_data.core.emit import drawing_record  # noqa: PLC0415
    from synthetic_ecommerce_data.domains.industrial.tabletype import PACK  # noqa: PLC0415

    groups: dict[str, list[tuple]] = collections.defaultdict(list)
    served: dict[tuple[str, str], int] = collections.Counter()
    shapes = {}
    for line in catalog.lines:
        fn, _ = domain.figure(line.type_key)
        shapes[line.type_key] = (fn, *figure_kit(fn, line.type_key))
        records = [drawing_record(catalog, line, child) for child in line.children]
        for i, (child, record) in enumerate(zip(line.children, records, strict=True)):
            pack = record.get(PACK) if domain.is_pack_type(line.type_key) else None
            key = ((PACK, pack),) if pack else ()
            groups[line.type_key].append((line, records, i, child, key))
        served[(line.type_key, shapes[line.type_key][2])] += len(line.children)
    renders, svgs, kits = [], {}, set()
    for ptype, members in sorted(groups.items()):
        fn, kit_name, shape = shapes[ptype]
        kits.add(kit_name)
        keys = [m[4] for m in members]
        for role, key in chosen_packs(keys):
            line, records, i, child, _ = members[keys.index(key)]
            t0 = time.perf_counter()
            served_svg = draw_product(ptype, line.brand, records, line.product_id)[i][0]
            seconds = (time.perf_counter() - t0) / len(records)
            whole, area = sheet_measures(served_svg)
            scaled = drawn_to_scale(fn, records[i])
            scope, note = in_scope(ptype, scaled)
            svgs[child.sku] = served_svg
            renders.append(
                {
                    "kit": kit_name,
                    "type": ptype,
                    "shape": shape,
                    "role": role,
                    "pack": dict(key),
                    "product_id": line.product_id,
                    "sku": child.sku,
                    "whole": round(whole, 4),
                    "area": round(area.cover, 4),
                    "solid": round(area.solid, 4),
                    "highlight": area.highlight,
                    "shadow": area.shadow,
                    "flat": area.flat,
                    "empty": area.cover < EMPTY_FLOOR,
                    "scale": scaled,
                    "in_scope": scope,
                    "note": note,
                    "seconds": seconds,
                    "domain": "industrial",
                    "spec_quality": line.spec_quality,
                }
            )
    return renders, served, svgs, kits


def _kit_modules() -> list[str]:
    here = Path(kit.__file__).parent
    return sorted(p.stem for p in [here / "kit.py", *here.glob("kit_*.py")])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--skus",
        type=int,
        default=None,
        help="measure the scaled build of this many SKUs (default: the templates)",
    )
    parser.add_argument(
        "--catalogue-skus",
        type=int,
        default=500_000,
        help="the catalogue size the re-render wall time is for",
    )
    parser.add_argument("--vcpus", type=int, default=os.cpu_count() or 1)
    parser.add_argument(
        "--no-industrial", action="store_true", help="measure the retail rows only (slice 1)"
    )
    args = parser.parse_args(argv)
    t0 = time.perf_counter()
    recs = scale.templates() if args.skus is None else scale.build(args.skus).records
    renders, served, svgs, kits = sweep(recs)
    spent_by = {"retail": cost([r["seconds"] for r in renders], args.catalogue_skus, args.vcpus)}
    if not args.no_industrial:
        from synthetic_ecommerce_data.domains.industrial.generate import generate  # noqa: PLC0415

        catalog = generate()
        more, more_served, more_svgs, _ = industrial_sweep(catalog)
        renders, svgs = renders + more, svgs | more_svgs
        served = {**served, **more_served}
        spent_by["industrial"] = cost([r["seconds"] for r in more], catalog.sku_count, args.vcpus)
    types = type_rows(renders, served)
    kits_drawn = kit_rows(types)
    unserved = [k for k in _kit_modules() if k not in kits]
    spent = cost([r["seconds"] for r in renders], args.catalogue_skus, args.vcpus)
    spent["by_domain"] = spent_by
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "types.md").write_text(type_table(types), encoding="utf-8")
    (args.out / "kits.md").write_text(kit_table(kits_drawn, unserved), encoding="utf-8")
    (args.out / "worst40.html").write_text(contact_sheet(types, svgs), encoding="utf-8")
    (args.out / "worst40.svg").write_text(contact_svg(types, svgs), encoding="utf-8")
    (args.out / "rows.json").write_text(
        json.dumps({"cost": spent, "renders": renders, "types": types}, indent=1, default=str),
        encoding="utf-8",
    )
    print(
        f"{len(renders)} renders, {len(types)} type rows, {len(kits_drawn)} kits, "
        f"{len(unserved)} kit modules unserved, {time.perf_counter() - t0:.0f} s"
    )
    for name, part in spent_by.items():
        print(
            f"{name}: render s/SKU median {part['median_s']:.4f} p95 {part['p95_s']:.4f}; "
            f"{part['skus']:,} SKUs on {part['vcpus']} vCPUs: {part['wall_s']:.0f} s wall"
        )
    print(f"out of scope (drawn to scale): {sum(not r['in_scope'] for r in types)} type rows")
    print(
        f"empty {sum(r['empty'] for r in types)}, flat {sum(r['flat'] for r in types)} "
        f"of {len(types)} type rows; written to {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
