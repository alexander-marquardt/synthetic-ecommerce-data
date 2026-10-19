"""Mutation rows for the PRISM field map: the committed artifact against its derivation, and the facet classification.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

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
    Mutation(
        "move the facet presence floor (the derivation side)",
        "prism/derive.py",
        "MIN_PRESENCE = 0.5",
        "MIN_PRESENCE = 0.6",
        "tests/test_prism_field_map_drift.py",
        "B",
        "the committed field map matches a fresh derivation",
    ),
    Mutation(
        "write the committed field map in place, not by replacement (#440)",
        "generate_cli.py",
        '        staged.write_text(render(emit.iter_flat(catalog)), encoding="utf-8")\n        os.replace(staged, target)',
        '        target.write_text(render(emit.iter_flat(catalog)), encoding="utf-8")',
        "tests/test_prism_field_map_drift.py::test_the_field_map_is_replaced_not_rewritten_in_place",
        "",
        "a reader never sees the committed field map cut short",
    ),
    # ---- PRISM field map: numeric vs terms classification ----------------
    Mutation(
        "demand near-total numeric coverage, so dimensions become terms facets",
        "prism/derive.py",
        "NUMERIC_SHARE = 0.5",
        "NUMERIC_SHARE = 0.99",
        "tests/test_prism_field_map_drift.py",
        "A",
        "an attribute's facet TYPE is derived from its parsed values",
    ),
    Mutation(
        "accept any numeric value at all, so text attributes become ranges",
        "prism/derive.py",
        "NUMERIC_SHARE = 0.5",
        "NUMERIC_SHARE = 0.0",
        "tests/test_prism_field_map_drift.py",
        "B",
        "an attribute's facet TYPE is derived from its parsed values",
    ),
    # ---- PRISM field map: the terms-vs-identifier rule (#31, #28) --------
    Mutation(
        "raise the identifier threshold past 1.0 so identifiers become facets",
        "prism/derive.py",
        "IDENTIFIER_DISPERSION = 0.5",
        "IDENTIFIER_DISPERSION = 1.01",
        (
            "tests/test_prism_field_map_drift.py",
            # Not the rendered List Number entry: the declaration withholds
            # that at any threshold.
            "tests/test_facet_control_rule.py -k identifier_threshold_is_the_midpoint",
        ),
        "A",
        "a terms attribute whose values do not repeat is an identifier, not a facet",
    ),
    Mutation(
        "lower the identifier threshold so real facets are dropped",
        "prism/derive.py",
        "IDENTIFIER_DISPERSION = 0.5",
        "IDENTIFIER_DISPERSION = 0.02",
        (
            "tests/test_prism_field_map_drift.py",
            "tests/test_facet_control_rule.py -k standards_and_thread_size",
        ),
        "B",
        "a terms attribute whose values do not repeat is an identifier, not a facet",
    ),
    Mutation(
        "bring back an absolute cap of 25 terms values",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS\n"
        "            and self.dispersion >= IDENTIFIER_DISPERSION",
        "            not self.is_numeric\n            and self.cardinality > 25",
        "tests/test_facet_control_rule.py -k any_size",
        "",
        "the identifier rule does not move with catalog size",
    ),
    Mutation(
        "call a terms attribute an identifier on a handful of products",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS",
        "            not self.is_numeric",
        (
            "tests/test_facet_control_rule.py -k small_terms_attribute",
            "tests/test_prism_field_map_drift.py",
        ),
        "",
        "below the observation floor a terms attribute is offered",
    ),
    Mutation(
        "count the identifier floor in (product, value) pairs again",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS",
        "            not self.is_numeric\n            and self.product_values >= RANGE_MIN_DOCS",
        "tests/test_facet_control_rule.py -k multi_valued",
        "",
        "the evidence floor counts products, so a kit's sizes are one product's",
    ),
    Mutation(
        "put the evidence floor back at 50, where small catalogs flip decisions",
        "prism/derive.py",
        "RANGE_MIN_DOCS = 250",
        "RANGE_MIN_DOCS = 50",
        "tests/test_facet_control_rule.py -k every_decision_is_the_same",
        "A",
        "no decision moves with --lines",
    ),
    Mutation(
        "raise the evidence floor past every attribute, so the ratio decides nothing",
        "prism/derive.py",
        "RANGE_MIN_DOCS = 250",
        "RANGE_MIN_DOCS = 100000",
        "tests/test_facet_control_rule.py -k widest_dispersion",
        "B",
        "no decision moves with --lines",
    ),
    Mutation(
        "ignore the generator's identifier declaration",
        "prism/derive.py",
        "    if stats.name in IDENTIFIER_ATTRIBUTES:",
        "    if False:",
        "tests/test_facet_control_rule.py -k declared_identifier",
        "",
        "a declared identifier is withheld whatever its ratio",
    ),
    Mutation(
        "restate the identifier declaration instead of reading the generator's",
        "prism/derive.py",
        "IDENTIFIER_ATTRIBUTES = frozenset(sentence_case(n) for n in Generator.IDENTIFIER_ATTRIBUTES)",
        'IDENTIFIER_ATTRIBUTES = frozenset({"List Number"})',
        "tests/test_facet_control_rule.py -k reads_the_generators",
        "",
        "a declared identifier is withheld whatever its ratio",
    ),
    Mutation(
        "call an under-floor quantity a standard set below the threshold",
        "prism/derive.py",
        "    if stats.is_numeric and stats.dispersion >= RANGE_DISPERSION:",
        "    if False:",
        "tests/test_facet_control_rule.py -k small_sample",
        "",
        "an under-floor decision names the floor in its reason",
    ),
    Mutation(
        "measure dispersion per SKU document again",
        "prism/derive.py",
        "return (self.magnitudes or 0) / self.product_magnitudes",
        "return (self.magnitudes or 0) / self.present",
        "tests/test_facet_control_rule.py -k products_not_sku_variants",
        "",
        "dispersion counts products, not SKU variants",
    ),
    Mutation(
        "count every SKU's copy of a product-scope value",
        "prism/derive.py",
        '                product_magnitudes[key].add((row["product_id"], magnitude))',
        '                product_magnitudes[key].add((row["sku"], magnitude))',
        "tests/test_prism_field_map_drift.py",
        "",
        "dispersion counts products, not SKU variants",
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

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: PRISM field map"


def rows() -> list[Mutation]:
    return MUTATIONS
