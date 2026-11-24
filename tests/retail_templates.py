"""The retail templates, read once per worker for every test file that needs them (#1035)."""

from __future__ import annotations

import functools

from synthetic_ecommerce_data.domains.retail import scale

#: ``scale.templates`` as the module defines it, held before a test monkeypatches it.
_TEMPLATES = scale.templates


@functools.cache
def templates() -> list[dict]:
    """``scale.templates()``, made once per process (#1035).

    A call takes 6 to 9 s, and ``tests/test_retail_ceiling_forms_237.py`` and
    ``tests/test_retail_scale.py`` made it in each test, most of their time. Every caller shares
    one list, as the ceiling build is shared: a test reads it and never edits it (copy a template
    before changing it). It calls the module's own function, so a test that monkeypatches
    ``scale.templates`` neither fills nor reads this cache with its replacement.
    """
    return _TEMPLATES()
