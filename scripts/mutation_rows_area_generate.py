"""Mutation rows for the measured generation rates, the title labels, the magnitude spelling and the document shape.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- generate: the measured rates, both directions -------------------
    Mutation(
        "make every tool line a matching-shank line",
        "domains/industrial/generate.py",
        "        shanks_match = rng.random() < cfg.shank_equals_cutting_dia",
        "        shanks_match = True",
        "tests/test_catalog_generate.py",
        "A",
        "the shank == cutting diameter rate is the measured one",
    ),
    Mutation(
        "make no tool line a matching-shank line",
        "domains/industrial/generate.py",
        "        shanks_match = rng.random() < cfg.shank_equals_cutting_dia",
        "        shanks_match = False",
        "tests/test_catalog_generate.py",
        "B",
        "the shank == cutting diameter rate is the measured one",
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
    Mutation(
        "stop counting titles, so the zero-truncation rate has an empty denominator",
        "domains/industrial/measure.py",
        "            titles += 1",
        "            titles += 0",
        "tests/test_catalog_generate.py -k truncated",
        "B",
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
        "never leave a title dimension token unlabelled",
        "domains/industrial/titles.py",
        "                if middle < cfg.title_token_unlabelled:",
        "                if False:",
        "tests/test_catalog_generate.py",
        "A",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "always leave a title dimension token unlabelled",
        "domains/industrial/titles.py",
        "                if middle < cfg.title_token_unlabelled:",
        "                if True:",
        "tests/test_catalog_generate.py",
        "B",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "use one spelling of the measurement-system attribute everywhere",
        "domains/industrial/finishing.py",
        "        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))",
        '        system_name = "Dimension Type"',
        "tests/test_catalog_generate.py",
        "",
        "the measurement-system attribute has more than one spelling",
    ),
    Mutation(
        "let a child redefine a name its line already carries",
        "domains/industrial/generate.py",
        '            retired(keyword_attribute("End Mill Style", style_name)),\n            keyword_attribute("Material", material),',
        '            retired(keyword_attribute("End Mill Style", style_name)),\n            keyword_attribute("Milling Dia.", "0"),\n            keyword_attribute("Material", material),',
        "tests/test_catalog_generate.py",
        "",
        "a child never redefines a line attribute",
    ),
    Mutation(
        "make the catalog non-deterministic",
        "core/typespec.py",
        '    return random.Random(f"{seed}:{type_key}")',
        "    return random.Random()",
        "tests/test_catalog_generate.py",
        "",
        "the same seed produces the same catalog",
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
        "read an inch tap's thread count as millimetres",
        "domains/industrial/generate.py",
        'else Attribute("Threads per Inch", str(pitch), bare_unit="TPI")',
        'else Attribute("Threads per Inch", str(pitch), bare_unit="MMT")',
        "tests/test_catalog_emit.py tests/test_nested_entry_contract.py",
        "",
        "an inch tap's Threads per Inch is TPI, never a length",
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
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: generate"


def rows() -> list[Mutation]:
    return MUTATIONS
