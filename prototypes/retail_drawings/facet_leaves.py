"""A jean's fit and a bra's shape are filters, not category leaves.

The build sorted every jean into a fit leaf (``Women/Jeans/Skinny Jeans``, about 25 of them)
and every bra into one of about 50 style leaves (``Women/Lingerie/Bras/Lace Plunge Bras``). A
retailer's tree stops at the kind of garment and lets a shopper filter the fit or the shape,
so :func:`export.standard_document` collapses those leaves here:

- a jean or a pair of trousers sits at ``<Root>/Jeans`` or ``<Root>/Trousers``, its fit in
  ``leg_fit`` alone. ``leg_style`` named the same thing in lower case on the failure-class
  rows (``barrel``, ``wide``), so it is folded into ``leg_fit`` (:data:`LEG_STYLE_FITS`);
- a bra sits at ``Women/Lingerie/Bras``, unless it is a purpose bra (:data:`PURPOSE_BRAS`),
  whose node stays. ``bra_style`` is split into ``bra_shape``, ``padding``, ``back_style``
  and ``fabric``, each the value the old leaf implied (:data:`BRA_LEAVES`). Every bra has a
  ``bra_shape``: a leaf that named none (Cotton, Racerback) takes the shape that kind of bra
  is cut in. The fibre content that ``fabric`` held on a bra ("Recycled Polyamide,
  Elastane") moves to ``composition``.

Only the document changes. The build record, its drawing and so its image id keep the old
leaf, so the seeded derivation and every image id are what they were. Titles keep their
words ("Skinny Jeans", "Lace Balcony Bra"), so a text search still finds them.
"""

from __future__ import annotations

from typing import Any

#: The kind nodes whose fit leaves collapse into them, by product type.
FIT_NODES = {"Jeans": "Jeans", "Trousers": "Trousers"}
#: The bra node, and the purpose nodes that stay under it.
BRA_NODE = "Bras"
PURPOSE_BRAS = ("Sports Bras", "Nursing Bras", "Sleep Bras", "Post-Surgery Bras")

#: ``leg_style`` (the failure-class rows' lower-case fit) -> its ``leg_fit`` value.
LEG_STYLE_FITS = {
    "balloon": "Balloon",
    "barrel": "Barrel",
    "slim": "Slim",
    "straight": "Straight",
    "tapered": "Tapered",
    "wide": "Wide Leg",
}

#: The keys a bra leaf's facets are written to, with their display names.
BRA_KEYS = {
    "bra_shape": "Bra shape",
    "padding": "Padding",
    "back_style": "Back style",
    "fabric": "Fabric",
}
#: A bra's fibre content, which ``fabric`` held before it named the fabric a shopper filters.
COMPOSITION = ("composition", "Composition")

