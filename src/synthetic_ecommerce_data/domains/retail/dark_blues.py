"""The dark blues products are drawn in, one definition each (gen#875).

Every swatch table imports these, so a later tweak is one line. Only drawn pixels read them:
no color name or facet value comes from a hex. This module imports nothing, so a type spec
can read it without importing the registry.
"""

from __future__ import annotations

#: The dark denim washes, darkest first (``variants.WASHES`` keeps this order).
RINSE = "#2b4a80"
DARK_INDIGO = "#32548c"
INDIGO = "#3d5f97"
MID_WASH = "#5578a8"

#: Navy: darker than the main color Blue (``main_color_hex.MAIN_COLORS``), still blue on screen.
NAVY = "#2c477e"
#: The lighter navy of the swimwear, underwear, babywear, trouser and suede shoe tables.
NAVY_LIGHT = "#34508a"
