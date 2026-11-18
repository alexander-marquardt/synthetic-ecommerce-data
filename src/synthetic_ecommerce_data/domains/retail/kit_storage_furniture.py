"""Own-kind shapes for the storage furniture the kit could not draw (gen#1022, slice 2).

Sideboards, bar cabinets, office storage cabinets, shoe storage and wall shelves, each a flat
front drawing in the kit's house style with the record's fill on the main surface, drawn from
the attributes a record states, as slice 1's shapes (:mod:`kit_home_furniture`) are: the variant
axis that changes how the piece looks is a param, and the drawn count of doors, drawers,
shelves, tiers and stools is the stated count.

===============  ==============================================  ===============================
shape            draws                                           params
===============  ==============================================  ===============================
sideboard        a long low cabinet: a row of drawers over a     doors, drawers, legs
                 row of doors (no door: an open bay), on legs
bar_cabinet      a drinks cabinet: a bottle rack over its        doors, glass_rack, stools
                 doors, glasses hung from a rack, and the
                 stools of a bar set standing in front
storage_cabinet  a tall office cabinet: files on its shelves,    front, shelves, drawers, lock
                 open or behind glass doors, filing drawers
                 under them, a lock
shoe_storage     tiers of shoes on an open rack, or under the    tiers, form, frame
                 cushioned seat of a bench
wall_shelf       boards on a wall, floating, on brackets or on   shelves, mount, layout
                 rails, stacked or staggered
===============  ==============================================  ===============================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. A White piece reads white (gen#226): what stands on a
shelf (books, files, bottles, shoes) is drawn in the kit's book colors and the metal parts in
its metal, and no body is shaded far toward black.

``drawings.render`` (:mod:`synthetic_ecommerce_data.drawings`) is the public call that draws
these shapes in a finish; no generator product uses them yet.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import LW, Fill, register
from synthetic_ecommerce_data.domains.retail.kit_furniture import _rect

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "sideboard": {"doors": ("0", "1", "2", "3", "4"), "drawers": ("0", "1", "2", "3", "4"), "legs": ("tapered", "plinth", "hairpin")},
    "bar_cabinet": {"doors": ("0", "1", "2"), "glass_rack": ("yes", "no"), "stools": ("0", "1", "2", "3")},
    "storage_cabinet": {"front": ("open", "glass"), "shelves": ("1", "2", "3", "4", "5"), "drawers": ("0", "1", "2", "3"), "lock": ("no", "yes")},
    "shoe_storage": {"tiers": ("2", "3", "4", "5"), "form": ("rack", "bench"), "frame": ("wood", "metal")},
    "wall_shelf": {"shelves": ("1", "2", "3", "4"), "mount": ("floating", "bracket", "rail"), "layout": ("stacked", "staggered")},
}  # fmt: skip


def _flat(paint: str, fill: Fill, label: str | None, **params: str) -> list[str]:
    """Red-commit stub: one flat body whatever the params say."""
    return [_rect(60, 140, 280, 120, paint, LW, cls="body")]


register({shape: _flat for shape in PARAMS})
