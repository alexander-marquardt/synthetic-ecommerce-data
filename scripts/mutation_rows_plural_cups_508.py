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
        '"Balcony Bikini Top with Padded Cups", _WF, "Balcony", "Yes",',
        '"Balcony Bikini Top with Padded Cups", _WF, "Balcony", "No",',
        f"{_T} -k states_them_as_an_attribute",
        "a bikini top titled with padded cups has padded Yes",
    ),
    (
        "the bra title drops the plural cups",
        "variants.py",
        '        return f"{self.line} {wire} {self.kind} Bra with {self.plural_cups}"',
        '        return f"{self.line} {wire} {self.kind} Bra"',
        (f"{_T} -k twenty_titles", f"{_T} -k floor_of_titles"),
        "about 20 titles carry the plural, and each type the issue names has a floor",
    ),
]

PREFIX = "plural cups"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
