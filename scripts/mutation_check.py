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
import shlex
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
        "    _bar(ax, half, body_bottom, cut_top, mark)",
        '    _bar(ax, half, body_bottom, cut_top, mark)\n    cv.diameter_callout(\n        ax, -0.2, half * 2, "Ø1/4\\"", "milling", side=1, overhang=0.02, gap=0.02\n    )',
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
        "    return render(drawing_for_record(record), path, profile)",
        '    fig, ax = build(drawing_for_record(record), profile)\n    ax.text(0, BOTTOM - 0.04, str(record.get("sku", "")), ha="center", color=cv.MUTED)\n    return cv.save(fig, path, profile)',
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
    # ---- the marking is a function of the RECORD, never of the identity ---
    #
    # These are the checks the issue exists for. The defect class is an
    # attribute published on every record and read by nothing -- which a
    # mutation harness structurally cannot find, since an unread input has no
    # code to mutate. What CAN be planted is the other half: a channel that
    # reads its attribute, validates it, and then draws something else. Every
    # A-direction mutation below is that shape.
    Mutation(
        "validate the brand's colour and then draw in plain black",
        "render/marking.py",
        '    ink = _lookup(BRAND_INK, str(brand).strip(), "outline-colour", ("brand",))',
        '    _lookup(BRAND_INK, str(brand).strip(), "outline-colour", ("brand",))\n    ink = "#1b1b1b"',
        "tests/test_line_drawings.py -k brand_is_readable",
        "A",
        "the outline colour is the brand, and reads back as the brand",
    ),
    Mutation(
        "make reading a colour back resolve to whichever brand comes first",
        "render/marking.py",
        "    for brand, colour in BRAND_INK.items():\n        if colour.lower() == lowered:\n            return brand",
        "    for brand, colour in BRAND_INK.items():\n        if lowered or colour.lower() == lowered:\n            return brand",
        "tests/test_marking.py -k brand",
        "B",
        "the outline colour is the brand, and reads back as the brand",
    ),
    Mutation(
        "put two brands close enough that one fades through the other",
        "render/marking.py",
        '    "Redmoor": "#e07b10",',
        '    "Redmoor": "#a04000",',
        'tests/test_marking.py tests/test_line_drawings.py -k "blend or brand_is_readable"',
        "",
        "no brand's colour can be mistaken for another's on the page",
    ),
    Mutation(
        "validate the coating and then leave the part unfilled",
        "render/marking.py",
        '        tint = _lookup(FINISH_TINT, found[1], "fill-tint", FINISH_ATTRIBUTES)',
        '        _lookup(FINISH_TINT, found[1], "fill-tint", FINISH_ATTRIBUTES)\n        tint = None',
        "tests/test_line_drawings.py -k coating",
        "A",
        "the fill is the coating the record publishes",
    ),
    Mutation(
        "give every material the same section hatch",
        "render/marking.py",
        '        hatch = _lookup(MATERIAL_HATCH, found[1], "section-hatch", MATERIAL_ATTRIBUTES)',
        '        _lookup(MATERIAL_HATCH, found[1], "section-hatch", MATERIAL_ATTRIBUTES)\n        hatch = "/"',
        "tests/test_line_drawings.py -k material",
        "A",
        "the section hatch is the material the record publishes",
    ),
    Mutation(
        "draw four flutes whatever the record says",
        "render/generic.py",
        "        step = (y1 - y0) / mark.flutes\n        starts = [y0 + step * (k + 0.5) - rise / 2 for k in range(mark.flutes)]",
        "        step = (y1 - y0) / 4\n        starts = [y0 + step * (k + 0.5) - rise / 2 for k in range(4)]",
        "tests/test_line_drawings.py -k flute",
        "A",
        "the flutes drawn are the flutes published",
    ),
    Mutation(
        "invent a flute count for a record that publishes none",
        "render/marking.py",
        "    flutes = None\n    found = _first_published(pairs, (FLUTES_ATTRIBUTE,))",
        "    flutes = 4\n    found = _first_published(pairs, (FLUTES_ATTRIBUTE,))",
        "tests/test_line_drawings.py -k flute",
        "B",
        "the flutes drawn are the flutes published",
    ),
    Mutation(
        "lean every flute right-handed and print the direction underneath",
        "render/generic.py",
        "    hand = mark.lean\n    style = {} if mark.flutes is not None else {\"ls\": (0, (6, 4))}",
        "    hand = 1\n    style = {} if mark.flutes is not None else {\"ls\": (0, (6, 4))}",
        "tests/test_line_drawings.py -k left_hand",
        "",
        "a left-hand tool is drawn leaning the other way",
    ),
    Mutation(
        "give the drawing a property derived from the product id",
        "render/generic.py",
        '    mark = marking_for_line(line["brand"], line["attributes"])',
        '    mark = marking_for_line(line["brand"], line["attributes"])\n    mark = replace(mark, flutes=2 + len(line["product_id"]) % 3)',
        "tests/test_line_drawings.py -k not_a_function_of_the_product_id",
        "A",
        "the drawing is a function of the record and of nothing else",
    ),
    Mutation(
        "let a SKU's dimensions reach the drawing its whole line shares",
        "render/generic.py",
        '    record = {entry["name"]: entry["value"] for entry in line["attributes"]}',
        '    record = {entry["name"]: entry["value"] for entry in line["attributes"]}\n    mark_rows = [e for v in line.get("variants", []) for e in v["attributes"]]\n    line = {**line, "attributes": [*line["attributes"], *mark_rows]}',
        "tests/test_line_drawings.py -k no_sku_of_the_line",
        "B",
        "the drawing is a function of the record and of nothing else",
    ),
    Mutation(
        "truncate the stamp so a long record is only partly shown",
        "render/marking.py",
        '        text = " · ".join(value for _, value in self.rows)',
        '        text = " · ".join(value for _, value in self.rows[:4])',
        "tests/test_line_drawings.py -k stamp_sets_every_published",
        "",
        "the stamp is the whole record's line-scope half",
    ),
    Mutation(
        "build the signature from the attributes common to a type, not each line's own",
        "render/marking.py",
        "    pairs = attribute_pairs(attributes)\n\n    ink = _lookup",
        '    pairs = tuple(p for p in attribute_pairs(attributes) if p[0] in {"Item", "Standards"})\n\n    ink = _lookup',
        "tests/test_line_drawings.py -k exactly_two",
        "",
        "498 of the 500 lines get a drawing of their own",
    ),
    # ---- every product and variant carries an image, both directions ------
    Mutation(
        "leave a product line without an image",
        "catalog/generate.py",
        "            image_id=image_id,\n            drawing=drawing_for(type_key),\n        )",
        '            image_id="",\n            drawing=drawing_for(type_key),\n        )',
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
        'ice_usd": 13.44, "stock": 17, "image_id": "end_mill_square/OST-K663-0001", '
        '"image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/card.png"',
        'ice_usd": 13.44, "stock": 17, "image_id": "end_mill_square/OST-K663-0001", '
        '"image_url": ""',
        "tests/test_catalog_golden.py::test_every_flat_document_carries_an_image_url",
        "A",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "drop the detail image url from one committed nested variant",
        "nested.jsonl",
        '"price_usd": 13.44, "stock": 17, "image_id": "end_mill_square/OST-K663-0001", '
        '"image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/card.png", '
        '"image_detail_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/detail.png"',
        '"price_usd": 13.44, "stock": 17, "image_id": "end_mill_square/OST-K663-0001", '
        '"image_url": "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/end_mill_square/OST-K663-0001/card.png"',
        "tests/test_catalog_golden.py::test_every_nested_line_and_variant_carries_an_image_url",
        "B",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "duplicate a sku in the committed flat catalog",
        "flat.jsonl",
        '{"sku": "19XN98", "product_id": "OST-K663-0001"',
        '{"sku": "80FY44", "product_id": "OST-K663-0001"',
        "tests/test_catalog_golden.py::test_flat_holds_one_document_per_sku",
        "",
        "flat.jsonl is 4,662 documents and 4,662 distinct skus",
        root="golden-catalog",
    ),
    Mutation(
        "point one committed document at a product line that does not exist",
        "flat.jsonl",
        '{"sku": "19XN98", "product_id": "OST-K663-0001"',
        '{"sku": "19XN98", "product_id": "OST-K663-9999"',
        "tests/test_catalog_golden.py::test_flat_covers_exactly_the_product_lines",
        "",
        "the catalog spans exactly 500 product lines",
        root="golden-catalog",
    ),
    Mutation(
        "publish a variant_count that disagrees with its own variants array",
        "nested.jsonl",
        '"variant_count": 9, "variants": [{"sku": "19XN98", "title": "Osterlund High Sp',
        '"variant_count": 10, "variants": [{"sku": "19XN98", "title": "Osterlund High Sp',
        "tests/test_catalog_golden.py::test_nested_lines_account_for_every_sku",
        "",
        "the nested lines account for every sku",
        root="golden-catalog",
    ),
    # ---- Length Under Head is DRAWN, both directions ---------------------
    Mutation(
        "draw the length-under-head dimension against the whole screw",
        "render/fastener.py",
        "        span = geom.length_under_head.inches",
        "        span = geom.total_height",
        'tests/test_fastener.py -k "length_under_head or three_published_lengths"',
        "A",
        "the length under head is a span on the drawing, to its published value",
    ),
    Mutation(
        "print the value in the attribute table and draw no dimension for it",
        "render/fastener.py",
        "    if geom.length_under_head is not None:\n        # The whole shank",
        "    if False:\n        # The whole shank",
        'tests/test_fastener.py -k "length_under_head or three_published_lengths or inked_in_the_drawing"',
        "B",
        "the length under head is a span on the drawing, to its published value",
    ),
    # ---- a record whose lengths disagree is refused, both directions ------
    Mutation(
        "draw a screw whose published lengths contradict each other",
        "render/fastener.py",
        "        if drift > UNDER_HEAD_TOLERANCE_IN:",
        "        if False:",
        "tests/test_fastener.py -k contradict",
        "A",
        "a length under head the other lengths contradict is refused",
    ),
    Mutation(
        "tighten the tolerance past the precision the catalog publishes at",
        "render/fastener.py",
        "UNDER_HEAD_TOLERANCE_IN = 0.01",
        "UNDER_HEAD_TOLERANCE_IN = 0.0",
        "tests/test_fastener.py -k rounding",
        "B",
        "a length under head the other lengths contradict is refused",
    ),
    # ---- the head style decides the SHAPE, both directions ---------------
    Mutation(
        "draw a button head as the cylinder a socket head cap screw has",
        "render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return False",
        'tests/test_fastener.py -k "each_head_style or button_head"',
        "A",
        "each head style draws the shape its record names",
    ),
    Mutation(
        "dome every head that is not countersunk, so socket and button agree again",
        "render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return not self.countersunk",
        "tests/test_fastener.py -k each_head_style",
        "B",
        "each head style draws the shape its record names",
    ),
    # ---- and it decides which line drawing a LINE gets, both directions ---
    Mutation(
        "point the button head style at the socket head drawing",
        "render/generic.py",
        '        "button": "screw_button_head",',
        '        "button": "screw_socket_head",',
        'tests/test_line_drawings.py tests/test_generic.py -k "two_styles or image_does_not_depend"',
        "A",
        "a screw style names its own shape, and two shapes never draw alike",
    ),
    Mutation(
        "draw the low head line with the socket head cap screw's own function",
        "render/generic.py",
        'GenericImage("screw_low_head", "Low Head Socket Cap Screw", _draw_low_head_screw),',
        'GenericImage("screw_low_head", "Low Head Socket Cap Screw", _draw_socket_head_screw),',
        'tests/test_line_drawings.py tests/test_generic.py -k "two_styles or DIFFERENT"',
        "B",
        "a screw style names its own shape, and two shapes never draw alike",
    ),
    # ---- the new silhouettes carry the proportions their standards give ---
    #
    # Planted first as "give the low head drawing a full socket head's
    # proportions", which came back GREEN: the two drawings still differed, in
    # the socket mouth and the end view, so every difference-based check passed
    # while the one difference the record names -- the height of the head --
    # had gone. The proportion tests in test_generic.py were written for this.
    Mutation(
        "give the low head drawing a full socket head's height",
        "render/generic.py",
        "    head_half, head_h = 0.105, 0.062",
        "    head_half, head_h = 0.105, 0.115",
        'tests/test_generic.py -k "drawn_lower or DIFFERENT"',
        "A",
        "the new screw silhouettes are drawn to the proportions their standards give them",
    ),
    # ---- the button head is a DOME, and not a bar, both directions -------
    #
    # The first metric here counted rows wider than the shank, which a dome's
    # height does not drive monotonically. All four of these came back GREEN
    # against it -- including the last, which is the whole shape -- and the
    # measurement in test_generic.py was rewritten for them.
    Mutation(
        "draw the button head's dome as the plain rectangle a bar head has",
        "render/generic.py",
        "                dome_profile(head_half, head_h, seat),",
        "                [(-head_half, seat), (-head_half, _HEAD_TOP), "
        "(head_half, _HEAD_TOP), (head_half, seat)],",
        'tests/test_generic.py -k "dome or head_measurement"',
        "A",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    Mutation(
        "dome the socket head cap screw, so the shape no longer names the style",
        "render/generic.py",
        "    _bar(ax, head_half, seat, _HEAD_TOP, mark)\n    # The socket, drawn as the opening",
        "    _hatched(\n        ax,\n        ax.add_patch(\n            Polygon(\n"
        "                dome_profile(head_half, head_h, seat),\n                closed=True,\n"
        "                fc=mark.tint or cv.BODY_FILL,\n                ec=mark.ink,\n"
        "                lw=cv.LW_BODY,\n                zorder=5,\n            )\n        ),\n"
        "        mark,\n    )\n    # The socket, drawn as the opening",
        'tests/test_generic.py -k "dome or head_measurement"',
        "B",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    # ---- the button head is drawn LOWER than a socket head, both ways -----
    Mutation(
        "draw the button head taller than the socket head cap screw",
        "render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.112, 0.200",
        'tests/test_generic.py -k "drawn_lower"',
        "A",
        "a button head is drawn lower than a socket head cap screw",
    ),
    Mutation(
        "flatten the socket head cap screw to the button head's height",
        "render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_lower"',
        "B",
        "a button head is drawn lower than a socket head cap screw",
    ),
    # ---- and WIDER than one, both ways -----------------------------------
    Mutation(
        "give the button head the socket head cap screw's own width",
        "render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_wider"',
        "A",
        "a button head is drawn wider than a socket head cap screw",
    ),
    Mutation(
        "widen the socket head cap screw past the button head",
        "render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.130, 0.115",
        'tests/test_generic.py -k "drawn_wider"',
        "B",
        "a button head is drawn wider than a socket head cap screw",
    ),
    # ---- the dome arc is the cap the two numbers name, both directions ----
    Mutation(
        "take the rim angle with asin, which draws the minor arc on a tall dome",
        "render/fastener.py",
        "    half_angle = math.atan2(r_head, radius - rise)",
        "    half_angle = math.asin(min(1.0, r_head / radius))",
        'tests/test_fastener.py -k "dome"',
        "A",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "strike the dome about the chord's own half-width instead of the sphere",
        "render/fastener.py",
        "    radius = (r_head * r_head + rise * rise) / (2 * rise)",
        "    radius = r_head",
        'tests/test_fastener.py -k "dome"',
        "B",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "flatten the socket head cap screw to a low head's height",
        "render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.062",
        'tests/test_generic.py -k "drawn_lower or DIFFERENT"',
        "B",
        "the new screw silhouettes are drawn to the proportions their standards give them",
    ),
    # ---- the catalog publishes the attribute at all, both directions ------
    Mutation(
        "publish the length under head on the countersunk line only",
        "catalog/generate.py",
        '                self._length("Length Under Head", under_head_in, style),',
        '                *([self._length("Length Under Head", under_head_in, style)] if flat else []),',
        "tests/test_catalog_generate.py -k length_under_head",
        "A",
        "every screw and bolt line publishes a length under head",
    ),
    Mutation(
        "measure the length under head over the head on every style",
        "catalog/generate.py",
        "            under_head_in = length_in - head.head_height_in if flat else length_in",
        "            under_head_in = length_in",
        "tests/test_catalog_generate.py -k shorter_than_the_length",
        "B",
        "every screw and bolt line publishes a length under head",
    ),
    # ---- the sizes the customer asks for exist, both directions ----------
    Mutation(
        "drop 25 mm back out of the metric cutting series",
        "catalog/series.py",
        "    15.0,\n    16.0,\n    20.0,\n    25.0,\n)",
        "    15.0,\n    16.0,\n    20.0,\n)",
        "tests/test_catalog_coverage.py",
        "A",
        "the cutting diameters the customer asks for exist",
    ),
    Mutation(
        "freeze the coverage rotation, so which sizes exist is luck again",
        "catalog/generate.py",
        "        index = self._rotations.get(key, 0)\n        self._rotations[key] = index + 1\n        return index",
        "        self._rotations[key] = self._rotations.get(key, 0) + 1\n        return 0",
        "tests/test_catalog_coverage.py",
        "B",
        "the cutting diameters the customer asks for exist",
    ),
    # ---- 7/16 exists, and its lengths are the standard's, both ways -------
    Mutation(
        "record 7/16 as absent from the hex bolt standard",
        "data/fastener_standards.json",
        '"size": "7/16",\n        "present_in_source": true,\n        "width_across_flats_in": 0.625,',
        '"size": "7/16",\n        "present_in_source": false,\n        "width_across_flats_in": 0.625,',
        "tests/test_catalog_coverage.py",
        "A",
        "7/16-14 exists, in the standard's own offered lengths",
    ),
    Mutation(
        "offer lengths the standard does not, by scaling the run",
        "catalog/generate.py",
        "        return ordered[start : start + count]",
        "        return [value * 1.5 for value in ordered[start : start + count]]",
        "tests/test_catalog_coverage.py",
        "B",
        "7/16-14 exists, in the standard's own offered lengths",
    ),
    # ---- a grading belongs to one measurement system, both directions ----
    Mutation(
        "grade every bolt on the inch scale, metric ones included",
        "catalog/generate.py",
        'grades = INCH_GRADES if head.published_unit == "in" else METRIC_GRADES',
        "grades = INCH_GRADES",
        "tests/test_catalog_coverage.py",
        "A",
        "a bolt never carries a grading from the other measurement system",
    ),
    Mutation(
        "grade every bolt on the metric scale, inch ones included",
        "catalog/generate.py",
        'grades = INCH_GRADES if head.published_unit == "in" else METRIC_GRADES',
        "grades = METRIC_GRADES",
        "tests/test_catalog_coverage.py",
        "B",
        "a bolt never carries a grading from the other measurement system",
    ),
    # ---- the parametric query resolves, both directions -------------------
    Mutation(
        "take the zinc finish off the hex bolt rotation",
        "catalog/generate.py",
        'HEX_BOLT_FINISHES: tuple[str, ...] = ("Zinc Plated", "Plain", "Hot Dip Galvanized")',
        'HEX_BOLT_FINISHES: tuple[str, ...] = ("Plain", "Hot Dip Galvanized")',
        "tests/test_catalog_coverage.py",
        "A",
        "the customer's parametric query has an answer",
    ),
    Mutation(
        "take Grade 8 off the inch grading rotation",
        "catalog/generate.py",
        'INCH_GRADES: tuple[str, ...] = ("Grade 5", "Grade 8")',
        'INCH_GRADES: tuple[str, ...] = ("Grade 5",)',
        "tests/test_catalog_coverage.py",
        "B",
        "the customer's parametric query has an answer",
    ),
    # ---- a size is not locked to one grading and one finish, both ways ----
    #
    # Direction A is the regression an adversarial review caught: the wrap
    # step alone leaves the three METRIC standards -- nine lines each, nine
    # sizes each -- replaying identical wheel positions, and 9 of the 15
    # published sizes came out locked. The first version of the guard grouped
    # by (standard, size), so every metric group held one line, was skipped,
    # and the check ran only on the inch half that was not broken.
    Mutation(
        "let every hex bolt standard start its wheels at the same position",
        "catalog/generate.py",
        "        phase = step + step // len(sizes) + HEX_BOLT_PHASE.index(standard)",
        "        phase = step + step // len(sizes)",
        "tests/test_catalog_coverage.py -k locked",
        "A",
        "one thread size is not locked to one grading or one finish",
    ),
    Mutation(
        "let the size, grading and finish wheels turn in step",
        "catalog/generate.py",
        "        phase = step + step // len(sizes) + HEX_BOLT_PHASE.index(standard)",
        "        phase = step",
        "tests/test_catalog_coverage.py -k locked",
        "B",
        "one thread size is not locked to one grading or one finish",
    ),
    # ---- the metric spelling the policy bridges, both directions ----------
    Mutation(
        "publish metric dimensions to no decimal places, so 25.00mm becomes 25mm",
        "catalog/formats.py",
        '    (LengthStyle("mm", "mm", "decimal", places=2), 0.55),',
        '    (LengthStyle("mm", "mm", "integer"), 0.55),',
        "tests/test_catalog_coverage.py",
        "A",
        "the catalog still spells a 25 mm cutting diameter 25.00mm",
    ),
    Mutation(
        "publish metric dimensions to four places instead of two",
        "catalog/formats.py",
        '    (LengthStyle("mm", "mm", "decimal", places=2), 0.55),',
        '    (LengthStyle("mm", "mm", "decimal", places=4), 0.55),',
        "tests/test_catalog_coverage.py",
        "B",
        "the catalog still spells a 25 mm cutting diameter 25.00mm",
    ),
    # ---- every offered fastener size reaches a line, both directions ------
    Mutation(
        "toss a coin for a screw line's measurement system instead of alternating",
        "catalog/generate.py",
        '        metric = self._rotate(f"system:{type_key}", 2) == 0',
        "        metric = rng.random() < 0.5",
        "tests/test_catalog_coverage.py",
        "A",
        "every size a fastener standard offers reaches a document",
    ),
    Mutation(
        "draw a screw line's size at random instead of rotating",
        "catalog/generate.py",
        '        size = sizes[self._rotate(f"size:{type_key}:{standard}", len(sizes))]',
        "        size = rng.choice(sizes)",
        "tests/test_catalog_coverage.py",
        "B",
        "every size a fastener standard offers reaches a document",
    ),
    # ---- no two SKUs of a line share a title, both directions -------------
    Mutation(
        "stop repairing the titles that tell a shopper nothing",
        "catalog/generate.py",
        "        if identifying is None or len(published) < 2:\n            return titles",
        "        return titles",
        "tests/test_catalog_titles.py",
        "A",
        "no two SKUs of one line share a title",
    ),
    Mutation(
        "repair only exact duplicates, the way the first version did",
        "catalog/generate.py",
        "            alone = [\n                value\n                for name, value in mine.items()",
        "            alone = [\n                value\n                for name, value in [*mine.items(), (None, title.text)]",
        "tests/test_catalog_titles.py",
        "B",
        "no two SKUs of one line share a title",
    ),
    # ---- the description is a tier of its own, both directions ------------
    Mutation(
        "put the line title back in the description field",
        "catalog/generate.py",
        '        return f"{title.text} - {\', \'.join(details)}"',
        '        return f"{draft.brand} {draft.series} -- {draft.item}"',
        "tests/test_catalog_titles.py",
        "A",
        "the description names what distinguishes the SKU",
    ),
    Mutation(
        "leave the SKU's own attributes out of the description",
        "catalog/generate.py",
        "        named = title.attribute_names()\n        details: list[str] = []",
        "        named = {a.name for a in attributes}\n        details: list[str] = []",
        "tests/test_catalog_titles.py",
        "B",
        "the description names what distinguishes the SKU",
    ),
    # ---- a title names a value, not a substring of one, both directions ---
    Mutation(
        "ask whether the title CONTAINS the value instead of states it",
        "catalog/naming.py",
        "    if not value:\n        return False\n    at = text.find(value)",
        "    if not value:\n        return False\n    return value in text\n    at = text.find(value)",
        "tests/test_catalog_titles.py",
        "A",
        "a title names a value as a value",
    ),
    Mutation(
        "treat every title as already naming everything, so nothing is repaired",
        "catalog/naming.py",
        "    if not value:\n        return False\n    at = text.find(value)",
        "    if not value:\n        return False\n    return True\n    at = text.find(value)",
        "tests/test_catalog_titles.py",
        "B",
        "a title names a value as a value",
    ),
    # ---- a published value is a token, not prose, both directions ---------
    Mutation(
        "let the stamp break a published value at its hyphen",
        "render/marking.py",
        "            tuple(textwrap.wrap(text, width=columns, break_on_hyphens=False)) if text else ()",
        "            tuple(textwrap.wrap(text, width=columns, break_on_hyphens=True)) if text else ()",
        "tests/test_marking.py -k hyphen",
        "A",
        "the card stamp sets every published value and nothing else",
    ),
    Mutation(
        "drop the last value off the card stamp",
        "render/marking.py",
        '        text = " \u00b7 ".join(value for _, value in self.rows)',
        '        text = " \u00b7 ".join(value for _, value in self.rows[:-1])',
        "tests/test_line_drawings.py -k stamp_sets_every_published_value",
        "B",
        "the card stamp sets every published value and nothing else",
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


class AmbiguousSelector(ValueError):
    """A selector carries two ``-k`` filters, so pytest silently uses one.

    ``a.py -k one b.py -k two`` looks like "these two filters, one per file"
    and is really "the second filter, applied to both" -- which ran a file
    with a filter that matched nothing in it and reported the mutation as not
    caught. Found by a mutation that came back green for the wrong reason, so
    the shape is refused rather than documented.
    """


def run(selector: str) -> bool:
    """True when the selector is GREEN."""
    # ``shlex`` rather than ``str.split``: a filter is written
    # ``-k "x or y"`` and splitting on whitespace hands pytest four arguments,
    # one of which is a stray quote. That fails the run for a reason that has
    # nothing to do with the mutation, and reports as "not caught".
    argv = shlex.split(selector)
    if argv.count("-k") > 1:
        raise AmbiguousSelector(
            f"{selector!r} has two -k filters; pytest keeps the last one. Write "
            'one filter: `a.py b.py -k "x or y"`.'
        )
    _drop_bytecode()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "--no-header", *argv],
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
