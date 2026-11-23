"""Game consoles (gen#1120): Electronics > Gaming > Consoles.

The invented console families the video games are sold for (``type_specs/video_game.py``
names them as platforms), one console maker each, so the game controllers of gen#956 have a
console to sit next to. Each console states its ``platform`` (its family) and its
``console_form``, which :func:`kit_gaming.game_console` draws: a home box, a slim box or a
handheld. Each comes in the six main colors. The rows are templates only (``derivable``
False): a console range is a handful of models, not a breadth type.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ELECTRONICS_OWNERS,
    PELLIMAR,
    QUORRIN,
    TORVANE,
)
from synthetic_ecommerce_data.domains.retail.gaming_rows import BLACK, ROOT, WHITE, decoy, row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a
from synthetic_ecommerce_data.domains.retail.type_specs.video_game import CONSOLE_FAMILIES

DEPARTMENT = "Electronics"
PATH = (ROOT, "Gaming", "Consoles")
KESTARA, LUMIVO, DROVIK = CONSOLE_FAMILIES


def _gcn(code: str, title: str, brand: str, price: float, description: str, family: str,
         form: str) -> object:  # fmt: skip
    attrs = (a("platform", "Platform", family), a("console_form", "Console form", form))
    return row(code, title, brand, PATH, "Game Console", "game_console", price, description,
               attrs, (("console_form", form.lower()),))  # fmt: skip


ROWS = (
    _gcn("GCN001", "Kestara Console", QUORRIN, 449.0, "A home console with a disc drive and 1 TB of storage, for Kestara games in 4K.", KESTARA, "Home"),
    _gcn("GCN002", "Kestara Slim Console", QUORRIN, 379.0, "The Kestara console in a slimmer case that stands or lies flat, with a disc drive.", KESTARA, "Slim"),
    _gcn("GCN003", "Lumivo Console", PELLIMAR, 399.0, "A quiet home console with a disc drive that plays every Lumivo game.", LUMIVO, "Home"),
    _gcn("GCN004", "Lumivo Handheld Console", PELLIMAR, 249.0, "A handheld with a seven inch screen and built-in controls that plays Lumivo games anywhere.", LUMIVO, "Handheld"),
    _gcn("GCN005", "Drovik Console", TORVANE, 429.0, "A home console with a disc drive and a fast-loading drive for Drovik games.", DROVIK, "Home"),
)  # fmt: skip

SPEC = TypeSpec(
    key="game_console",
    department=DEPARTMENT,
    product_type="Game Console",
    derivable=False,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red game console", "vocabulary", decoy(ROWS[0], "GCNRDT", "Kestara Console with Red Trim",
              "A black home console whose front trim is picked out in red.", BLACK)),
        Decoy(6, "green game console", "generic", decoy(ROWS[2], "GCNGHB", "Lumivo Console Green Hollow Bundle",
              "The Green Hollow bundle: a Lumivo console in white with a second controller.", WHITE)),
    ),
)  # fmt: skip
