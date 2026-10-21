"""Mutations that plant a defect in the PRISM customization package's data and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- PRISM field map: the committed artifact vs the derivation -------
    # This property has two sides and BOTH must red. A drift test proven only
    # from the derivation side would still pass if someone hand-edited the
    # committed YAML, which is the likelier mistake of the two.
    Mutation(
        "hand-edit the committed field map's source (the artifact side)",
        "data/field_weights/synthetic_industrial_flat.yaml",
        "    source: facets.abrasive_material\n",
        "    source: facets.abrasive_materials\n",
        "tests/test_prism_field_map_drift.py",
        "A",
        "the committed field map matches a fresh derivation",
        root="src/prism_synthetic_industrial",
    ),
    # ---- filter_routing.hard must carry every numeric facet -------------
    Mutation(
        "drop the routed range axis, so price loses its slider",
        "data/customization.yaml",
        "    - price\n",
        "",
        "tests/test_prism_field_map_drift.py",
        "A",
        "every derived range facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
    ),
    Mutation(
        # Direction B is the one that is a BOOT REFUSAL rather than a missing
        # slider: a routed name that resolves to no range axis makes Engine and
        # Studio refuse to start (elastic/prism#7114). Since #9285 turned every
        # dimensional attribute into a discrete list, routing one of them is
        # exactly that mistake -- so this plants a real former entry rather
        # than an invented name.
        "route a discrete list as though it were a range axis",
        "data/customization.yaml",
        "    - price\n",
        "    - price\n    - drive_size\n",
        "tests/test_prism_field_map_drift.py",
        "B",
        "every derived range facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
    ),
]
