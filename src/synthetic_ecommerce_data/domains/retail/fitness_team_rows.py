"""Fitness, team-sport and racket-sport types of Sports & Outdoors (gen#959, slice 2): paths.

Slice 1 took the department to about 3,300 SKUs at the ceiling build with fishing and golf. Slice 2
adds nine more breadth types, every one a spec of its own in ``type_specs/`` drawn by
:mod:`kit_fitness_team`: exercise bikes, weight plates and weight benches under Yoga & Fitness;
basketballs, volleyballs, shin guards, hockey sticks, pickleball paddles and table tennis bats
under Team & Racket Sports. Each is ``derivable``, so the scaled build draws more styles from it by
the values its titles show. The rows use the department's own brands (Wrenfield, Harbour & Pine
and Larkmoor), so no brand is added to the scale roster.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_fitness_team,  # noqa: F401 -- registers exercise_bike, weight_plate, basketball, ...
)
from synthetic_ecommerce_data.domains.retail.sports_helpers import DEPARTMENT

FIT = (DEPARTMENT, "Yoga & Fitness")
TEAM = (DEPARTMENT, "Team & Racket Sports")
EXERCISE_BIKES = (*FIT, "Exercise Bikes")
WEIGHT_PLATES = (*FIT, "Weights", "Weight Plates")
WEIGHT_BENCHES = (*FIT, "Weight Benches")
BASKETBALLS = (*TEAM, "Basketballs")
VOLLEYBALLS = (*TEAM, "Volleyballs")
SHIN_GUARDS = (*TEAM, "Shin Guards")
HOCKEY_STICKS = (*TEAM, "Hockey Sticks")
PICKLEBALL_PADDLES = (*TEAM, "Pickleball Paddles")
TABLE_TENNIS_BATS = (*TEAM, "Table Tennis Bats")
