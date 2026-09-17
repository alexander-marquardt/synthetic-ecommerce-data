"""Prove the new tests bite, by breaking the code they guard.

    python scripts/mutation_check.py

A test that passes tells you nothing on its own: it might be asserting
something that cannot fail. So each mutation below plants a specific, plausible
defect in the source and checks that a named test goes red. Where a property
has two directions -- a rate that could be too high or too low, a guarantee
that could be too strict or too lax -- both are planted, because a test that
only catches one direction leaves the other unguarded.

**A mutation that reds nothing is reported as a zero.** It means the test does
not cover that defect, and hiding it would make this whole exercise
decorative.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "synthetic_industrial_products"


@dataclass(frozen=True)
class Mutation:
    name: str
    #: Path relative to ``root``.
    file: str
    old: str
    new: str
    #: The test selector expected to go red.
    tests: str
    #: "A" and "B" label the two directions of one property.
    direction: str = ""
    property_name: str = ""
    #: Path relative to the REPO root that ``file`` hangs off. Defaults to the
    #: generator package; the PRISM customization is a second package, and the
    #: committed field map has to be mutable from here too -- a drift test that
    #: is only ever proven from the DERIVATION side is not proven at all.
    root: str = "src/synthetic_industrial_products"


MUTATIONS: list[Mutation] = [
    # ---- the generic images carry no dimension, both directions ----------
    Mutation(
        "put a diameter callout on a generic drawing",
        "render/generic.py",
        "    _bar(ax, half, body_bottom, cut_top)",
        '    _bar(ax, half, body_bottom, cut_top)\n    cv.diameter_callout(\n        ax, -0.2, half * 2, "Ø1/4\\"", "milling", side=1, overhang=0.02, gap=0.02\n    )',
        "tests/test_generic.py",
        "A",
        "a generic drawing carries no dimension",
    ),
    Mutation(
        "stop DIM being a distinct colour, blinding the whole measurement",
        "render/canvas.py",
        'DIM = "#b03a2e"',
        'DIM = "white"',
        "tests/test_generic.py",
        "B",
        "a generic drawing carries no dimension",
    ),
    # ---- the generic image is not derived from the record, both ways ------
    Mutation(
        "print the SKU on the generic image, as the old fallback did",
        "render/generic.py",
        '    """Write the generic drawing this record\'s product shows."""\n    return render(image_id_for_record(record), path, profile)',
        '    """Write the generic drawing this record\'s product shows."""\n    fig, ax = build(image_id_for_record(record), profile)\n    ax.text(0, BOTTOM - 0.04, str(record.get("sku", "")), ha="center", color=cv.MUTED)\n    return cv.save(fig, path, profile)',
        "tests/test_generic.py",
        "A",
        "the generic image is the same file whatever the record says",
    ),
    Mutation(
        "make a dimensioned drawing ignore its diameter, blinding the control",
        "render/endmill.py",
        "        cut_d=parse_length(require(record, \"Milling Dia.\")),",
        "        cut_d=parse_length('1/4\"') if require(record, \"Milling Dia.\") else None,",
        "tests/test_generic.py",
        "B",
        "the generic image is the same file whatever the record says",
    ),
    # ---- End Mill Style is read, both directions -------------------------
    Mutation(
        "draw every end mill with a square end, whatever the record says",
        "render/endmill.py",
        "    published = str(require(record, \"End Mill Style\")).strip().lower()\n    try:\n        return END_STYLES[published]",
        "    published = str(require(record, \"End Mill Style\")).strip().lower()\n    try:\n        return \"square\" if published else END_STYLES[published]",
        "tests/test_endmill.py tests/test_derivation.py",
        "A",
        "the cutting end comes from the record",
    ),
    Mutation(
        "draw every GENERIC end mill with a ball nose, whatever it is of",
        "render/generic.py",
        "    body_bottom = BOTTOM + (half if ball else 0.0)",
        "    ball = True\n    body_bottom = BOTTOM + (half if ball else 0.0)",
        "tests/test_generic.py",
        "B",
        "the cutting end comes from the record",
    ),
    # ---- a hex head is drawn hexagonal, both directions -------------------
    Mutation(
        "draw a hex head's end view as a circle",
        "render/fastener.py",
        "    if geom.hex_headed:\n        # Six flats, to the published across-flats dimension.",
        "    if False:\n        # Six flats, to the published across-flats dimension.",
        "tests/test_fastener.py",
        "A",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    Mutation(
        "draw EVERY head's end view as a hexagon",
        "render/fastener.py",
        "HEX_HEADED = {\"hex\", \"hex head\", \"hexagon\"}",
        "HEX_HEADED = CYLINDRICAL | COUNTERSUNK",
        "tests/test_fastener.py",
        "B",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    # ---- the length dimension spans the published length, both ways -------
    Mutation(
        "measure a cylindrical head's length OVER the head",
        "render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.total_height\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "A",
        "the length dimension spans the published length",
    ),
    Mutation(
        "measure a countersunk head's length UNDER the head",
        "render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.shank_length\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "B",
        "the length dimension spans the published length",
    ),
    # ---- the flute slope is the helix, both directions --------------------
    Mutation(
        "draw the flute rise from the diameter, not the circumference",
        "render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.cut_d.inches / math.tan(math.radians(self.helix_deg))",
        "tests/test_endmill.py",
        "A",
        "one flute rises half a helix lead across the visible face",
    ),
    Mutation(
        "draw the flute rise as a WHOLE lead instead of half of one",
        "render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.helix_lead",
        "tests/test_endmill.py",
        "B",
        "one flute rises half a helix lead across the visible face",
    ),
    # ---- every published attribute reaches the drawing, both directions ---
    Mutation(
        "ignore which hand the record says the helix is, while still listing it",
        "render/endmill.py",
        '        hand=HANDS.get(hand_raw, 1),',
        "        hand=1,",
        "tests/test_endmill.py",
        "",
        "the hand of the helix comes from the record",
    ),
    Mutation(
        "drop an attribute from the drawing AND from the sheet",
        "render/endmill.py",
        '        ("Coolant Fed", record.get("Coolant Fed", "")),\n',
        "",
        "tests/test_derivation.py",
        "A",
        "every published attribute reaches the drawing or is declared",
    ),
    Mutation(
        "declare an attribute NOT DRAWN that the drawing does draw",
        "render/attrs.py",
        'NOT_DRAWN: dict[str, str] = {\n    # The measurement-system attribute',
        'NOT_DRAWN: dict[str, str] = {\n    "Helix Angle": "a claim that nothing in the drawing depends on it",\n    # The measurement-system attribute',
        "tests/test_derivation.py",
        "B",
        "every published attribute reaches the drawing or is declared",
    ),
    # ---- a renderer refuses rather than defaulting, both directions -------
    Mutation(
        "default a drill's shank diameter to its nominal size",
        "render/drill.py",
        '        shank_d=parse_length(require(record, "Shank Dia.")),',
        '        shank_d=parse_length(record.get("Shank Dia.") or record["Drill Size"]),',
        "tests/test_refusals.py",
        "A",
        "a dimension is refused, never defaulted",
    ),
    Mutation(
        "clamp a self-contradictory washer instead of refusing it",
        "render/washer.py",
        "    if geom.inside_d.inches >= geom.outside_d.inches:",
        "    if False:",
        "tests/test_refusals.py",
        "B",
        "a dimension is refused, never defaulted",
    ),
    # ---- every product and variant carries an image, both directions ------
    Mutation(
        "leave a product line without an image",
        "catalog/generate.py",
        "            image_id=image_id_for(type_key),\n        )",
        '            image_id="",\n        )',
        "tests/test_catalog_generate.py tests/test_catalog_emit.py",
        "A",
        "every product and every variant carries an image that resolves",
    ),
    Mutation(
        "publish a URL for a drawing nothing renders",
        "catalog/taxonomy.py",
        '    "washer_flat": "washer_flat",',
        '    "washer_flat": "washer_flat_plain",',
        "tests/test_catalog_emit.py tests/test_generic.py",
        "B",
        "every product and every variant carries an image that resolves",
    ),
    # ---- the batch driver keeps going (issue #2) -------------------------
    Mutation(
        "abort the batch on the first record it cannot draw",
        "cli.py",
        "                if not keep_going:\n                    raise",
        "                raise",
        "tests/test_cli.py",
        "",
        "a batch skips what it cannot draw and reports it",
    ),
    Mutation(
        "count a refusal as a failure, so a normal catalog run reports failure",
        "cli.py",
        "                bucket = report.refused if isinstance(exc, DECLINED) else report.failed",
        "                bucket = report.failed",
        "tests/test_cli.py",
        "",
        "a refusal is not a failure",
    ),
    # ---- formats: the never-round rule, both directions ------------------
    Mutation(
        "round a magnitude that has no fractional spelling",
        "catalog/formats.py",
        'raise UnpublishableMagnitude(\n        f"{inches} in is not a multiple of 1/{_INCH_DENOMINATORS[-1]}; "\n        "it has no fractional spelling and will not be rounded into one"\n    )',
        "return Fraction(round(inches * 64), 64)",
        "tests/test_catalog_formats.py",
        "A",
        "a magnitude is never rounded to reach a shape",
    ),
    Mutation(
        "refuse a magnitude that DOES have a fractional spelling",
        "catalog/formats.py",
        "    for denominator in _INCH_DENOMINATORS:",
        "    for denominator in ():",
        "tests/test_catalog_formats.py",
        "B",
        "a magnitude is never rounded to reach a shape",
    ),
    Mutation(
        "drop the caller's decimal precision",
        "catalog/formats.py",
        'places = style.places if shape == style.shape else (4 if style.system == "in" else 2)',
        'places = 4 if style.system == "in" else 2',
        "tests/test_catalog_formats.py",
        "",
        "a decimal is written to the precision asked for",
    ),
    # ---- vocab: disjointness, both directions ----------------------------
    Mutation(
        "leak a hammer attribute into the screw vocabulary",
        "catalog/vocab.py",
        '    _spec("Rockwell Hardness", "line", 0.48),',
        '    _spec("Rockwell Hardness", "line", 0.48),\n    _spec("Handle Material", "line", 0.5),',
        "tests/test_catalog_vocab.py tests/test_catalog_generate.py",
        "A",
        "unrelated product types share no vocabulary",
    ),
    Mutation(
        "remove the one name a screw and a hammer legitimately share",
        "catalog/vocab.py",
        '_HAMMER = (\n    _spec("Item", "line"),',
        '_HAMMER = (\n    _spec("Item ", "line"),',
        "tests/test_catalog_vocab.py",
        "B",
        "unrelated product types share no vocabulary",
    ),
    # ---- series: geometry coherence, both directions ---------------------
    Mutation(
        "let the cut run past the end of the tool",
        "catalog/series.py",
        "        if self.length_of_cut_in >= self.overall_length_in:",
        "        if False:",
        "tests/test_catalog_series.py",
        "A",
        "a tool always has a shank left to hold",
    ),
    Mutation(
        "refuse a tool whose geometry is fine",
        "catalog/series.py",
        "        if self.length_of_cut_in >= self.overall_length_in:",
        "        if self.length_of_cut_in < self.overall_length_in:",
        "tests/test_catalog_series.py",
        "B",
        "a tool always has a shank left to hold",
    ),
    Mutation(
        "reorder the measured flute marginal",
        "catalog/series.py",
        "    (4, 0.42),\n    (2, 0.375),",
        "    (4, 0.375),\n    (2, 0.42),",
        "tests/test_catalog_series.py",
        "",
        "flute counts follow the measured marginal",
    ),
    # ---- standards: the published value, both directions -----------------
    Mutation(
        "read the actual head diameter where the standard publishes the theoretical one",
        "catalog/standards.py",
        '            head_dia_in=row["head_diameter_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        '            head_dia_in=row["head_diameter_actual_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        "tests/test_catalog_standards.py",
        "A",
        "the published #10 flat head is reproduced exactly",
    ),
    Mutation(
        "convert an inch standard as though it were metric",
        "catalog/standards.py",
        '            head_dia_in=row["head_diameter_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        '            head_dia_in=row["head_diameter_in"] / MM_PER_INCH,\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        "tests/test_catalog_standards.py",
        "B",
        "the published #10 flat head is reproduced exactly",
    ),
    Mutation(
        "back-fill a size the standard does not define",
        "catalog/standards.py",
        '    return tuple(row["size"] for row in rows(standard) if row.get("present_in_source"))',
        '    return tuple(row["size"] for row in rows(standard))',
        "tests/test_catalog_standards.py",
        "",
        "a size the standard omits is refused, not invented",
    ),
    # ---- noncopy: the guarantee, both directions -------------------------
    Mutation(
        "make the non-copying check always say 'not a copy'",
        "catalog/noncopy.py",
        "    return fingerprint(attributes) in reference_tuple_hashes()",
        "    return False",
        "tests/test_catalog_noncopy.py",
        "A",
        "the non-copying check is neither blind nor paranoid",
    ),
    Mutation(
        "make the non-copying check always say 'copy'",
        "catalog/noncopy.py",
        "    return fingerprint(attributes) in reference_tuple_hashes()",
        "    return True",
        "tests/test_catalog_noncopy.py",
        "B",
        "the non-copying check is neither blind nor paranoid",
    ),
    Mutation(
        "salt the fingerprint so nothing can ever match",
        "catalog/noncopy.py",
        '    canonical = json.dumps(pairs_of(attributes), separators=(",", ":"), ensure_ascii=False)',
        '    canonical = json.dumps(pairs_of(attributes), separators=(",", ":"), ensure_ascii=False) + "salt"',
        "tests/test_catalog_noncopy.py",
        "",
        "the fingerprint matches the one the reference set was built with",
    ),
    Mutation(
        "let a generated SKU wear a reference SKU code",
        "catalog/generate.py",
        "            if code in self._used_skus or code in REFERENCE_SKUS:",
        "            if code in self._used_skus:",
        "tests/test_catalog_noncopy.py",
        "",
        "no generated SKU collides with a real archived one",
    ),
    # ---- generate: the measured rates, both directions -------------------
    Mutation(
        "make every tool line a matching-shank line",
        "catalog/generate.py",
        "        shanks_match = rng.random() < cfg.shank_equals_cutting_dia",
        "        shanks_match = True",
        "tests/test_catalog_generate.py",
        "A",
        "the shank == cutting diameter rate is the measured one",
    ),
    Mutation(
        "make no tool line a matching-shank line",
        "catalog/generate.py",
        "        shanks_match = rng.random() < cfg.shank_equals_cutting_dia",
        "        shanks_match = False",
        "tests/test_catalog_generate.py",
        "B",
        "the shank == cutting diameter rate is the measured one",
    ),
    Mutation(
        "stop injecting the angle-carries-a-length-unit defect",
        "catalog/generate.py",
        "        if self.rng.random() >= self.config.scaled_defect(\n            self.config.defect_angle_carries_length_unit\n        ):\n            return line_attrs",
        "        if True:\n            return line_attrs",
        "tests/test_catalog_generate.py",
        "A",
        "the angle defect occurs at its measured rate",
    ),
    Mutation(
        "inject the angle defect into every line",
        "catalog/generate.py",
        "        if self.rng.random() >= self.config.scaled_defect(\n            self.config.defect_angle_carries_length_unit\n        ):\n            return line_attrs",
        "        if False:\n            return line_attrs",
        "tests/test_catalog_generate.py",
        "B",
        "the angle defect occurs at its measured rate",
    ),
    Mutation(
        "never truncate a title label",
        "catalog/generate.py",
        "        if segments and rng.random() < cfg.scaled_defect(cfg.title_label_truncation):",
        "        if False:",
        "tests/test_catalog_generate.py",
        "A",
        "title labels are truncated at the measured rate",
    ),
    Mutation(
        "truncate every title label",
        "catalog/generate.py",
        "        if segments and rng.random() < cfg.scaled_defect(cfg.title_label_truncation):",
        "        if segments:",
        "tests/test_catalog_generate.py",
        "B",
        "title labels are truncated at the measured rate",
    ),
    Mutation(
        "never leave a title dimension token unlabelled",
        "catalog/generate.py",
        "        if roll < cfg.title_token_unlabelled:",
        "        if False:",
        "tests/test_catalog_generate.py",
        "A",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "always leave a title dimension token unlabelled",
        "catalog/generate.py",
        "        if roll < cfg.title_token_unlabelled:",
        "        if True:",
        "tests/test_catalog_generate.py",
        "B",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "use one spelling of the measurement-system attribute everywhere",
        "catalog/generate.py",
        "        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))",
        '        system_name = "Dimension Type"',
        "tests/test_catalog_generate.py",
        "",
        "the measurement-system attribute has more than one spelling",
    ),
    Mutation(
        "let a child redefine a name its line already carries",
        "catalog/generate.py",
        '            keyword_attribute("Item", item),\n            keyword_attribute("End Mill Style", style_name),',
        '            keyword_attribute("Item", item),\n            keyword_attribute("Milling Dia.", "0"),\n            keyword_attribute("End Mill Style", style_name),',
        "tests/test_catalog_generate.py",
        "",
        "a child never redefines a line attribute",
    ),
    Mutation(
        "make the catalog non-deterministic",
        "catalog/generate.py",
        "        self.rng = random.Random(self.config.seed)",
        "        self.rng = random.Random()",
        "tests/test_catalog_generate.py",
        "",
        "the same seed produces the same catalog",
    ),
    Mutation(
        "ignore the defect-rate knob",
        "catalog/config.py",
        "    def scaled_defect(self, rate: float) -> float:\n        return max(0.0, min(1.0, rate * self.defect_scale))",
        "    def scaled_defect(self, rate: float) -> float:\n        return rate",
        "tests/test_catalog_generate.py",
        "",
        "the defect knob turns defects off",
    ),
    Mutation(
        "ignore the sparsity knob",
        "catalog/config.py",
        "        return max(0.0, min(1.0, presence * self.sparsity_scale))",
        "        return presence",
        "tests/test_catalog_generate.py",
        "",
        "the sparsity knob changes attribute coverage",
    ),
    # ---- model / emit: the document shape --------------------------------
    Mutation(
        "carry a null value_num instead of omitting it",
        "catalog/model.py",
        '        entry: dict[str, Any] = {"name": self.name, "value": self.value}\n        if self.value_num is not None:\n            entry["value_num"] = self.value_num',
        '        entry: dict[str, Any] = {"name": self.name, "value": self.value}\n        entry["value_num"] = self.value_num',
        "tests/test_catalog_emit.py",
        "A",
        "a keyword attribute omits value_num rather than nulling it",
    ),
    Mutation(
        "collapse a multi-valued attribute to a single entry",
        "catalog/model.py",
        '        if self.values is not None:\n            return tuple({"name": self.name, "value": value} for value in self.values)',
        '        if self.values is not None:\n            return ({"name": self.name, "value": self.values[0]},)',
        "tests/test_catalog_emit.py tests/test_catalog_generate.py",
        "B",
        "a multi-valued attribute becomes several nested entries",
    ),
    Mutation(
        "un-nest the nested attributes",
        "catalog/emit.py",
        '            "attributes": {\n                "type": "nested",',
        '            "attributes": {\n                "type": "object",',
        "tests/test_catalog_emit.py",
        "A",
        "the nested mapping nests what has to be nested",
    ),
    Mutation(
        "nest the flat shape's attributes",
        "catalog/emit.py",
        '            "attributes": {\n                "type": "object",\n                "properties": {\n                    "name": {"type": "keyword"},\n                    "value": {"type": "keyword"},\n                    "value_num": {"type": "double"},\n                },\n            },\n            "facets": {"type": "object", "dynamic": True},',
        '            "attributes": {\n                "type": "nested",\n                "properties": {\n                    "name": {"type": "keyword"},\n                    "value": {"type": "keyword"},\n                    "value_num": {"type": "double"},\n                },\n            },\n            "facets": {"type": "object", "dynamic": True},',
        "tests/test_catalog_emit.py",
        "B",
        "the flat mapping deliberately does not nest",
    ),
    Mutation(
        "let a facet field fall back to dynamic text mapping",
        "catalog/emit.py",
        '{"facet_values": {"path_match": "facets.*", "mapping": {"type": "keyword"}}}',
        '{"facet_values": {"path_match": "facets.*", "mapping": {"type": "text"}}}',
        "tests/test_catalog_emit.py",
        "",
        "facet fields are keyword, not analysed text",
    ),
    Mutation(
        "leave a dot in a sanitised field name",
        "catalog/emit.py",
        '    return _NON_WORD.sub("_", name.strip().lower()).strip("_")',
        "    return name.strip().lower()",
        "tests/test_catalog_emit.py",
        "",
        "a sanitised facet key is a legal field name",
    ),
    Mutation(
        "drop attribute values out of the searchable text",
        "catalog/emit.py",
        "    parts = [child.title, line.brand, line.series, *line.category]",
        '    parts = [child.title, line.brand, line.series]\n    return " ".join(part for part in parts if part)\n    parts = []',
        "tests/test_catalog_emit.py",
        "",
        "attribute values are reachable by full text",
    ),
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
    # ---- PRISM field map: the terms-vs-identifier cap --------------------
    Mutation(
        "raise the terms cap so identifiers become facets",
        "prism/derive.py",
        "MAX_TERMS_CARDINALITY = 25",
        "MAX_TERMS_CARDINALITY = 500",
        "tests/test_prism_field_map_drift.py",
        "A",
        "a high-cardinality terms attribute is an identifier, not a facet",
    ),
    Mutation(
        "lower the terms cap so real facets are dropped",
        "prism/derive.py",
        "MAX_TERMS_CARDINALITY = 25",
        "MAX_TERMS_CARDINALITY = 3",
        "tests/test_prism_field_map_drift.py",
        "B",
        "a high-cardinality terms attribute is an identifier, not a facet",
    ),
    # ---- filter_routing.hard must carry every numeric facet -------------
    Mutation(
        "drop a numeric facet from filter_routing.hard (its slider disappears)",
        "data/customization.yaml",
        "    - arbor_hole_size\n",
        "",
        "tests/test_prism_field_map_drift.py",
        "A",
        "every derived numeric facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
    ),
    Mutation(
        "route a name the catalog does not derive as a numeric facet",
        "data/customization.yaml",
        "    - arbor_hole_size\n",
        "    - arbor_hole_size\n    - not_a_catalog_attribute\n",
        "tests/test_prism_field_map_drift.py",
        "B",
        "every derived numeric facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
    ),
    # ---- the structural-collision guard ---------------------------------
    Mutation(
        "let a catalog attribute claim a structural field name",
        "prism/field_map.py",
        '        "attribute_names",\n        "fulltext",',
        '        "attribute_names",\n        "fulltext",\n        "item",',
        "tests/test_prism_field_map_drift.py",
        "",
        "no attribute silently redefines a structural field",
    ),
    # ---- the committed catalog is what the generator writes --------------
    #
    # Two ROOTS, because the golden test has two independent halves and each
    # one has to be proven from its own side. Mutating the GENERATOR proves
    # the sha256 comparison notices a build that moved; mutating the COMMITTED
    # DATA proves the headline invariants notice a corrupted regeneration on
    # their own, without the hashes' help -- which is the whole reason they
    # are asserted against the committed bytes rather than the fresh build.
    Mutation(
        "move the image host without regenerating the catalog",
        "catalog/emit.py",
        'DEFAULT_IMAGE_BASE_URL = "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial"',
        'DEFAULT_IMAGE_BASE_URL = "https://example.invalid/moved/images/industrial"',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "A",
        "the committed catalog is byte-identical to a fresh build",
    ),
    Mutation(
        "emit an eighth file the build does not commit",
        "catalog/cli.py",
        '    (out / "mapping.flat.json").write_text(',
        '    (out / "mapping.extra.json").write_text("{}\\n", encoding="utf-8")\n'
        '    (out / "mapping.flat.json").write_text(',
        "tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output",
        "B",
        "the committed catalog is byte-identical to a fresh build",
    ),
    Mutation(
        "change the default seed and leave the catalog on the old one",
        "catalog/config.py",
        "    seed: int = 20260917",
        "    seed: int = 20260918",
        "tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed",
        "",
        "the committed catalog is the DEFAULT configuration",
    ),
    # ---- the headline invariants, mutated in the COMMITTED DATA ----------
    Mutation(
        "blank one card image url in the committed catalog",
        "flat.jsonl",
        'ice_usd": 8.23, "stock": 18, "image_id": "end_mill_square", "image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/card.png"',
        'ice_usd": 8.23, "stock": 18, "image_id": "end_mill_square", "image_url": ""',
        "tests/test_catalog_golden.py::test_every_flat_document_carries_an_image_url",
        "A",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "drop the detail image url from one committed nested variant",
        "nested.jsonl",
        '"price_usd": 8.23, "stock": 18, "image_id": "end_mill_square", "image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/card.png", "image_detail_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/detail.png"',
        '"price_usd": 8.23, "stock": 18, "image_id": "end_mill_square", "image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/card.png"',
        "tests/test_catalog_golden.py::test_every_nested_line_and_variant_carries_an_image_url",
        "B",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "duplicate a sku in the committed flat catalog",
        "flat.jsonl",
        '{"sku": "60EX58", "product_id": "OST-K663-0001"',
        '{"sku": "98WF97", "product_id": "OST-K663-0001"',
        "tests/test_catalog_golden.py::test_flat_holds_one_document_per_sku",
        "",
        "flat.jsonl is 4,624 documents and 4,624 distinct skus",
        root="golden-catalog",
    ),
    Mutation(
        "point one committed document at a product line that does not exist",
        "flat.jsonl",
        '{"sku": "60EX58", "product_id": "OST-K663-0001"',
        '{"sku": "60EX58", "product_id": "OST-K663-9999"',
        "tests/test_catalog_golden.py::test_flat_covers_exactly_the_product_lines",
        "",
        "the catalog spans exactly 500 product lines",
        root="golden-catalog",
    ),
    Mutation(
        "publish a variant_count that disagrees with its own variants array",
        "nested.jsonl",
        '"variant_count": 8, "variants": [{"sku": "60EX58", "title": "High Speed Steel Sq',
        '"variant_count": 9, "variants": [{"sku": "60EX58", "title": "High Speed Steel Sq',
        "tests/test_catalog_golden.py::test_nested_lines_account_for_every_sku",
        "",
        "the nested lines account for every sku",
        root="golden-catalog",
    ),
]


def _drop_bytecode() -> None:
    """Remove every cached .pyc under the package.

    Python validates a cached .pyc on (mtime, size). A mutation that swaps two
    values of the SAME total length, written back within the same second,
    produces a file the interpreter considers unchanged -- so it runs the stale
    bytecode. That is not hypothetical: the flute-weight mutation below swaps
    0.42 and 0.375 between two lines, which is length-preserving, and the
    restore silently did not take effect. The suite stayed red with a clean
    `git diff`, which is a genuinely confusing state to debug.

    The failure mode that matters is the quiet one: a mutation that does not
    take effect reports GREEN, and GREEN reads as "the test does not cover
    this" when the truth is "the mutation never ran".
    """
    for cached in SRC.rglob("__pycache__"):
        for pyc in cached.glob("*.pyc"):
            pyc.unlink()


def run(selector: str) -> bool:
    """True when the selector is GREEN."""
    _drop_bytecode()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "--no-header", *selector.split()],
        cwd=REPO,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode == 0


def _mutation_is_live(path: Path, mutation: Mutation) -> bool:
    """Confirm the file on disk really carries the mutation.

    A GREEN result is only evidence about the test if the mutation was
    actually present. This is the cheap half of that check; dropping the
    bytecode cache is the other half.
    """
    return mutation.new in path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="substring filter on the mutation name")
    args = parser.parse_args(argv)

    mutations = [m for m in MUTATIONS if not args.only or args.only in m.name]

    print("checking the suite is green before mutating ...")
    for selector in sorted({m.tests for m in mutations}):
        if not run(selector):
            print(f"  {selector} is ALREADY RED -- fix that before mutating")
            return 2
    print("  green\n")

    rows: list[tuple[Mutation, bool, str]] = []
    for mutation in mutations:
        path = REPO / mutation.root / mutation.file
        original = path.read_text(encoding="utf-8")
        if mutation.old not in original:
            rows.append((mutation, False, "MUTATION DID NOT APPLY"))
            print(f"[!!] {mutation.name}: the text to mutate was not found")
            continue
        if original.count(mutation.old) != 1:
            rows.append((mutation, False, "MUTATION TEXT IS AMBIGUOUS"))
            print(f"[!!] {mutation.name}: matches {original.count(mutation.old)} places")
            continue
        path.write_text(original.replace(mutation.old, mutation.new), encoding="utf-8")
        try:
            green = run(mutation.tests)
            if green and not _mutation_is_live(path, mutation):
                rows.append((mutation, False, "MUTATION DID NOT REACH THE INTERPRETER"))
                print(f"[!!] {mutation.name}: source changed but the import did not")
                continue
        finally:
            path.write_text(original, encoding="utf-8")
        caught = not green
        rows.append((mutation, caught, "red" if caught else "GREEN -- NOT CAUGHT"))
        print(f"[{'ok' if caught else '  '}] {mutation.name}: {rows[-1][2]}")

    print("\nre-checking the suite is green after restoring ...")
    ok = all(run(selector) for selector in sorted({m.tests for m in mutations}))
    print("  green" if ok else "  STILL RED -- a mutation was not reverted")

    caught = sum(1 for _, c, _ in rows if c)
    print(f"\n{caught} of {len(rows)} mutations caught")
    missed = [(m, note) for m, c, note in rows if not c]
    if missed:
        print("\nNOT CAUGHT -- these defects would ship green:")
        for mutation, note in missed:
            print(f"  - {mutation.name} ({mutation.property_name}): {note}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
