"""Mutations that plant a defect in the generator core (config, emit, formats, naming, noise, standards) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    Mutation(
        "label: the flat document drops the label",
        "core/emit.py",
        '            "product_type_label": line.type_label,\n            "title": child.title,',
        '            "title": child.title,',
        "tests/test_product_type_label_331.py -k documents_carry_the_label",
        "",
        "an industrial document carries its label",
    ),
    Mutation(
        "label: the standard stops requiring the label",
        "core/standard.py",
        '    "product_type_label": (_STR, True),',
        '    "product_type_label": (_STR, False),',
        "tests/test_product_type_label_331.py -k standard_requires_the_label",
        "",
        "a product without a label is refused",
    ),
    Mutation(
        "let a product of a brand drop its template's use line",
        "core/voice.py",
        "        0: USE_LINES.get(type_key, GENERIC_USE_LINES)[voice.use_style],",
        "        0: USE_LINES.get(type_key, GENERIC_USE_LINES)[voice.use_style] if len(facts) % 2 else None,",
        "tests/test_catalog_brands_voice.py -k one_template",
        "A",
        "every brand follows one template per type",
    ),
    # ---- formats: the never-round rule, both directions ------------------
    Mutation(
        "round a magnitude that has no fractional spelling",
        "core/formats.py",
        'raise UnpublishableMagnitude(\n        f"{inches} in is not a multiple of 1/{_INCH_DENOMINATORS[-1]}; "\n        "it has no fractional spelling and will not be rounded into one"\n    )',
        "return Fraction(round(inches * 64), 64)",
        "tests/test_catalog_formats.py",
        "A",
        "a magnitude is never rounded to reach a shape",
    ),
    Mutation(
        "refuse a magnitude that DOES have a fractional spelling",
        "core/formats.py",
        "    for denominator in _INCH_DENOMINATORS:",
        "    for denominator in ():",
        "tests/test_catalog_formats.py",
        "B",
        "a magnitude is never rounded to reach a shape",
    ),
    Mutation(
        "drop the caller's decimal precision",
        "core/formats.py",
        'places = style.places if shape == style.shape else (4 if style.system == "in" else 2)',
        'places = 4 if style.system == "in" else 2',
        "tests/test_catalog_formats.py",
        "",
        "a decimal is written to the precision asked for",
    ),
    # ---- noncopy: the guarantee, both directions -------------------------
    Mutation(
        "make the non-copying check always say 'not a copy'",
        "core/noncopy.py",
        "    return fingerprint(attributes) in reference_tuple_hashes()",
        "    return False",
        "tests/test_catalog_noncopy.py",
        "A",
        "the non-copying check is neither blind nor paranoid",
    ),
    Mutation(
        "make the non-copying check always say 'copy'",
        "core/noncopy.py",
        "    return fingerprint(attributes) in reference_tuple_hashes()",
        "    return True",
        "tests/test_catalog_noncopy.py",
        "B",
        "the non-copying check is neither blind nor paranoid",
    ),
    Mutation(
        "salt the fingerprint so nothing can ever match",
        "core/noncopy.py",
        '    canonical = json.dumps(pairs_of(attributes), separators=(",", ":"), ensure_ascii=False)',
        '    canonical = json.dumps(pairs_of(attributes), separators=(",", ":"), ensure_ascii=False) + "salt"',
        "tests/test_catalog_noncopy.py",
        "",
        "the fingerprint matches the one the reference set was built with",
    ),
    Mutation(
        "type seam: a breadth row file named for another key is read",
        "core/breadth.py",
        "        if f\"{raw['key']}.yaml\" != entry.name:",
        "        if False:",
        "tests/test_type_registration.py::test_a_row_file_named_for_another_key_is_refused",
        "",
        "each breadth row is a file of its own",
    ),
    # ---- no title label is truncated, both directions --------------------
    # The property inverted with the ruling on elastic/prism#9284: titles used
    # to be truncated AT a measured rate and are now truncated at none. Only
    # direction A can plant truncation -- there is no code left to disable --
    # so B mutates the ASSERTION instead of the generator, which is the only
    # way to show the test is not vacuous on a catalog that contains no
    # truncation at all. Without B, a test asserting 0 on data that is 0 for
    # an unrelated reason would look exactly like a test that bites.
    # THE SELECTOR HERE WAS `-k 'mid_word or sheds'`, A DISJUNCTION. The
    # harness's verdict is "pytest went red", so that row was caught the
    # moment EITHER test failed and printed [ok] on the other one's back.
    # Measured after splitting it: `-k sheds` reds and `-k mid_word` stays
    # GREEN -- the string-level test was never proven to bite by this
    # mutation, and the table said otherwise for both.
    #
    # THAT GREEN IS NOT A COVERAGE HOLE, and it is worth saying which it is: a
    # title sliced at the cap usually lands mid-VALUE (``...Solid Carbide,
    # U``), and no prefix match against attribute names finds that.
    # ``test_an_over_long_title_sheds_a_whole_segment_rather_than_being_cut``
    # says so in its own docstring and exists for exactly this reason. So this
    # row names the test that does the catching, and the row below plants the
    # mid-LABEL cut that the string test IS the guard for -- which is what
    # makes both of them proven rather than one of them assumed.
    #
    # ``_selector_names_one_test`` refuses the disjunctive spelling outright,
    # so a row can no longer be satisfied by a test it does not name.
    Mutation(
        "cut an over-long title at the cap instead of shedding a whole segment",
        "core/naming.py",
        "    kept = len(segments)\n"
        "    text = assemble(kept)\n"
        "    while kept > 0 and len(text) > cap:\n"
        "        kept -= 1\n"
        "        text = assemble(kept)",
        "    kept = len(segments)\n    text = assemble(kept)[:cap].rstrip()",
        "tests/test_catalog_titles.py -k sheds",
        "A",
        "no title label is truncated",
    ),
    Mutation(
        "truncate a title's LABEL, the defect the published-string test guards",
        "core/naming.py",
        '        return f"{self.value} {self.label}"',
        '        return f"{self.value} {self.label[:-1]}"',
        "tests/test_catalog_titles.py -k mid_word",
        "A",
        "no title label is truncated",
    ),
    # ---- one spelling per magnitude, both directions ----------------------
    # The defect this guards is the one that made a discrete facet
    # unshippable: 137 published strings for 53 drive sizes, measured on the
    # generation before this one (the catalog now publishes 51 for 51). Both directions
    # re-introduce a SECOND spelling -- A by varying the metric shape, B by
    # varying the imperial suffix -- because a single spelling is the whole
    # property and a test that only caught one system would leave the other
    # free to fragment.
    Mutation(
        "spell a whole number of millimetres two ways",
        "core/formats.py",
        'METRIC_CANONICAL = LengthStyle("mm", "mm", "integer")',
        'METRIC_CANONICAL = LengthStyle("mm", "mm", "decimal", places=2)',
        "tests/test_catalog_coverage.py -k one_spelling",
        "A",
        "one magnitude has one spelling",
    ),
    Mutation(
        "publish imperial dimensions with a trailing 'in' instead of the double-prime",
        "core/formats.py",
        'IMPERIAL_CANONICAL = LengthStyle("in", \'"\', "fraction")',
        'IMPERIAL_CANONICAL = LengthStyle("in", " in", "fraction")',
        "tests/test_catalog_formats.py -k canonical_spellings_are_the_ones",
        "B",
        "one magnitude has one spelling",
    ),
    Mutation(
        "ignore the defect-rate knob",
        "core/config.py",
        "    def scaled_defect(self, rate: float) -> float:\n        return max(0.0, min(1.0, rate * self.defect_scale))",
        "    def scaled_defect(self, rate: float) -> float:\n        return rate",
        "tests/test_catalog_generate.py",
        "",
        "the defect knob turns defects off",
    ),
    Mutation(
        "ignore the sparsity knob",
        "core/config.py",
        "        return max(0.0, min(1.0, presence * self.sparsity_scale))",
        "        return presence",
        "tests/test_catalog_generate.py",
        "",
        "the sparsity knob changes attribute coverage",
    ),
    # ---- model / emit: the document shape --------------------------------
    Mutation(
        "carry a null unit code instead of omitting it",
        "core/entry.py",
        '    if match is None or unit is None:\n        return {"value": published}',
        '    if match is None or unit is None:\n        return {"value": published, "unit_code": None}',
        "tests/test_catalog_emit.py",
        "A",
        "an unmeasured attribute omits the unit parts rather than nulling them",
    ),
    Mutation(
        # elastic/prism#9877: a TPI entry's canonical is its pitch length,
        # 127/5 / n mm. The count itself is the wrong number this plants.
        "store a thread count's canonical as the bare count, not its pitch length",
        "core/entry.py",
        "        return float(RECIPROCAL_PER_UNIT[unit] / exact)",
        "        return float(exact)",
        (
            "tests/test_nested_entry_contract.py -k hand_worked",
            "tests/test_nested_entry_contract.py -k magnitude_unit_code_and_value_canonical",
            "tests/test_nested_entry_contract.py -k published_spelling",
        ),
        "",
        "a TPI entry's canonical is the ruled reciprocal length",
    ),
    Mutation(
        "collapse a multi-valued attribute to a single entry",
        "core/model.py",
        "        values = self.values if self.values is not None else (self.value,)",
        "        values = (self.value,)",
        "tests/test_catalog_emit.py tests/test_catalog_generate.py",
        "B",
        "a multi-valued attribute becomes several nested entries",
    ),
    Mutation(
        "un-nest the nested attributes",
        "core/emit.py",
        '            "attributes": {\n                "type": "nested",',
        '            "attributes": {\n                "type": "object",',
        "tests/test_catalog_emit.py",
        "A",
        "the nested mapping nests what has to be nested",
    ),
    Mutation(
        "nest the flat shape's attributes",
        "core/emit.py",
        '            "attributes": {\n                "type": "object",\n                "properties": {\n                    "key": {"type": "keyword"},\n                    "name": {"type": "keyword"},\n                    "value": {"type": "keyword"},\n                    "unit_code": {"type": "keyword"},\n                    "value_canonical": {"type": "double"},\n                },\n            },\n            "facets": {"type": "object", "dynamic": True},',
        '            "attributes": {\n                "type": "nested",\n                "properties": {\n                    "key": {"type": "keyword"},\n                    "name": {"type": "keyword"},\n                    "value": {"type": "keyword"},\n                    "unit_code": {"type": "keyword"},\n                    "value_canonical": {"type": "double"},\n                },\n            },\n            "facets": {"type": "object", "dynamic": True},',
        "tests/test_catalog_emit.py",
        "B",
        "the flat mapping deliberately does not nest",
    ),
    Mutation(
        "let a facet field fall back to dynamic text mapping",
        "core/emit.py",
        '{"facet_values": {"path_match": "facets.*", "mapping": {"type": "keyword"}}}',
        '{"facet_values": {"path_match": "facets.*", "mapping": {"type": "text"}}}',
        "tests/test_catalog_emit.py",
        "",
        "facet fields are keyword, not analysed text",
    ),
    Mutation(
        "leave a dot in a sanitised field name",
        "core/entry.py",
        '    return _NON_WORD.sub("_", name.strip().lower()).strip("_")',
        "    return name.strip().lower()",
        "tests/test_catalog_emit.py",
        "",
        "a sanitised facet key is a legal field name",
    ),
    Mutation(
        "drop attribute values out of the searchable text",
        "core/emit.py",
        "    parts = [\n        child.title,\n        line.brand,\n        line.series,\n"
        "        *(letter_case.sentence_case(node) for node in line.category),\n    ]\n",
        '    parts = [child.title, line.brand, line.series]\n    return " ".join(part for part in parts if part)\n    parts = []\n',
        "tests/test_catalog_emit.py",
        "",
        "attribute values are reachable by full text",
    ),
    # ---- the structural-collision guard ---------------------------------
    Mutation(
        "let a catalog attribute claim a structural field name",
        "core/entry.py",
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
        "core/emit.py",
        'IMAGE_ROOT = "industrial"',
        'IMAGE_ROOT = "moved"',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "A",
        "the committed catalog is byte-identical to a fresh build",
    ),
    Mutation(
        "change the default seed and leave the catalog on the old one",
        "core/config.py",
        "    seed: int = 20260917",
        "    seed: int = 20260918",
        "tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed",
        "",
        "the committed catalog is the DEFAULT configuration",
    ),
    Mutation(
        "name the coarse thread's drill on its fine sibling",
        "core/standards_library/tables/metric_tap_drills.json",
        '"thread": "M12x1.5",\n   "drill_mm": 10.5',
        '"thread": "M12x1.5",\n   "drill_mm": 10.2',
        (
            "tests/test_compatibility_text.py -k diameter_less_the_pitch",
            "tests/test_compatibility_text.py -k every_compatibility_sentence_holds",
        ),
        "A",
        "every compatibility sentence is a fact of a standard's table",
    ),
    Mutation(
        "leave the cross-reference out of the searchable text",
        "core/emit.py",
        "    parts.append(child.compatibility)\n",
        "",
        "tests/test_compatibility_text.py -k every_compatibility_sentence_holds",
        "A",
        "every compatibility sentence is a fact of a standard's table",
    ),
    Mutation(
        "leave a metric designation's diameter out of the searchable text",
        "core/emit.py",
        """        parts.extend(f"M{m.group('dia')}" for value in values if (m := _METRIC_THREAD.match(value)))""",
        """        parts.extend(f"M{m.group('dia')}" for value in values if (m := _METRIC_THREAD.match(value)) and False)""",
        "tests/test_compatibility_text.py -k searchable_by_its_diameter",
        "A",
        "a metric designation is searchable by its diameter",
    ),
    Mutation(
        "stop writing the sibling sizes in parts",
        "core/noise.py",
        '    return f"Also available in {named} sizes{thread_gloss(named)}."',
        '    return f"Also available in {named} sizes."',
        "tests/test_glued_thread_sizes.py -k also_written_in_parts",
        "",
        "a glued metric size is also written in its parts",
    ),
    Mutation(
        "write a part the designation does not carry",
        "core/naming.py",
        "        part = f\"M{m['dia']} thread, {m['pitch']} mm pitch\"",
        "        part = f\"M{m['dia']} thread, {m['dia']} mm pitch\"",
        "tests/test_glued_thread_sizes.py -k part_is_a_glued_size",
        "",
        "a glued metric size is also written in its parts",
    ),
    # ---- the copy's noise is true, and moves no attribute ---------------------
    Mutation(
        "claim high speed steel cuts stainless",
        "core/noise.py",
        '    "High Speed Steel": ("aluminum", "brass", "mild steel"),',
        '    "High Speed Steel": ("aluminum", "brass", "mild steel", "stainless steel"),',
        "tests/test_noise_text.py -k every_noise_sentence_is_true",
        "A",
        "every noise sentence is true",
    ),
    Mutation(
        "name the record's own diameter as one it does not fit",
        "core/noise.py",
        "        near = [series[j] for j in (i - 1, i + 1) if 0 <= j < len(series)]",
        "        near = [series[j] for j in (i, i + 1) if 0 <= j < len(series)]",
        "tests/test_noise_text.py -k every_noise_sentence_is_true",
        "A",
        "every noise sentence is true",
    ),
    Mutation(
        "write unit equivalents on half the records",
        "core/noise.py",
        '    "unit_equivalent": 0.175,',
        '    "unit_equivalent": 0.5,',
        "tests/test_noise_text.py -k minority_within_their_bound",
        "A",
        "unit equivalents stay a minority",
    ),
    # ---- 7/16 exists, and its lengths are the standard's, both ways -------
    Mutation(
        "record 7/16 as absent from the hex bolt standard",
        "core/standards_library/tables/fastener_standards.json",
        '"size": "7/16",\n        "present_in_source": true,\n        "width_across_flats_in": 0.625,',
        '"size": "7/16",\n        "present_in_source": false,\n        "width_across_flats_in": 0.625,',
        "tests/test_catalog_coverage.py",
        "A",
        "7/16-14 exists, in the standard's own offered lengths",
    ),
    # ---- a title names a value, not a substring of one, both directions ---
    Mutation(
        "ask whether the title CONTAINS the value instead of states it",
        "core/naming.py",
        "    if not value:\n        return False\n    at = text.find(value)",
        "    if not value:\n        return False\n    return value in text\n    at = text.find(value)",
        "tests/test_catalog_titles.py",
        "A",
        "a title names a value as a value",
    ),
    Mutation(
        "treat every title as already naming everything, so nothing is repaired",
        "core/naming.py",
        "    if not value:\n        return False\n    at = text.find(value)",
        "    if not value:\n        return False\n    return True\n    at = text.find(value)",
        "tests/test_catalog_titles.py",
        "B",
        "a title names a value as a value",
    ),
    Mutation(
        "product-word decoys: the text check ignores the exempt list",
        "core/standard.py",
        'if doc.get("product_id") not in text_exempt',
        "if True",
        "tests/test_retail_scale.py -k 20k_build_meets_the_output_standard",
        "A",
        "a decoy's misleading detail color is exempt from the text check, nothing else is",
    ),
    Mutation(
        "product-word decoys: an ordinary product naming another color is exempt too",
        "core/standard.py",
        'if doc.get("product_id") not in text_exempt',
        "if True",
        "tests/test_retail_product_word_decoys_326.py -k exempt_by_decoy",
        "A",
        "only a declared decoy id is exempt; an ordinary id naming Red with color Black is refused",
    ),
]
