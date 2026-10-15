"""Toy shapes for the retail drawing kit (gen#201): sets, puzzles, games, dolls, ride-ons.

Each type of :mod:`toys_rows` has its own flat drawing in the kit's house style: outlines
in the kit's ink, the record's fill (color and pattern) on the product's main surface, so a
shopper tells a jigsaw from a board game and a balance bike from a scooter at thumbnail
size.

============  ===========================================================  ==================
shape         draws                                                        params
============  ===========================================================  ==================
building_set  a set's box, its art the theme, and one loose brick         theme, bricks
jigsaw        a finished puzzle cut into exactly ``pieces`` tiles, and     pieces, theme
              one loose piece (``class="cut-h"`` / ``"cut-v"`` per cut)
board_game    a track board, a hex board, a fan of cards or a party box    kind
doll          a fashion, baby or rag doll, or a row of doll's house        kind, accessories,
              figures; each accessory beside it (``class="accessory"``)    counts
wooden_toy    stacking rings, a shape sorter, a train on its track, a      kind, counts,
              peg puzzle or a pull-along animal                            animal
role_play     a play kitchen, a tool bench, a doctor's case, a shop till   kind, counts
              or a tea set
craft_kit     a paint tin, a bead tray, slime tubs, yarn and needles or a  kind, counts
              pencil tin
ride_on       a balance bike, a scooter, a trike or a ride-on car, each    kind, wheels,
              wheel a ``class="wheel"`` group                              wheel_size_in
============  ===========================================================  ==================

Every shape also takes ``character``: the motif (:mod:`motifs`) of the style's invented
range, drawn on a round badge, so a range is recognised across kinds. ``counts`` is a set's
quantity per line of its contents ("12,2,1"): the shape draws each piece as a
``class="piece"`` group, so the drawn pieces are the row's ``piece_count``. A drawing never
prints a number: a building set's sizes share one box, so it carries no piece count.
Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _line, _path, _shade, _tint, register

BLACK = "#2f2f35"
WHITE = "#ffffff"
WOOD = "#d9b98a"
SKIN = "#f1c9a5"
HAIR = "#6b4226"
STEEL = "#cfd5da"
#: Paint, bead, pencil and yarn colors a kit holds whatever the box's own color.
RAINBOW = ("#d93b30", "#f08a24", "#f2c94c", "#5f9a4a", "#2f8fc4", "#3f5fb5", "#7b4fa0",
           "#e46aa0", "#8a5a3a", "#2f2f35", "#9a9ca0", "#f4f1ea")  # fmt: skip
#: A range's badge color, by the motif that marks it.
BADGE = {"star": "#f2c94c", "dinosaur": "#5f9a4a", "bird": "#e07a1f", "whale": "#3f6fb5"}


def _n(value: str, default: int) -> int:
    try:
        return max(0, int(str(value).split()[0]))
    except (ValueError, IndexError):
        return default


def _counts(value: str, default: tuple[int, ...]) -> list[int]:
    try:
        return [max(0, int(v)) for v in str(value).split(",")] if value else list(default)
    except ValueError:
        return list(default)


def _ell(
    cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, extra: str = ""
) -> str:
    return (f'<ellipse{extra} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    r: float = 4,
    width: float = LW,
    extra: str = "",
) -> str:
    return (f'<rect{extra} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _group(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _shadow(cx: float, cy: float, rx: float) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.08:.1f}" fill="#000000" fill-opacity=".08"/>'


def _badge(character: str, cx: float = 350, cy: float = 50, r: float = 28) -> list[str]:
    """The range's mark: its motif on a round white badge (nothing when there is none)."""
    if not character:
        return []
    import motifs  # deferred: motifs draws with this kit's shapes

    return [_group("character", [_ell(cx, cy, r, r, WHITE, 2.4),
                                 motifs.motif_svg(character, BADGE.get(character, INK), cx, cy, r * 2.6)])]  # fmt: skip


def _star(cx: float, cy: float, r: float, fill: str, width: float = LW_DETAIL) -> str:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return _path("M" + " L".join(pts) + " Z", fill, width)


# --------------------------------------------------------------------------
# Building sets
# --------------------------------------------------------------------------


def _brick(x: float, y: float, w: float, h: float, studs: int, fill: str) -> list[str]:
    """A brick from the front: its body and a row of studs on top."""
    sw = w / studs
    out = [
        _rect(
            x + sw * i + sw * 0.2, y - h * 0.22, sw * 0.6, h * 0.24, _shade(fill, 0.1), 2, LW_DETAIL
        )
        for i in range(studs)
    ]
    return [*out, _rect(x, y, w, h, fill, 3)]


def _box_art(theme: str, x: float, y: float, w: float, h: float, ink: str) -> list[str]:
    """The theme's silhouette inside the box art window (x, y, w, h)."""
    cx, base = x + w / 2, y + h
    if theme == "space":
        rocket = f"M{cx:.1f},{y + 18:.1f} Q{cx + 26:.1f},{y + 50:.1f} {cx + 22:.1f},{base - 40:.1f} L{cx - 22:.1f},{base - 40:.1f} Q{cx - 26:.1f},{y + 50:.1f} {cx:.1f},{y + 18:.1f} Z"
        return [_path(f"M{x:.1f},{base - 18:.1f} Q{cx:.1f},{base - 40:.1f} {x + w:.1f},{base - 18:.1f} L{x + w:.1f},{base:.1f} L{x:.1f},{base:.1f} Z", _tint(ink, 0.5), LW_DETAIL),
                _path(f"M{cx - 22:.1f},{base - 60:.1f} L{cx - 42:.1f},{base - 34:.1f} L{cx - 20:.1f},{base - 40:.1f} Z M{cx + 22:.1f},{base - 60:.1f} L{cx + 42:.1f},{base - 34:.1f} L{cx + 20:.1f},{base - 40:.1f} Z", ink, LW_DETAIL),
                _path(rocket, WHITE, LW_DETAIL), _ell(cx, y + 62, 10, 10, ink, LW_DETAIL),
                _star(x + 30, y + 30, 9, WHITE), _star(x + w - 30, y + 48, 7, WHITE), _star(x + 40, y + 92, 6, WHITE)]  # fmt: skip
    if theme == "castle":
        out = []
        for tx in (x + 22, x + w - 62):
            d = (
                f"M{tx:.1f},{base:.1f} L{tx:.1f},{y + 40:.1f} "
                + " ".join(
                    f"L{tx + i * 10:.1f},{y + (30 if i % 2 else 40):.1f} L{tx + (i + 1) * 10:.1f},{y + (30 if i % 2 else 40):.1f}"
                    for i in range(4)
                )
                + f" L{tx + 40:.1f},{base:.1f} Z"
            )
            out.append(_path(d, _tint(ink, 0.35), LW_DETAIL))
        out.append(
            _path(
                f"M{x + 62:.1f},{base:.1f} L{x + 62:.1f},{y + 80:.1f} L{x + w - 62:.1f},{y + 80:.1f} L{x + w - 62:.1f},{base:.1f} Z",
                _tint(ink, 0.55),
                LW_DETAIL,
            )
        )
        out.append(
            _path(
                f"M{cx - 16:.1f},{base:.1f} L{cx - 16:.1f},{base - 30:.1f} Q{cx:.1f},{base - 48:.1f} {cx + 16:.1f},{base - 30:.1f} L{cx + 16:.1f},{base:.1f} Z",
                ink,
                LW_DETAIL,
            )
        )
        out.append(
            _path(
                f"M{x + 42:.1f},{y + 30:.1f} L{x + 42:.1f},{y + 10:.1f} L{x + 60:.1f},{y + 16:.1f} L{x + 42:.1f},{y + 22:.1f}",
                WHITE,
                LW_DETAIL,
            )
        )
        return out
    if theme == "city":
        out = []
        for bx, bw, bh in ((x + 14, 52, 0.72), (x + 72, 64, 0.9), (x + 142, w - 156, 0.6)):
            top = base - h * bh
            out.append(_rect(bx, top, bw, base - top, _tint(ink, 0.45), 2, LW_DETAIL))
            for wy in range(int(top) + 10, int(base) - 16, 18):
                for wx in (bx + 8, bx + bw / 2 + 2):
                    out.append(_rect(wx, wy, bw / 2 - 12, 9, WHITE, 1, 1))
        return out
    if theme == "dinosaurs":
        import motifs  # deferred: motifs draws with this kit's shapes

        return [_path(f"M{x + 10:.1f},{base:.1f} L{x + 60:.1f},{y + 40:.1f} L{x + 84:.1f},{y + 40:.1f} L{x + 134:.1f},{base:.1f} Z", _tint(ink, 0.35), LW_DETAIL),
                _path(f"M{x + 60:.1f},{y + 40:.1f} Q{x + 72:.1f},{y + 54:.1f} {x + 84:.1f},{y + 40:.1f}", "#e07a1f", LW_DETAIL),
                _path(f"M{x + 66:.1f},{y + 30:.1f} Q{x + 56:.1f},{y + 14:.1f} {x + 72:.1f},{y + 8:.1f} Q{x + 92:.1f},{y + 4:.1f} {x + 84:.1f},{y + 22:.1f}", "none", LW_DETAIL),
                motifs.motif_svg("dinosaur", WHITE, x + w - 62, base - 52, 120)]  # fmt: skip
    if theme == "farm":
        return [_path(f"M{cx - 64:.1f},{base:.1f} L{cx - 64:.1f},{y + 70:.1f} L{cx:.1f},{y + 22:.1f} L{cx + 64:.1f},{y + 70:.1f} L{cx + 64:.1f},{base:.1f} Z", _tint(ink, 0.2), LW_DETAIL),
                _rect(cx - 26, base - 60, 52, 60, WHITE, 1, LW_DETAIL),
                _line(f"M{cx - 26:.1f},{base - 60:.1f} L{cx + 26:.1f},{base:.1f} M{cx + 26:.1f},{base - 60:.1f} L{cx - 26:.1f},{base:.1f}", LW_DETAIL)]  # fmt: skip
    # animals: a treehouse in a round tree
    return [_rect(cx - 10, y + 80, 20, base - y - 80, "#8a5a3a", 2, LW_DETAIL), _ell(cx, y + 62, 70, 50, _tint(ink, 0.35), LW_DETAIL),
            _path(f"M{cx - 30:.1f},{y + 92:.1f} L{cx:.1f},{y + 66:.1f} L{cx + 30:.1f},{y + 92:.1f} Z", "#c8312e", LW_DETAIL),
            _rect(cx - 24, y + 92, 48, 34, WOOD, 1, LW_DETAIL), _ell(cx, y + 108, 7, 7, INK, 1)]  # fmt: skip


