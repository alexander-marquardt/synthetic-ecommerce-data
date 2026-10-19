"""A sleeve length on every knit (gen#434).

``long sleeve v neck cardigan`` reads a sleeve length. The knitwear grid (:mod:`knitwear_rows`)
states one on every product it makes, but twenty of the older Womens jumpers and cardigans (the
first rows, the color-group rows and the text-match decoys cloned from them) stated none, so the
filter had nothing to read on them. :func:`complete` runs over the templates, before the
decoys are cloned, and gives each knitwear style without a sleeve length the one its drawing
shows, else Long (every one of them is drawn and described with long sleeves). A style that
states one is not changed.
"""

from __future__ import annotations

#: The stored sleeve length for each drawing key (:data:`knitwear_rows.DRAWN_SLEEVE` reversed).
STORED = {"long": "Long", "three_quarter": "Three quarter", "short": "Short",
          "sleeveless": "Sleeveless"}  # fmt: skip
#: The knitwear leaves (third path node) that take a sleeve length.
LEAVES = frozenset({"Jumpers", "Cardigans", "Knitted Tops"})


def _stated(rec: dict) -> bool:
    return any(a.get("key") == "sleeve_length" for a in rec.get("attributes", []))


def _value(rec: dict) -> str:
    drawn = ((rec.get("drawing") or {}).get("params") or {}).get("sleeve")
    return STORED.get(drawn, "Long")


def complete(tpls: list[dict]) -> list[dict]:
    """The templates with a ``sleeve_length`` on each knitwear style that lacked one.

    A completed record is a copy: the records are shared with the authored samples, which the
    image release draws too."""
    out = []
    for r in tpls:
        path = r.get("category_path", [])
        if len(path) < 3 or path[1] != "Knitwear" or path[2] not in LEAVES or _stated(r):
            out.append(r)
            continue
        attr = {"key": "sleeve_length", "name": "Sleeve length", "value": _value(r)}
        out.append({**r, "attributes": [*r.get("attributes", []), attr]})
    return out
