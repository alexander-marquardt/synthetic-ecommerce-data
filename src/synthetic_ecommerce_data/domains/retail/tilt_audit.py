"""The build report's tilt audit (#1101): a stub that audits nothing, until the next commit."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

#: How many of the largest turned products the report lists.
LARGEST = 20


def audit(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """The tilt section of the build report over product ``records``: empty in this stub."""
    return {"products": 0, "turned": 0, "per_category": {}, "largest_turned": [], "refused": []}


def refusals(section: dict[str, Any]) -> list[str]:
    """One line per product the audit ``section`` refuses: none in this stub."""
    return []
