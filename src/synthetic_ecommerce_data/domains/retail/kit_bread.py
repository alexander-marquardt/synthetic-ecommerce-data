"""A bakery loaf drawn by its crust and its form, filling its picture (gen#1126, slice 1).

Before gen#1126, every bread SKU was one flat ``kit.loaf`` outline in its line's color,
covering 0.29 (400g) or 0.46 (800g) of the product area. A loaf is now drawn by:

- its **crust** (:data:`CRUSTS`, keyed by the line's flavour): a color and a texture of its own.
  A farmhouse White is pale golden with a dust of flour, a Sourdough is dark and blistered with a
  scored ear, a Wholemeal is brown with bran flecks, a Seeded crust carries its seeds, a Malted
  Beer top is dark and glossy with malt flakes, and a Gluten Free Brown is matt and crackled;
- its **form** (:data:`FORMS`, read from the line's own word by :func:`form_of`): a tin loaf with
  a domed crown over straight tin-baked sides, a round hand-shaped boule, a flat-bottomed
  oven-bottom loaf with diagonal slashes, and a stonebaked loaf under its flour. A sliced line
  (Medium or Thick Sliced) is a tin loaf cut into slices in a printed bag (:func:`_bagged`,
  slice 2): a clear window shows the slices, a thick-sliced loaf fewer and wider ones, and the
  bag's end is gathered in a twist and held by a clip;
- a highlight up top and a shade below (:data:`GLOSS`) and a shadow on the ground, so it reads as
  baked and not as a flat fill.

Every form covers at least 0.62 of the product area at its natural size, so a 400g drawn at the
loaf's pack factor (``pack_scale.SHAPE_FLOORS``) still holds half. A small label sticker carries
the range name and the flavour band.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    Fill,
    _line,
    _mix,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)

#: Flavour -> (crust, side, texture, gloss): the top crust's color, the paler color of a tin
#: loaf's sides and of a slash's opened crumb edge, the texture its crust carries, and how strong
#: its highlight is (a malted top shines, a gluten free crust is matt).
CRUSTS: dict[str, tuple[str, str, str, float]] = {
    "White": ("#e0a95c", "#f2d9a4", "dusted", 0.5),
    "Wholemeal": ("#93592b", "#c08a55", "bran", 0.4),
    "Seeded": ("#b0763c", "#d4a066", "seeds", 0.4),
    "Sourdough": ("#74421c", "#b07a42", "blisters", 0.45),
    "Gluten Free Brown": ("#a5805c", "#cbab86", "cracks", 0.18),
    "Malted Beer": ("#4a2a12", "#7d4c24", "flakes", 0.7),
}

#: The crumb an opened slash shows.
CRUMB = "#f3e4c4"

#: Form -> (the loaf's outline, the box its crust texture is scattered in as (cx, cy, rx, ry),
#: its slashes as (cx, cy, length, angle in degrees), where its label sits as (x, y, w, h)).
#: Coordinates are the 400 x 400 sheet's, the loaf standing on y=352 and centered on x=200.
FORMS: dict[
    str,
    tuple[
        str,
        tuple[float, float, float, float],
        tuple[tuple[float, float, float, float], ...],
        tuple[float, float, float, float],
    ],
] = {
    "tin": (
        "M44,214 L44,338 Q44,352 58,352 L342,352 Q356,352 356,338 L356,214 "
        "C368,206 370,186 352,176 C340,108 272,84 200,84 C128,84 60,108 48,176 C30,186 32,206 44,214 Z",
        (200, 150, 140, 52),
        ((200, 118, 200, 0),),
        (116, 252, 168, 70),
    ),
    "boule": (
        "M24,324 C14,170 92,70 200,70 C308,70 386,170 376,324 Q374,352 342,352 L58,352 Q26,352 24,324 Z",
        (200, 190, 140, 92),
        ((160, 150, 120, -38), (240, 150, 120, 38)),
        (116, 262, 168, 70),
    ),
    "oven_bottom": (
        "M18,352 C6,324 8,258 40,200 C74,136 134,98 200,96 C266,98 326,136 360,200 C392,258 394,324 382,352 Z",
        (200, 196, 140, 80),
        ((118, 196, 84, -58), (172, 158, 96, -58), (228, 150, 96, -58), (282, 182, 88, -58)),
        (116, 262, 168, 70),
    ),
    "stonebaked": (
        "M14,320 C8,226 64,104 200,96 C336,104 392,226 386,320 C388,346 362,352 332,352 "
        "L68,352 C40,352 14,346 16,318 Z",
        (200, 196, 150, 82),
        ((200, 150, 230, -8),),
        (116, 262, 168, 70),
    ),
}

#: Line word -> form, in the order :func:`form_of` reads them. A farmhouse loaf is baked in a tin.
#: A line with none of them is a tin loaf, but an unworded sourdough is hand shaped, as one is in
#: a bakery.
FORM_WORDS = (
    ("Thick Sliced", "thick_sliced"),
    ("Medium Sliced", "medium_sliced"),
    ("Hand Shaped", "boule"),
    ("Crusty", "boule"),
    ("Oven Bottom", "oven_bottom"),
    ("Stonebaked", "stonebaked"),
    ("Farmhouse", "tin"),
)

#: A sliced form -> how many slices its bag's window shows: a thick slice is about half as wide
#: again as a medium one.
SLICES = {"medium_sliced": 13, "thick_sliced": 9}

#: Flavour -> the ink its bag is printed in, chosen to stand off the crust seen through the
#: window (no White line is sold sliced, but its bag is here for when one is).
BAG_PRINT = {
    "White": "#2c62b0",
    "Wholemeal": "#3f6e3a",
    "Seeded": "#c2562b",
    "Sourdough": "#2f4f7a",
    "Gluten Free Brown": "#4f7f8c",
    "Malted Beer": "#7a2430",
}

#: The bag: its body (a tin loaf's shape, a little larger), gathered at the right into a neck,
#: the clip across the neck as (x, y, w, h), and the twisted tail flaring past it.
BAG = (
    "M54,352 Q32,352 32,330 L32,168 C32,118 72,94 124,92 L260,92 C298,94 312,118 314,150 "
    "C318,180 326,198 336,208 L336,248 C326,258 318,276 314,306 C310,338 298,352 276,352 Z"
)
BAG_CLIP = (334, 194, 16, 68)
BAG_TAIL = "M350,214 C356,198 362,182 370,168 L370,290 C362,276 356,260 350,244 Z"
#: The clear window in the bag's print, as (x, y, w, h): the loaf's slices show through it.
WINDOW = (46, 112, 254, 176)

#: The stonebaked loaf's flour, thickest on its crown; then the highlight (up top) and the shade
#: (down low) over every loaf's crust.
FLOUR = (
    '<defs><linearGradient id="bread-flour" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity=".75"/>'
    '<stop offset=".55" stop-color="#ffffff" stop-opacity=".15"/>'
    '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient></defs>'
)
GLOSS = (
    '<defs><linearGradient id="bread-gloss-{0}" x1="0" y1="0" x2=".25" y2="1">'
    '<stop offset="0" stop-color="#ffffff" stop-opacity="{1:g}"/>'
    '<stop offset=".38" stop-color="#ffffff" stop-opacity="0"/>'
    '<stop offset=".7" stop-color="#000000" stop-opacity="0"/>'
    '<stop offset="1" stop-color="#000000" stop-opacity=".24"/></linearGradient></defs>'
)


def form_of(line: str, flavor: str) -> str:
    """The form the line's own word names (:data:`FORM_WORDS`), else a tin loaf, or a boule for
    an unworded sourdough."""
    for word, form in FORM_WORDS:
        if word in line:
            return form
    return "boule" if flavor == "Sourdough" else "tin"


def _spots(
    box: tuple[float, float, float, float], n: int, salt: int
) -> list[tuple[float, float, float]]:
    """``n`` points spread over the ellipse ``box`` on a golden-angle spiral (no randomness: the
    same loaf draws the same marks), each with a turn in degrees."""
    cx, cy, rx, ry = box
    out = []
    for i in range(n):
        rad = math.sqrt((i + 0.5) / n)
        ang = i * 2.39996 + salt
        out.append(
            (
                cx + rad * rx * math.cos(ang),
                cy + rad * ry * math.sin(ang),
                (i * 47 + salt * 13) % 180,
            )
        )
    return out


def _texture(kind: str, crust: str, box: tuple[float, float, float, float]) -> list[str]:
    """The crust's own marks, scattered over ``box``."""
    marks: list[str] = []
    if kind == "dusted":
        for x, y, _ in _spots(box, 26, 1):
            marks.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="#ffffff" fill-opacity=".7"/>'
            )
    elif kind == "bran":
        dark, light = _shade(crust, 0.4), _mix(crust, "#e8c890", 0.6)
        for i, (x, y, a) in enumerate(_spots(box, 70, 2)):
            marks.append(
                f'<rect x="{x - 3:.1f}" y="{y - 1:.1f}" width="6" height="2" rx="1" '
                f'fill="{dark if i % 3 else light}" transform="rotate({a} {x:.1f} {y:.1f})"/>'
            )
    elif kind == "seeds":
        inks = ("#8f9377", "#5d7a35", "#3a2716", "#eadbb0")
        for i, (x, y, a) in enumerate(_spots(box, 64, 3)):
            marks.append(
                f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5" ry="2.4" fill="{inks[i % 4]}" '
                f'stroke="{INK}" stroke-width=".6" transform="rotate({a} {x:.1f} {y:.1f})"/>'
            )
    elif kind == "blisters":
        dark = _shade(crust, 0.45)
        for i, (x, y, _) in enumerate(_spots(box, 34, 4)):
            r = 3.0 + i % 4
            marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:g}" fill="{dark}"/>')
            marks.append(
                f'<circle cx="{x - r * 0.4:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.4:.1f}" fill="#ffffff" fill-opacity=".35"/>'
            )
    elif kind == "cracks":
        dark = _shade(crust, 0.35)
        for x, y, a in _spots(box, 18, 5):
            d = f"M{x - 12:.1f},{y:.1f} L{x - 3:.1f},{y - 3:.1f} L{x + 4:.1f},{y + 2:.1f} L{x + 12:.1f},{y - 1:.1f}"
            marks.append(_line(d, 1.4, f' transform="rotate({a} {x:.1f} {y:.1f})"', dark))
    elif kind == "flakes":
        for x, y, a in _spots(box, 22, 6):
            marks.append(
                f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6" ry="3.2" fill="#c89a5a" '
                f'stroke="{INK}" stroke-width=".6" transform="rotate({a} {x:.1f} {y:.1f})"/>'
            )
    return [f'<g class="texture {kind}">{"".join(marks)}</g>']


