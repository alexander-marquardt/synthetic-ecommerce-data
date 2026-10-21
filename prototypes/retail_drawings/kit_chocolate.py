"""The chocolate selection box (gen#609).

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
chocolate_box   a flat, wide, shallow lidded box seen at a slight     --
                angle, a ribbon across the lid
==============  ===================================================  ======
"""

from __future__ import annotations

from kit import Fill, box, register


def chocolate_box(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Stub: the generic carton, until the flat box is drawn."""
    return box(paint, fill, label)


register({"chocolate_box": chocolate_box})
