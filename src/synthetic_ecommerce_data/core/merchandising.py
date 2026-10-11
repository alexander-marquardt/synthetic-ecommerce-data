"""The merchandising score: a retailer's own 0-100 ranking preference, per product.

A retailer ranks by more than popularity: margin, a supplier deal, a clearance, a
launch. The score is that blended preference, published as the integer
``merchandising_score`` on a nested product and as ``facets_num.merchandising_score``
on its flat documents (gen#182), so a business-signal boost can point at it.

It is derived, never drawn from the generator's stream, so adding it moves no other
value of a build: a SHA-256 of ``seed``, the product's key and a salt gives each
product its own uniform draws (:func:`unit`), which are the same on every run.

* **Loosely correlated.** The score is a mix of the product's ``signal`` (0-1, from
  the volume the domain does model, see :func:`log_signal`) and an independent draw,
  :data:`SIGNAL_WEIGHT` to the rest. Ranking by it reorders a page that popularity
  alone ranked; it does not repeat it.
* **Strategic pushes.** Of the products whose signal is weak (below
  :data:`WEAK_SIGNAL`), :data:`PUSH_OF_WEAK` get a score of :data:`PUSH_FLOOR` or
  more: a few percent of the catalog, high score on weak popularity.
* **A product with no signal** (a retail style the build gave no sales) takes the
  independent draw alone and is never a push: "weak popularity" needs a popularity.
"""

from __future__ import annotations

import hashlib
import math

#: The share of the score that follows the signal; the rest is independent.
SIGNAL_WEIGHT = 0.5
#: A signal below this is "weak popularity".
WEAK_SIGNAL = 0.4
#: The share of weak-signal products that are strategic pushes.
PUSH_OF_WEAK = 0.2
#: A strategic push scores at least this.
PUSH_FLOOR = 80


def unit(seed: int, key: str, salt: str) -> float:
    """A uniform draw in [0, 1) fixed by ``seed``, ``key`` and ``salt`` alone."""
    digest = hashlib.sha256(f"{seed}:{key}:{salt}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def log_signal(value: float, ceiling: float) -> float:
    """``value`` on a log scale where ``ceiling`` is 1.0, clipped to [0, 1]: sales and
    stock span orders of magnitude, so a linear scale would put every product at 0."""
    return min(1.0, max(0.0, math.log1p(max(value, 0.0)) / math.log1p(ceiling)))


def merchandising_score(seed: int, key: str, signal: float | None) -> int:
    """The 0-100 score of the product ``key`` whose existing signals blend to ``signal``."""
    free = unit(seed, key, "free")
    if signal is None:
        return round(100 * free)
    if signal < WEAK_SIGNAL and unit(seed, key, "push") < PUSH_OF_WEAK:
        return PUSH_FLOOR + round((100 - PUSH_FLOOR) * unit(seed, key, "push-height"))
    return round(100 * (SIGNAL_WEIGHT * signal + (1 - SIGNAL_WEIGHT) * free))


def blend(parts: list[tuple[float, float | None]]) -> float | None:
    """The weighted mean of the ``(weight, value)`` parts that have a value, else ``None``."""
    have = [(w, v) for w, v in parts if v is not None]
    total = sum(w for w, _ in have)
    return sum(w * v for w, v in have) / total if total else None
