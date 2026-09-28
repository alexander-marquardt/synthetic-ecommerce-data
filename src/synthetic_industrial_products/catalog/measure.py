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

from ..dimensions import DimensionParseError, parse_length
from .config import GeneratorConfig
from .model import Catalog
from .vocab import MEASUREMENT_SYSTEM_NAMES, STANDARDS_NAME


@dataclass(frozen=True)
class Comparison:
    """One measured-against-target row of the report."""

    name: str
    target: float | None
    achieved: float
    numerator: int
    denominator: int
    note: str = ""

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
    config = config or GeneratorConfig()

    by_type: Counter[str] = Counter()
    skus_by_type: Counter[str] = Counter()
    attrs_per_record: list[int] = []

    shank_both = shank_equal = 0
    loc_oal_eligible = loc_oal_defect = 0
    angle_eligible = angle_defect = 0
    system_eligible = system_defect = 0
    mixing_eligible = mixing_defect = 0

    system_names: Counter[str] = Counter()
    system_values: Counter[str] = Counter()
    suffixes: Counter[str] = Counter()

    standards_present = standards_multi = standards_values = 0
    images_present = images_diverge = images_missing = 0

    titles = 0
    title_truncated = 0

    multivalued_names: Counter[str] = Counter()
    names_by_type: dict[str, set[str]] = {}

    for line in catalog.lines:
        by_type[line.type_key] += 1
        names_by_type.setdefault(line.type_key, set()).update(a.name for a in line.attributes)

        for child in line.children:
            skus_by_type[line.type_key] += 1
            merged = catalog.merged_attributes(line, child)
            attrs_per_record.append(len(merged))
            names_by_type[line.type_key].update(a.name for a in merged)
            titles += 1

            by_name = {a.name: a for a in merged}

            for attribute in merged:
                if attribute.multivalued:
                    multivalued_names[attribute.name] += 1
                if attribute.name == STANDARDS_NAME:
                    standards_present += 1
                    values = attribute.values or (attribute.value,)
                    standards_values += len(values)
                    if len(values) > 1:
                        standards_multi += 1

            # -- the attribute-role ambiguity rate
            cutting = by_name.get("Milling Dia.")
            shank = by_name.get("Shank Dia.")
            if (
                cutting is not None
                and shank is not None
                and cutting.value_num is not None
                and shank.value_num is not None
            ):
                shank_both += 1
                if abs(cutting.value_num - shank.value_num) < 1e-4:
                    shank_equal += 1

            # -- defect class 1, against records carrying the pair
            loc = by_name.get("Length of Cut") or by_name.get("Flute Length")
            oal = by_name.get("Overall Length") or by_name.get("Length")
            if (
                loc is not None
                and oal is not None
                and loc.value_num is not None
                and oal.value_num is not None
            ):
                loc_oal_eligible += 1
                if loc.value_num > oal.value_num:
                    loc_oal_defect += 1

            # -- defect class 2, against records carrying an angle
            angle = by_name.get("Helix Angle") or by_name.get("Point Angle")
            if angle is not None:
                angle_eligible += 1
                if "degree" not in angle.value.lower():
                    angle_defect += 1

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
                system_eligible += 1
                declared = by_name[declared_name].value
                declared_metric = declared == "Metric"
                observed_metric = units == {"mm"}
                observed_imperial = units == {"in"}
                if declared_metric and observed_imperial or not declared_metric and observed_metric:
                    system_defect += 1
                system_names[declared_name] += 1
                system_values[declared] += 1

            # -- unit mixing within one record
            if len(units) >= 1:
                mixing_eligible += 1
                if len(units) > 1:
                    mixing_defect += 1

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
                suffixes[_unit_of(attribute.value) or "unitless"] += 1

            if child.image_id:
                images_present += 1
                # Measured, not assumed: an id that does not end in this SKU
                # is a shared drawing. Every SKU has its own since
                # elastic/prism-industrial-products#103, so this reads 0.
                if not child.image_id.endswith("/" + child.sku):
                    images_diverge += 1
            else:
                images_missing += 1

    counters = catalog.stats
    title_tokens = counters.get("title_token", 0)
    title_truncated = counters.get("title_label_truncated", 0)

    comparisons = [
        Comparison(
            "shank == cutting diameter",
            config.shank_equals_cutting_dia,
            _rate(shank_equal, shank_both),
            shank_equal,
            shank_both,
            "over records carrying both dimensions",
        ),
        Comparison(
            "length of cut > overall length",
            config.defect_loc_exceeds_oal,
            _rate(loc_oal_defect, loc_oal_eligible),
            loc_oal_defect,
            loc_oal_eligible,
            "over records carrying the pair",
        ),
        Comparison(
            "angle attribute carries a length unit",
            config.defect_angle_carries_length_unit,
            _rate(angle_defect, angle_eligible),
            angle_defect,
            angle_eligible,
            "over records carrying an angle",
        ),
        Comparison(
            "declared system contradicts value units",
            config.defect_system_contradicts_units,
            _rate(system_defect, system_eligible),
            system_defect,
            system_eligible,
            "over records carrying both",
        ),
        Comparison(
            "unit mixing within one record",
            config.unit_mixing_within_record,
            _rate(mixing_defect, mixing_eligible),
            mixing_defect,
            mixing_eligible,
            "over records with a readable dimension",
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
            _rate(title_truncated, titles),
            title_truncated,
            titles,
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
            _rate(images_missing, titles),
            images_missing,
            titles,
            "deliberate: the corpus measures 0.1089",
        ),
        Comparison(
            "image id is shared, not the product's own",
            0.0,
            _rate(images_diverge, images_present),
            images_diverge,
            images_present,
            "deliberate: the corpus measures 0.7353",
        ),
        Comparison(
            "attributes per record (mean)",
            config.target_attrs_per_record,
            sum(attrs_per_record) / len(attrs_per_record) if attrs_per_record else 0.0,
            sum(attrs_per_record),
            len(attrs_per_record),
            "count, not a rate",
        ),
    ]

    return {
        "lines": len(catalog.lines),
        "skus": catalog.sku_count,
        "lines_by_type": dict(by_type),
        "skus_by_type": dict(skus_by_type),
        "attribute_names_by_type": {k: sorted(v) for k, v in names_by_type.items()},
        "total_attribute_entries": sum(attrs_per_record),
        "comparisons": comparisons,
        "measurement_system_names": dict(system_names),
        "measurement_system_values": dict(system_values),
        "unit_suffix_distribution": dict(suffixes),
        "standards_present": standards_present,
        "standards_multivalued": standards_multi,
        "standards_total_values": standards_values,
        "multivalued_attribute_names": dict(multivalued_names),
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
