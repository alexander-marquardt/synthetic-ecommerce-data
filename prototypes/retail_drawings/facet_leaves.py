"""A jean's fit and a bra's shape are filters, not category leaves.

The build sorted every jean into a fit leaf (``Womens/Jeans/Skinny Jeans``, about 25 of them)
and every bra into one of about 50 style leaves (``Womens/Lingerie/Bras/Lace Plunge Bras``). A
retailer's tree stops at the kind of garment and lets a shopper filter the fit or the shape,
so :func:`export.standard_document` collapses those leaves here:

- a jean or a pair of trousers sits at ``<Root>/Jeans`` or ``<Root>/Trousers``, its fit in
  ``leg_fit`` alone. ``leg_style`` named the same thing in lower case on the failure-class
  rows (``barrel``, ``wide``), so it is folded into ``leg_fit`` (:data:`LEG_STYLE_FITS`). A
  jean whose text says it is cropped also carries ``Cropped`` (:data:`CROPPED`);
- a bra sits at ``Womens/Lingerie/Bras``, unless it is a purpose bra (:data:`PURPOSE_BRAS`),
  whose node stays. ``bra_style`` is split into ``bra_shape``, ``padding``, ``back_style``
  and ``fabric``, each the value the old leaf implied (:data:`BRA_LEAVES`). Every bra has a
  ``bra_shape``: a leaf that named none (Cotton, Racerback) takes the shape that kind of bra
  is cut in. A value the bra's title names that its leaf did not ("Lace Demi Cup Bra",
  "Padded Balcony Bra") is added too (:func:`stated_bra_facets`).
  The fibre content that ``fabric`` held on a bra ("Recycled Polyamide,
  Elastane") becomes the fibre a shopper names (Nylon) and its blend a detail.
- on every other type, ``fabric`` is the fibre or weave a shopper names (Cotton, Linen,
  Denim, Oxford); a grade or blend becomes the document's ``fibre_content``, a detail and
  no facet (:data:`FABRIC_MOVES`, gen#187; :data:`TYPED_FABRIC_MOVES` for a move that
  reads one type's text, gen#291).

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

#: Every ``fabric`` value that is not the fibre or weave a shopper names -> (fabric, the blend
#: or grade it held). A grade or a blend ("Organic Cotton", "98% Cotton, 2% Elastane") is a
#: Cotton; a weave joined to a fibre ("100% Cotton Oxford") is the weave; a bra's fibre
#: content ("Recycled Polyamide, Elastane") is the fibre a shopper asks for (Nylon). The blend
#: becomes the document's ``fibre_content`` (:func:`fibre_content`), a detail and no facet. A
#: blend names fibres, so the fabric is the one the row states: a cotton blend is a cotton,
#: the tailored shorts' polyester blend is the suiting their text names (gen#258), which is a
#: call on one product type's text and so lives in :data:`TYPED_FABRIC_MOVES`.
#: Boucle, Chenille, Corduroy, Faux Fur, Knitted, Linen, Plush and Velvet are fabrics and stay.
FABRIC_MOVES: dict[str, tuple[str, str | None]] = {
    "100% Cotton": ("Cotton", "100% Cotton"),
    "70% Cotton, 28% Polyester, 2% Elastane": ("Cotton", "70% Cotton, 28% Polyester, 2% Elastane"),
    "92% Cotton, 6% Polyester, 2% Elastane": ("Cotton", "92% Cotton, 6% Polyester, 2% Elastane"),
    "98% Cotton, 2% Elastane": ("Cotton", "98% Cotton, 2% Elastane"),
    "Organic Cotton": ("Cotton", "Organic Cotton"),
    "Turkish Cotton": ("Cotton", "Turkish Cotton"),
    "Zero Twist Cotton": ("Cotton", "Zero Twist Cotton"),
    "100% Cotton Oxford": ("Oxford", "100% Cotton"),
    "Brushed Cotton Flannel": ("Flannel", "Cotton"),
    "Mid Weight Denim": ("Denim", None),
    "Washed Linen": ("Linen", None),
    "Cotton Blend": ("Cotton", "Cotton Blend"),
    "Cotton Jersey": ("Jersey", "Cotton"),
    "Silk Dupion": ("Silk", "Silk Dupion"),
    "Cotton, Elastane": ("Cotton", "Cotton, Elastane"),
    "Modal, Elastane": ("Modal", "Modal, Elastane"),
    "Recycled Polyamide, Elastane": ("Nylon", "Recycled Polyamide, Elastane"),
    "Recycled Polyester, Elastane": ("Polyester", "Recycled Polyester, Elastane"),
}

#: A move that reads one product type's text, not the value alone: (product type, fabric) ->
#: (fabric, blend). A value here on another type is moved by no one and stays as it is, so the
#: closed-list guard names it and the new row's author decides (gen#291).
TYPED_FABRIC_MOVES: dict[tuple[str, str], tuple[str, str | None]] = {
    ("Shorts", "Polyester Blend"): ("Suiting", "Polyester Blend"),
}


def fabric_move(product_type: str, value: str) -> tuple[str, str | None] | None:
    """The (fabric, blend) a ``fabric`` value of a ``product_type`` becomes, or ``None`` when
    it is already a shopper's fabric. The typed move wins over the value's own."""
    return TYPED_FABRIC_MOVES.get((product_type, value)) or FABRIC_MOVES.get(value)


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


def fibre_content(entries: list[dict[str, Any]], product_type: str) -> str | None:
    """The blend or grade ``entries``' ``fabric`` held ("98% Cotton, 2% Elastane"), for the
    document's ``fibre_content`` detail; ``None`` when the fabric is already a shopper's."""
    for entry in entries:
        move = fabric_move(product_type, entry["value"]) if entry["key"] == "fabric" else None
        if move:
            return move[1]
    return None


def _fabric_facets(
    have: dict[str, str], product_type: str
) -> tuple[list[tuple[str, str, str]], set[str]]:
    """The fabric a fibre-content ``fabric`` becomes, as (key, name, value), and the key it
    replaces. Neither for a value that is already a fabric."""
    move = fabric_move(product_type, have["fabric"]) if "fabric" in have else None
    return ([("fabric", "Fabric", move[0])], {"fabric"}) if move else ([], set())


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
        moved, keys = _fabric_facets(have, ptype)
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
        moved, _ = _fabric_facets(have, ptype)
        out += [m for m in moved if (m[0], m[2]) not in implied]
        return out, {"bra_style", "fabric"}
    return _fabric_facets(have, ptype)
