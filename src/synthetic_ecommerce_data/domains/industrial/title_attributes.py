"""Which attributes an industrial title names, per product type, and how it abbreviates each
(#937)."""

from __future__ import annotations

#: A product type's title attributes, in title order: the attribute's full name beside the
#: abbreviation the title writes after its value.
TITLE_ATTRIBUTES: dict[str, tuple[tuple[str, str | None], ...]] = {}
