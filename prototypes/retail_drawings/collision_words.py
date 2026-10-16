"""The collision words and how many styles carry each sense (gen#273).

A collision word is one a shopper types and the catalog answers in two kinds of product:
"lemon" is a fruit and a flavor in Food & Drink, and a scent in a dish soap or a shower gel.
:func:`count` measures, per word, the styles of each sense, so a thin side is a number and not
a guess. :data:`TARGET` is the least each side holds ("dozens, not one", gen#154). The measure
runs over ``scale.templates()`` (authored and grocery styles; a derived style only copies one),
and ``retail_figures`` writes it to ``golden-retail/stats.json`` as ``collision_words``.

- ``food``: a Food & Drink style whose title, ``flavor`` or ``variety`` holds the word;
- ``scent``: a style outside Food & Drink whose ``scent`` attribute holds the word. Scent is
  the one key for it (gen#273); a word in a garment's print title is not a scent.
"""

from __future__ import annotations

import re
from typing import Any

#: Words with a food sense and a scent sense, both stocked: the demo's collisions.
WORDS = ("lemon", "orange", "lime", "mint", "vanilla", "honey", "coconut", "almond", "cherry")
#: The least styles each sense of each word holds.
TARGET = 24
FOOD_KEYS = ("flavor", "variety")


def _pattern(word: str) -> re.Pattern[str]:
    return re.compile(rf"\b{word}s?\b", re.IGNORECASE)


def count(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """``word -> {"food": styles, "scent": styles}`` over ``records``."""
    out: dict[str, dict[str, int]] = {w: {"food": 0, "scent": 0} for w in WORDS}
    for rec in records:
        food = rec["department"][0] == "Food & Drink"
        for word in WORDS:
            pat = _pattern(word)
            if food:
                held = pat.search(rec["title"]) or any(
                    a["key"] in FOOD_KEYS and pat.search(str(a["value"])) for a in rec["attributes"]
                )
                out[word]["food"] += bool(held)
            else:
                held = any(
                    a["key"] == "scent" and pat.search(str(a["value"])) for a in rec["attributes"]
                )
                out[word]["scent"] += bool(held)
    return out
