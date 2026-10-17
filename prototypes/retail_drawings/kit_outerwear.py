"""Bomber and puffer jackets for the retail drawing kit (gen#447).

``coat`` draws a double-breasted trench, so a bomber and a puffer drawn with it are a different
garment from their title. Each shape here is its own cut:

* ``bomber_jacket``: a short body that ends in a ribbed hem band, ribbed cuffs and a ribbed stand
  collar, a centre zip and two slanted pockets.
* ``puffer_jacket``: quilted horizontal baffles through the body and the sleeves, a high funnel
  collar, a centre zip and elasticated cuffs.

Both paint the body in the record's fill and keep the ribbed or quilted bands in it too, so the
named part of a decoy (``hem``) is the band's own paint (:mod:`details`).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _both, _line, _mirror, _path, _shade, register


def _dark(d: str, opacity: float) -> str:
    """A shadow laid over a painted area, so pattern fills shade too."""
    return f'<path d="{d}" fill="#000000" fill-opacity="{opacity:g}" stroke="none"/>'


def _ribs(x0: float, x1: float, y0: float, y1: float, step: float = 7) -> str:
    return _line(
        " ".join(f"M{x:g},{y0:g} L{x:g},{y1:g}" for x in _frange(x0 + step / 2, x1 - 2, step)),
        1.0,
        ' stroke-opacity=".5"',
    )


def _frange(a: float, b: float, step: float) -> list[float]:
    out, x = [], a
    while x < b:
        out.append(x)
        x += step
    return out


def bomber_jacket(paint: str, fill: Fill, label: str | None) -> list[str]:
    sleeve = "M132,76 L96,98 L72,290 L112,298 L128,172 Z"
    cuff = "M72,290 L112,298 L110,324 L68,316 Z"
    body = "M170,50 L230,50 L270,76 L284,286 L116,286 L130,76 Z"
    hem = "M116,284 L284,284 L282,318 L118,318 Z"
    collar = "M168,52 Q200,66 232,52 L232,34 Q200,26 168,34 Z"
    pocket = "M138,206 L170,226 L168,252 L138,236 Z"
    out = [
        *_both(sleeve, paint),
        *_both(cuff, paint, LW_DETAIL),
        _path(body, paint),
        _path(hem, paint, LW_DETAIL),
        _dark(hem, 0.14),
        _ribs(120, 280, 288, 316),
        _path(collar, paint, LW_DETAIL),
        _dark(collar, 0.14),
        _line("M200,56 L200,284", 2.2),
        *_both(pocket, _shade(fill.base, 0.12), LW_DETAIL),
        f'<rect x="194" y="62" width="12" height="16" rx="2" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>',
    ]
    out += [_ribs(70, 110, 298, 322, 6), _ribs(290, 330, 298, 322, 6)]
    return out


def puffer_jacket(paint: str, fill: Fill, label: str | None) -> list[str]:
    sleeve = "M130,80 L90,104 L66,300 L112,310 L128,176 Z"
    cuff = "M66,300 L112,310 L110,334 L62,324 Z"
    body = "M166,60 L234,60 L276,84 L292,330 L108,330 L124,84 Z"
    collar = "M164,62 L166,30 Q200,22 234,30 L236,62 Q200,76 164,62 Z"
    baffles = " ".join(
        f"M{x0:g},{y:g} Q200,{y + 12:g} {x1:g},{y:g}"
        for y, x0, x1 in ((112, 126, 274), (150, 124, 276), (188, 122, 278), (226, 120, 280), (264, 118, 282), (302, 114, 286))
    )
    sleeve_baffles = " ".join(f"M{x0:g},{y:g} L{x1:g},{y + 6:g}" for y, x0, x1 in ((130, 112, 88), (180, 108, 82), (230, 104, 76), (278, 100, 70)))
    return [
        *_both(sleeve, paint),
        _line(sleeve_baffles, 1.6),
        _line(_mirror(sleeve_baffles), 1.6),
        *_both(cuff, paint, LW_DETAIL),
        _path(body, paint),
        _line(baffles, 1.8),
        _path(collar, paint, LW_DETAIL),
        _dark(collar, 0.12),
        _line("M200,70 L200,330", 2.2),
        f'<rect x="194" y="76" width="12" height="16" rx="2" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>',
    ]




register({"bomber_jacket": bomber_jacket, "puffer_jacket": puffer_jacket})
