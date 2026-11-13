"""Measure a generated catalog against the statistics it was built to reproduce.

Every rate here is computed the way the reference statistics computed theirs,
and in particular **each defect class is measured against its own
denominator** -- the records that actually carry the attribute pair the class
tests. A rate over the whole catalog would be a different number answering a
different question, and comparing it to the measured one would be comparing
two unlike things.

The point of this module is that the claim "the generator reproduces the
measured distribution" is checkable rather than asserted. Where it does not,
the gap shows up as a number.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.model import Catalog
from synthetic_ecommerce_data.domains.industrial.price_report import PriceTally
from synthetic_ecommerce_data.domains.industrial.product_split import (
    skus_per_product,
    split_products,
)
from synthetic_ecommerce_data.domains.industrial.vocab import (
    MEASUREMENT_SYSTEM_NAMES,
    STANDARDS_NAME,
)


@dataclass(frozen=True)
class Comparison:
    """One measured-against-target row of the report."""

    name: str
    target: float | None
    achieved: float
    numerator: int
    denominator: int
    note: str = ""
    #: The (low, high) a price row must land in, or None for the older rows,
    #: whose bounds live in the tests.
    band: tuple[float, float] | None = None

    @property
    def within(self) -> bool | None:
        if self.band is None:
            return None
        return self.band[0] <= self.achieved <= self.band[1]

    @property
    def delta(self) -> float | None:
        if self.target is None:
            return None
        return self.achieved - self.target


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _unit_of(value: str) -> str | None:
    """Which unit system a published value is written in, or None."""
    text = value.strip().lower()
    if text.endswith("mm"):
        return "mm"
    if text.endswith('"') or text.endswith("in") or text.endswith("in."):
        return "in"
    return None


def measure(catalog: Catalog, config: GeneratorConfig | None = None) -> dict[str, Any]:
    measurement = Measurement(config)
    measurement.add(catalog)
    return measurement.result(catalog.stats)


class Measurement:
    """:func:`measure` taken one part of the catalog at a time (gen#952).

    The build hands it each type as it is built and then drops the type, so what it keeps is
    tallies, per-type summaries and the price census's per-SKU ids, never a product. A part
    holds each of its types whole: a type's SKUs-per-product summary and its price cells are
    read off all of its lines at once. Adding the parts one by one gives the figures adding
    their concatenation would.
    """

    def __init__(self, config: GeneratorConfig | None = None) -> None:
        self.config = config or GeneratorConfig()
        self.lines = self.skus = 0
        self.by_type: Counter[str] = Counter()
        self.skus_by_type: Counter[str] = Counter()
        #: Each SKU's attribute count, summed; :attr:`titles` counts the SKUs.
        self.attribute_entries = 0

        self.shank_both = self.shank_equal = 0
        self.loc_oal_eligible = self.loc_oal_defect = 0
        self.angle_eligible = self.angle_defect = 0
        self.system_eligible = self.system_defect = 0
        self.mixing_eligible = self.mixing_defect = 0

        self.system_names: Counter[str] = Counter()
        self.system_values: Counter[str] = Counter()
        self.suffixes: Counter[str] = Counter()

        self.standards_present = self.standards_multi = self.standards_values = 0
        self.images_present = self.images_diverge = self.images_missing = 0

        self.titles = 0

        self.multivalued_names: Counter[str] = Counter()
        self.names_by_type: dict[str, set[str]] = {}
        self.pair_parents = self.pair_repeated = 0

        self.split_sizes: dict[str, dict[str, Any]] = {}
        self.disagreeing = 0
        self.prices = PriceTally()

    def add(self, catalog: Catalog) -> None:
        """Count ``catalog``'s lines and SKUs in."""
        self.lines += len(catalog.lines)
        self.skus += catalog.sku_count
        for line in catalog.lines:
            self.by_type[line.type_key] += 1
            self.names_by_type.setdefault(line.type_key, set()).update(
                a.name for a in line.attributes
            )

            for child in line.children:
                self.skus_by_type[line.type_key] += 1
                merged = catalog.merged_attributes(line, child)
                self.names_by_type[line.type_key].update(a.name for a in merged)
                self.titles += 1
                self.attribute_entries += len(merged)

                by_name = {a.name: a for a in merged}

                for attribute in merged:
                    if attribute.multivalued:
                        self.multivalued_names[attribute.name] += 1
                    if attribute.name == STANDARDS_NAME:
                        self.standards_present += 1
                        values = attribute.values or (attribute.value,)
                        self.standards_values += len(values)
                        if len(set(values)) > 1:  # distinct values: a repeat is not multi-valued
                            self.standards_multi += 1

                # -- the attribute-role ambiguity rate
                cutting = by_name.get("Milling Dia.")
                shank = by_name.get("Shank Dia.")
                if (
                    cutting is not None
                    and shank is not None
                    and cutting.value_num is not None
                    and shank.value_num is not None
                ):
                    self.shank_both += 1
                    if abs(cutting.value_num - shank.value_num) < 1e-4:
                        self.shank_equal += 1

                # -- defect class 1, against records carrying the pair
                loc = by_name.get("Length of Cut") or by_name.get("Flute Length")
                oal = by_name.get("Overall Length") or by_name.get("Length")
                if (
                    loc is not None
                    and oal is not None
                    and loc.value_num is not None
                    and oal.value_num is not None
                ):
                    self.loc_oal_eligible += 1
                    if loc.value_num > oal.value_num:
                        self.loc_oal_defect += 1

                # -- defect class 2, against records carrying an angle
                angle = by_name.get("Helix Angle") or by_name.get("Point Angle")
                if angle is not None:
                    self.angle_eligible += 1
                    if "degree" not in angle.value.lower():
                        self.angle_defect += 1

                # -- defect class 3, against records carrying both a declared
                #    system and at least one dimension whose unit can be read
                declared_name = next(
                    (name for name, _ in MEASUREMENT_SYSTEM_NAMES if name in by_name), None
                )
                units = {
                    _unit_of(a.value)
                    for a in merged
                    if a.value_num is not None and _unit_of(a.value) is not None
                }
                if declared_name is not None and units:
                    self.system_eligible += 1
                    declared = by_name[declared_name].value
                    declared_metric = declared == "Metric"
                    observed_metric = units == {"mm"}
                    observed_imperial = units == {"in"}
                    if (
                        declared_metric
                        and observed_imperial
                        or not declared_metric
                        and observed_metric
                    ):
                        self.system_defect += 1
                    self.system_names[declared_name] += 1
                    self.system_values[declared] += 1

                # -- unit mixing within one record
                if len(units) >= 1:
                    self.mixing_eligible += 1
                    if len(units) > 1:
                        self.mixing_defect += 1

                # The suffix census covers LENGTHS only. Counting a flute count or
                # an RPM figure as "unitless" would pad that bucket with values
                # that were never going to carry a unit, and the measured suffix
                # partition it is compared against is over dimensions.
                for attribute in merged:
                    if attribute.value_num is None:
                        continue
                    try:
                        parse_length(attribute.value)
                    except DimensionParseError:
                        continue
                    self.suffixes[_unit_of(attribute.value) or "unitless"] += 1

                if child.image_id:
                    self.images_present += 1
                    # Measured, not assumed: an id that does not end in this SKU
                    # is a shared drawing. Every SKU has its own since
                    # elastic/prism-industrial-products#103, so this reads 0.
                    if not child.image_id.endswith("/" + child.sku):
                        self.images_diverge += 1
                else:
                    self.images_missing += 1

        for line in catalog.lines:
            if not any(a.name == STANDARDS_NAME for a in line.attributes):
                continue
            self.pair_parents += 1
            pairs = Counter((a.name, v) for a in line.attributes for v in (a.values or (a.value,)))
            if any(n > 1 for n in pairs.values()):
                self.pair_repeated += 1

        sizes = skus_per_product(catalog)
        twice = sorted(sizes.keys() & self.split_sizes.keys())
        if twice:
            raise ValueError(f"a type came in two parts: {twice}")
        self.split_sizes.update(sizes)
        self.disagreeing += len(split_products(catalog))
        self.prices.add(catalog)

    def result(self, counters: dict[str, Any]) -> dict[str, Any]:
        """The figures over every part added; ``counters`` is the build's counter dict."""
        config = self.config
        title_tokens = counters.get("title_token", 0)
        title_truncated = counters.get("title_label_truncated", 0)

        comparisons = [
            Comparison(
                "shank == cutting diameter",
                config.shank_equals_cutting_dia,
                _rate(self.shank_equal, self.shank_both),
                self.shank_equal,
                self.shank_both,
                "over records carrying both dimensions",
            ),
            Comparison(
                "length of cut > overall length",
                0.0,
                _rate(self.loc_oal_defect, self.loc_oal_eligible),
                self.loc_oal_defect,
                self.loc_oal_eligible,
                "deliberate: the corpus measures 0.0829",
            ),
            Comparison(
                "angle attribute carries a length unit",
                0.0,
                _rate(self.angle_defect, self.angle_eligible),
                self.angle_defect,
                self.angle_eligible,
                "deliberate: the corpus measures 0.0469",
            ),
            Comparison(
                "declared system contradicts value units",
                0.0,
                _rate(self.system_defect, self.system_eligible),
                self.system_defect,
                self.system_eligible,
                "deliberate: the corpus measures 0.0323",
            ),
            Comparison(
                "unit mixing within one record",
                config.unit_mixing_within_record,
                _rate(self.mixing_defect, self.mixing_eligible),
                self.mixing_defect,
                self.mixing_eligible,
                "over records with a readable dimension",
            ),
            Comparison(
                "parent repeats a (name, value) pair",
                config.defect_repeated_pair,
                _rate(self.pair_repeated, self.pair_parents),
                self.pair_repeated,
                self.pair_parents,
                "over parents carrying Standards; the shape reverse_nested exists for (#1)",
            ),
            Comparison(
                "title dimension token unlabelled",
                config.title_token_unlabelled,
                _rate(counters.get("title_token_unlabelled", 0), title_tokens),
                counters.get("title_token_unlabelled", 0),
                title_tokens,
                "over title dimension tokens",
            ),
            Comparison(
                "title dimension token is not the primary dimension",
                config.title_token_not_primary,
                _rate(counters.get("title_token_not_primary", 0), title_tokens),
                counters.get("title_token_not_primary", 0),
                title_tokens,
                "over title dimension tokens",
            ),
            Comparison(
                "title label truncated",
                config.title_label_truncation,
                _rate(title_truncated, self.titles),
                title_truncated,
                self.titles,
                "over titles",
            ),
            # Both image rates are DELIBERATE DEVIATIONS, so the target column
            # shows what this catalog aims at -- every SKU carrying a drawing of
            # its own -- and GeneratorConfig carries the measured figures and the
            # reasons. Showing the corpus rate as the target here would
            # print a permanent, meaningless miss.
            Comparison(
                "image reference missing",
                0.0,
                _rate(self.images_missing, self.titles),
                self.images_missing,
                self.titles,
                "deliberate: the corpus measures 0.1089",
            ),
            Comparison(
                "image id is shared, not the product's own",
                0.0,
                _rate(self.images_diverge, self.images_present),
                self.images_diverge,
                self.images_present,
                "deliberate: the corpus measures 0.7353",
            ),
            Comparison(
                "attributes per record (mean)",
                config.target_attrs_per_record,
                self.attribute_entries / self.titles if self.titles else 0.0,
                self.attribute_entries,
                self.titles,
                "count, not a rate",
            ),
            *self.prices.comparisons(),
        ]

        return {
            "lines": self.lines,
            "skus": self.skus,
            "lines_by_type": dict(self.by_type),
            "skus_by_type": dict(self.skus_by_type),
            "skus_per_product_by_type": dict(sorted(self.split_sizes.items())),
            "products_disagreeing_on_a_product_constant": self.disagreeing,
            "attribute_names_by_type": {k: sorted(v) for k, v in self.names_by_type.items()},
            "total_attribute_entries": self.attribute_entries,
            "comparisons": comparisons,
            "measurement_system_names": dict(self.system_names),
            "measurement_system_values": dict(self.system_values),
            "unit_suffix_distribution": dict(self.suffixes),
            "standards_present": self.standards_present,
            "standards_multivalued": self.standards_multi,
            "standards_total_values": self.standards_values,
            "multivalued_attribute_names": dict(self.multivalued_names),
        }


def unparseable_dimensions(catalog: Catalog) -> list[tuple[str, str, str]]:
    """Dimension-shaped values nothing can range over, with the SKU that has them.

    These are not bugs. They are the defect classes, and this is the list a
    consumer needs in order to know which records will not render.
    """
    out: list[tuple[str, str, str]] = []
    for line, child in catalog.all_skus():
        for attribute in catalog.merged_attributes(line, child):
            if attribute.value_num is not None:
                continue
            if attribute.name in ("Helix Angle", "Point Angle"):
                try:
                    parse_length(attribute.value)
                except DimensionParseError:
                    continue
                out.append((child.sku, attribute.name, attribute.value))
    return out
