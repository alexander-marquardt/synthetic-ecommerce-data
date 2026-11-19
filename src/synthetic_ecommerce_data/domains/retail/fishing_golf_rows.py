"""The Fishing and Golf families of Sports & Outdoors (gen#959, slice 1): paths and brands.

The department held 1,093 SKUs at the ceiling build against the 11,000 of the #837 mix, and no
fishing or golf product at all. Slice 1 adds two families of three types each, every one a spec
of its own in ``type_specs/`` (``fishing_rod``, ``fishing_reel``, ``tackle_box``, ``golf_club``,
``golf_ball``, ``golf_glove``) drawn by :mod:`kit_fishing_golf`. Unlike the earlier Sports
types, these are breadth types (``derivable`` True): the scaled build draws more styles from
each by the values its titles show. The rows are built with :func:`sports_helpers._row`, so they
share the department's colors and its brands; two new invented brands, one per family, widen
the department's brand pool. Every name here is invented.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_fishing_golf,  # noqa: F401 -- registers fishing_rod, fishing_reel, tackle_box, golf_*
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS as _BREADTH_OWNERS
from synthetic_ecommerce_data.domains.retail.sports_helpers import DEPARTMENT

FISHING = (DEPARTMENT, "Fishing")
GOLF = (DEPARTMENT, "Golf")
RODS = (*FISHING, "Fishing Rods")
REELS = (*FISHING, "Fishing Reels")
TACKLE_BOXES = (*FISHING, "Tackle Boxes")
CLUBS = (*GOLF, "Golf Clubs")
BALLS = (*GOLF, "Golf Balls")
GLOVES = (*GOLF, "Golf Gloves")

#: The invented brands of the two families, beside the department's Wrenfield, Harbour & Pine
#: and Larkmoor.
PENNYWHISTLE = "Pennywhistle Angling"
LARCHMERE = "Larchmere Golf"
#: Their owners, stated by every spec of the two families (``TypeSpec.owners``) and here at import,
#: so a row's own ``doc()`` knows its brand's owner before any build has run.
OWNERS = ((PENNYWHISTLE, "third_party"), (LARCHMERE, "third_party"))
for _brand, _owner in OWNERS:
    _BREADTH_OWNERS.setdefault(_brand, _owner)
