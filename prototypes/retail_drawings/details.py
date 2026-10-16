"""A named part of a product, drawn in one color (gen#311).

A text-match decoy's title names a part in a misleading color ("Bra with Red Straps"), and its
picture shows what the title says: that part, in that color, and nothing else of the drawing. So
the color is never a stripe across the whole garment. :data:`PARTS` lists, per drawing shape, the
parts it can show and where each one sits:

* ``band``: a share of the garment's own bounding box (a waistband is the top of it, a hem the
  bottom), painted only where the garment's body is: a mask of the body's own elements, so the
  band follows the cut and leaves the outline alone.
* ``free``: strokes over a part the kit draws as a bare line (a bra's or a dress's straps).
* ``shapes``: filled shapes (a bow).
* ``marked``: a part the kit draws as its own path (a shoe's sole), drawn again in the color.

Every element drawn here carries ``data-part="<part>"`` and the part's color as its fill or
stroke, which ``tests/test_retail_apparel_decoys_311.py`` reads. A shape with no entry in
:data:`PARTS` shows no part, and the decoys of its types do not name one.
"""

from __future__ import annotations

import re

from kit import INK, SIZE, Fill

Box = tuple[float, float, float, float]
_NUM = re.compile(r"[MLCQZHVAmlcqzhva]|-?\d+(?:\.\d+)?")


def band(box: Box, mask: str = "paint") -> dict:
    return {"kind": "band", "box": box, "mask": mask}


def free(*strokes: tuple[str, float]) -> dict:
    return {"kind": "free", "strokes": strokes}


def shapes(*paths: str) -> dict:
    return {"kind": "shapes", "paths": paths}


def marked(cls: str) -> dict:
    """A part the kit draws as its own path and marks ``class="<cls>"``: it is drawn again in the
    part's color, on the very same outline, so the color sits where the kit puts the part."""
    return {"kind": "marked", "cls": cls}


def sock_part(name: str) -> dict:
    """A part of each sock of a pack, the kit's own path in the sock's own group (``kit_more``
    draws a pack's socks rotated and scaled, so a box of the whole drawing would miss)."""
    return {"kind": "sock", "path": name}


WAIST = band((0.0, 0.0, 1.0, 0.13))
HEM = band((0.0, 0.89, 1.0, 1.0))
#: A hem is the torso's: a sleeve's cuff reaches the same bottom and is its own part.
TORSO_HEM = band((0.0, 0.89, 1.0, 1.0), "torso")
COLLAR = band((0.33, 0.0, 0.67, 0.1))
STRAPS_TOP = band((0.0, 0.0, 1.0, 0.17))

#: shape -> part (as the title words it, lowercased) -> where it sits.
PARTS: dict[str, dict[str, dict]] = {
    "bra": {
        "straps": free(("M118,130 L140,48 M282,130 L260,48", 4.0)),
        "bow": shapes(
            "M200,200 L176,186 L176,214 Z",
            "M200,200 L224,186 L224,214 Z",
            "M194,194 L206,194 L206,206 L194,206 Z",
        ),
    },
    "dress": {"straps": free(("M164,114 L172,48 M236,114 L228,48", 5.0))},
    "vest": {"straps": STRAPS_TOP},
    "slip": {"straps": STRAPS_TOP},
    "shapewear": {"straps": STRAPS_TOP},
    "blouse": {"hem": TORSO_HEM},
    "tshirt": {"hem": TORSO_HEM, "collar": COLLAR},
    "top": {"hem": TORSO_HEM, "collar": COLLAR},
    "sweatshirt": {"hem": TORSO_HEM, "collar": COLLAR},
    "cardigan": {"hem": TORSO_HEM},
    "coat": {"hem": TORSO_HEM},
    "bodysuit": {"hem": TORSO_HEM},
    "dressing_gown": {"hem": TORSO_HEM},
    "pyjamas": {"cuffs": HEM},
    "trousers": {"waistband": WAIST, "cuffs": HEM},
    "joggers": {"waistband": WAIST, "cuffs": HEM},
    "leggings": {"waistband": WAIST, "cuffs": HEM},
    "shorts": {"waistband": WAIST},
    "cycling_shorts": {"waistband": WAIST, "cuffs": HEM},
    "skirt": {"waistband": WAIST},
    "school_trousers": {"waistband": WAIST, "cuffs": HEM},
    "school_skirt": {"waistband": WAIST},
    "school_pinafore": {"straps": STRAPS_TOP},
    "school_shirt": {"hem": TORSO_HEM, "collar": COLLAR},
    "tracksuit": {"cuffs": HEM},
    "outfit_set": {"waistband": band((0.55, 0.0, 1.0, 0.12))},
    "tights": {"waistband": WAIST},
    "boxers": {"waistband": WAIST},
    "knickers": {"waistband": WAIST},
    "socks": {"heel": sock_part("_HEEL"), "toe": sock_part("_TOE")},
    "boot_sock": {
        "cuff": band((0.0, 0.0, 1.0, 0.18), "all"),
        "toe": band((0.72, 0.78, 1.0, 1.0), "all"),
        "heel": band((0.0, 0.78, 0.34, 1.0), "all"),
    },
    "shoe": {"sole": marked("sole")},
}


