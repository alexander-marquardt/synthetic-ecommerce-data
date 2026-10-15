"""The category tree, in the shape of the real catalog it imitates.

The tree exists to be *insufficient*. Category narrows a shopper down to a
leaf and then stops discriminating: every product under
``Milling / End Mills / Square End Mills`` is a square end mill, and choosing
between them -- by material, coating, diameter, flute count -- is entirely a
matter of attributes. That is the handover this catalog is built to exercise.

THE RULE, read off the real distributor's own breadcrumbs and category facet
(elastic/prism-industrial-products#77):

* **The leaf is always a self-describing plural product type** --
  ``Square End Mills``, ``Jobber Length Drill Bits``, ``Socket Cap Screws``.
  A leaf a shopper reads out of context still says what the product is.
* **Intermediate levels group types** (``Metalworking & Multipurpose Drill
  Bits``); they never narrow by a specification.
* **Specifications are never path levels.** Material, coating/finish, drive,
  size and standard are attributes. An earlier version of this tree ended the
  end mills at a MATERIAL (``... / Square End Mills / Cobalt``), which the
  real catalog never does; ``tests/test_catalog_vocab.py`` now reds if any
  path segment equals a value its own products publish as an attribute.
* **Depth varies, 3 to 5 levels**, because it varies in the real catalog:
  drill bits sit one grouping deeper than taps.
* **Root names are the real catalog's** (``Holemaking``, not ``Drilling``).
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.typespec import RegistryTable

#: A category path, root first.
CategoryPath = tuple[str, ...]


@dataclass(frozen=True)
class Category:
    path: CategoryPath

    @property
    def leaf(self) -> str:
        return self.path[-1]

    @property
    def depth(self) -> int:
        return len(self.path)

    def text(self) -> str:
        return " / ".join(self.path)


#: Every product type's category path. One path per type: the leaf IS the type.
_LEAVES: dict[str, tuple[CategoryPath, ...]] = {
    "end_mill_square": (("Milling", "End Mills", "Square End Mills"),),
    "end_mill_ball": (("Milling", "End Mills", "Ball End Mills"),),
    "tap_spiral_point": (("Threading", "Taps", "Spiral Point Taps"),),
    "screw_flat_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Flat Socket Cap Screws"),),
    "screw_button_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Button Socket Cap Screws"),),
    "screw_low_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Low Socket Cap Screws"),),
    "bolt_hex": (("Fasteners", "Bolts, Screws & Cap Screws", "Hex Head Bolts"),),
    "hammer_ball_pein": (
        # One node for every hammer kind (#305); see SHARED_LEAVES.
        ("Hand Tools", "Hammers"),
    ),
    "abrasive_flap_disc": (("Abrasives", "Coated & Non-Woven Abrasives", "Discs", "Flap Discs"),),
    # elastic/prism-industrial-products#103, stage 1. Depth runs to five, as
    # the reference distributor's own breadcrumbs do for hex keys.
    "nut_hex": (("Fasteners", "Nuts", "Hex Nuts"),),
    "bearing_radial_ball": (("Motion Control & Fluid Power", "Bearings", "Radial Ball Bearings"),),
    "wheel_depressed_center": (
        (
            "Abrasives",
            "Grinding & Cut-Off",
            "Grinding & Cut-Off Wheels",
            "Depressed-Center Wheels",
        ),
    ),
    "hex_key": (
        (
            "Hand Tools",
            "Screwdrivers & Hex Keys",
            "Hex & Torx Keys",
            "Hex Keys & Accessories",
            "Hex Keys",
        ),
    ),
    "kit_assortment": (("Hand Tools", "Tool Sets & Kits", "Assortment Kits"),),
}
# A read registers the type modules first, so a type in its own module is listed.
LEAVES: RegistryTable[str, tuple[CategoryPath, ...]] = RegistryTable(_LEAVES)

#: The end-mill tool materials each style is made in, in the order the draw
#: indexes them. Material used to be read off a fourth path level; it is an
#: attribute (``End Mill Material``), drawn here. The tuples keep the length
#: and order the old per-material paths had, so the generator's random stream
#: -- and with it every product id, SKU, dimension and price -- is unchanged by
#: moving material out of the path.
END_MILL_MATERIALS: dict[str, tuple[str, ...]] = {
    "end_mill_square": ("Solid Carbide", "Cobalt", "High Speed Steel"),
    "end_mill_ball": ("Solid Carbide", "Cobalt"),
}


#: Leaves that hold several product types, each one a kind of the node (#305): every hammer
#: kind is its own ``product_type`` under the one ``Hammers`` node. The rule that a leaf is one
#: type's own two-word plural (``test_every_leaf_is_its_types_own_self_describing_plural``)
#: holds for every leaf not named here.
SHARED_LEAVES: frozenset[CategoryPath] = frozenset({("Hand Tools", "Hammers")})


def all_paths() -> tuple[CategoryPath, ...]:
    """Every distinct category path, in type order (a shared leaf once)."""
    return tuple(dict.fromkeys(path for paths in LEAVES.values() for path in paths))


def tree_depths() -> set[int]:
    return {len(path) for path in all_paths()}


def ancestors(path: CategoryPath) -> tuple[CategoryPath, ...]:
    """Every prefix of ``path``, shortest first, including ``path`` itself."""
    return tuple(path[: n + 1] for n in range(len(path)))


#: Which of the twelve shapes a product type's products are drawn as.
#:
#: Written out rather than derived, even though every pair is currently an
#: identity. The two sides mean different things -- the left is a catalog
#: product type, the right is a drawing in :mod:`..render.generic` -- and a
#: product type that gained a second style, or two types that turned out to be
#: the same shape, would show up here as a pair that no longer matches instead
#: of as nothing at all. ``tests/test_generic.py`` asserts that the right-hand
#: side is exactly the set of drawings that exist.
#:
#: This does NOT decide where an image is published. Images are one per product
#: LINE, and a line's image id carries its own product type, so the published
#: directory is the line's rather than something inferred from the shape it
#: shares with four hundred others.
_DRAWING: dict[str, str] = {
    "end_mill_square": "end_mill_square",
    "end_mill_ball": "end_mill_ball",
    "tap_spiral_point": "tap_spiral_point",
    "screw_flat_head": "screw_flat_head",
    "screw_button_head": "screw_button_head",
    "screw_low_head": "screw_low_head",
    "bolt_hex": "bolt_hex",
    "hammer_ball_pein": "hammer_ball_pein",
    "abrasive_flap_disc": "abrasive_flap_disc",
    "nut_hex": "nut_hex",
    "bearing_radial_ball": "bearing_radial_ball",
    "wheel_depressed_center": "wheel_depressed_center",
    "hex_key": "hex_key",
    "kit_assortment": "kit_assortment",
}
# A read registers the type modules first, so a type in its own module is listed.
DRAWING: RegistryTable[str, str] = RegistryTable(_DRAWING)


class ImageIdError(Exception):
    """An image id is not ``<product type>/<product id>``.

    Raised rather than patched up. The id is a directory in a published URL:
    an id repaired here would move every image under it and break every link to
    it, silently and long after the change that caused it.
    """


def drawing_for(type_key: str) -> str:
    """Which of the twelve shapes a product of ``type_key`` is drawn as."""
    return DRAWING[type_key]


def image_id_for(type_key: str, product_id: str, sku: str) -> str:
    """One SKU's image id: ``end_mill_square/OST-K663-0001/97NR28``.

    ONE IMAGE PER SKU (elastic/prism-industrial-products#103, 2026-09-26): each
    variant is drawn from its own dimensions, so selecting a variant can switch
    the picture once a grouped view exists. The product type is in the id, then
    the product, then the SKU -- enough on its own to say where the file lives
    (:func:`..emit.image_path` appends ``.svg`` and nothing else), so no second
    table can make a record's URL and the manifest's path disagree.
    """
    if type_key not in DRAWING:
        raise ImageIdError(
            f"{type_key!r} is not a product type, so no image can be published under it"
        )
    for part, what in ((product_id, "product id"), (sku, "SKU")):
        if not part or "/" in part:
            raise ImageIdError(
                f"{part!r} cannot be a {what} in an image id: it is empty "
                "or it carries the separator"
            )
    return f"{type_key}/{product_id}/{sku}"


def product_type_for_image(image_id: str) -> str:
    """The product type an image is published under -- the first segment of its id.

    Read off the id rather than looked up, because the id was built from the
    line's own product type. A malformed id raises: a guess here would file a
    drawing under a category nothing else agrees with.
    """
    parts = image_id.split("/")
    if len(parts) != 3 or not all(parts) or parts[0] not in DRAWING:
        raise ImageIdError(
            f"{image_id!r} is not an image id. One reads "
            "<product type>/<product id>/<sku>, and the product type must be one of "
            f"{sorted(DRAWING)}."
        )
    return parts[0]
