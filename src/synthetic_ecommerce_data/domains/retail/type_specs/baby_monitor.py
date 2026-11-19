"""Baby Monitors (gen#965, slice 3): Kids > Baby > Safety > Baby Monitors.

A breadth type: ``derivable`` True, so the scaled build draws more baby monitors from these seven
by the values their titles show (the feature and the type: audio, video or smart). Every feature
suits every type, and a description's words after the feature and the type suit any of them,
because a derived style swaps those two words and keeps the rest. The SKU is a color, which the
casing takes; the type draws the monitor (:func:`kit_baby_gear.baby_monitor`):
a handset with a speaker grille and a sound light bar beside a small baby unit, a parent screen
beside a camera on a stand, or a phone app beside a Wi-Fi camera.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    BLACK,
    BLUE,
    CALDERBY,
    DEPARTMENT,
    FENWOLD,
    GREEN,
    GREY,
    LANTERNBY,
    LITTLE_FERNBY,
    MIREFIELD,
    MONITORS,
    PINK,
    RED,
    THISTLE,
    WHITE,
    YELLOW,
    article,
    decoy,
    gear_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _monitor(feature: str, kind: str) -> tuple[tuple, ...]:
    return (a("feature", "Feature", feature), a("monitor_type", "Monitor type", kind))


def _drawn(kind: str) -> tuple[tuple[str, str], ...]:
    return (("monitor_type", kind.lower()),)


def _row(code: str, feature: str, kind: str, brand: str, price: float, colors: tuple, rest: str):
    return gear_row(code, f"{feature} {kind} Baby Monitor", brand, MONITORS, "Baby Monitor", "baby_monitor",
                    f"{article(feature)} {feature.lower()} {kind.lower()} baby monitor with {rest}",
                    _monitor(feature, kind), price, _drawn(kind), colors)  # fmt: skip


ROWS = (
    _row("BMNLRA", "Long Range", "Audio", FENWOLD, 39.0, (WHITE, GREY, BLUE),
         "an alert when the baby cries, heard from the next room or the garden."),
    _row("BMNTTA", "Two-Way Talk", "Audio", LITTLE_FERNBY, 49.0, (WHITE, GREEN, YELLOW),
         "a soft glow on the nursery unit for night feeds."),
    _row("BMNRCV", "Rechargeable", "Video", FENWOLD, 119.0, (WHITE, BLACK, GREY),
         "a low-energy mode that wakes only when the room grows loud."),
    _row("BMNSAV", "Sound-Activated", "Video", CALDERBY, 149.0, (WHITE, BLUE, RED),
         "a private, encrypted link, so no neighbour hears the nursery."),
    _row("BMNNLV", "Night Light", "Video", THISTLE, 169.0, (WHITE, GREY, PINK),
         "a wall bracket and a long cable for the nursery unit."),
    _row("BMNRTS", "Room Temperature", "Smart", MIREFIELD, 179.0, (WHITE, GREEN, BLACK),
         "an alert when the nursery grows too warm or too cold."),
    _row("BMNLLS", "Lullaby", "Smart", LANTERNBY, 199.0, (WHITE, YELLOW, RED),
         "a set-up that takes minutes and a link that holds through the night."),
)  # fmt: skip

SPEC = TypeSpec(
    key="baby_monitor",
    department=DEPARTMENT,
    product_type="Baby Monitor",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "crib", "category", decoy(ROWS[2], "BMNCRM", "Rechargeable Video Baby Monitor with Crib Mount",
              "A rechargeable video baby monitor with a clamp that fixes its camera to a crib rail: the crib is sold separately.")),
        Decoy(6, "red baby monitor", "generic", decoy(ROWS[0], "BMNRRB", "Red Robin Long Range Audio Baby Monitor",
              "From the Red Robin range: a white long range audio baby monitor that alerts you when the baby cries.", (WHITE,))),
    ),
)  # fmt: skip