def parts_of(shape: str) -> tuple[str, ...]:
    """The parts ``shape`` can show, as a title words them, lowercased."""
    return tuple(PARTS.get(shape, ()))


def _coords(d: str) -> list[tuple[float, float]]:
    """The absolute points of a path ``d`` (the kit writes absolute commands only)."""
    pts: list[tuple[float, float]] = []
    cmd, nums = "", []
    for tok in _NUM.findall(d) + ["Z"]:
        if tok.isalpha():
            if cmd in "MLCQT" and cmd:
                pts += list(zip(nums[0::2], nums[1::2], strict=False))
            elif cmd == "A":
                pts += [(nums[i + 5], nums[i + 6]) for i in range(0, len(nums) - 6, 7)]
            elif cmd == "H":
                pts += [(x, pts[-1][1] if pts else 0.0) for x in nums]
            elif cmd == "V":
                pts += [(pts[-1][0] if pts else 0.0, y) for y in nums]
            cmd, nums = tok.upper(), []
        else:
            nums.append(float(tok))
    return pts


_TOKEN = re.compile(r"<g\b[^>]*>|</g>|<(?:path|rect)\b[^>]*/>")
_XFORM = re.compile(r'transform="translate\((-?[\d.]+)[ ,](-?[\d.]+)\)(?: scale\((-?[\d.]+)\))?"')
Placed = tuple[float, float, float, str]  # (tx, ty, scale, element)


def _flat(drawn: list[str]) -> list[Placed]:
    """The kit's path and rect elements, each with the translate and scale of the groups it sits
    in (a set draws its pieces in ``<g transform=...>`` groups)."""
    out: list[Placed] = []
    stack: list[tuple[float, float, float]] = [(0.0, 0.0, 1.0)]
    for tok in _TOKEN.findall("".join(drawn)):
        if tok == "</g>":
            stack.pop()
        elif tok.startswith("<g"):
            m = _XFORM.search(tok)
            ptx, pty, psc = stack[-1]
            if m:
                ctx, cty = float(m.group(1)), float(m.group(2))
                csc = float(m.group(3)) if m.group(3) else 1.0
                stack.append((ptx + psc * ctx, pty + psc * cty, psc * csc))
            else:
                stack.append(stack[-1])
        else:
            out.append((*stack[-1], tok))
    return out


def _body(drawn: list[str], paint: str, mode: str) -> list[Placed]:
    """The elements that make up the garment's body: those painted with the surface (``paint``),
    or, for ``all``, every filled path and rect (a sole, a cuff and a toe are not the surface)."""
    out = []
    for placed in _flat(drawn):
        fill = re.search(r' fill="([^"]*)"', placed[3])
        if fill is None or fill.group(1) in ("none", "#000000"):  # a shading wash is no body
            continue
        if mode in ("paint", "torso") and fill.group(1) != paint:
            continue
        out.append(placed)
    if mode == "torso" and out:  # the pieces that cross the garment's middle, not its sleeves
        x0, _, x1, _ = _bbox(out) or (0.0, 0.0, 0.0, 0.0)
        mid = (x0 + x1) / 2
        out = [p for p in out if (b := _bbox([p])) and b[0] <= mid <= b[2]]
    return out


