"""Outdoors and winter-sports types of Sports & Outdoors (gen#959, slice 3): paths.

Slice 2 took the department to about 7,500 SKUs at the ceiling build with fitness, team and racket
sports. Slice 3, the last, adds eight more breadth types, every one a spec of its own in
``type_specs/`` drawn by :mod:`kit_outdoor_winter`: hiking backpacks under a new Hiking family;
coolers and insulated water bottles under Camping; bike lights and bike locks under Cycling; sleds,
snowboards and ski goggles under a new Winter Sports family. Each is ``derivable``, so the scaled
build draws more styles from it by the values its titles show. The rows use the department's own
brands (Wrenfield, Harbour & Pine and Larkmoor), so no brand is added to the scale roster.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_outdoor_winter,  # noqa: F401 -- registers hiking_backpack, cooler, bottle_insul, ...
)
from synthetic_ecommerce_data.domains.retail.sports_helpers import DEPARTMENT

CAMP = (DEPARTMENT, "Camping")
CYCLE = (DEPARTMENT, "Cycling")
WINTER = (DEPARTMENT, "Winter Sports")
HIKING_BACKPACKS = (DEPARTMENT, "Hiking", "Hiking Backpacks")
COOLERS = (*CAMP, "Coolers")
INSULATED_BOTTLES = (*CAMP, "Insulated Water Bottles")
BIKE_LIGHTS = (*CYCLE, "Bike Lights")
BIKE_LOCKS = (*CYCLE, "Bike Locks")
SLEDS = (*WINTER, "Sleds")
SNOWBOARDS = (*WINTER, "Snowboards")
SKI_GOGGLES = (*WINTER, "Ski Goggles")
