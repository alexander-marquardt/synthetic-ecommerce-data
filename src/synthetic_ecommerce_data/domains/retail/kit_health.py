"""The Health department's own shape: a capped supplement bottle (gen#1028).

=================  ==================================================  ===============
shape              what it draws                                       params
=================  ==================================================  ===============
supplement_bottle  a capped bottle with a wrapped label: a band in     nutrient, form
                   the nutrient's colour, its name, a tablet or a
                   capsule glyph
=================  ==================================================  ===============

Vitamins and minerals drew the retail ``tub`` (a tall tapered open pot), which reads as a paper
cup. The bottle is the colourway's base (white, amber, sage), the screw cap its accent. The
label carries what tells two bottles of one brand apart on a shelf: the nutrient's name, a
band coloured by the nutrient (:func:`band_colour`), and a glyph by ``form`` (a scored tablet
for ``Tablets``, a two-tone capsule for ``Capsules``). Both are drawing params holding the
attribute values, so a derived style that swaps the nutrient or the form is redrawn.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import zlib

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _rim,
    _word,
    register,
)

#: The label band's colours: a nutrient or mineral picks one by a stable hash of its name, so
#: one nutrient has one colour across brands and builds.
BANDS = (
    "#d9532b", "#e8a33a", "#e2c93f", "#7aa846", "#3f9a83", "#3e86c2",
    "#5b5fb8", "#9a58a8", "#c94f7c", "#8a6a4a", "#4a6f80", "#b33a3a",
)  # fmt: skip

#: The bottle's outline: a wide shoulder, a short neck under the cap, a round foot.
_BODY = "M124,186 Q124,152 160,142 L160,128 L240,128 L240,142 Q276,152 276,186 L276,346 A76,17 0 0 1 124,346 Z"
#: The wrapped label: its left and right edges, its top, its height and its band's height.
_LEFT, _RIGHT, _TOP, _HEIGHT, _BAND = 130, 270, 196, 128, 30


def band_colour(nutrient: str) -> str:
    """The label band's colour for ``nutrient``: one of :data:`BANDS`, by a stable hash."""
    return BANDS[zlib.crc32(nutrient.lower().encode()) % len(BANDS)]


def _wrapped(top: float, height: float) -> str:
    """A strip of the label from ``top`` down ``height``, its edges arcs of the bottle's rim."""
    rx, ry = _rim(76)
    return (
        f"M{_LEFT},{top:g} A{rx:g},{ry:g} 0 0 0 {_RIGHT},{top:g} "
        f"L{_RIGHT},{top + height:g} A{rx:g},{ry:g} 0 0 1 {_LEFT},{top + height:g} Z"
    )


def _glyph(form: str, cx: float, cy: float, colour: str) -> str:
    """A scored tablet for ``Tablets``, a two-tone capsule for ``Capsules``, else nothing."""
    kind = form.strip().lower()
    if kind.startswith("tablet"):
        return (
            f'<g class="tablet">'
            f'<ellipse cx="{cx:g}" cy="{cy + 3:g}" rx="14" ry="9" fill="#e4e4e0" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="14" ry="9" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<path d="M{cx - 8:g},{cy:g} L{cx + 8:g},{cy:g}" stroke="{INK}" stroke-width="1"/>'
            "</g>"
        )
    if kind.startswith("capsule"):
        left = f"M{cx:g},{cy - 8:g} L{cx - 10:g},{cy - 8:g} A8,8 0 0 0 {cx - 10:g},{cy + 8:g} L{cx:g},{cy + 8:g} Z"
        right = f"M{cx:g},{cy - 8:g} L{cx + 10:g},{cy - 8:g} A8,8 0 0 1 {cx + 10:g},{cy + 8:g} L{cx:g},{cy + 8:g} Z"
        return (
            f'<g class="capsule" transform="rotate(-30 {cx:g} {cy:g})">'
            f'<path d="{left}" fill="{colour}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            f'<path d="{right}" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            "</g>"
        )
    return ""


def supplement_bottle(
    paint: str, fill: Fill, label: str | None, nutrient: str = "", form: str = ""
) -> list[str]:
    """A capped supplement bottle: the nutrient's band and name and the form's glyph on its label."""
    name = nutrient or label or ""
    colour = band_colour(name)
    _rx, ry = _rim(76)
    sag = ry * (1 - (1 - ((_RIGHT - _LEFT) / 2 / 76) ** 2) ** 0.5)
    word_y = _TOP + _BAND + sag + 26
    glyph_y = word_y + 36
    ridges = " ".join(f"M{x},86 L{x},124" for x in range(160, 248, 10))
    return [
        f'<path class="bottle" d="{_BODY}" fill="{paint}" stroke="{INK}" stroke-width="{LW}" stroke-linejoin="round"/>',
        _highlight("M134,190 Q136,164 158,152", 5, 0.5),
        f'<rect class="cap" x="148" y="80" width="104" height="50" rx="6" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _line(ridges, 1.0, ' stroke-opacity=".5"'),
        f'<path class="label" d="{_wrapped(_TOP, _HEIGHT)}" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<path class="band" d="{_wrapped(_TOP, _BAND)}" fill="{colour}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _word(name, 200, word_y, _RIGHT - _LEFT - 16, 26) if name else "",
        _glyph(form, 174, glyph_y, colour),
        _word(form, 228, glyph_y, 64, 13, "#5a5f66") if form else "",
    ]


register({"supplement_bottle": supplement_bottle})
