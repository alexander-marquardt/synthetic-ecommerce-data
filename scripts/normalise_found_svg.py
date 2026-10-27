"""Reduce a found SVG drawing to the plain vocabulary the generator loads (#102).

    python scripts/normalise_found_svg.py SOURCE.svg OUT.svg --select 0/-1 \\
        --role '#b3b3b3=part' --role gray=plain

A found drawing (an Openclipart or Wikimedia Commons file) carries what its author's editor
put there: logos and text in sibling groups, strokes, metadata, transforms, curves. None of it
may reach a sheet. This keeps ONE group, the one ``--select`` names, and writes every filled
path under it as polygons in a new file whose only elements are ``<svg>`` and ``<path>``:

* ``--select`` is a ``/``-separated list of child indices (negative counts from the end), walked
  from the root: ``0/-1`` is the last child of the root's first child;
* every ancestor ``transform`` (translate, scale, rotate, matrix) is applied to the points;
* a curve is flattened to :data:`CURVE_STEPS` segments;
* a subpath is a path of its own, because the generator's ``Poly`` has no holes;
* a fill becomes a role (``part``, ``plain``) through ``--role``; a fill with no role is an
  error, never a default, so nothing is painted that was not chosen;
* strokes, ids, styles and metadata are dropped;
* the drawing is shifted to the origin and scaled so its longer side is :data:`SIZE` units, to
  :data:`DECIMALS` decimals. The sheet scales it again; only the shape and its proportion count.

Anything the file may not hold is refused with ``ValueError`` (an arc, a DOCTYPE or entity, a
selected element that is not a ``g`` or a ``path``): a downloaded file is untrusted.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "{http://www.w3.org/2000/svg}"
#: The longer side of the written drawing, in its own units.
SIZE = 1000.0
DECIMALS = 1
#: Segments a cubic curve is flattened into.
CURVE_STEPS = 8

_NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_TRANSFORM = re.compile(r"(\w+)\s*\(([^)]*)\)")
#: How many numbers one repeat of each command takes.
_ARGS = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "z": 0}

Point = tuple[float, float]
Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _multiply(a: Matrix, b: Matrix) -> Matrix:
    """The matrix of ``b`` inside ``a``: a point goes through ``b`` first, then ``a``."""
    return (
        a[0] * b[0] + a[2] * b[1],
        a[1] * b[0] + a[3] * b[1],
        a[0] * b[2] + a[2] * b[3],
        a[1] * b[2] + a[3] * b[3],
        a[0] * b[4] + a[2] * b[5] + a[4],
        a[1] * b[4] + a[3] * b[5] + a[5],
    )


def _transform(text: str | None) -> Matrix:
    matrix = IDENTITY
    for name, body in _TRANSFORM.findall(text or ""):
        n = [float(v) for v in _NUMBER.findall(body)]
        if name == "translate":
            step: Matrix = (1.0, 0.0, 0.0, 1.0, n[0], n[1] if len(n) > 1 else 0.0)
        elif name == "scale":
            step = (n[0], 0.0, 0.0, n[1] if len(n) > 1 else n[0], 0.0, 0.0)
        elif name == "matrix" and len(n) == 6:
            step = (n[0], n[1], n[2], n[3], n[4], n[5])
        elif name == "rotate":
            c, s = math.cos(math.radians(n[0])), math.sin(math.radians(n[0]))
            cx, cy = (n[1], n[2]) if len(n) == 3 else (0.0, 0.0)
            step = (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy)
        else:
            raise ValueError(f"unsupported transform {name!r}")
        matrix = _multiply(matrix, step)
    return matrix


def _apply(m: Matrix, p: Point) -> Point:
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


def _subpaths(d: str) -> list[list[Point]]:
    """The points of each subpath of ``d``, curves flattened, in the path's own coordinates."""
    out: list[list[Point]] = []
    current: list[Point] = []
    start = pos = (0.0, 0.0)
    for command, body in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        low = command.lower()
        if low == "a":
            raise ValueError("unsupported path command 'arc'")
        if low not in _ARGS:
            raise ValueError(f"unsupported path command {command!r}")
        rel = command.islower()
        numbers = [float(v) for v in _NUMBER.findall(body)]
        if low == "z":
            if current:
                out.append(current)
            current, pos = [start], start
            continue
        size = _ARGS[low]
        if not numbers or len(numbers) % size:
            raise ValueError(f"path command {command!r} has {len(numbers)} numbers")
        for i in range(0, len(numbers), size):
            a = numbers[i : i + size]
            ox, oy = pos if rel else (0.0, 0.0)
            if low == "m" and i == 0:
                if current:
                    out.append(current)
                pos = start = (ox + a[0], oy + a[1])
                current = [pos]
            elif low in ("m", "l"):
                pos = (ox + a[0], oy + a[1])
                current.append(pos)
            elif low == "h":
                pos = (ox + a[0] if rel else a[0], pos[1])
                current.append(pos)
            elif low == "v":
                pos = (pos[0], oy + a[0] if rel else a[0])
                current.append(pos)
            else:
                c1, c2, end = (ox + a[0], oy + a[1]), (ox + a[2], oy + a[3]), (ox + a[4], oy + a[5])
                for k in range(1, CURVE_STEPS + 1):
                    t = k / CURVE_STEPS
                    u = 1 - t
                    current.append(
                        tuple(
                            u**3 * pos[j]
                            + 3 * u * u * t * c1[j]
                            + 3 * u * t * t * c2[j]
                            + t**3 * end[j]
                            for j in (0, 1)
                        )
                    )
                pos = end
    if current:
        out.append(current)
    return out