def _slash(cx: float, cy: float, length: float, angle: float, side: str, ear: bool) -> list[str]:
    """One opened slash: a lens of crumb edged by the paler crust, with a raised lip (an ear)
    on a sourdough's."""
    half, open_ = length / 2, (22 if ear else 13)
    d = f"M{-half:g},0 Q0,{-open_:g} {half:g},0 Q0,{open_:g} {-half:g},0 Z"
    at = f' transform="translate({cx:g} {cy:g}) rotate({angle:g})"'
    out = [
        _path(d, side, LW_DETAIL, at),
        _path(
            f"M{-half * 0.8:g},1 Q0,{open_ * 0.55:g} {half * 0.8:g},1 Q0,{-open_ * 0.2:g} {-half * 0.8:g},1 Z",
            CRUMB,
            0.8,
            at,
        ),
    ]
    if ear:  # the lip a sourdough's blade lifts, catching the oven's heat
        out.append(
            _line(f"M{-half:g},0 Q0,{-open_ * 1.3:g} {half:g},0", 3.4, at, _shade(side, 0.55))
        )
    return out


def loaf(
    paint: str, fill: Fill, label: str | None, flavor: str = "White", form: str = "tin"
) -> list[str]:
    """A loaf of ``flavor``'s crust in ``form`` (gen#1126): the outline in the crust color, a
    tin loaf's paler sides, the crust's texture, its slashes, a highlight and a shade, a ground
    shadow, and a label sticker. ``paint`` is not read: a loaf's color is its crust's."""
    del paint, fill
    if flavor not in CRUSTS:
        raise ValueError(f"no bread crust {flavor!r}; known: {sorted(CRUSTS)}")
    if form in SLICES:
        return _bagged(flavor, SLICES[form], label)
    shape = form
    if shape not in FORMS:
        raise ValueError(f"no bread form {form!r}; known: {sorted([*FORMS, *SLICES])}")
    crust, side, texture, shine = CRUSTS[flavor]
    outline, box, slashes, (lx, ly, lw, lh) = FORMS[shape]
    key = f"{texture}-{shape}"
    body = [
        GLOSS.format(key, shine),
        *([FLOUR] if shape == "stonebaked" else []),
        _path(outline, crust, extra=' class="crust"'),
    ]
    if shape == "tin":  # the sides baked against the tin are paler than the crown
        body.append(
            _path(
                "M48,216 C120,234 280,234 352,216 L352,338 Q352,348 342,348 L58,348 Q48,348 48,338 Z",
                side,
                LW_DETAIL,
                ' class="tin-side"',
            )
        )
    else:  # the floured, baked base
        body.append(_line("M44,346 L356,346", 6, ' stroke-opacity=".5"', _shade(crust, 0.45)))
    body += _texture(texture, crust, box)
    ear = flavor == "Sourdough"
    cuts = slashes[:1] if ear else slashes
    for cx, cy, length, angle in cuts:
        body += _slash(cx, cy, length * (1.2 if ear else 1), angle, side, ear)
    if shape == "stonebaked":  # the stone's flour, heaviest on the crown
        body.append(_path(outline, "url(#bread-flour)", 0, ' class="flour"', "none"))
        body += [
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="10" ry="5" fill="#ffffff" fill-opacity=".5"/>'
            for x, y, _ in _spots(box, 36, 7)
        ]
    body.append(_path(outline, f"url(#bread-gloss-{key})", 0, ' class="gloss"', "none"))
    body += _panel(lx, ly, lw, lh, label, 30)
    shadow = f'<ellipse class="ground" cx="200" cy="356" rx="176" ry="9" fill="{INK}" fill-opacity=".18"/>'
    return [shadow, f'<g class="bread">{"".join(body)}</g>']


