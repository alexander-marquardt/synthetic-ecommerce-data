"""Mutation rows for the continuity test that counts magnitudes, not spellings (gen#77).

Each row plants one defect on a changed line of ``prism/derive.py`` or of the roller chain types
and names the test that must go red. Found by ``mutation_row.discover``; ``--only "facet
magnitudes:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "facet magnitudes"

_T = "tests/test_facet_magnitudes_77.py"
_SERIES = f"{_T}::test_a_thirteen_size_series_in_several_spellings_has_thirteen_values[68-4]"
_CHAINS = f"{_T}::test_chains_publish_brand_spellings_and_stay_discrete"
_MOTION = "domains/industrial/product_types/motion"


def rows() -> list[Row]:
    return [
        Row(
            "dispersion counts spellings again",
            "prism/derive.py",
            "return (self.magnitudes or 0) / self.product_magnitudes",
            "return self.cardinality / self.product_values",
            _SERIES,
            "a standard series in several spellings has one value per size",
        ),
        Row(
            "a document's magnitude is its spelling",
            "prism/derive.py",
            "if number is not None and len(spellings) == 1:",
            "if False:",
            (
                _SERIES,
                f"{_T}::test_a_standard_series_past_the_evidence_floor_is_a_discrete_list",
            ),
            "a parsed number is the value, whatever its spelling",
        ),
        Row(
            "a chain is written in the catalog's one spelling again",
            f"{_MOTION}/roller_chain.py",
            'style = feed_style(brand, "in", BRANDS)',
            'style = gen._style("in")',
            _CHAINS,
            "a chain takes its brand's spelling and stays a discrete list",
        ),
        Row(
            "a link is written in the catalog's one spelling again",
            f"{_MOTION}/roller_chain_links.py",
            'style = feed_style(draft.brand, "in", BRANDS)',
            'style = gen._style("in")',
            "tests/test_type_roller_chain_links.py::"
            "test_a_link_publishes_what_it_shares_with_its_chain_exactly_as_the_chain_does",
            "a link is written as the chain of its brand is",
        ),
        Row(
            "a three-decimal feed rounds a size it cannot write",
            f"{_MOTION}/roller_chain.py",
            "while places < MAX_PLACES and abs(round(inches, places) - inches) > 1e-9:",
            "while False:",
            f"{_T}::test_a_brand_feed_never_rounds_a_chain_dimension_into_a_second_magnitude",
            "a chain dimension is one of the table's own magnitudes",
        ),
    ]
