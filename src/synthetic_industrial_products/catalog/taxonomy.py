"""The category tree.

The tree exists to be *insufficient*. Category narrows a shopper down to a
leaf and then stops discriminating: every product under
``Milling / End Mills / Square End Mills / Solid Carbide`` is a square solid
carbide end mill, and choosing between them is entirely a matter of attributes.
That is the handover this catalog is built to exercise, so the leaves are
deliberately specific enough to be exhausted.

Depth varies by branch, 3 to 4 levels, because it varies in real catalogs: the
cutting-tool branches earn a fourth level from tool material, and a flat washer
does not.
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


#: Every leaf in the tree, with the product-type key that populates it.
LEAVES: dict[str, tuple[CategoryPath, ...]] = {
    "end_mill_square": (
        ("Milling", "End Mills", "Square End Mills", "Solid Carbide"),
        ("Milling", "End Mills", "Square End Mills", "Cobalt"),
        ("Milling", "End Mills", "Square End Mills", "High Speed Steel"),
    ),
    "end_mill_ball": (
        ("Milling", "End Mills", "Ball Nose End Mills", "Solid Carbide"),
        ("Milling", "End Mills", "Ball Nose End Mills", "Cobalt"),
    ),
    "drill_jobber": (("Drilling", "Twist Drills", "Jobber Length Drill Bits"),),
    "tap_spiral_point": (("Threading", "Taps", "Spiral Point Taps"),),
    "screw_socket_head": (("Fasteners", "Screws", "Socket Head Cap Screws"),),
    "screw_flat_head": (("Fasteners", "Screws", "Flat Head Socket Cap Screws"),),
    "bolt_hex": (("Fasteners", "Bolts", "Hex Head Bolts"),),
    "washer_flat": (("Fasteners", "Washers", "Flat Washers"),),
    "hammer_ball_pein": (("Hand Tools", "Striking Tools", "Ball Pein Hammers"),),
    "abrasive_flap_disc": (("Abrasives", "Coated Abrasives", "Flap Discs"),),
}


def all_paths() -> tuple[CategoryPath, ...]:
    return tuple(path for paths in LEAVES.values() for path in paths)


def tree_depths() -> set[int]:
    return {len(path) for path in all_paths()}


def ancestors(path: CategoryPath) -> tuple[CategoryPath, ...]:
    """Every prefix of ``path``, shortest first, including ``path`` itself."""
    return tuple(path[: n + 1] for n in range(len(path)))


#: Which of the ten generic drawings a product type's products show.
#:
#: Written out rather than derived, even though every pair is currently an
#: identity. The two sides mean different things -- the left is a catalog
#: product type, the right is a drawing in :mod:`..render.generic` -- and a
#: product type that gained a second style, or two types that turned out to be
#: the same drawing, would show up here as a pair that no longer matches
#: instead of as nothing at all. ``tests/test_generic.py`` asserts that the
#: right-hand side is exactly the set of drawings that exist.
IMAGE_ID: dict[str, str] = {
    "end_mill_square": "end_mill_square",
    "end_mill_ball": "end_mill_ball",
    "drill_jobber": "drill_jobber",
    "tap_spiral_point": "tap_spiral_point",
    "screw_socket_head": "screw_socket_head",
    "screw_flat_head": "screw_flat_head",
    "bolt_hex": "bolt_hex",
    "washer_flat": "washer_flat",
    "hammer_ball_pein": "hammer_ball_pein",
    "abrasive_flap_disc": "abrasive_flap_disc",
}


def image_id_for(type_key: str) -> str:
    """The generic drawing every product of ``type_key`` shows."""
    return IMAGE_ID[type_key]
