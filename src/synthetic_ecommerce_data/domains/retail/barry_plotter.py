"""Barry Plotter, an invented franchise range named only in the product text (gen#925): a stub
with no rows yet, so its test fails on its assertions."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_rows import Row

NAME = "Barry Plotter"
FROM = f"from the {NAME} films"
MOTIFS: dict[str, str] = {}
GROUPS = (
    "Building sets", "Kids' clothing", "Adult clothing", "Accessories", "Home",
    "Party and stationery",
)  # fmt: skip
ROWS: tuple[Row, ...] = ()
SALE: frozenset[str] = frozenset()
DESCRIPTION_ONLY: frozenset[str] = frozenset()


def group_of(row: Row) -> str:
    return GROUPS[0]


def ids() -> frozenset[str]:
    return frozenset(r.product_id for r in ROWS)


def rows_of(product_type: str) -> tuple[Row, ...]:
    return ()


def on_sale(rec: dict) -> dict:
    return rec


def structured_names(doc: dict) -> list[str]:
    fields = {
        "brand": doc.get("brand") or "",
        "product_line": doc.get("product_line") or "",
        **{f"category_path[{i}]": v for i, v in enumerate(doc.get("category_path", ()))},
        "category_leaf": doc.get("category_leaf") or "",
        **{f"attribute {a['key']}": a.get("value") for a in doc.get("attributes", ())},
    }
    return [f for f, v in fields.items() if NAME.lower() in str(v).lower()]
