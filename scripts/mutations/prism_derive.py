"""Mutations that plant a defect in the PRISM field-map derivation (``prism/derive.py``) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    Mutation(
        "move the facet presence floor (the derivation side)",
        "prism/derive.py",
        "MIN_PRESENCE = 0.5",
        "MIN_PRESENCE = 0.6",
        "tests/test_prism_field_map_drift.py",
        "B",
        "the committed field map matches a fresh derivation",
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
    Mutation(
        "figures: the dispersion band's densest end taken over every quantity",
        "prism/derive.py",
        "        densest = max(faceted, key=lambda s: s.dispersion)",
        "        densest = max(quantitative, key=lambda s: s.dispersion)",
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
    # ---- the control follows CONTINUITY, not numeracy, both directions ----
    # The defect on each side is a real one somebody could write. A restores
    # the old rule -- numbers get a slider -- and publishes a range over 53
    # standard hex-key sizes. B pushes the threshold past every attribute so
    # nothing is ever a range, which would break the grocery catalog this rule
    # has to serve next (elastic/prism#9290) while leaving this catalog's
    # output unchanged -- so it is deliberately a mutation that THIS catalog's
    # data cannot reveal, and the test has to bite on the rule itself.
    Mutation(
        "offer a range over any attribute whose values are numbers",
        "prism/derive.py",
        "            self.is_numeric\n            and self.products >= RANGE_MIN_DOCS\n            and self.dispersion >= RANGE_DISPERSION",
        "            self.is_numeric",
        "tests/test_facet_control_rule.py -k continuity",
        "A",
        "a discrete standard set is not offered as a range",
    ),
    Mutation(
        "put the continuity threshold above 1.0, so nothing is ever continuous",
        "prism/derive.py",
        "RANGE_DISPERSION = 0.5",
        "RANGE_DISPERSION = 1.01",
        "tests/test_facet_control_rule.py -k continuity",
        "B",
        "a discrete standard set is not offered as a range",
    ),
]
