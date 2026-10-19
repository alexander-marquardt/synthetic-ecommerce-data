"""Mutation rows for the sale share of every people department (gen#359), kept out of
``mutation_check.py``.

Each row undoes one part of ``sale_share.py`` or its call sites and names the test that must go
red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``sale share: ...``
(``--only "sale share:"`` re-runs them). A row is ``(name, file, old, new, test, property)``; the
root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_SHARE = "tests/test_retail_sale_share_359.py"
_DEPT = f"{_SHARE} -k test_each_department_has_a_few_hundred_reduced_skus_across_three_types"
_MARKED = f"{_SHARE} -k test_a_reduced_document_is_marked_the_same_way_whoever_made_it"
_MARKED_PROP = "a discount goes with a was-price and with nothing else"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "Baby takes a share too small to reach a few hundred reduced SKUs",
        "sale_share.py",
        '"Baby": 0.25',
        '"Baby": 0.05',
        _DEPT,
        "each of Womens, Mens, Kids and Baby holds at least 300 reduced SKUs",
    ),
    (
        "a derived style is never reduced",
        "scale.py",
        "    sale_share.apply(out)  # a share of every people department is reduced (gen#359)\n",
        "",
        f"{_SHARE} -k test_derived_styles_are_reduced_too_not_only_the_authored_ones",
        "a share of the derived styles is reduced as well as the authored ones",
    ),
    (
        "a derived copy keeps its template's discount without its was-price",
        "scale.py",
        'rec.pop("discount_pct", None)',
        'rec.get("discount_pct")',
        _MARKED,
        _MARKED_PROP,
    ),
    (
        "a reduced skirt row states no discount",
        "lowerbody_rows.py",
        'out["discount_pct"] = round(100 * (out["was_price"] - cheapest) / out["was_price"])',
        'out.pop("discount_pct", None)',
        _MARKED,
        _MARKED_PROP,
    ),
    (
        "a petite style may be reduced (the size range and the text guards both gone)",
        "sale_share.py",
        '        and "petite" not in rec.get("size_range", ())\n        and "petite" not in text\n',
        "",
        f"{_SHARE} -k test_a_petite_style_is_never_in_the_share_a_regular_one_may_be",
        "petite stays a pair only a policy may honour: a petite style is not eligible",
    ),
]


PREFIX = "sale share"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
