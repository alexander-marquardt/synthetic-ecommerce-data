"""Mutation rows for the one ``pack_size`` vocabulary (gen#246), kept out of ``mutation_check.py``.

Each row puts one old spelling back ("Set of 4", a bare digit) or breaks the count, and names the
test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``pack size:
...`` (``--only "pack size:"`` re-runs them). A row is ``(name, file, old, new, test, property)``;
every file is under ``prototypes/retail_drawings``.
"""

from __future__ import annotations

_VOCAB = "tests/test_pack_size_values_246.py -k one_vocabulary_or_a_measure"
_USE = "tests/test_pack_size_values_246.py -k all_use"
_UNITS = "tests/test_pack_size_values_246.py -k units_per_pack"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "tableware packs are 'Set of N' again",
        "tableware_rows.py",
        'f"{n} pack", p) for n, p in pairs',
        'f"Set of {n}", p) for n, p in pairs',
        _VOCAB,
        "a tableware pack is 'N pack', as underwear's is",
    ),
    (
        "a dining chair set is 'Set of N' again",
        "furniture_rows.py",
        'f"{n} pack", price, (("units_per_pack", n),)',
        'f"Set of {n}", price, (("units_per_pack", n),)',
        _VOCAB,
        "a chair pack is 'N pack', as underwear's is",
    ),
    (
        "the lemons' pack is a bare digit again",
        "distractors.py",
        'f"{LEMON_PACK} pack")',
        "str(LEMON_PACK))",
        _USE,
        "a count pack is 'N pack', never a bare digit",
    ),
    (
        "the oranges' pack is a bare digit again",
        "distractors.py",
        'f"{ORANGE_PACK} pack")',
        "str(ORANGE_PACK))",
        _VOCAB,
        "a count pack is 'N pack', never a bare digit",
    ),
    (
        "the jeans hanger's pack is a bare digit again",
        "distractors.py",
        '("pack_size", "Pack size", "5 pack")',
        '("pack_size", "Pack size", "5")',
        _VOCAB,
        "a distractor's pack is 'N pack', never a bare digit",
    ),
    (
        "the hanger decoy's pack is a bare digit again",
        "decoy_rows.py",
        '("pack_size", "Pack size", "10 pack")',
        '("pack_size", "Pack size", "10")',
        _USE,
        "a decoy's pack is 'N pack', never a bare digit",
    ),
    (
        "a chair pack is labelled one more than it holds",
        "furniture_rows.py",
        'f"{n} pack", price, (("units_per_pack", n),)',
        'f"{n + 1} pack", price, (("units_per_pack", n),)',
        _UNITS,
        "a pack label states the SKU's units_per_pack",
    ),
]
