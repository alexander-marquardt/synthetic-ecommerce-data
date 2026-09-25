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
* **Depth varies, 3 to 4 levels**, because it varies in the real catalog:
  drill bits sit one grouping deeper than taps.
* **Root names are the real catalog's** (``Holemaking``, not ``Drilling``).
"""

from __future__ import annotations

from dataclasses import dataclass

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
LEAVES: dict[str, tuple[CategoryPath, ...]] = {
    "end_mill_square": (("Milling", "End Mills", "Square End Mills"),),
    "end_mill_ball": (("Milling", "End Mills", "Ball End Mills"),),
    "drill_jobber": (
        (
            "Holemaking",
            "Drilling & Drill Bits",
            "Metalworking & Multipurpose Drill Bits",
            "Jobber Length Drill Bits",
        ),
    ),
    "tap_spiral_point": (("Threading", "Taps", "Spiral Point Taps"),),
    "screw_socket_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Socket Cap Screws"),),
    "screw_flat_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Flat Socket Cap Screws"),),
    "screw_button_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Button Socket Cap Screws"),),
    "screw_low_head": (("Fasteners", "Bolts, Screws & Cap Screws", "Low Socket Cap Screws"),),
    "bolt_hex": (("Fasteners", "Bolts, Screws & Cap Screws", "Hex Head Bolts"),),
    "washer_flat": (
        ("Fasteners", "Washers & Shims", "Flat & Square Flat Washers", "Flat Washers"),
    ),
    "hammer_ball_pein": (
        (
            "Hand Tools",
            "Hammers, Striking & Demolition Tools",
            "Hammers & Mallets",
            "Ball Pein & Cross Pein Hammers",
        ),
    ),
    "abrasive_flap_disc": (("Abrasives", "Coated & Non-Woven Abrasives", "Discs", "Flap Discs"),),
}

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


def all_paths() -> tuple[CategoryPath, ...]:
    return tuple(path for paths in LEAVES.values() for path in paths)


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
DRAWING: dict[str, str] = {
    "end_mill_square": "end_mill_square",
    "end_mill_ball": "end_mill_ball",
    "drill_jobber": "drill_jobber",
    "tap_spiral_point": "tap_spiral_point",
    "screw_socket_head": "screw_socket_head",
    "screw_flat_head": "screw_flat_head",
    "screw_button_head": "screw_button_head",
    "screw_low_head": "screw_low_head",
    "bolt_hex": "bolt_hex",
    "washer_flat": "washer_flat",
    "hammer_ball_pein": "hammer_ball_pein",
    "abrasive_flap_disc": "abrasive_flap_disc",
}


class ImageIdError(Exception):
    """An image id is not ``<product type>/<product id>``.

    Raised rather than patched up. The id is a directory in a published URL:
    an id repaired here would move every image under it and break every link to
    it, silently and long after the change that caused it.
    """


def drawing_for(type_key: str) -> str:
    """Which of the twelve shapes a product of ``type_key`` is drawn as."""
    return DRAWING[type_key]


def image_id_for(type_key: str, product_id: str) -> str:
    """One product line's image id: ``end_mill_square/OST-K663-0001``.

    The product type is IN the id, and so is the line. That is what makes the
    id enough on its own to say where the drawing is published -- see
    :func:`..emit.image_path`, which does nothing but append the profile. A
    second table mapping ids to directories is exactly how a record's URL and
    the manifest's path would come to disagree, which is the defect
    ``images.jsonl`` exists to prevent.
    """
    if type_key not in DRAWING:
        raise ImageIdError(
            f"{type_key!r} is not a product type, so no image can be published under it"
        )
    if not product_id or "/" in product_id:
        raise ImageIdError(
            f"{product_id!r} cannot be a product id in an image id: it is empty "
            "or it carries the separator"
        )
    return f"{type_key}/{product_id}"


def product_type_for_image(image_id: str) -> str:
    """The product type an image is published under -- the first segment of its id.

    Read off the id rather than looked up, because the id was built from the
    line's own product type. A malformed id raises: a guess here would file a
    drawing under a category nothing else agrees with.
    """
    type_key, _, product_id = image_id.partition("/")
    if not product_id or "/" in product_id or type_key not in DRAWING:
        raise ImageIdError(
            f"{image_id!r} is not an image id. One reads "
            "<product type>/<product id>, and the product type must be one of "
            f"{sorted(DRAWING)}."
        )
    return type_key
