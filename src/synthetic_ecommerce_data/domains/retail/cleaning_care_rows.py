"""The Cleaning department's sponges, cloths, tablets and pods (gen#962 slice 3): paths, attributes.

Sponges and cloths sit under ``Cleaning > Cleaning Tools``, dishwasher tablets under
``Cleaning > Kitchen & Surfaces`` and laundry pods under ``Cleaning > Laundry``, beside the
department's mops, dish soaps and detergents. Each type is a spec of its own
(``type_specs/sponges_cloths.py``, ``dishwasher_tablets.py``, ``laundry_pods.py``) drawn by
:mod:`kit_cleaning_care`. The department, the brands, the six main colors, ``packs()``, ``row()``
and ``decoy()`` are slice 1's (:mod:`paper_rows`). A sponge or a cloth is sold in the six main
colors (gen#275); a box of tablets and a tub of pods are sold without a color (``colorless``), as
a roll of white paper is. Every brand here is invented (ruling 2026-10-30, gen#720).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_cleaning_care,  # noqa: F401 -- registers sponge_cloth, tablet_box, pod_tub
)
from synthetic_ecommerce_data.domains.retail.paper_rows import ROOT
from synthetic_ecommerce_data.domains.retail.type_registry import a

SPONGES = (ROOT, "Cleaning Tools", "Sponges & Cloths")
TABLETS = (ROOT, "Kitchen & Surfaces", "Dishwasher Tablets")
PODS = (ROOT, "Laundry", "Laundry Pods")


def sponge(grade: str, kind: str, use: str) -> tuple[tuple, ...]:
    """A sponge's or a cloth's attributes: its grade, its kind and the room it is for."""
    return (a("grade", "Grade", grade), a("kind", "Kind", kind), a("use", "Use", use))


def tablet(formula: str, scent: str, count: str) -> tuple[tuple, ...]:
    """A box of dishwasher tablets' attributes: its formula, its scent and its tablet count."""
    return (a("formula", "Formula", formula), a("scent", "Scent", scent),
            a("tablet_count", "Tablet count", count))  # fmt: skip


def pod(formula: str, scent: str, loads: str) -> tuple[tuple, ...]:
    """A tub of laundry pods' attributes: its formula, its scent and the loads it washes."""
    return (a("formula", "Formula", formula), a("scent", "Scent", scent),
            a("loads", "Loads", loads))  # fmt: skip
