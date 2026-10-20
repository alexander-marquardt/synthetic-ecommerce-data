"""Mutation rows for the titles that carry the plural "cups" (gen#508), kept out of
``mutation_check.py``. Each row plants one defect on a changed line and names the test that must go
red. ``mutation_check.py`` finds this file by glob and names its rows ``plural cups: ...``
(``--only "plural cups:"`` re-runs them). A row is ``(name, file, old, new, tests, property)``;
the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_plural_cups_508.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "the derivation copies the plural-cups rows as styles",
        "scale.py",
        "| NEEDS_IDS | CUPS_PLURAL_IDS\n",
        "| NEEDS_IDS\n",
        f"{_T} -k leaves_out",
        "the plural-cups rows stay templates",
    ),
    (
        "a title that says Removable Cups no longer states the padding",
        "facet_leaves.py",
        'STATED_ONLY: dict[str, tuple[str, ...]] = {"padding": ("Removable Cups",)}',
        "STATED_ONLY: dict[str, tuple[str, ...]] = {}",
        (f"{_T} -k title_words_removable_cups", f"{_T} -k states_them_as_an_attribute"),
        "a bra titled with removable cups carries the padding value Removable Cups",
    ),
    (
        "a title that says Removable Straps states the removable cups",
        "facet_leaves.py",
        'STATED_ONLY: dict[str, tuple[str, ...]] = {"padding": ("Removable Cups",)}',
        'STATED_ONLY: dict[str, tuple[str, ...]] = {"padding": ("Removable",)}',
        f"{_T} -k does_not_state_them",
        "only the whole phrase Removable Cups states the padding value",
    ),
    (
        "a swimsuit titled with padded cups states padded No",
        "swimwear_rows.py",
        '"Plunge Swimsuit with Padded Cups", _TW, "Plunge", "No", "Yes",',
        '"Plunge Swimsuit with Padded Cups", _TW, "Plunge", "No", "No",',
        f"{_T} -k states_them_as_an_attribute",
        "a swimsuit titled with padded cups has padded Yes",
    ),
    (
        "a bikini top titled with padded cups states padded No",
        "swimwear_rows.py",
        '"Triangle Bikini Top with Padded Cups", _TW, "Triangle", "Yes",',
        '"Triangle Bikini Top with Padded Cups", _TW, "Triangle", "No",',
        f"{_T} -k states_them_as_an_attribute",
        "a bikini top titled with padded cups has padded Yes",
    ),
    (
        "a bralette description names an espresso cup",
        "cups_plural_rows.py",
        '"A satin bralette with removable cups and thin adjustable straps."',
        '"A satin bralette with removable espresso cups and thin adjustable straps."',
        f"{_T} -k names_drinkware",
        "no lingerie row names drinkware, so mugs and espresso cups still lead with drinkware",
    ),
    (
        "the bras move out of Lingerie",
        "cups_plural_rows.py",
        'BRAS = ("Womens", "Lingerie", "Bras")',
        'BRAS = ("Womens", "Home", "Bras")',
        f"{_T} -k lingerie_or_swimwear",
        "every title with cups is under Lingerie or Swimwear",
    ),
    (
        "the bras keep nine decoys per class after the plural-cups bras joined",
        "decoy_apparel.py",
        'Spec("Bra", "b", 10),',
        'Spec("Bra", "b", 9),',
        "tests/test_retail_apparel_decoys_311.py -k ten_percent",
        "the bras still hold a tenth of their size in text-match decoys",
    ),
    (
        "the module adds only its first eight styles",
        "cups_plural_rows.py",
        "return [s.doc() for s in STYLES]",
        "return [s.doc() for s in STYLES[:8]]",
        (f"{_T} -k twenty_titles", f"{_T} -k floor_of_titles"),
        "about 20 titles carry the plural, and each type the issue names has a floor",
    ),
]

PREFIX = "plural cups"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