def building_set(
    paint: str,
    fill: Fill,
    label: str | None,
    theme: str = "city",
    bricks: str = "standard",
    character: str = "",
) -> list[str]:
    """A building set's box in three-quarter view, its art the ``theme``, and a loose brick:
    a 2 x 4 standard brick, or a large brick of two big studs for a toddler set."""
    x0, y0, x1, y1, dx, dy = 52, 96, 292, 326, 46, -34
    top = f"M{x0},{y0} L{x0 + dx},{y0 + dy} L{x1 + dx},{y0 + dy} L{x1},{y0} Z"
    side = f"M{x1},{y0} L{x1 + dx},{y0 + dy} L{x1 + dx},{y1 + dy} L{x1},{y1} Z"
    ink = _shade(fill.base, 0.45)
    out = [_shadow(200, 340, 170), _path(side, _shade(fill.base, 0.3)), _path(top, _tint(fill.base, 0.25)),
           _rect(x0, y0, x1 - x0, y1 - y0, paint, 2),
           _rect(x0 + 16, y0 + 26, x1 - x0 - 32, y1 - y0 - 50, _tint(fill.base, 0.78), 6, LW_DETAIL),
           *_box_art(theme, x0 + 16, y0 + 26, x1 - x0 - 32, y1 - y0 - 50, ink),
           _rect(x0 + 16, y0 + 8, 64, 12, WHITE, 3, 1)]  # fmt: skip
    if bricks == "large":
        out += _brick(250, 300, 112, 52, 2, "#2f8fc4")
    else:
        out += _brick(266, 318, 96, 28, 4, "#f2c94c")
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Jigsaw puzzles
# --------------------------------------------------------------------------


