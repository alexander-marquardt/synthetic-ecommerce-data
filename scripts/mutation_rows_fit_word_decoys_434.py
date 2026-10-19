"""Mutation rows for the class 8 fit and shape word decoys (gen#434, gap 4).

Each row plants one defect in ``decoy_apparel.py`` or ``facet_leaves.py`` and names the test that
must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``fit word decoys: ...``
(``--only "fit word decoys:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_fit_word_decoys_434.py"
_ROOT = "prototypes/retail_drawings"
_D = "decoy_apparel.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a word gets two decoys",
        _D,
        "WORD_DECOYS = 3",
        "WORD_DECOYS = 2",
        f"{_T} -k 'has_three_class_8_decoys'",
        "every value has three class 8 decoys",
        _ROOT,
    ),
    (
        "a decoy is planted on a product that holds the word",
        _D,
        "if _in_path(word, ex) or any(_same_word(word, h) for h in held):",
        "if False:",
        f"{_T} -k 'its_attribute_is_another'",
        "a decoy's attribute is never its word",
        _ROOT,
    ),
    (
        "barrel and balloon are not read as one",
        _D,
        'WORD_SYNONYMS = {"barrel": "balloon"}',
        "WORD_SYNONYMS = {}",
        f"{_T} -k 'its_attribute_is_another'",
        "neither of barrel and balloon is planted on the other",
        _ROOT,
    ),
    (
        "a decoy is no more popular than the rest",
        _D,
        "        sold += 2000\n",
        "        sold += 0\n",
        f"{_T} -k 'top_10 and leg_fit'",
        "the balloon and barrel decoys reach the top 10",
        _ROOT,
    ),
    (
        "a bra reads its line as its shape",
        "facet_leaves.py",
        'return rec["title"].replace(line, " ", 1) if line else rec["title"]',
        'return rec["title"]',
        f"{_T} -k 'its_attribute_is_another'",
        "a bra line named Plunge Lane is not a plunge bra",
        _ROOT,
    ),
    (
        "a cropped fit is planted as a decoy",
        _D,
        '"Skinny", "Super Skinny", "Slim", "Straight",',
        '"Cropped", "Skinny", "Super Skinny", "Slim", "Straight",',
        f"{_T} -k 'its_attribute_is_another'",
        "a jean whose text says cropped is a cropped fit",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "fit word decoys"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
