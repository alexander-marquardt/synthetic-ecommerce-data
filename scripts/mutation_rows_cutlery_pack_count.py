"""Mutation rows for the cutlery pack count (gen#228), kept out of ``mutation_check.py``.

Each row plants one defect in how a cutlery style's image shows a pack count and names the test
that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``cutlery pack count: ...`` (``--only "cutlery pack count:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a cutlery row draws four pieces for every pack size",
        "tableware_rows.py",
        'return (("piece", piece.lower()), ("handle", handle.lower()))',
        'return (("piece", piece.lower()), ("handle", handle.lower()), ("count", "4"))',
        'tests/test_retail_cutlery_pack_count_228.py -k "draws_no_count"',
        "a style's image shows no count that one of its pack sizes does not sell",
        "prototypes/retail_drawings",
    ),
    (
        "a cutlery row draws four pieces for every pack size, rendered",
        "tableware_rows.py",
        'return (("piece", piece.lower()), ("handle", handle.lower()))',
        'return (("piece", piece.lower()), ("handle", handle.lower()), ("count", "4"))',
        'tests/test_retail_cutlery_pack_count_228.py -k "renders_one_piece"',
        "a multi-pack cutlery style renders one piece",
        "prototypes/retail_drawings",
    ),
    (
        "a cutlery piece with no count fans four",
        "kit_tableware.py",
        'handle: str = "plain", count: str = "1",',
        'handle: str = "plain", count: str = "4",',
        'tests/test_retail_cutlery_pack_count_228.py -k "renders_one_piece"',
        "no count means one piece drawn",
        "prototypes/retail_drawings",
    ),
]