def _crown(x: float) -> float:
    """The top of the sliced tin loaf inside the bag at ``x``: a dome, highest at x=172."""
    return 106 + 54 * ((x - 172) / 128) ** 2


def _slices(flavor: str, n: int) -> list[str]:
    """A tin loaf cut into ``n`` slices, seen from its side: each slice a band of crust under
    the dome, every other one a shade darker so the cuts read, and the cut end at the left
    showing its crumb inside a rim of crust."""
    crust, side, texture, _ = CRUSTS[flavor]
    left, right, base = 64.0, 300.0, 342.0
    width = (right - left) / n
    out = []
    for i in range(n):
        x0, x1 = left + i * width, left + (i + 1) * width
        xm = (x0 + x1) / 2
        ctrl = 2 * _crown(xm) - (_crown(x0) + _crown(x1)) / 2
        d = (
            f"M{x0:.1f},{base:g} L{x0:.1f},{_crown(x0):.1f} "
            f"Q{xm:.1f},{ctrl:.1f} {x1:.1f},{_crown(x1):.1f} L{x1:.1f},{base:g} Z"
        )
        tone = crust if i % 2 else _mix(crust, side, 0.35)
        out.append(_path(d, tone, 1.2, ' class="slice"', _shade(crust, 0.55)))
    out += _texture(texture, crust, (180, 140, 110, 22))
    top = _crown(left)
    out.append(  # the cut end: crumb in its crust, a little turned toward the viewer
        f'<ellipse class="slice end" cx="{left:g}" cy="{(top + base) / 2:.1f}" rx="16" '
        f'ry="{(base - top) / 2:.1f}" fill="{CRUMB}" stroke="{crust}" stroke-width="5"/>'
    )
    return out