def grid(pieces: int) -> tuple[int, int]:
    """(rows, columns) with rows x columns == pieces, the shape nearest a 4:5 landscape board."""
    pairs = [(r, pieces // r) for r in range(1, int(math.isqrt(pieces)) + 1) if pieces % r == 0]
    return min(pairs, key=lambda rc: abs(rc[0] / rc[1] - 0.72))


def _jig_picture(theme: str, x: float, y: float, w: float, h: float, fill: Fill) -> list[str]:
    base = y + h
    if theme == "space":
        out = [_ell(x + w * 0.72, y + h * 0.38, 46, 46, "#e07a1f", LW_DETAIL), _ell(x + w * 0.72, y + h * 0.38, 76, 14, "none", 2.4),
               _path(f"M{x + 70:.1f},{y + 40:.1f} A36,36 0 1,0 {x + 98:.1f},{y + 104:.1f} A28,28 0 1,1 {x + 70:.1f},{y + 40:.1f} Z", "#f2e9b8", LW_DETAIL)]  # fmt: skip
        out += [
            _star(x + sx * w, y + sy * h, 7, WHITE, 1)
            for sx, sy in (
                (0.1, 0.75),
                (0.35, 0.2),
                (0.45, 0.65),
                (0.9, 0.85),
                (0.55, 0.9),
                (0.2, 0.5),
            )
        ]
        return out
    if theme == "maps":
        return [_path(f"M{x + 30:.1f},{y + 40:.1f} Q{x + 90:.1f},{y + 20:.1f} {x + 110:.1f},{y + 70:.1f} Q{x + 100:.1f},{y + 120:.1f} {x + 80:.1f},{y + 200:.1f} Q{x + 50:.1f},{y + 130:.1f} {x + 30:.1f},{y + 40:.1f} Z", "#8fc07a", LW_DETAIL),
                _path(f"M{x + 150:.1f},{y + 30:.1f} Q{x + 230:.1f},{y + 10:.1f} {x + 270:.1f},{y + 60:.1f} Q{x + 230:.1f},{y + 90:.1f} {x + 200:.1f},{y + 80:.1f} Q{x + 190:.1f},{y + 160:.1f} {x + 160:.1f},{y + 150:.1f} Q{x + 140:.1f},{y + 90:.1f} {x + 150:.1f},{y + 30:.1f} Z", "#e6c46a", LW_DETAIL),
                _path(f"M{x + 230:.1f},{y + 160:.1f} Q{x + 270:.1f},{y + 150:.1f} {x + 280:.1f},{y + 190:.1f} Q{x + 250:.1f},{y + 210:.1f} {x + 230:.1f},{y + 160:.1f} Z", "#d98a5a", LW_DETAIL)]  # fmt: skip
    if theme == "seaside":
        return [_ell(x + w * 0.8, y + 50, 26, 26, "#f2c94c", LW_DETAIL),
                _path(f"M{x:.1f},{y + h * 0.55:.1f} Q{x + w * 0.25:.1f},{y + h * 0.5:.1f} {x + w * 0.5:.1f},{y + h * 0.55:.1f} T{x + w:.1f},{y + h * 0.55:.1f} L{x + w:.1f},{base:.1f} L{x:.1f},{base:.1f} Z", _shade(fill.base, 0.3), LW_DETAIL),
                _path(f"M{x + 40:.1f},{y + h * 0.5:.1f} L{x + 110:.1f},{y + h * 0.5:.1f} L{x + 98:.1f},{y + h * 0.6:.1f} L{x + 52:.1f},{y + h * 0.6:.1f} Z M{x + 74:.1f},{y + h * 0.5:.1f} L{x + 74:.1f},{y + h * 0.2:.1f} L{x + 104:.1f},{y + h * 0.46:.1f} Z", WHITE, LW_DETAIL)]  # fmt: skip
    if theme == "dinosaurs":
        import motifs  # deferred: motifs draws with this kit's shapes

        return [_path(f"M{x:.1f},{y + h * 0.7:.1f} Q{x + w / 2:.1f},{y + h * 0.6:.1f} {x + w:.1f},{y + h * 0.72:.1f} L{x + w:.1f},{base:.1f} L{x:.1f},{base:.1f} Z", "#8fc07a", LW_DETAIL),
                _path(f"M{x + 20:.1f},{y + h * 0.66:.1f} L{x + 80:.1f},{y + 40:.1f} L{x + 104:.1f},{y + 40:.1f} L{x + 160:.1f},{y + h * 0.64:.1f} Z", "#8a6a5a", LW_DETAIL),
                motifs.motif_svg("dinosaur", "#f2c94c", x + w * 0.72, y + h * 0.55, 170)]  # fmt: skip
    # landscapes: snowy peaks over a lake
    return [_path(f"M{x:.1f},{y + h * 0.62:.1f} L{x + w * 0.28:.1f},{y + h * 0.18:.1f} L{x + w * 0.5:.1f},{y + h * 0.5:.1f} L{x + w * 0.7:.1f},{y + h * 0.12:.1f} L{x + w:.1f},{y + h * 0.6:.1f} L{x + w:.1f},{y + h * 0.66:.1f} L{x:.1f},{y + h * 0.66:.1f} Z", "#7d8a99", LW_DETAIL),
            _path(f"M{x + w * 0.21:.1f},{y + h * 0.29:.1f} L{x + w * 0.28:.1f},{y + h * 0.18:.1f} L{x + w * 0.34:.1f},{y + h * 0.27:.1f} Z M{x + w * 0.64:.1f},{y + h * 0.22:.1f} L{x + w * 0.7:.1f},{y + h * 0.12:.1f} L{x + w * 0.77:.1f},{y + h * 0.23:.1f} Z", WHITE, 1.2),
            _path(f"M{x:.1f},{y + h * 0.66:.1f} L{x + w:.1f},{y + h * 0.66:.1f} L{x + w:.1f},{base:.1f} L{x:.1f},{base:.1f} Z", _tint("#2f8fc4", 0.35), LW_DETAIL),
            _path(f"M{x:.1f},{y + h * 0.86:.1f} Q{x + w / 2:.1f},{y + h * 0.78:.1f} {x + w:.1f},{y + h * 0.88:.1f} L{x + w:.1f},{base:.1f} L{x:.1f},{base:.1f} Z", "#5f9a4a", LW_DETAIL)]  # fmt: skip


def _cut(horizontal: bool, at: float, a: float, b: float, cells: int, knob: float) -> str:
    """One straight cut across the board, with a knob bump in every cell when ``knob``."""
    if knob <= 0:
        d = (
            f"M{a:.1f},{at:.1f} L{b:.1f},{at:.1f}"
            if horizontal
            else f"M{at:.1f},{a:.1f} L{at:.1f},{b:.1f}"
        )
    else:
        step, parts = (b - a) / cells, []
        for i in range(cells):
            s0, mid = a + i * step, a + (i + 0.5) * step
            k = knob if (i + int(at)) % 2 else -knob
            seg = [
                (s0, 0),
                (mid - knob * 0.6, 0),
                (mid - knob, k),
                (mid + knob, k),
                (mid + knob * 0.6, 0),
                (a + (i + 1) * step, 0),
            ]
            pts = [(p, at + o) if horizontal else (at + o, p) for p, o in seg]
            parts.append(
                ("M" if i == 0 else "L")
                + f"{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f} C{pts[2][0]:.1f},{pts[2][1]:.1f} {pts[3][0]:.1f},{pts[3][1]:.1f} {pts[4][0]:.1f},{pts[4][1]:.1f} L{pts[5][0]:.1f},{pts[5][1]:.1f}"
            )
        d = " ".join(parts)
    cls = "cut-h" if horizontal else "cut-v"
    return f'<path class="{cls}" d="{d}" fill="none" stroke="{INK}" stroke-width="{1.4 if knob else 0.7}" stroke-opacity="{0.8 if knob else 0.55}"/>'


def _loose_piece(cx: float, cy: float, s: float, paint: str) -> str:
    """One loose piece: a square with a knob out on two sides and a hole in on the others."""
    h = s / 2
    k = s * 0.2
    d = (
        f"M{cx - h:.1f},{cy - h:.1f} L{cx - k:.1f},{cy - h:.1f} C{cx - k * 1.6:.1f},{cy - h - k * 1.8:.1f} {cx + k * 1.6:.1f},{cy - h - k * 1.8:.1f} {cx + k:.1f},{cy - h:.1f} "
        f"L{cx + h:.1f},{cy - h:.1f} L{cx + h:.1f},{cy - k:.1f} C{cx + h + k * 1.8:.1f},{cy - k * 1.6:.1f} {cx + h + k * 1.8:.1f},{cy + k * 1.6:.1f} {cx + h:.1f},{cy + k:.1f} "
        f"L{cx + h:.1f},{cy + h:.1f} L{cx + k:.1f},{cy + h:.1f} C{cx + k * 1.6:.1f},{cy + h - k * 1.8:.1f} {cx - k * 1.6:.1f},{cy + h - k * 1.8:.1f} {cx - k:.1f},{cy + h:.1f} "
        f"L{cx - h:.1f},{cy + h:.1f} L{cx - h:.1f},{cy + k:.1f} C{cx - h + k * 1.8:.1f},{cy + k * 1.6:.1f} {cx - h + k * 1.8:.1f},{cy - k * 1.6:.1f} {cx - h:.1f},{cy - k:.1f} Z"
    )
    return f'<g class="loose" transform="rotate(-14 {cx:.1f} {cy:.1f})">{_path(d, paint)}</g>'


def jigsaw(
    paint: str,
    fill: Fill,
    label: str | None,
    pieces: str = "100",
    theme: str = "landscapes",
    character: str = "",
) -> list[str]:
    """A finished puzzle of ``pieces`` tiles: rows x columns cuts over the ``theme`` picture
    (knobbed at 100 pieces or fewer), and one loose piece lifted off at the corner."""
    n = max(1, _n(pieces, 100))
    rows, cols = grid(n)
    x, y, w, h = 34.0, 46.0, 300.0, 240.0
    knob = min(w / cols, h / rows) * 0.18 if n <= 100 else 0.0
    out = [
        _shadow(190, 300, 170),
        _rect(x, y, w, h, paint, 2),
        *_jig_picture(theme, x, y, w, h, fill),
    ]
    out += [_cut(True, y + h * r / rows, x, x + w, cols, knob) for r in range(1, rows)]
    out += [_cut(False, x + w * c / cols, y, y + h, rows, knob) for c in range(1, cols)]
    out += [_rect(x, y, w, h, "none", 2), _loose_piece(318, 318, 62, paint)]
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Board games
# --------------------------------------------------------------------------


def _die(x: float, y: float, s: float, pips: int) -> list[str]:
    spots = {
        1: [(0.5, 0.5)],
        3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
        5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    }[pips]
    return [
        _rect(x, y, s, s, WHITE, s * 0.18, LW_DETAIL),
        *(
            f'<circle cx="{x + s * a:.1f}" cy="{y + s * b:.1f}" r="{s * 0.08:.1f}" fill="{INK}"/>'
            for a, b in spots
        ),
    ]


def _pawn(cx: float, base: float, color: str) -> list[str]:
    return [_path(f"M{cx - 13:.1f},{base:.1f} L{cx - 6:.1f},{base - 30:.1f} L{cx + 6:.1f},{base - 30:.1f} L{cx + 13:.1f},{base:.1f} Z", color, LW_DETAIL),
            _ell(cx, base - 36, 9, 9, color, LW_DETAIL)]  # fmt: skip


def _card(x: float, y: float, w: float, h: float, turn: float, mark: str, color: str) -> str:
    cx, cy = x + w / 2, y + h / 2
    inner = [
        _rect(x, y, w, h, WHITE, 6, LW_DETAIL),
        _rect(x + 6, y + 6, w - 12, h - 12, "none", 4, 1),
    ]
    if mark == "star":
        inner.append(_star(cx, cy, w * 0.26, color, 1.2))
    else:
        inner.append(_ell(cx, cy, w * 0.22, w * 0.22, color, 1.2))
    inner.append(f'<circle cx="{x + 14:.1f}" cy="{y + 16:.1f}" r="4" fill="{color}"/>')
    return f'<g transform="rotate({turn:g} {x + w / 2:.1f} {y + h:.1f})">{"".join(inner)}</g>'


def board_game(
    paint: str, fill: Fill, label: str | None, kind: str = "family", character: str = ""
) -> list[str]:
    """A ``family`` game's square board with a track of squares round its edge, dice and
    pawns; a ``strategy`` game's board of hex tiles with pieces on it; a ``card`` game's
    tuck box and a fan of cards; a ``party`` game's box, a sand timer and a stack of cards."""
    out = [_shadow(200, 344, 170)]
    if kind == "card":
        out += [_rect(46, 150, 120, 180, paint, 8), _rect(46, 150, 120, 38, _shade(fill.base, 0.2), 8, LW_DETAIL),
                _ell(106, 252, 34, 34, WHITE, LW_DETAIL)]  # fmt: skip
        out += [
            _card(196, 120, 110, 160, t, "star" if i % 2 else "dot", c)
            for i, (t, c) in enumerate(zip((-24, -12, 0, 12, 24), RAINBOW[::2], strict=False))
        ]
        return [*out, *_badge(character)]
    if kind == "party":
        out += [_rect(40, 120, 220, 200, paint, 6), _rect(40, 120, 220, 40, _shade(fill.base, 0.2), 6, LW_DETAIL),
                _ell(150, 240, 56, 40, WHITE, LW_DETAIL), _path("M126,230 Q150,214 174,230 Q150,262 126,230 Z", fill.base if fill.pattern == "solid" else INK, 1.2),
                # a sand timer
                _rect(282, 124, 64, 12, WOOD, 3, LW_DETAIL), _rect(282, 300, 64, 12, WOOD, 3, LW_DETAIL),
                _path("M292,136 L336,136 Q336,190 314,218 Q336,246 336,300 L292,300 Q292,246 314,218 Q292,190 292,136 Z", "#e3eef0", LW_DETAIL),
                _path("M300,300 Q314,262 328,300 Z M306,168 L322,168 Q318,190 314,200 Q310,190 306,168 Z", "#e6c46a", 1),
                # a stack of cards
                *[_rect(270 - i * 2, 322 - i * 4, 90, 26, WHITE, 4, 1.2) for i in range(4)]]  # fmt: skip
        return [*out, *_badge(character)]
    if kind == "strategy":
        out.append(_rect(30, 60, 340, 280, paint, 6))
        out.append(_rect(44, 74, 312, 252, _tint(fill.base, 0.85), 3, LW_DETAIL))
        r = 26.0
        tones = ("#8fc07a", "#e6c46a", "#c9a96e", "#7d8a99", "#5f9a4a")
        for row in range(5):
            for col in range(6):
                cx = 82 + col * r * 1.75 + (r * 0.87 if row % 2 else 0)
                cy = 104 + row * r * 1.5
                pts = " L".join(
                    f"{cx + r * math.cos(math.pi / 6 + i * math.pi / 3):.1f},{cy + r * math.sin(math.pi / 6 + i * math.pi / 3):.1f}"
                    for i in range(6)
                )
                out.append(_path(f"M{pts} Z", tones[(row * 2 + col) % 5], 1.2))
        out += [
            _rect(x, y, 16, 16, c, 2, LW_DETAIL)
            for x, y, c in (
                (120, 140, "#d93b30"),
                (210, 186, "#2f8fc4"),
                (260, 120, "#f4f1ea"),
                (160, 232, "#2f2f35"),
            )
        ]
        return [*out, *_badge(character)]
    # family: a track of squares round the board, a centre panel, dice and pawns
    out += [_rect(36, 56, 328, 290, _tint(fill.base, 0.85), 6), _rect(36, 56, 328, 290, "none", 6)]
    n, s = 9, 328 / 9
    squares = (
        [(i, 0) for i in range(n)]
        + [(n - 1, j) for j in range(1, 8)]
        + [(i, 7) for i in range(n - 2, -1, -1)]
        + [(0, j) for j in range(6, 0, -1)]
    )
    sh = 290 / 8
    for k, (i, j) in enumerate(squares):
        out.append(_rect(36 + i * s, 56 + j * sh, s, sh, paint if k % 2 else WHITE, 0, 1.2))
    out += [_rect(36 + s * 1.6, 56 + sh * 1.6, s * 5.8, sh * 4.8, paint, 10, LW_DETAIL),
            _ell(200, 200, 58, 40, WHITE, LW_DETAIL)]  # fmt: skip
    out += [
        *_die(110, 238, 34, 5),
        *_die(156, 252, 34, 3),
        *_pawn(256, 266, "#f2c94c"),
        *_pawn(290, 250, "#2f8fc4"),
    ]
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Dolls
# --------------------------------------------------------------------------


def _accessories(n: int, x: float = 312, y0: float = 96) -> list[str]:
    """Each accessory a small tile beside the doll (``class="accessory"``)."""
    glyphs = ("bag", "hat", "shoe", "brush")
    out = []
    step = min(64.0, 240 / max(n, 1))
    for i in range(n):
        y = y0 + i * step
        g = glyphs[i % len(glyphs)]
        inner = [_rect(x, y, 56, step - 8, WHITE, 6, 1.2)]
        cx, cy = x + 28, y + (step - 8) / 2
        if g == "bag":
            inner += [
                _rect(cx - 14, cy - 6, 28, 18, "#e46aa0", 3, 1.2),
                _path(
                    f"M{cx - 8:.1f},{cy - 6:.1f} Q{cx:.1f},{cy - 20:.1f} {cx + 8:.1f},{cy - 6:.1f}",
                    "none",
                    1.2,
                ),
            ]
        elif g == "hat":
            inner += [
                _ell(cx, cy + 6, 20, 6, "#e6c46a", 1.2),
                _path(
                    f"M{cx - 10:.1f},{cy + 6:.1f} Q{cx:.1f},{cy - 16:.1f} {cx + 10:.1f},{cy + 6:.1f} Z",
                    "#e6c46a",
                    1.2,
                ),
            ]
        elif g == "shoe":
            inner += [
                _path(
                    f"M{cx - 16:.1f},{cy + 8:.1f} L{cx - 14:.1f},{cy - 6:.1f} L{cx - 2:.1f},{cy - 4:.1f} Q{cx + 6:.1f},{cy + 4:.1f} {cx + 16:.1f},{cy + 4:.1f} L{cx + 16:.1f},{cy + 8:.1f} Z",
                    "#d93b30",
                    1.2,
                )
            ]
        else:
            inner += [
                _rect(cx - 4, cy - 2, 22, 6, "#8a5a3a", 2, 1.2),
                _ell(cx - 10, cy + 1, 9, 7, "#9a9ca0", 1.2),
            ]
        out.append(_group("accessory", inner))
    return out


def _figure(cx: float, base: float, h: float, paint: str) -> str:
    """One small bendy figure, ``h`` tall: head, body and legs (``class="piece"``)."""
    r = h * 0.13
    return _group("piece", [
        _rect(cx - h * 0.09, base - h * 0.42, h * 0.07, h * 0.42, "#26365c", 2, 1.2),
        _rect(cx + h * 0.02, base - h * 0.42, h * 0.07, h * 0.42, "#26365c", 2, 1.2),
        _rect(cx - h * 0.15, base - h * 0.74, h * 0.3, h * 0.36, paint, 5, LW_DETAIL),
        _ell(cx, base - h * 0.74 - r, r, r, SKIN, LW_DETAIL),
        _path(f"M{cx - r:.1f},{base - h * 0.74 - r:.1f} Q{cx:.1f},{base - h * 0.74 - r * 2.6:.1f} {cx + r:.1f},{base - h * 0.74 - r:.1f} Z", HAIR, 1.2)])  # fmt: skip


def _face(cx: float, cy: float, r: float, buttons: bool = False) -> list[str]:
    if buttons:
        eyes = [
            _ell(cx + dx, cy - r * 0.05, r * 0.13, r * 0.13, BLACK, 1)
            for dx in (-r * 0.35, r * 0.35)
        ]
    else:
        eyes = [
            f'<circle cx="{cx + dx:.1f}" cy="{cy - r * 0.05:.1f}" r="{r * 0.08:.1f}" fill="{INK}"/>'
            for dx in (-r * 0.35, r * 0.35)
        ]
    return [*eyes, _line(f"M{cx - r * 0.25:.1f},{cy + r * 0.35:.1f} Q{cx:.1f},{cy + r * 0.5:.1f} {cx + r * 0.25:.1f},{cy + r * 0.35:.1f}", 1.4),
            f'<circle cx="{cx - r * 0.55:.1f}" cy="{cy + r * 0.25:.1f}" r="{r * 0.12:.1f}" fill="#e88a8a" fill-opacity=".6"/>',
            f'<circle cx="{cx + r * 0.55:.1f}" cy="{cy + r * 0.25:.1f}" r="{r * 0.12:.1f}" fill="#e88a8a" fill-opacity=".6"/>']  # fmt: skip


def doll(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "fashion",
    accessories: str = "0",
    counts: str = "",
    character: str = "",
) -> list[str]:
    """A ``fashion`` doll (slim, long hair), a ``baby`` doll (bonnet, romper) or a ``rag``
    doll (yarn hair, button eyes, stitched dress), in the outfit's color, with each of its
    ``accessories`` beside it; ``house`` draws a set's figures in a row, grown-ups first."""
    if kind == "house":
        sizes = _counts(counts, (2, 2))
        hs = [250.0] * sizes[0] + [170.0] * sum(sizes[1:])
        step = 300 / max(len(hs), 1)
        out = [_shadow(200, 330, 160)]
        out += [
            _figure(50 + step * (i + 0.5), 326, h, paint if i % 2 == 0 else _tint(fill.base, 0.4))
            for i, h in enumerate(hs)
        ]
        return [*out, *_badge(character)]
    acc = _n(accessories, 0)
    cx = 160.0 if acc else 200.0
    out = [_shadow(cx, 340, 90)]
    if kind == "baby":
        out += [_rect(cx - 82, 196, 34, 58, SKIN, 16, LW), _rect(cx + 48, 196, 34, 58, SKIN, 16, LW),
                _rect(cx - 48, 274, 40, 62, SKIN, 18, LW), _rect(cx + 8, 274, 40, 62, SKIN, 18, LW),
                _rect(cx - 62, 172, 124, 132, paint, 40), _ell(cx, 120, 56, 54, SKIN),
                _path(f"M{cx - 60:.1f},{130:.1f} Q{cx - 64:.1f},{56:.1f} {cx:.1f},{58:.1f} Q{cx + 64:.1f},{56:.1f} {cx + 60:.1f},{130:.1f} Q{cx:.1f},{86:.1f} {cx - 60:.1f},{130:.1f} Z", paint),
                *_face(cx, 128, 50), _ell(cx, 176, 18, 8, WHITE, LW_DETAIL)]  # fmt: skip
    elif kind == "rag":
        out += [
            _rect(cx - 30, 260, 18, 74, WHITE, 6, LW),
            _rect(cx + 12, 260, 18, 74, WHITE, 6, LW),
        ]
        out += [
            _line(
                f"M{cx - 30 + (0 if i % 2 else 0):.1f},{270 + i * 14:.1f} L{cx - 12:.1f},{270 + i * 14:.1f} M{cx + 12:.1f},{270 + i * 14:.1f} L{cx + 30:.1f},{270 + i * 14:.1f}",
                4,
                stroke="#d93b30",
            )
            for i in range(5)
        ]
        out += [_path(f"M{cx - 30:.1f},{148:.1f} L{cx - 72:.1f},{240:.1f} L{cx - 58:.1f},{248:.1f} L{cx - 30:.1f},{196:.1f} Z M{cx + 30:.1f},{148:.1f} L{cx + 72:.1f},{240:.1f} L{cx + 58:.1f},{248:.1f} L{cx + 30:.1f},{196:.1f} Z", SKIN),
                _path(f"M{cx - 34:.1f},{142:.1f} L{cx + 34:.1f},{142:.1f} L{cx + 70:.1f},{272:.1f} L{cx - 70:.1f},{272:.1f} Z", paint),
                _line(f"M{cx - 64:.1f},{262:.1f} L{cx + 64:.1f},{262:.1f}", 1.4, ' stroke-dasharray="4 4"'),
                _rect(cx - 16, 196, 32, 30, _tint(fill.base, 0.5), 3, 1.4, ' stroke-dasharray="3 3"'),
                _ell(cx, 100, 46, 46, SKIN)]  # fmt: skip
        out += [
            _path(
                f"M{cx - 46 + i * 11.5:.1f},{96:.1f} Q{cx - 52 + i * 11.5:.1f},{58:.1f} {cx - 40 + i * 11.5:.1f},{56:.1f}",
                "none",
                4,
                stroke="#e07a1f",
            )
            for i in range(9)
        ]
        out += _face(cx, 104, 44, buttons=True)
    else:
        out += [_rect(cx - 16, 250, 12, 84, SKIN, 5, LW_DETAIL), _rect(cx + 4, 250, 12, 84, SKIN, 5, LW_DETAIL),
                _ell(cx - 10, 334, 12, 6, "#d93b30", LW_DETAIL), _ell(cx + 10, 334, 12, 6, "#d93b30", LW_DETAIL),
                _path(f"M{cx - 50:.1f},{70:.1f} Q{cx - 58:.1f},{170:.1f} {cx - 40:.1f},{190:.1f} L{cx + 40:.1f},{190:.1f} Q{cx + 58:.1f},{170:.1f} {cx + 50:.1f},{70:.1f} Z", "#e6c46a"),
                _path(f"M{cx - 24:.1f},{130:.1f} L{cx - 50:.1f},{220:.1f} L{cx - 42:.1f},{224:.1f} L{cx - 20:.1f},{160:.1f} Z M{cx + 24:.1f},{130:.1f} L{cx + 50:.1f},{220:.1f} L{cx + 42:.1f},{224:.1f} L{cx + 20:.1f},{160:.1f} Z", SKIN, LW_DETAIL),
                _path(f"M{cx - 22:.1f},{126:.1f} L{cx + 22:.1f},{126:.1f} L{cx + 16:.1f},{176:.1f} L{cx + 48:.1f},{260:.1f} L{cx - 48:.1f},{260:.1f} L{cx - 16:.1f},{176:.1f} Z", paint),
                _rect(cx - 6, 108, 12, 20, SKIN, 3, LW_DETAIL), _ell(cx, 82, 32, 36, SKIN),
                _path(f"M{cx - 34:.1f},{86:.1f} Q{cx - 34:.1f},{40:.1f} {cx:.1f},{42:.1f} Q{cx + 34:.1f},{40:.1f} {cx + 34:.1f},{86:.1f} Q{cx + 10:.1f},{58:.1f} {cx - 34:.1f},{86:.1f} Z", "#e6c46a"),
                *_face(cx, 88, 30)]  # fmt: skip
    return [*out, *_accessories(acc), *_badge(character, 52, 50)]


# --------------------------------------------------------------------------
# Wooden toys
# --------------------------------------------------------------------------


def _grain(x: float, y: float, w: float, h: float) -> str:
    return _line(
        " ".join(
            f"M{x + 6:.1f},{y + h * f:.1f} Q{x + w / 2:.1f},{y + h * f - 3:.1f} {x + w - 6:.1f},{y + h * f:.1f}"
            for f in (0.35, 0.7)
        ),
        0.8,
        ' stroke-opacity=".35"',
    )


def _wheel(
    cx: float, cy: float, r: float, tire: str = BLACK, hub: str = STEEL, spokes: int = 0
) -> str:
    parts = [_ell(cx, cy, r, r, tire), _ell(cx, cy, r * 0.62, r * 0.62, hub, LW_DETAIL)]
    if spokes:
        parts.append(
            _line(
                " ".join(
                    f"M{cx:.1f},{cy:.1f} L{cx + r * 0.62 * math.cos(i * 2 * math.pi / spokes):.1f},{cy + r * 0.62 * math.sin(i * 2 * math.pi / spokes):.1f}"
                    for i in range(spokes)
                ),
                1,
            )
        )
    parts.append(_ell(cx, cy, r * 0.14, r * 0.14, INK, 1))
    return _group("wheel", parts)


def wooden_toy(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "stacking",
    counts: str = "",
    animal: str = "",
    character: str = "",
) -> list[str]:
    """``stacking`` rings on a peg, a ``sorter`` cube and its shapes, a ``train`` on its
    track, a ``puzzle`` board and its pieces (each piece a ``class="piece"`` group, as many
    as ``counts`` holds), or a ``pull_along`` whale or dog on wheels. A Natural colorway
    (``fill.base`` is the wood color) is unpainted, so its body shows the wood's grain."""
    out = [_shadow(200, 344, 170)]
    natural = fill.base.lower() == WOOD
    if kind == "stacking":
        rings, bases = (_counts(counts, (5, 1)) + [1])[:2]
        out.append(_rect(196, 112, 8, 200, WOOD, 3, LW_DETAIL))
        if bases:
            out.append(
                _group("piece", [_rect(100, 304, 200, 30, WOOD, 6), _grain(100, 304, 200, 30)])
            )
        for i in range(rings):
            w = 190 - i * (110 / max(rings - 1, 1))
            y = 270 - i * 36
            out.append(
                _group("piece", [_rect(200 - w / 2, y, w, 34, _tint(fill.base, 0.12 * i), 17)])
            )
        out.append(_ell(200, 104, 18, 18, paint))
    elif kind == "sorter":
        cube, shapes = (_counts(counts, (1, 6)) + [0])[:2]
        if cube:
            out.append(_group("piece", [_path("M60,160 L100,120 L250,120 L210,160 Z", _tint(fill.base, 0.3)),
                                        _path("M210,160 L250,120 L250,280 L210,320 Z", _shade(fill.base, 0.2)),
                                        _rect(60, 160, 150, 160, paint, 2),
                                        _ell(110, 140, 16, 7, INK, 1), _path("M150,134 L176,134 L170,146 L144,146 Z", INK, 1),
                                        _path("M196,146 L206,128 L218,146 Z", INK, 1), _star(135, 240, 26, INK, 1)]))  # fmt: skip
        slots = [
            (282, 166),
            (338, 166),
            (282, 236),
            (338, 236),
            (282, 306),
            (338, 306),
            (230, 340),
            (170, 350),
        ]
        draws = ("circle", "square", "triangle", "star", "hexagon", "rect")
        for i in range(shapes):
            sx, sy = slots[i % len(slots)]
            c = (paint, _tint(fill.base, 0.35), _shade(fill.base, 0.2))[i % 3]
            g = draws[i % len(draws)]
            if g == "circle":
                p = _ell(sx, sy, 22, 22, c)
            elif g == "square":
                p = _rect(sx - 20, sy - 20, 40, 40, c, 3)
            elif g == "triangle":
                p = _path(f"M{sx - 24},{sy + 18} L{sx},{sy - 22} L{sx + 24},{sy + 18} Z", c)
            elif g == "star":
                p = _star(sx, sy, 26, c, LW)
            elif g == "hexagon":
                p = _path(
                    "M"
                    + " L".join(
                        f"{sx + 22 * math.cos(k * math.pi / 3):.1f},{sy + 22 * math.sin(k * math.pi / 3):.1f}"
                        for k in range(6)
                    )
                    + " Z",
                    c,
                )
            else:
                p = _rect(sx - 26, sy - 14, 52, 28, c, 3)
            out.append(_group("piece", [p]))
    elif kind == "train":
        engines, cars, track = (_counts(counts, (1, 2, 6)) + [0, 0])[:3]
        seg = 340 / max(track, 1)
        for i in range(track):
            out.append(_group("piece", [_rect(30 + i * seg + 1, 300, seg - 2, 26, WOOD, 3, LW_DETAIL),
                                        _line(f"M{32 + i * seg:.1f},{308:.1f} L{28 + (i + 1) * seg:.1f},{308:.1f} M{32 + i * seg:.1f},{318:.1f} L{28 + (i + 1) * seg:.1f},{318:.1f}", 1)]))  # fmt: skip
        x = 34.0
        for _ in range(cars):
            out.append(_group("piece", [_rect(x, 230, 92, 52, _tint(fill.base, 0.25), 6), _rect(x + 14, 206, 64, 24, WOOD, 4, LW_DETAIL),
                                        _ell(x + 22, 290, 13, 13, BLACK, LW_DETAIL), _ell(x + 70, 290, 13, 13, BLACK, LW_DETAIL)]))  # fmt: skip
            x += 100
        if engines:
            out.append(_group("piece", [_rect(x + 50, 170, 62, 112, paint, 6), _rect(x + 44, 160, 74, 16, _shade(fill.base, 0.3), 4, LW_DETAIL),
                                        _rect(x, 222, 54, 60, paint, 6), _rect(x + 10, 190, 14, 34, BLACK, 3, LW_DETAIL),
                                        _rect(x + 62, 190, 38, 30, WHITE, 4, LW_DETAIL),
                                        _ell(x + 22, 290, 15, 15, BLACK, LW_DETAIL), _ell(x + 88, 290, 15, 15, BLACK, LW_DETAIL)]))  # fmt: skip
    elif kind == "puzzle":
        pieces = sum(_counts(counts, (6,)))
        import motifs  # deferred: motifs draws with this kit's shapes

        cols = max(1, math.ceil(pieces / 2))
        out += [_rect(40, 80, 320, 240, WOOD, 10), _grain(40, 80, 320, 240)]
        cw_, ch = 300 / cols, 110
        names = ("cat", "bird", "whale", "dinosaur", "cat", "bird")
        for i in range(pieces):
            cx = 50 + cw_ * (i % cols) + cw_ / 2
            cy = 90 + ch * (i // cols) + ch / 2
            c = (paint, _tint(fill.base, 0.35))[i % 2]
            out.append(_group("piece", [_rect(cx - cw_ / 2 + 6, cy - ch / 2 + 6, cw_ - 12, ch - 12, c, 14),
                                        motifs.motif_svg(names[i % len(names)], WHITE, cx, cy + 6, min(cw_, ch) * 1.1),
                                        _ell(cx, cy - ch / 2 + 22, 8, 8, "#d93b30", 1.2)]))  # fmt: skip
    else:  # pull_along
        out.append(
            _path(
                "M330,248 Q370,280 340,320 Q300,350 250,340 Q180,330 150,350 Q110,370 60,350",
                "none",
                2.4,
            )
        )
        out.append(_ell(56, 350, 9, 9, "#d93b30", LW_DETAIL))
        if animal == "dog":
            out += [
                _ell(130, 300, 24, 24, BLACK, LW_DETAIL),
                _ell(290, 300, 24, 24, BLACK, LW_DETAIL),
            ]
            for i, x in enumerate((90, 160, 230)):
                out += [_rect(x, 210, 72, 66, paint if i % 2 == 0 else _tint(fill.base, 0.2), 14)]
                out += [_grain(x, 210, 72, 66)] if natural else []
            out += [_ell(318, 196, 42, 34, paint), _path("M300,170 Q290,214 312,226 Q322,196 316,172 Z", _shade(fill.base, 0.3), LW_DETAIL),
                    _ell(354, 204, 7, 7, BLACK, 1), f'<circle cx="330" cy="188" r="4" fill="{INK}"/>',
                    _path("M92,226 Q62,200 70,176", "none", 6, stroke=paint)]  # fmt: skip
        else:
            out += [_ell(140, 304, 22, 22, BLACK, LW_DETAIL), _ell(270, 304, 22, 22, BLACK, LW_DETAIL),
                    _path("M60,230 Q60,150 170,146 Q290,142 320,218 Q326,260 280,282 L110,282 Q60,280 60,230 Z", paint),
                    _path("M320,214 L366,170 Q372,206 352,222 Q376,236 368,268 Z", paint),
                    _path("M80,250 Q180,268 300,250", "none", 1.4, ' stroke-opacity=".6"'),
                    *([_grain(90, 150, 210, 90)] if natural else []),
                    f'<circle cx="112" cy="206" r="6" fill="{INK}"/>',
                    _line("M150,148 Q144,118 160,104 M150,148 Q160,120 180,114", 2.4, stroke="#2f8fc4")]  # fmt: skip
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Role play
# --------------------------------------------------------------------------


def _teapot(cx: float, base: float, paint: str) -> str:
    return _group("piece", [_path(f"M{cx + 50:.1f},{base - 60:.1f} Q{cx + 92:.1f},{base - 80:.1f} {cx + 96:.1f},{base - 112:.1f} L{cx + 84:.1f},{base - 112:.1f} Q{cx + 80:.1f},{base - 86:.1f} {cx + 46:.1f},{base - 78:.1f} Z", paint, LW_DETAIL),
                            _path(f"M{cx - 52:.1f},{base - 90:.1f} Q{cx - 92:.1f},{base - 80:.1f} {cx - 56:.1f},{base - 36:.1f}", "none", 6),
                            _path(f"M{cx - 60:.1f},{base - 10:.1f} Q{cx - 74:.1f},{base - 100:.1f} {cx:.1f},{base - 104:.1f} Q{cx + 74:.1f},{base - 100:.1f} {cx + 60:.1f},{base - 10:.1f} Z", paint),
                            _ell(cx, base - 104, 32, 8, WHITE, LW_DETAIL), _ell(cx, base - 116, 8, 8, WHITE, LW_DETAIL)])  # fmt: skip


def _cup(cx: float, base: float, paint: str) -> str:
    return _group("piece", [_path(f"M{cx + 18:.1f},{base - 30:.1f} Q{cx + 34:.1f},{base - 26:.1f} {cx + 18:.1f},{base - 12:.1f}", "none", 3),
                            _path(f"M{cx - 22:.1f},{base - 40:.1f} L{cx + 22:.1f},{base - 40:.1f} Q{cx + 20:.1f},{base - 4:.1f} {cx:.1f},{base - 4:.1f} Q{cx - 20:.1f},{base - 4:.1f} {cx - 22:.1f},{base - 40:.1f} Z", paint)])  # fmt: skip


def role_play(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "kitchen",
    counts: str = "",
    character: str = "",
) -> list[str]:
    """A play ``kitchen`` (hob, oven door, sink and tap), a ``tool_bench`` (pegboard of
    tools, a vice), a ``doctor``'s case and stethoscope, a ``shop_till`` (keys, screen,
    drawer, scanner) or a ``tea_set``, each piece of which is a ``class="piece"`` group."""
    out = [_shadow(200, 346, 170)]
    if kind == "kitchen":
        out += [_rect(70, 40, 260, 96, _tint(fill.base, 0.55), 4), _rect(92, 56, 100, 14, WOOD, 2, LW_DETAIL),
                _ell(280, 80, 22, 22, WHITE, LW_DETAIL), _line("M280,80 L280,66 M280,80 L292,84", 1.6),
                _rect(56, 136, 288, 22, WOOD, 3), _rect(70, 158, 260, 182, paint, 4),
                _ell(118, 146, 30, 7, BLACK, LW_DETAIL), _ell(182, 146, 30, 7, BLACK, LW_DETAIL),
                _ell(272, 147, 40, 8, STEEL, LW_DETAIL), _path("M300,140 L300,112 Q300,100 286,100 L276,100", "none", 4, stroke=STEEL),
                _rect(86, 186, 130, 136, _shade(fill.base, 0.12), 6), _rect(106, 210, 90, 64, "#3a3f4a", 6, LW_DETAIL), _rect(110, 194, 82, 8, STEEL, 3, 1.2),
                _rect(234, 186, 80, 136, _shade(fill.base, 0.12), 6), _ell(300, 254, 5, 12, STEEL, 1.2)]  # fmt: skip
        out += [_ell(x, 172, 7, 7, WHITE, 1.2) for x in (100, 126, 152, 178)]
    elif kind == "tool_bench":
        out += [_rect(70, 50, 260, 126, _tint(fill.base, 0.6), 4)]
        out += [
            f'<circle cx="{x}" cy="{y}" r="2" fill="{INK}" fill-opacity=".4"/>'
            for x in range(86, 330, 22)
            for y in range(64, 170, 22)
        ]
        out += [_rect(100, 74, 14, 70, "#8a5a3a", 3, LW_DETAIL), _rect(84, 66, 46, 20, "#9a9ca0", 3, LW_DETAIL),
                _path("M170,70 L250,70 L250,92 L176,128 Z", STEEL, LW_DETAIL), _rect(250, 66, 20, 30, "#d93b30", 4, LW_DETAIL),
                _path("M290,70 L300,70 L300,140 Q308,150 296,160 Q284,150 290,140 Z", "#9a9ca0", LW_DETAIL),
                _rect(40, 176, 320, 28, paint, 4), _rect(60, 204, 24, 136, paint, 3), _rect(316, 204, 24, 136, paint, 3),
                _rect(84, 286, 232, 16, _shade(fill.base, 0.15), 3, LW_DETAIL),
                _rect(34, 150, 50, 30, "#9a9ca0", 3, LW_DETAIL), _line("M34,166 L14,166", 4), _ell(12, 166, 6, 6, "#d93b30", 1.2)]  # fmt: skip
    elif kind == "doctor":
        out += [_path("M150,150 L150,118 Q150,104 164,104 L236,104 Q250,104 250,118 L250,150", "none", 10, stroke=_shade(fill.base, 0.3)),
                _rect(70, 146, 260, 186, paint, 18), _rect(70, 146, 260, 32, _shade(fill.base, 0.15), 18, LW_DETAIL),
                _path("M184,206 L216,206 L216,232 L242,232 L242,264 L216,264 L216,290 L184,290 L184,264 L158,264 L158,232 L184,232 Z", WHITE, LW_DETAIL),
                _path("M290,160 Q350,190 340,260 Q330,320 290,330", "none", 5, stroke="#2f2f35"),
                _ell(290, 336, 18, 18, STEEL, LW_DETAIL), _path("M290,160 Q280,110 300,80 M290,160 Q330,120 330,80", "none", 4, stroke="#2f2f35"),
                _ell(300, 78, 6, 6, BLACK, 1), _ell(330, 78, 6, 6, BLACK, 1)]  # fmt: skip
    elif kind == "shop_till":
        out += [_rect(186, 70, 12, 60, "#9a9ca0", 3, LW_DETAIL), _rect(140, 40, 104, 46, "#3a3f4a", 6), _rect(150, 50, 84, 26, "#8fc07a", 3, 1.2),
                _path("M60,140 L300,140 L330,280 L40,280 Z", paint), _rect(30, 280, 320, 30, _shade(fill.base, 0.2), 4),
                _rect(46, 304, 288, 40, _tint(fill.base, 0.5), 4), _rect(176, 316, 48, 8, INK, 3, 1)]  # fmt: skip
        out += [
            _rect(96 + c * 36, 156 + r * 28, 28, 20, WHITE, 3, 1.2)
            for r in range(4)
            for c in range(5)
        ]
        out += [
            _path("M330,180 L376,170 L384,196 L346,204 L352,240 L334,244 Z", "#2f2f35", LW_DETAIL),
            _line("M376,170 L384,196", 3, stroke="#d93b30"),
        ]
        out += [_ell(x, 324, 10, 4, "#e6c46a", 1) for x in (80, 110, 280, 300)]
    else:  # tea_set
        pots, cups, saucers, jugs = (_counts(counts, (1, 4, 4, 1)) + [0, 0, 0])[:4]
        if jugs:
            out.append(_group("piece", [_path("M58,206 Q42,200 50,184 L62,180 Z", paint, 1.4),
                                        _path("M60,180 L104,180 Q110,230 82,236 Q56,230 60,180 Z", paint),
                                        _path("M104,190 Q124,200 104,220", "none", 3)]))  # fmt: skip
        if pots:
            out.append(_teapot(220, 240, paint))
        xs = [60 + i * (280 / max(max(cups, saucers) - 1, 1)) for i in range(max(cups, saucers))]
        for i in range(saucers):
            out.append(
                _group(
                    "piece",
                    [
                        _ell(xs[i], 316, 38, 10, WHITE, LW_DETAIL),
                        _ell(xs[i], 316, 26, 6, "none", 1),
                    ],
                )
            )
        for i in range(cups):
            out.append(_cup(xs[i], 316, paint))
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Arts and crafts
# --------------------------------------------------------------------------


def _brush(x: float, y: float, turn: float, color: str) -> str:
    return _group("piece", [f'<g transform="rotate({turn:g} {x:.1f} {y:.1f})">',
                            _rect(x, y - 4, 120, 8, "#d93b30", 3, 1.2), _rect(x + 120, y - 5, 18, 10, STEEL, 1, 1.2),
                            _path(f"M{x + 138:.1f},{y - 5:.1f} Q{x + 160:.1f},{y:.1f} {x + 138:.1f},{y + 5:.1f} Z", color, 1.2), "</g>"])  # fmt: skip


def _pencil(x: float, y: float, w: float, h: float, color: str) -> str:
    return _group("piece", [_rect(x, y + w * 1.4, w, h - w * 1.4, color, 1, 1),
                            _path(f"M{x:.1f},{y + w * 1.4:.1f} L{x + w / 2:.1f},{y:.1f} L{x + w:.1f},{y + w * 1.4:.1f} Z", WOOD, 0.8),
                            _path(f"M{x + w * 0.35:.1f},{y + w * 0.5:.1f} L{x + w / 2:.1f},{y:.1f} L{x + w * 0.65:.1f},{y + w * 0.5:.1f} Z", color, 0.6)])  # fmt: skip


def craft_kit(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "painting",
    counts: str = "",
    character: str = "",
) -> list[str]:
    """An opened kit, every piece of ``counts`` drawn (``class="piece"``): a ``painting``
    tin of paint pans with brushes and a water pot; a ``bead`` tray of tubs with cords; a
    ``slime`` kit's tubs, glitter pots and cup; ``knitting`` needles, yarn and booklet; a
    ``coloring`` tin of pencils with a sharpener and a book. The kit's box is in the fill."""
    out = [_shadow(200, 352, 170)]
    if kind == "painting":
        pans, brushes, pots = (_counts(counts, (12, 2, 1)) + [0, 0])[:3]
        rows = 1 if pans <= 6 else 2
        cols = max(1, math.ceil(pans / rows))
        out += [
            _rect(34, 36, 300, 70, paint, 8),
            _rect(34, 112, 300, 140 if rows == 2 else 90, "#3a3f4a", 8),
        ]
        pw = 280 / cols
        for i in range(pans):
            x = 44 + pw * (i % cols)
            y = 124 + 62 * (i // cols)
            out.append(
                _group("piece", [_rect(x, y, pw - 8, 52, RAINBOW[i % len(RAINBOW)], 6, 1.4)])
            )
        for i in range(brushes):
            out.append(_brush(50, 290 + i * 26, -6 + i * 4, RAINBOW[i * 4 % len(RAINBOW)]))
        for _ in range(pots):
            out.append(
                _group(
                    "piece",
                    [
                        _path("M296,270 L360,270 L352,344 L304,344 Z", "#e3eef0"),
                        _path("M300,300 L356,300 L352,344 L304,344 Z", _tint("#2f8fc4", 0.5), 1.2),
                    ],
                )
            )
    elif kind == "bead":
        tubs, cords, trays = (_counts(counts, (8, 4, 1)) + [0, 0])[:3]
        if trays:
            out.append(
                _group(
                    "piece",
                    [
                        _rect(40, 60, 320, 200, paint, 12),
                        _rect(52, 72, 296, 176, _tint(fill.base, 0.5), 8, LW_DETAIL),
                    ],
                )
            )
        cols = max(1, math.ceil(tubs / 2))
        tw = 296 / cols
        for i in range(tubs):
            x, y = 52 + tw * (i % cols), 72 + 88 * (i // cols)
            c = RAINBOW[i % len(RAINBOW)]
            dots = "".join(
                f'<circle cx="{x + 12 + (k % 4) * (tw - 24) / 3:.1f}" cy="{y + 22 + (k // 4) * 18:.1f}" r="6" fill="{c}" stroke="{INK}" stroke-width=".8"/>'
                for k in range(12)
            )
            out.append(_group("piece", [_rect(x + 4, y + 6, tw - 8, 76, WHITE, 8, 1.4), dots]))
        for i in range(cords):
            out.append(
                _group(
                    "piece",
                    [
                        _path(
                            f"M{60 + i * 8:.1f},{280 + i * 16:.1f} Q{150:.1f},{262 + i * 16:.1f} {220:.1f},{290 + i * 16:.1f} T{350 - i * 6:.1f},{284 + i * 14:.1f}",
                            "none",
                            2.6,
                            stroke=RAINBOW[(i * 3 + 1) % len(RAINBOW)],
                        )
                    ],
                )
            )
    elif kind == "slime":
        tubs, glitter, cups = (_counts(counts, (6, 3, 1)) + [0, 0])[:3]
        out.append(_rect(30, 40, 340, 110, paint, 10))
        out.append(_rect(46, 56, 308, 78, _tint(fill.base, 0.6), 6, LW_DETAIL))
        cols = max(1, math.ceil(tubs / 2))
        for i in range(tubs):
            cx, cy = 66 + (i % cols) * 70, 200 + (i // cols) * 80
            c = RAINBOW[(i * 2) % len(RAINBOW)]
            out.append(_group("piece", [_path(f"M{cx - 28:.1f},{cy - 16:.1f} L{cx + 28:.1f},{cy - 16:.1f} L{cx + 24:.1f},{cy + 30:.1f} L{cx - 24:.1f},{cy + 30:.1f} Z", _tint(c, 0.3)),
                                        _rect(cx - 31, cy - 30, 62, 16, c, 4, LW_DETAIL)]))  # fmt: skip
        for i in range(glitter):
            x = 278 + i * 28
            out.append(_group("piece", [_rect(x, 180, 22, 60, "#e3eef0", 4, LW_DETAIL), _rect(x, 172, 22, 12, RAINBOW[(i * 3) % len(RAINBOW)], 2, 1.2),
                                        *(f'<circle cx="{x + 5 + (k % 3) * 6:.1f}" cy="{200 + (k // 3) * 10:.1f}" r="1.8" fill="#f2c94c"/>' for k in range(9))]))  # fmt: skip
        for _ in range(cups):
            out.append(
                _group(
                    "piece",
                    [
                        _path("M282,270 L354,270 L346,340 L290,340 Z", WHITE),
                        _line("M290,290 L346,290", 1),
                    ],
                )
            )
    elif kind == "knitting":
        needles, balls, books = (_counts(counts, (2, 3, 1)) + [0, 0])[:3]
        if books:
            out.append(_group("piece", [_rect(40, 60, 150, 200, paint, 4), _rect(56, 80, 118, 90, WHITE, 3, LW_DETAIL),
                                        _path("M80,150 Q115,90 150,150", "none", 2), _line("M60,196 L170,196 M60,212 L170,212 M60,228 L140,228", 1.2)]))  # fmt: skip
        for i in range(balls):
            cx, cy = (250, 240, 320)[i % 3] + (i // 3) * 20, (150, 280, 270)[i % 3]
            c = _tint(fill.base, 0.1 + 0.25 * i) if fill.pattern == "solid" else RAINBOW[i]
            wraps = " ".join(
                f"M{cx - 44:.1f},{cy - 30 + k * 14:.1f} Q{cx:.1f},{cy - 50 + k * 14:.1f} {cx + 44:.1f},{cy - 26 + k * 14:.1f}"
                for k in range(5)
            )
            out.append(
                _group(
                    "piece", [_ell(cx, cy, 52, 52, c), _line(wraps, 1.2, ' stroke-opacity=".55"')]
                )
            )
        for i in range(needles):
            x0, y0, x1, y1 = (190, 60, 330, 200) if i % 2 == 0 else (330, 60, 200, 210)
            out.append(
                _group(
                    "piece",
                    [
                        _line(f"M{x0},{y0} L{x1},{y1}", 6, stroke=WOOD),
                        _line(f"M{x0},{y0} L{x1},{y1}", 1),
                        _ell(x0, y0, 9, 9, "#d93b30", 1.4),
                    ],
                )
            )
    else:  # coloring
        pencils, sharpeners, books = (_counts(counts, (24, 1, 1)) + [0, 0])[:3]
        out += [
            _rect(30, 60, 340, 180, paint, 8),
            _rect(42, 72, 316, 156, _tint(fill.base, 0.7), 6, LW_DETAIL),
        ]
        pw = 300 / max(pencils, 1)
        for i in range(pencils):
            out.append(_pencil(50 + i * pw, 86, pw - 2, 130, RAINBOW[i % len(RAINBOW)]))
        for _ in range(books):
            out.append(
                _group(
                    "piece",
                    [
                        _rect(40, 262, 200, 90, WHITE, 3),
                        _star(140, 307, 30, "none", 1.6),
                        _line("M40,262 L40,352", 4),
                    ],
                )
            )
        for _ in range(sharpeners):
            out.append(
                _group(
                    "piece",
                    [_rect(280, 290, 54, 40, "#2f8fc4", 4), _ell(307, 310, 8, 8, BLACK, 1.2)],
                )
            )
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Ride-ons
# --------------------------------------------------------------------------


#: The wheel sizes (inches) a bike or a trike is sold in, and the drawing's scale at the
#: smallest and the largest: a 10 inch bike draws smaller than a 14 inch one (gen#271).
WHEEL_SCALE = {10: 0.8, 14: 1.0}


def _size_scale(wheel_size_in: str) -> float:
    """The drawing's scale for a wheel size in inches: 1.0 when it states none."""
    inches = _n(wheel_size_in, 0)
    if not inches:
        return 1.0
    (lo, s_lo), (hi, s_hi) = sorted(WHEEL_SCALE.items())
    return round(s_lo + (s_hi - s_lo) * (min(max(inches, lo), hi) - lo) / (hi - lo), 3)


def ride_on(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "balance_bike",
    wheels: str = "2",
    character: str = "",
    wheel_size_in: str = "",
) -> list[str]:
    """A ``balance_bike`` (no pedals), a ``scooter`` (a deck and a T-bar; two wheels, or
    three with two at the front), a ``trike`` with its push handle, or a ride-on ``car``
    whose far wheels show behind its body; every wheel a ``class="wheel"`` group.
    ``wheel_size_in`` scales the whole drawing about its ground line, so each size of a
    bike is its own picture."""
    body = _ride_on_body(paint, fill, label, kind, wheels, character)
    scale = _size_scale(wheel_size_in)
    if scale == 1.0:
        return body
    return [f'<g transform="translate(200 350) scale({scale}) translate(-200 -350)">',
            *body, "</g>"]  # fmt: skip


def _ride_on_body(
    paint: str, fill: Fill, label: str | None, kind: str, wheels: str, character: str
) -> list[str]:
    n = _n(wheels, 2)
    out = [_shadow(200, 350, 170)]
    if kind == "scooter":
        three = n >= 3
        out += [_wheel(306, 312, 28, BLACK, "#e6c46a")]
        if three:
            out += [
                _wheel(116, 306, 28, _shade(BLACK, 0.2), "#e6c46a"),
                _wheel(90, 314, 28, BLACK, "#e6c46a"),
            ]
        else:
            out += [_wheel(96, 312, 28, BLACK, "#e6c46a")]
        out += [_path("M110,292 L300,292 Q320,292 320,304 L110,304 Z", paint), _rect(118, 282, 180, 14, _shade(fill.base, 0.2), 6, LW_DETAIL),
                _path("M98,300 L112,292 L140,70 L128,68 Z", paint, LW_DETAIL), _rect(70, 58, 130, 14, "#2f2f35", 7, LW_DETAIL),
                _rect(62, 56, 28, 18, BLACK, 8, LW_DETAIL), _rect(180, 56, 28, 18, BLACK, 8, LW_DETAIL)]  # fmt: skip
        return [*out, *_badge(character, 350, 120)]
    if kind == "trike":
        out += [_line("M304,290 L330,60", 6, stroke="#2f2f35"), _path("M316,64 Q330,40 356,56", "none", 8, stroke="#2f2f35"),
                _wheel(296, 300, 38, _shade(BLACK, 0.2), STEEL, 6), _wheel(110, 290, 58, BLACK, STEEL, 8),
                _path("M120,180 L140,180 L250,280 L330,300 L330,312 L240,300 L130,200 Z", paint),
                _wheel(330, 306, 38, BLACK, STEEL, 6),
                _line("M244,214 L244,272", 8, stroke="#2f2f35"), _rect(206, 196, 76, 20, "#2f2f35", 9), _path("M206,196 Q200,150 230,150 L246,196 Z", "#2f2f35", LW_DETAIL),
                _line("M110,290 L120,170", 7, stroke=paint if fill.pattern == "solid" else "#9a9ca0"), _rect(86, 160, 72, 12, "#2f2f35", 6, LW_DETAIL),
                _rect(96, 280, 34, 10, "#2f2f35", 3, 1.2)]  # fmt: skip
        return [*out, *_badge(character)]
    if kind == "car":
        out += [_wheel(140, 300, 30, _shade(BLACK, 0.2)), _wheel(310, 300, 30, _shade(BLACK, 0.2)),
                _path("M40,290 Q40,220 100,214 L150,214 Q170,160 220,160 L260,160 Q300,160 316,214 L350,220 Q376,226 370,290 Z", paint),
                _path("M166,214 Q178,174 214,172 L214,214 Z", "#dcebef", LW_DETAIL), _rect(226, 190, 70, 24, "#2f2f35", 8, LW_DETAIL),
                _path("M190,160 L176,128", "none", 4), _ell(176, 126, 18, 7, "#2f2f35", LW_DETAIL),
                _ell(54, 252, 10, 12, "#f2c94c", LW_DETAIL), _ell(360, 256, 6, 10, "#d93b30", LW_DETAIL),
                _wheel(110, 306, 34), _wheel(286, 306, 34)]  # fmt: skip
        return [*out, *_badge(character)]
    # balance bike: two wheels, a frame, a saddle, bars; no pedals
    frame = paint if fill.pattern == "solid" else _shade(fill.base, 0.1)
    out += [_wheel(100, 290, 62, BLACK, STEEL, 10), _wheel(300, 290, 62, BLACK, STEEL, 10),
            _path("M100,290 L170,200 L270,196 L300,290", "none", 14, stroke=INK), _path("M100,290 L170,200 L270,196 L300,290", "none", 9, stroke=frame),
            _line("M270,196 L250,110", 12, stroke=INK), _line("M270,196 L250,110", 7, stroke=frame),
            _line("M170,200 L156,150", 10, stroke="#9a9ca0"), _path("M120,150 Q156,138 196,148 L190,158 Q156,154 124,160 Z", "#2f2f35", LW_DETAIL),
            _rect(214, 98, 76, 12, "#2f2f35", 6, LW_DETAIL), _rect(206, 96, 26, 16, BLACK, 7, 1.2)]  # fmt: skip
    return [*out, *_badge(character)]


SHAPES = {"building_set": building_set, "jigsaw": jigsaw, "board_game": board_game, "doll": doll,
          "wooden_toy": wooden_toy, "role_play": role_play, "craft_kit": craft_kit, "ride_on": ride_on}  # fmt: skip

register(SHAPES)
