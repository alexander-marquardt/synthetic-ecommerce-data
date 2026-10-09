"""Pack shapes the grocery build draws that the kit lacked (gen#154).

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
bar             a wrapped bar: crimped ends, the wrapper torn back    --
                at one corner to show the segments
bag             a stand-up bag: a zip seal across the top, a          --
                rounded gusset at the foot
==============  ===================================================  ======

Each paints the record's fill on the pack's main surface and carries the product
word on a white label panel, as the kit's other packs do (``kit.box``, ``kit.jar``).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import Fill, _line, _mix, _panel, _path, register


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


register({"bar": bar, "bag": bag})
