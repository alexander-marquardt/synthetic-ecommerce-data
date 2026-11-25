"""Book (gen#1119): 480 invented titles in three formats, and the Barry Plotter series.

**Books > <leaf>** holds the titles of eight leaves (cookery, crafts, gardening, DIY, pets,
children's, fiction, travel); each SKU is one format (``format``). The rows, their publishers
and the titles that collide with other departments are in :mod:`books_rows`, and the Barry
Plotter books (slice 2) in :mod:`barry_plotter_books`; :mod:`kit_books` draws the covers. Books
are templates only: the scaled build invents no title.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import barry_plotter_books, books_rows
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="book",
    department=books_rows.DEPARTMENT,
    product_type=books_rows.PRODUCT_TYPE,
    derivable=False,
    owners=(*books_rows.OWNERS, *barry_plotter_books.OWNERS),
    rows=(*books_rows.rows(), *barry_plotter_books.ROWS),
    options=(Option("format", "format", "Format"),),
)
