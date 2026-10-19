"""Mutation rows for the ring size keys (gen#249), kept out of ``mutation_check.py``.

Each row plants one defect in a place that names a ring's size keys and names the tests that must
go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``ring sizes: ...``
(``--only "ring sizes:"`` re-runs them). A row is ``(name, file, old, new, tests, property)``;
the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_ring_size_keys_249.py"

ROWS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    (
        "a ring's UK size goes back under the garment key",
        "accessory_rows.py",
        '(("kind", "band"),), _rs(*_L4, base=10.0), "ring_size_uk", _rx(*_L4)),',
        '(("kind", "band"),), _rs(*_L4, base=10.0), "size_uk", _rx(*_L4)),',
        (f"{_T} -k a_ring_sku_states", f"{_T} -k a_ring_export_carries",
         f"{_T} -k never_hold_a_ring_letter"),
        "a ring's UK letter is never under size_uk",
    ),
    (
        "a ring's US size goes back under the garment key",
        "accessory_rows.py",
        'return tuple((s, (("ring_size_us", _US[s]),)) for s in letters)',
        'return tuple((s, (("size_us", _US[s]),)) for s in letters)',
        (f"{_T} -k a_ring_sku_states", f"{_T} -k a_ring_export_carries"),
        "a ring's US number is never under size_us",
    ),
    (
        "the ring UK key is shown with a garment name",
        "export.py",
        '"ring_size_uk": ("ring_size_uk", "Ring size (UK)", None),',
        '"ring_size_uk": ("ring_size_uk", "Size (UK)", None),',
        f"{_T} -k named_for_a_ring",
        "the ring keys carry the ring names",
    ),
    (
        "the ring US key is exported as the garment key",
        "export.py",
        '"ring_size_us": ("ring_size_us", "Ring size (US)", None),',
        '"ring_size_us": ("size_us", "Ring size (US)", None),',
        (f"{_T} -k a_ring_export_carries", f"{_T} -k named_for_a_ring"),
        "the ring option is exported under the ring key",
    ),
    (
        "the ring keys leave the size options",
        "variants.py",
        '"size_us", "ring_size_uk", "ring_size_us", "length",',
        '"size_us", "length",',
        f"{_T} -k size_options_are_listed",
        "a ring's size_options hold the ring keys",
    ),
    (
        "a shoe states a ring key",
        "footwear_rows.py",
        'row |= {"size_uk": uk, "size_eu": eu,',
        'row |= {"ring_size_uk": uk, "size_uk": uk, "size_eu": eu,',
        f"{_T} -k held_by_rings_alone",
        "only a ring states a ring key",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "ring sizes"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