def _fill(path: ET.Element, ancestors: list[ET.Element]) -> str:
    for element in (path, *reversed(ancestors)):
        if element.get("fill") is not None:
            return element.get("fill", "").strip().lower()
    raise ValueError("a selected path has no fill")


def _walk(node: ET.Element, matrix: Matrix, ancestors: list[ET.Element], roles: dict[str, str]):
    """``(role, points)`` for every subpath under ``node``, in document order."""
    for child in node:
        tag = child.tag.removeprefix(SVG)
        inner = _multiply(matrix, _transform(child.get("transform")))
        if tag == "g":
            yield from _walk(child, inner, [*ancestors, child], roles)
        elif tag == "path":
            fill = _fill(child, [*ancestors, child])
            if fill not in roles:
                raise ValueError(f"no role for fill {fill!r}")
            for points in _subpaths(child.get("d", "")):
                yield roles[fill], [_apply(inner, p) for p in points]
        else:
            raise ValueError(f"unsupported element <{tag}> in the selection")


def _select(root: ET.Element, select: str) -> tuple[ET.Element, Matrix, list[ET.Element]]:
    node, matrix, chain = root, _transform(root.get("transform")), []
    for index in select.split("/"):
        node = list(node)[int(index)]
        matrix = _multiply(matrix, _transform(node.get("transform")))
        chain.append(node)
    return node, matrix, chain


def normalise(svg_text: str, *, select: str, roles: dict[str, str]) -> str:
    """The normalised drawing of the group ``select`` names, as SVG text."""
    if "<!DOCTYPE" in svg_text or "<!ENTITY" in svg_text:
        raise ValueError("a DOCTYPE or entity in a found file")
    roles = {fill.lower(): role for fill, role in roles.items()}
    node, matrix, chain = _select(ET.fromstring(svg_text), select)
    # ``_select`` has already applied the transform of ``node`` and of every ancestor.
    shapes = [
        (role, points[:-1] if points[0] == points[-1] else points)
        for role, points in _walk(node, matrix, chain, roles)
        if len(set(points)) >= 3
    ]
    if not shapes:
        raise ValueError("the selection holds no filled path")
    xs = [p[0] for _, points in shapes for p in points]
    ys = [p[1] for _, points in shapes for p in points]
    x0, y0 = min(xs), min(ys)
    width, height = max(xs) - x0, max(ys) - y0
    k = SIZE / max(width, height)

    def number(value: float) -> str:
        return f"{round(value, DECIMALS):g}"

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {number(width * k)} '
        f'{number(height * k)}">'
    ]
    for role, points in shapes:
        d = " L ".join(f"{number((x - x0) * k)} {number((y - y0) * k)}" for x, y in points)
        lines.append(f'<path class="{role}" d="M {d} Z"/>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--select", required=True)
    parser.add_argument("--role", action="append", default=[], metavar="FILL=ROLE")
    args = parser.parse_args(argv)
    roles = dict(item.rsplit("=", 1) for item in args.role)
    args.out.write_text(
        normalise(args.source.read_text(), select=args.select, roles=roles), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
