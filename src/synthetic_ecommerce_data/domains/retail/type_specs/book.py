"""Book (gen#1119, slice 1): 480 invented titles, each sold as an ebook, a paperback and a hardback.

**Books > <leaf>** holds the titles of eight leaves (cookery, crafts, gardening, DIY, pets,
children's, fiction, travel); each SKU is one format (``format``). The rows, their publishers
and the titles that collide with other departments are in :mod:`books_rows`; :mod:`kit_books`
draws the cover. Books are templates only: the scaled build invents no title.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import books_rows
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

SPEC = TypeSpec(
    key="book",
    department=books_rows.DEPARTMENT,
    product_type=books_rows.PRODUCT_TYPE,
    derivable=False,
    owners=books_rows.OWNERS,
    rows=books_rows.rows(),
    options=(Option("format", "format", "Format"),),
)
