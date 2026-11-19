"""The fitness, team and racket types of gen#959 slice 2: no print decoy sits in their nodes.

"bat" already names Baseball Bats and "tenni" Tennis Rackets, so the table tennis bat decoys carry
"table"; "bike" is the bicycles' word, so the exercise bike decoys carry "exercise".
"""

from __future__ import annotations

#: noun -> the category node of the product the noun really names.
NODES: dict[str, str] = {
    "exercise": "Exercise Bikes",
    "weight": "Weights",
    "bench": "Weight Benches",
    "basketball": "Basketballs",
    "volleyball": "Volleyballs",
    "shin": "Shin Guards",
    "hockey": "Hockey Sticks",
    "pickleball": "Pickleball Paddles",
    "table": "Table Tennis Bats",
}
