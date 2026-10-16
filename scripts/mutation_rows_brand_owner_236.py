"""Mutation rows for the one-owner-per-brand rule (gen#236), kept out of ``mutation_check.py``.

Each row gives a grocery brand a second owner again (the owners table says one thing, the
class table another, or a derived style takes the default) and names the test that must go
red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``brand owner: ...``
(``--only "brand owner:"`` re-runs them). A row is ``(name, file, old, new, test, property)``;
the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

_TEST = (
    "tests/test_retail_scale.py "
    "-k test_every_brand_has_exactly_one_owner_across_the_templates_and_the_ceiling"
)
_PROP = "a brand holds one owner across the templates and the ceiling build"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        f"the grocery table calls {brand} own while the class table calls it third party",
        "grocery_rows.py",
        f'"{brand}": "third_party"',
        f'"{brand}": "own"',
        _TEST,
        _PROP,
    )
    for brand in (
        "Crofter's Bakehouse", "Goldfield Farms", "Copper Hill Preserves", "Velling Apothecary",
    )
] + [
    (
        "a derived style takes the third-party default for a grocery brand's owner",
        "scale.py",
        'owners = {r["brand"]: r["brand_owner"] for r in tpls if "brand_owner" in r}',
        'owners = {r["brand"]: r["brand_owner"] for r in base if "brand_owner" in r}',
        _TEST,
        _PROP,
    ),
]
