"""A jean's fit and a bra's shape are filters, not category leaves.

The build sorted every jean into a fit leaf (``Women/Jeans/Skinny Jeans``, about 25 of them)
and every bra into one of about 50 style leaves (``Women/Lingerie/Bras/Lace Plunge Bras``). A
retailer's tree stops at the kind of garment and lets a shopper filter the fit or the shape,
so :func:`export.standard_document` collapses those leaves here:

- a jean or a pair of trousers sits at ``<Root>/Jeans`` or ``<Root>/Trousers``, its fit in
  ``leg_fit`` alone. ``leg_style`` named the same thing in lower case on the failure-class
  rows (``barrel``, ``wide``), so it is folded into ``leg_fit`` (:data:`LEG_STYLE_FITS`). A
  jean whose text says it is cropped also carries ``Cropped`` (:data:`CROPPED`);
- a bra sits at ``Women/Lingerie/Bras``, unless it is a purpose bra (:data:`PURPOSE_BRAS`),
  whose node stays. ``bra_style`` is split into ``bra_shape``, ``padding``, ``back_style``
  and ``fabric``, each the value the old leaf implied (:data:`BRA_LEAVES`). Every bra has a
  ``bra_shape``: a leaf that named none (Cotton, Racerback) takes the shape that kind of bra
  is cut in. A value the bra's title names that its leaf did not ("Lace Demi Cup Bra",
  "Padded Balcony Bra") is added too (:func:`stated_bra_facets`).
  The fibre content that ``fabric`` held on a bra ("Recycled Polyamide,
  Elastane") moves to ``composition``.
- on every other type, ``fabric`` keeps only a fabric or weave; fibre content moves to
  ``composition`` the same way (:data:`FABRIC_MOVES`).

Only the document changes. The build record, its drawing and so its image id keep the old
leaf, so the seeded derivation and every image id are what they were. Titles keep their
words ("Skinny Jeans", "Lace Balcony Bra"), so a text search still finds them.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.standard import words

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
#: The one fit a jean of another fit is also cut in: a cropped balloon jean ("curving back in
#: at a cropped ankle") was filed under Balloon Jeans, but a "Cropped" filter must find it, and
#: once every fit shares the Jeans leaf its text would otherwise contradict its ``leg_fit``.
CROPPED = "Cropped"

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
#: ``None`` is a facet the leaf did not imply; a tuple is several values (a convertible bra's
#: straps convert to a halterneck or a cross back, and its text says so). A shape written
#: for a leaf that named none is the shape that kind of bra is cut in: a moulded or everyday
#: cup is a T-Shirt bra, a strapless or multiway one a Balcony, a halter or low back a
#: Plunge, the rest a Full Cup.
Facet = str | tuple[str, ...] | None
BRA_LEAVES: dict[str, tuple[str, Facet, Facet, Facet]] = {
    "Balconette Bras": ("Balcony", None, None, None),
    "Balcony Bras": ("Balcony", None, None, None),
    "Bandeau Bras": ("Bandeau", None, "Strapless", None),
    "Bralette Bras": ("Bralette", None, None, None),
    "Contour Bras": ("T-Shirt", "Moulded", None, None),
    "Convertible Bras": ("Balcony", None, ("Multiway", "Halterneck", "Cross Back"), None),
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

#: Every other product type's ``fabric`` value that is not a fabric a shopper names ->
#: (fabric, composition) of the document. A fibre content ("98% Cotton, 2% Elastane", a
#: cotton grade, Bamboo) moves whole to ``composition`` and leaves no fabric; a value that
#: joins a weave to a fibre or a finish ("100% Cotton Oxford", "Washed Linen", "Cotton Jersey")
#: splits. A blend names fibres, so it is the composition and the fabric is the one the row
#: states: a cotton blend is a cotton, the tailored shorts' polyester blend is the suiting
#: their text names (gen#258).
#: Boucle, Chenille, Corduroy, Faux Fur, Knitted, Linen, Plush and Velvet are fabrics and stay.
FABRIC_MOVES: dict[str, tuple[str | None, str | None]] = {
    "100% Cotton": (None, "100% Cotton"),
    "70% Cotton, 28% Polyester, 2% Elastane": (None, "70% Cotton, 28% Polyester, 2% Elastane"),
    "92% Cotton, 6% Polyester, 2% Elastane": (None, "92% Cotton, 6% Polyester, 2% Elastane"),
    "98% Cotton, 2% Elastane": (None, "98% Cotton, 2% Elastane"),
    "Bamboo": (None, "Bamboo"),
    "Organic Cotton": (None, "Organic Cotton"),
    "Turkish Cotton": (None, "Turkish Cotton"),
    "Zero Twist Cotton": (None, "Zero Twist Cotton"),
    "100% Cotton Oxford": ("Oxford", "100% Cotton"),
    "Brushed Cotton Flannel": ("Flannel", "Cotton"),
    "Mid Weight Denim": ("Denim", None),
    "Washed Linen": ("Linen", None),
    "Cotton Blend": ("Cotton", "Cotton Blend"),
    "Polyester Blend": ("Suiting", "Polyester Blend"),
    "Cotton Jersey": ("Jersey", "Cotton"),
}


def _vocabulary() -> dict[str, set[str]]:
    """Every value of each :data:`BRA_KEYS` key that some leaf implies."""
    vocab: dict[str, set[str]] = {key: set() for key in BRA_KEYS}
    for row in BRA_LEAVES.values():
        for key, facet in zip(BRA_KEYS, row, strict=True):
            vocab[key] |= {facet} if isinstance(facet, str) else set(facet or ())
    return vocab


BRA_VOCABULARY = _vocabulary()


def stated_bra_facets(text: str) -> list[tuple[str, str]]:
    """The (key, value) pairs ``text`` names: a bra under Demi Cup Bras whose title says
    "Lace" is lace, whatever its leaf. The longest value wins ("Push-Up" over "Up"). Only a
    title is read: a description says "a non padded full cup bra" or "in cotton, elastane"
    (fibre content, not the fabric), so it names a value to deny it or to list a fibre."""
    padded = words(text)
    out = []
    for key, vocab in BRA_VOCABULARY.items():
        named = {v for v in vocab if f" {words(v).strip()} " in padded}
        out += [
            (key, v)
            for v in sorted(named)
            if not any(v != w and f" {words(v).strip()} " in words(w) for w in named)
        ]
    return out


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


def _fabric_facets(have: dict[str, str]) -> tuple[list[tuple[str, str, str]], set[str]]:
    """The fabric and composition a fibre-content ``fabric`` splits into, as (key, name,
    value), and the key it replaces. Neither for a value that is already a fabric."""
    if have.get("fabric") not in FABRIC_MOVES:
        return [], set()
    fabric, composition = FABRIC_MOVES[have["fabric"]]
    pairs = ((("fabric", "Fabric"), fabric), (COMPOSITION, composition))
    return [(*pair, value) for pair, value in pairs if value], {"fabric"}


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
        fits = [fit] if fit else []
        text = words(f"{rec['title']} {rec.get('description', '')}")
        if fits and CROPPED not in fits and f" {CROPPED.lower()} " in text:
            fits.append(CROPPED)
        moved, keys = _fabric_facets(have)
        return [("leg_fit", "Leg fit", f) for f in fits] + moved, {"leg_fit", "leg_style"} | keys
    if ptype == "Bra":
        out = [
            (key, BRA_KEYS[key], value)
            for key, facet in zip(BRA_KEYS, BRA_LEAVES[path[-1]], strict=True)
            for value in ((facet,) if isinstance(facet, str) else facet or ())
        ]
        implied = {(key, value) for key, _, value in out}
        out += [
            (key, BRA_KEYS[key], value)
            for key, value in stated_bra_facets(rec["title"])
            if (key, value) not in implied
        ]
        if "fabric" in have:
            out.append((*COMPOSITION, have["fabric"]))
        return out, {"bra_style", "fabric"}
    return _fabric_facets(have)