#: Bra leaf (``<x> Bras``, or a purpose node) -> (bra_shape, padding, back_style, fabric).
#: ``None`` is a facet the leaf did not imply. A shape written for a leaf that named none is
#: the shape that kind of bra is cut in: a moulded or everyday cup is a T-Shirt bra, a
#: strapless or multiway one a Balcony, a halter or low back a Plunge, the rest a Full Cup.
BRA_LEAVES: dict[str, tuple[str, str | None, str | None, str | None]] = {
    "Balconette Bras": ("Balcony", None, None, None),
    "Balcony Bras": ("Balcony", None, None, None),
    "Bandeau Bras": ("Bandeau", None, "Strapless", None),
    "Bralette Bras": ("Bralette", None, None, None),
    "Contour Bras": ("T-Shirt", "Moulded", None, None),
    "Convertible Bras": ("Balcony", None, "Multiway", None),
    "Cotton Bras": ("Full Cup", None, None, "Cotton"),
    "Cross Back Bras": ("Full Cup", None, "Cross Back", None),
    "Deep Plunge Bras": ("Plunge", None, None, None),
    "Demi Bras": ("Demi", None, None, None),
    "Demi Cup Bras": ("Demi", None, None, None),
    "Embroidered Balcony Bras": ("Balcony", None, None, None),
    "Everyday Bras": ("T-Shirt", None, None, None),
    "Front Fastening Bras": ("Plunge", None, None, None),
    "Full Cup Bras": ("Full Cup", None, None, None),
    "Full Support Bras": ("Full Cup", None, None, None),
    "Halterneck Bras": ("Plunge", None, "Halterneck", None),
    "High Apex Bras": ("High Apex", None, None, None),
    "Lace Balcony Bras": ("Balcony", None, None, "Lace"),
    "Lace Bralette Bras": ("Bralette", None, None, "Lace"),
    "Lace Demi Bras": ("Demi", None, None, "Lace"),
    "Lace Full Cup Bras": ("Full Cup", None, None, "Lace"),
    "Lace Longline Bras": ("Longline", None, None, "Lace"),
    "Lace Plunge Bras": ("Plunge", None, None, "Lace"),
    "Lightly Lined Bras": ("T-Shirt", "Lightly Lined", None, None),
    "Longline Bras": ("Longline", None, None, None),
    "Low Back Bras": ("Plunge", None, "Low Back", None),
    "Mesh Bras": ("Full Cup", None, None, "Mesh"),
    "Minimiser Bras": ("Minimiser", None, None, None),
    "Moulded Cup Bras": ("T-Shirt", "Moulded", None, None),
    "Multiway Bras": ("Balcony", None, "Multiway", None),
    "Padded Bras": ("T-Shirt", "Padded", None, None),
    "Plunge Bras": ("Plunge", None, None, None),
    "Push-Up Bras": ("Plunge", "Push-Up", None, None),
    "Racerback Bras": ("Full Cup", None, "Racerback", None),
    "Satin Bras": ("Full Cup", None, None, "Satin"),
    "Seamless Bras": ("T-Shirt", "Moulded", None, None),
    "Side Support Bras": ("Full Cup", None, None, None),
    "Smoothing Bras": ("T-Shirt", "Moulded", None, None),
    "Soft Cup Bras": ("Full Cup", "Unlined", None, None),
    "Spacer Cup Bras": ("T-Shirt", "Lightly Lined", None, None),
    "Strapless Bras": ("Balcony", None, "Strapless", None),
    "Strappy Bras": ("Full Cup", None, "Strappy", None),
    "T-Shirt Bras": ("T-Shirt", None, None, None),
    "Triangle Bras": ("Triangle", "Unlined", None, None),
    "Unlined Bras": ("Full Cup", "Unlined", None, None),
    "Wide Strap Bras": ("Full Cup", None, "Wide Strap", None),
    # The purpose nodes stay in the tree; their bras still carry a shape.
    "Sports Bras": ("Full Cup", None, "Racerback", None),
    "Nursing Bras": ("Full Cup", None, None, None),
    "Sleep Bras": ("Bralette", "Unlined", None, None),
    "Post-Surgery Bras": ("Full Cup", None, None, None),
}


def collapsed_path(path: list[str], product_type: str) -> list[str]:
    """``path`` with a jean's or trousers' fit leaf, or a bra's non-purpose leaf, dropped."""
    if len(path) >= 2 and path[-2] == FIT_NODES.get(product_type):
        return path[:-1]
    if product_type == "Bra" and len(path) >= 2 and path[-2] == BRA_NODE:
        return path if path[-1] in PURPOSE_BRAS else path[:-1]
    return path


def _fit_of_leaf(leaf: str, node: str) -> str | None:
    suffix = f" {node}"
    return leaf[: -len(suffix)] if leaf.endswith(suffix) else None


def leaf_facets(
    rec: dict[str, Any], entries: list[dict[str, Any]]
) -> tuple[list[tuple[str, str, str]], set[str]]:
    """The facets ``rec``'s collapsed leaf implied, as (key, name, value), and the keys of
    ``entries`` they replace. Neither for a style whose leaf does not collapse."""
    ptype, path = rec["product_type"], list(rec["category_path"])
    have = {e["key"]: str(e["value"]) for e in entries}
    if ptype in FIT_NODES:
        fit = have.get("leg_fit")
        fit = fit or LEG_STYLE_FITS.get(have.get("leg_style", ""))
        fit = fit or _fit_of_leaf(path[-1], FIT_NODES[ptype])
        return ([("leg_fit", "Leg fit", fit)] if fit else []), {"leg_fit", "leg_style"}
    if ptype == "Bra":
        out = [
            (key, BRA_KEYS[key], value)
            for key, value in zip(BRA_KEYS, BRA_LEAVES[path[-1]], strict=True)
            if value is not None
        ]
        if "fabric" in have:
            out.append((*COMPOSITION, have["fabric"]))
        return out, {"bra_style", "fabric"}
    return [], set()
