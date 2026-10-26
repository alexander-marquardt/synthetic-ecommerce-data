"""A brand's type treatment: font, weight, case, spacing (#412). Stub for the red commit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Family:
    """One of the four wordmark families."""

    stack: str
    cap_height: float


FAMILIES: dict[str, Family] = {
    "sans": Family("Helvetica, Arial, sans-serif", 0.716),
    "serif": Family("Georgia, 'Times New Roman', serif", 0.692),
    "mono": Family("'Courier New', Courier, monospace", 0.571),
    "humanist": Family("'Trebuchet MS', Verdana, sans-serif", 0.715),
}
