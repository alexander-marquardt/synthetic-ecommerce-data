"""The Barry Plotter book series (gen#1119, slice 2): data only.

Barry Plotter (:mod:`barry_plotter`) is an invented book-and-film series, and its merchandise is
licensed from the films. These are the books: seven numbered volumes, each in the three formats of
:mod:`books_rows`, a box set of the seven in paperback and in hardback, and an illustrated hardback
of book 1. That is 24 SKUs of the Book type, in ``Books > Children's Books``.

A volume's title is the series, its number and one of the range's motifs, in our own words:
``Barry Plotter, Book 3: The Moonlit Glasshouse``. No title follows a real series' pattern. The
name is in the title and the description only (``barry_plotter.structured_names``), no description
says "Barry's", and each says "the Barry Plotter books" where the merchandise says "from the Barry
Plotter films". A cover prints its motif's badge (:mod:`kit_books`) and no licence line: the books
are what the films were made from. The author and the publisher are invented and sell nothing else.

The rows are not among ``barry_plotter.ROWS``, so the merchandise's counts, sale and emblem rules
are unchanged.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import functools

from synthetic_ecommerce_data.domains.retail import barry_plotter, books_rows
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.type_registry import a, count

PUBLISHER = "Trowelgate Books"
AUTHOR = "Winifred Tansley"
OWNERS = ((PUBLISHER, "third_party"),)

#: What every description calls the series.
OF = f"the {barry_plotter.NAME} books"
PATH = books_rows.CHILDRENS.path
AGE_BAND = "9-12 years"
_ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh")

#: Each volume, in order: its motif, pages, publication year, and ebook, paperback and hardback
#: prices. Its cover color is the one at its index in :data:`books_rows.COVERS`.
VOLUMES: tuple[tuple[str, int, int, tuple[float, float, float]], ...] = (
    ("Enchanted Allotment", 240, 2016, (3.99, 6.99, 12.99)),
    ("Talking Scarecrow", 264, 2017, (3.99, 6.99, 12.99)),
    ("Moonlit Glasshouse", 296, 2018, (4.99, 7.99, 13.99)),
    ("Compost Dragon", 328, 2019, (4.99, 7.99, 13.99)),
    ("Clockwork Mole", 344, 2020, (4.99, 7.99, 14.99)),
    ("Whispering Bramble", 368, 2021, (5.99, 8.99, 14.99)),
    ("Frost Fairy", 400, 2022, (5.99, 8.99, 15.99)),
)
#: The motif whose badge the box set prints.
BOX_MOTIF = VOLUMES[0][0]


def _row(code: str, title: str, says: str, motif: str, pages: int, year: int,
         sizes: tuple[tuple[str, float], ...], cover: int, shape: str,
         params: tuple[tuple[str, str], ...] = ()) -> Row:  # fmt: skip
    attrs = (
        a("author", "Author", AUTHOR), a("publisher", "Publisher", PUBLISHER),
        a("genre", "Genre", books_rows.CHILDRENS.genre), count("pages", "Pages", pages),
        a("publication_year", "Publication year", str(year)), a("age_band", "Age band", AGE_BAND),
    )  # fmt: skip
    return Row(
        code, title, PUBLISHER, books_rows.DEPARTMENT, PATH, books_rows.PRODUCT_TYPE, sizes[0][1],
        shape, f"{says} Written by {AUTHOR}.", (books_rows.COVERS[cover],), attrs, sizes,
        colorless=True, size_key="format", params=(*params, ("motif", motif)),
    )  # fmt: skip


def _volume_title(n: int) -> str:
    return f"{barry_plotter.NAME}, Book {n}: The {VOLUMES[n - 1][0]}"


def _rows() -> tuple[Row, ...]:
    out = []
    for i, (motif, pages, year, prices) in enumerate(VOLUMES):
        says = f"The {_ORDINALS[i]} of {OF}, a story about {barry_plotter.MOTIFS[motif]}."
        sizes = tuple(zip(books_rows.FORMATS, prices, strict=True))
        out.append(_row(f"BYPBK{i + 1:02d}", _volume_title(i + 1), says, motif, pages, year, sizes,
                        i, books_rows.SHAPE, (("layout", "2"),)))  # fmt: skip
    out.append(_row(
        "BYPBK08", f"{barry_plotter.NAME} Box Set, Books 1 to 7",
        f"All seven of {OF} in one slipcase, from the first day on the enchanted allotment to the last frost.",
        BOX_MOTIF, sum(v[1] for v in VOLUMES), 2023,
        (("Paperback", 44.99), ("Hardback", 79.99)), 4, "book_box_set",
    ))  # fmt: skip
    out.append(_row(
        "BYPBK09", f"{_volume_title(1)}, Illustrated Edition",
        f"The first of {OF} in a large illustrated edition, with a color picture in every chapter.",
        VOLUMES[0][0], 256, 2024, (("Hardback", 24.99),), 3, books_rows.SHAPE, (("layout", "4"),),
    ))  # fmt: skip
    return tuple(out)


ROWS: tuple[Row, ...] = _rows()


@functools.cache
def ids() -> frozenset[str]:
    """Every product id of the series."""
    return frozenset(r.product_id for r in ROWS)