def _bbox(els: list[Placed]) -> Box | None:
    xs: list[float] = []
    ys: list[float] = []
    for tx, ty, sc, el in els:
        pts: list[tuple[float, float]] = []
        d = re.search(r' d="([^"]*)"', el)
        if d:
            pts = _coords(d.group(1))
        else:
            g = {k: float(v) for k, v in re.findall(r' (x|y|width|height)="(-?[\d.]+)"', el)}
            if {"x", "y", "width", "height"} <= g.keys():
                pts = [(g["x"], g["y"]), (g["x"] + g["width"], g["y"] + g["height"])]
        xs += [tx + sc * x for x, _ in pts]
        ys += [ty + sc * y for _, y in pts]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _mask_shape(placed: Placed) -> str:
    """The element as a white shape with a black outline: the outline stays out of the mask."""
    tx, ty, sc, el = placed
    el = re.sub(r' fill="[^"]*"', ' fill="#ffffff"', el, count=1)
    el = re.sub(r' stroke="[^"]*"', ' stroke="#000000"', el, count=1)
    el = re.sub(r' stroke-opacity="[^"]*"', "", el)
    return (
        f'<g transform="translate({tx:g} {ty:g}) scale({sc:g})">{el}</g>'
        if sc != 1 or tx or ty
        else el
    )


def overlay(shape: str, fill: Fill, drawn: list[str], paint: str, uid: str) -> str:
    """The named part of ``fill.detail`` over the drawn ``shape``, in its color."""
    assert fill.detail
    part, color = fill.detail
    spec = PARTS.get(shape, {}).get(part)
    if spec is None:
        raise ValueError(f"{shape!r} shows no part named {part!r}; it shows {parts_of(shape)}")
    mark = f' data-part="{part}"'
    if spec["kind"] == "free":
        under = "".join(
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w + 3:g}"'
            f' stroke-linecap="round"/>'
            for d, w in spec["strokes"]
        )
        over = "".join(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:g}"'
            f' stroke-linecap="round"{mark}/>'
            for d, w in spec["strokes"]
        )
        return under + over
    if spec["kind"] == "marked":
        out = []
        for tx, ty, sc, el in _flat(drawn):
            if f' class="{spec["cls"]}"' not in el:
                continue
            el = re.sub(r' fill="[^"]*"', f' fill="{color}"', el, count=1)
            el = el.replace(f' class="{spec["cls"]}"', mark)
            out.append(f'<g transform="translate({tx:g} {ty:g}) scale({sc:g})">{el}</g>')
        if not out:
            raise ValueError(f"{shape!r}: the kit draws no element marked {spec['cls']!r}")
        return "".join(out)
    if spec["kind"] == "sock":
        import kit_more  # deferred: it registers the sock shape

        d = getattr(kit_more, spec["path"])
        groups = re.findall(r'<g class="sock" transform="([^"]*)"', "".join(drawn))
        return "".join(
            f'<g transform="{t}"><path d="{d}" fill="{color}" stroke="{INK}" stroke-width="1.2"'
            f' stroke-linejoin="round"{mark}/></g>'
            for t in groups
        )
    if spec["kind"] == "shapes":
        return "".join(
            f'<path d="{d}" fill="{color}" stroke="{INK}" stroke-width="1.6"'
            f' stroke-linejoin="round"{mark}/>'
            for d in spec["paths"]
        )
    body = _body(drawn, paint, spec["mask"])
    box = _bbox(body)
    if box is None:
        raise ValueError(f"{shape!r}: no body to place the {part!r} on")
    x0, y0, x1, y1 = box
    fx0, fy0, fx1, fy1 = spec["box"]
    w, h = x1 - x0, y1 - y0
    rect = (x0 + fx0 * w, y0 + fy0 * h, (fx1 - fx0) * w, (fy1 - fy0) * h)
    mid = f"detail-{uid}"
    shapes_ = "".join(_mask_shape(el) for el in body)
    return (
        f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{SIZE}" height="{SIZE}">'
        f"{shapes_}</mask>"
        f'<g mask="url(#{mid})"><rect x="{rect[0]:.1f}" y="{rect[1]:.1f}" width="{rect[2]:.1f}"'
        f' height="{rect[3]:.1f}" fill="{color}" stroke="none"{mark}/></g>'
    )