def _bagged(flavor: str, n: int, label: str | None) -> list[str]:
    """A sliced loaf of ``flavor``'s crust in its printed bag (gen#1126 slice 2): the bag's
    print, a clear window showing the ``n`` slices, the film's sheen, the gathered neck held
    by a clip, the twisted tail, a highlight and a shade over it all, and the label on the
    bag's lower band."""
    ink = BAG_PRINT[flavor]
    wx, wy, ww, wh = WINDOW
    key = f"bag-{n}"
    window = f'<rect x="{wx:g}" y="{wy:g}" width="{ww:g}" height="{wh:g}" rx="16"'
    body = [
        GLOSS.format(key, 0.45),
        f'<defs><clipPath id="bread-window-{key}">{window}/></clipPath></defs>',
        _path(BAG, ink, extra=' class="bag"'),
        _line(  # the print's lighter band along the bag's shoulder
            "M40,150 C60,108 100,100 130,100 L256,100 C290,102 304,120 306,150",
            8,
            ' stroke-opacity=".8"',
            _tint(ink, 0.45),
        ),
        f'{window} class="window-film" fill="#eef4f6" stroke="none"/>',
        f'<g clip-path="url(#bread-window-{key})">{"".join(_slices(flavor, n))}</g>',
        f'{window} class="window" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *(  # the film's sheen across the window
            _line(d, 5, ' stroke-opacity=".55"', "#ffffff")
            for d in ("M78,280 L150,120", "M98,284 L162,142", "M232,282 L290,150")
        ),
        _path(
            "M314,150 C318,180 326,198 336,208 L336,248 C326,258 318,276 314,306", "none", LW_DETAIL
        ),
        *(  # the film gathered into the neck
            _line(d, 1.2, "", _shade(ink, 0.35))
            for d in ("M318,196 L334,214", "M320,226 L334,228", "M318,262 L334,242")
        ),
        _path(BAG_TAIL, _tint(ink, 0.25), LW_DETAIL, ' class="bag-tail"'),
        *(
            _line(d, 1.2, "", _shade(ink, 0.35))
            for d in ("M354,212 L368,184", "M354,229 L368,229", "M354,246 L368,274")
        ),
        f'<rect class="clip" x="{BAG_CLIP[0]:g}" y="{BAG_CLIP[1]:g}" width="{BAG_CLIP[2]:g}" '
        f'height="{BAG_CLIP[3]:g}" rx="4" fill="#f4f1e8" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line(
            f"M{BAG_CLIP[0] + 8:g},{BAG_CLIP[1] + 8:g} L{BAG_CLIP[0] + 8:g},{BAG_CLIP[1] + BAG_CLIP[3] - 8:g}",
            2,
        ),
        _path(BAG, f"url(#bread-gloss-{key})", 0, ' class="gloss"', "none"),
    ]
    body += _panel(112, 296, 176, 50, label, 26)
    shadow = f'<ellipse class="ground" cx="200" cy="356" rx="176" ry="9" fill="{INK}" fill-opacity=".18"/>'
    return [shadow, f'<g class="bread bagged">{"".join(body)}</g>']


register({"loaf": loaf})
