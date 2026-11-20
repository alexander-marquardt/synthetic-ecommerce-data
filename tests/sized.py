"""The authored ``size`` as the retail export writes it (gen#125).

A build row's bare ``size`` is exported under its size system's key (``size_letter``,
``size_age``, ``dimensions``, ...: ``domains/retail/size_systems.py``), so a test asking that
an authored ``size`` reach the export asks that one of those keys does.
"""

from __future__ import annotations

from collections.abc import Set

from synthetic_ecommerce_data.domains.retail import size_systems


def with_size(keys: Set[str]) -> set[str]:
    """*keys*, an export's keys, with the authored ``size`` among them when they hold a key a
    bare ``size`` becomes."""
    return set(keys) | {size_systems.SIZE} if keys & size_systems.KEYS else set(keys)
