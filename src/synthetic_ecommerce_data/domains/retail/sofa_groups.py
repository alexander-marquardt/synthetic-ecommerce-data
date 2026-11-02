"""Grouped sofas and sofa cushions (gen#808): one product, several versions (data only).

A search for a blue sofa cushion or a sofa with grouping on never showed a grouped card: the
catalog's cushions held no blue, and :mod:`sofa_rows` sells each seat count of a sofa as its own
style. The maintainer asked for "a few grouped blue sofa cushions, and a few grouped sofas ..
perhaps a 2 seater, 3 seater, and corner sofa .. versions of the exact same product".

- :data:`CUSHIONS`: three cushions, each sold in three colors (Blue among them) and three sizes,
  so nine SKUs that share the brand, the name and the fabric. The size is the cushion's ``size``,
  on its type's size ladder (:mod:`size_ladder`), so each size draws at its own scale and each
  color in its own swatch.
- :data:`SOFAS`: three sofas, each sold as a 2 seater, a 3 seater and a corner sofa in one fabric
  and one color. The version is the SKU's ``configuration``, the one axis; its seat count, width
  and depth follow it, so ``variant_axes`` names ``configuration`` alone. The drawing,
  ``kit_seating.sofa_version``, reads the SKU's own configuration, so each version draws its own
  sofa, the corner its L-shape. A sofa sits at ``Home/Furniture/Sofas``, which holds ``Corner
  Sofas``, and is also filed at ``Sofas > Corner Sofas`` (:mod:`multi_path`), so the corner
  version is found from both nodes.

The product name states no version (no seat count, size or color); each SKU states its own as an
attribute. :mod:`sofa_rows` lists these rows among its own, so they are templates only, as every
seating style is, and the seeded derivation is what it was.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.kit_seating import CONFIGURATION_SEATS
from synthetic_ecommerce_data.domains.retail.variants import cw

_SOFAS = ("Home", "Furniture", "Sofas")
_CUSHIONS = ("Home", "Soft Furnishings", "Cushions")

BLUE, TEAL, MUSTARD = cw("Blue", "#3f6fb5"), cw("Teal", "#1c7c7d"), cw("Mustard", "#d4a32a")
SAGE, NATURAL, GREY = cw("Sage", "#9bb08f"), cw("Natural", "#d8cdb8"), cw("Grey", "#9a9ca0")
RUST, OAT = cw("Rust", "#a4502a"), cw("Oat", "#d8c9a8")

#: The cushion sizes, smallest first, and what each adds to the smallest's price.
CUSHION_SIZES = (("40 x 40cm", 0.0), ("45 x 45cm", 4.0), ("50 x 50cm", 8.0))


def _cushion(
    code: str,
    title: str,
    brand: str,
    fabric: str,
    price: float,
    text: str,
    colors: tuple,
    trim: str = "",
) -> Row:
    """A cushion in each of ``colors`` and :data:`CUSHION_SIZES`; ``trim`` (a hex color) draws its
    piped edge, so no two of the cushions draw one picture in one color and size."""
    return Row(code, title, brand, "Home", _CUSHIONS, "Cushion", price, "cushion",
               f"{text} Sold in 40, 45 and 50 cm squares.", colors,
               (("line", "Line", title.split()[0]), ("fabric", "Fabric", fabric)),
               tuple((size, price + more) for size, more in CUSHION_SIZES),
               params=(("trim", trim),) if trim else ())  # fmt: skip


CUSHIONS = (
    _cushion("GRCVEL", "Elmsworth Velvet Sofa Cushion", "Hearth & Table", "Velvet", 16.0,
             "A plump square sofa cushion in soft velvet, with a feather pad and a hidden zip.",
             (BLUE, TEAL, MUSTARD)),
    _cushion("GRCLIN", "Quenby Linen Sofa Cushion", "Lanternby", "Linen", 18.0,
             "A square sofa cushion in washed linen, with a contrast piped edge and a hollowfibre"
             " pad.", (BLUE, SAGE, NATURAL), trim="#f4f1ea"),
    _cushion("GRCCHN", "Harrowden Chenille Sofa Cushion", "Calderby & Lune", "Chenille", 20.0,
             "A square sofa cushion in a thick, soft chenille with a dark piped edge.",
             (BLUE, GREY, RUST), trim="#3b3b3e"),
)  # fmt: skip


@dataclass(frozen=True)
class SofaVersions(Row):
    """A sofa sold as several versions of one product: each version is a SKU in each color."""

    #: ``(configuration, width cm, depth cm, price)`` of each version, the smallest first.
    versions: tuple[tuple[str, int, int, float], ...] = ()

    def skus(self) -> list[dict]:
        return [
            {"color": c[0], "configuration": name, "seat_count": CONFIGURATION_SEATS[name],
             "width_cm": width, "depth_cm": depth, "price": price, "in_stock": True}
            for c in self.colors
            for name, width, depth, price in self.versions
        ]  # fmt: skip


def _sofa(
    code: str,
    line: str,
    brand: str,
    mat: str,
    color: tuple,
    arms: str,
    legs: str,
    filling: str,
    firmness: str,
    text: str,
    prices: tuple[float, float, float],
) -> Row:
    sizes = ((168, 92), (214, 92), (262, 212))
    return SofaVersions(
        code, f"{line} {mat} Sofa", brand, "Home", _SOFAS, "Sofa", prices[0], "sofa_version",
        f"{text} Sold as a 2 seater (168 cm wide), a 3 seater (214 cm) and a left-hand L-shaped"
        " corner sofa (262 x 212 cm).",
        (color,),
        (("line", "Line", line), ("item_height", "Item height", "84", "CMT", 840.0),
         ("material", "Material", mat), ("arm_style", "Arm style", arms.title()),
         ("leg_finish", "Leg finish", legs.replace("_", " ").title()),
         ("filling", "Filling", filling), ("firmness", "Firmness", firmness),
         ("removable_covers", "Removable covers", "yes"), ("pet_friendly", "Pet friendly", "no")),
        params=(("configuration", "2 Seater"), ("arms", arms), ("legs", legs)),
        versions=tuple((name, w, d, p) for name, (w, d), p
                       in zip(CONFIGURATION_SEATS, sizes, prices, strict=True)),
    )  # fmt: skip


SOFAS = (
    _sofa("GRSMAD", "Maddox", "Brackenmere Home", "Velvet", BLUE, "track", "oak", "Foam", "Firm",
          "A tailored velvet sofa with square track arms on oak legs.", (699.0, 849.0, 1349.0)),
    _sofa("GRSWEX", "Wexley", "Emberly Home", "Chenille", GREY, "rolled", "walnut",
          "Feather Blend", "Soft", "A deep chenille sofa with rolled arms on walnut legs.",
          (649.0, 799.0, 1249.0)),
    _sofa("GRSELL", "Ellery", "Larchwood Living", "Boucle", OAT, "slim", "black_metal", "Fiber",
          "Medium", "A boucle sofa with slim arms on black metal legs.", (749.0, 899.0, 1449.0)),
)  # fmt: skip
