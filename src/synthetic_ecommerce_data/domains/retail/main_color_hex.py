"""The six main colors and their swatches (gen#275), on their own so a type spec can read them.

:mod:`main_colors` imports the decoy plans, which read the registry of type specs; a spec that
imports a module reading ``MAIN_COLORS`` from there would import the registry while it is being
built. This module imports nothing, and :mod:`main_colors` re-exports the dict (one definition).
"""

from __future__ import annotations

#: The baseline: plain color -> swatch hex (the color word is also the swatch family).
MAIN_COLORS = {
    "Red": "#c8322b", "Blue": "#2f6db5", "Green": "#3c8d4f", "Yellow": "#f2c230",
    "Black": "#2a2a2e", "White": "#ffffff",
}  # fmt: skip
