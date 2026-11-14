"""The fishing and golf types of gen#959: the print decoys sit in no Fishing or Golf node.

"glove" already names Baseball Gloves, so the golf ball and golf glove decoys carry "golf".
"""

from __future__ import annotations

#: noun -> the category node of the product the noun really names.
NODES: dict[str, str] = {
    "rod": "Fishing Rods",
    "reel": "Fishing Reels",
    "tackle": "Tackle Boxes",
    "club": "Golf Clubs",
    "golf": "Golf",
}
