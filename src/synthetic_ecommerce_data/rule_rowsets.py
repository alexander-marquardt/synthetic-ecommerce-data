"""The row sets of the realism rules that the retail domain does not build (gen#538, #716).

``domains/retail/rules.py`` holds the rules and the retail row sets. ``sentence_case`` and
``one_key_per_concept`` also run over the industrial build's rows, and a domain reaches core only,
never another domain (#125), so those rows are built here, above ``domains/``, and handed in:
``rules.run_all(rule_rowsets.ROWSETS)``. Each row set's minima sit beside its loader.
"""

from __future__ import annotations

import functools

from synthetic_ecommerce_data.domains.retail.rules import Doc, RowSet


@functools.cache
def _industrial() -> tuple[list[Doc], list[Doc]]:
    """The small industrial build, nested and flat, as the exporter writes it."""
    from synthetic_ecommerce_data.core import emit
    from synthetic_ecommerce_data.core.config import SMALL
    from synthetic_ecommerce_data.domains.industrial.generate import generate

    catalog = generate(SMALL)
    return list(emit.iter_nested(catalog)), list(emit.iter_flat(catalog))


ROWSETS: dict[str, RowSet] = {
    "industrial": RowSet(
        lambda: _industrial()[0], {"sentence_case": 400, "one_key_per_concept": 400}
    ),
    "industrial_flat": RowSet(lambda: _industrial()[1], {"sentence_case": 800}),
}
