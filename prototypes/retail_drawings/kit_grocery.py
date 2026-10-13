"""Pack shapes the grocery build draws that the kit lacked (gen#154).

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
bar             a wrapped bar: crimped ends, the wrapper torn back    --
                at one corner to show the segments
bag             a stand-up bag: a zip seal across the top, a          --
                rounded gusset at the foot
butter_block    a foil-wrapped block of butter, the foil folded       --
                at the end and peeled back to show the butter
lidded_tub      a tapering tub with a snap-on lid and a thumb         --
                tab (ice cream, a spread)
steak_tray      a black tray under film holding one cut of meat:      --
                a fat rim, marbling and a label on the tray (a steak)
==============  ===================================================  ======

Each paints the record's fill on the pack's main surface and carries the product
word on a white label panel, as the kit's other packs do (``kit.box``, ``kit.jar``).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, Fill, _line, _mix, _panel, _path, register


def bar(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A wrapped bar, the wrapper peeled back at the top right to show the segments."""
    crimp_l = " ".join(f"L{52 if i % 2 else 60},{132 + i * 12}" for i in range(12))
    crimp_r = " ".join(f"L{348 if i % 2 else 340},{264 - i * 12}" for i in range(12))
    body = "M60,132 L300,132 L340,170 L340,276 L60,276 Z"
    segment = _mix(fill.base, "#3b2416", 0.75)
    return [
        _path(f"M60,128 {crimp_l} L60,280 Z", paint, 1.6),
        _path(f"M340,166 {crimp_r} L340,280 Z", paint, 1.6),
        _path(body, paint),
        _path("M300,132 L340,132 L340,170 Z", segment),
        _line("M306,140 L332,140 M318,132 L318,162", 1.2, ' stroke-opacity=".6"'),
        _path("M300,132 L340,170 L318,176 Z", _mix(fill.base, "#ffffff", 0.35), 1.6),
        *_panel(110, 172, 180, 64, label, 40),
    ]


def bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A stand-up bag with a zip seal and a rounded gusset."""
    return [
        _path("M112,70 L288,70 L300,330 Q300,352 278,352 L122,352 Q100,352 100,330 Z", paint),
        _line("M110,98 L290,98", 2.4),
        _line("M110,106 L290,106", 1.0, ' stroke-dasharray="4 4"'),
        _line("M104,316 Q200,300 296,316", 1.4, ' stroke-opacity=".6"'),
        *_panel(122, 160, 156, 96, label, 44),
    ]


def butter_block(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A foil-wrapped butter block, seen from above-left, the foil peeled back at one end."""
    return [
        _path("M70,196 L130,150 L350,150 L290,196 Z", _mix(fill.base, "#ffffff", 0.45)),
        _path("M290,196 L350,150 L350,262 L290,310 Z", _mix(fill.base, "#000000", 0.2)),
        _path("M70,196 L290,196 L290,310 L70,310 Z", paint),
        _line("M290,226 L350,182 M290,262 L350,218", 1.2, ' stroke-opacity=".55"'),
        _line("M80,204 L282,204", 1.2, ' stroke-opacity=".5"'),
        _path("M70,196 L130,150 L150,170 L96,206 Z", "#f6dc7a", 1.6),
        _line("M94,300 L270,300", 1.4, ' stroke-opacity=".5"'),
        *_panel(84, 214, 190, 80, label, 44),
    ]


def lidded_tub(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tapering tub with a snap-on lid, its rim and a thumb tab."""
    lid = _mix(fill.base, "#ffffff", 0.7)
    return [
        _path("M116,156 L284,156 L266,350 Q200,364 134,350 Z", paint),
        f'<rect x="104" y="118" width="192" height="42" rx="12" fill="{lid}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M116,132 L284,132", 1.2, ' stroke-opacity=".5"'),
        _path("M284,136 L312,142 L312,152 L284,150 Z", lid, 1.6),
        *_panel(128, 186, 144, 106, label, 48),
    ]


def steak_tray(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A black tray under film holding one steak: its fat rim, marbling and a label panel.

    The meat is the record's fill; the rim is a lighter tone of it and the marbling a pale
    streak, so a sirloin, a ribeye and a minute steak differ by color and by their label."""
    fat = _mix(fill.base, "#fff4e6", 0.7)
    meat = "M92,246 C88,214 138,198 192,202 C250,196 312,210 310,248 C308,284 252,298 196,294 C140,296 96,282 92,246 Z"
    return [
        _path("M52,190 L348,190 L328,326 L72,326 Z", "#3a3d42"),
        f'<rect x="38" y="156" width="324" height="44" rx="14" fill="{_mix("#3a3d42", "#ffffff", 0.25)}" stroke="{INK}" stroke-width="{LW}"/>',
        _path("M62,206 L338,206 L324,316 L76,316 Z", _mix("#f4efe6", "#ffffff", 0.4), 1.4),
        _path(meat, fat, extra=' class="steak"'),
        _path("M104,246 C102,222 142,210 192,214 C246,208 298,220 296,248 C294,276 248,286 196,282 C146,284 106,272 104,246 Z", paint, 1.4, ' class="lean"'),
        _line("M134,238 Q160,226 188,236 M214,230 Q246,222 272,238 M150,262 Q184,252 214,262 M232,258 Q256,252 276,262", 2.2, ' stroke-opacity=".55"', _mix(fill.base, "#fff4e6", 0.8)),
        _line("M72,170 L340,170", 1.2, ' stroke-opacity=".5"', "#ffffff"),
        *_panel(206, 268, 130, 46, label, 30),
    ]


register({"bar": bar, "bag": bag, "butter_block": butter_block, "lidded_tub": lidded_tub,
          "steak_tray": steak_tray})
