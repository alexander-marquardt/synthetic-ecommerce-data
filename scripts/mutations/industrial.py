"""Mutations that plant a defect in the rest of the industrial domain and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- hammers: the incidental-word decoy's indexed title (gen#320) ------
    # The ranking and word-count tests read the COMMITTED golden, so a source defect reds
    # them only through the golden's drift test; this row proves that link holds.
    Mutation(
        "hammer decoy: an incidental-word decoy keeps its brand and size in the title",
        "domains/industrial/hammers.py",
        "            bare_title=bare,\n",
        "            bare_title=False,\n",
        "tests/test_catalog_golden.py",
        "A",
        "the short indexed title of the incidental-word decoy",
    ),
    # ---- standards: the published value, both directions -----------------
    Mutation(
        "read the actual head diameter where the standard publishes the theoretical one",
        "domains/industrial/standards.py",
        '            head_dia_in=row["head_diameter_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        '            head_dia_in=row["head_diameter_actual_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        "tests/test_catalog_standards.py",
        "A",
        "the published #10 flat head is reproduced exactly",
    ),
    Mutation(
        "convert an inch standard as though it were metric",
        "domains/industrial/standards.py",
        '            head_dia_in=row["head_diameter_in"],\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        '            head_dia_in=row["head_diameter_in"] / MM_PER_INCH,\n            head_height_in=row["head_height_in"],\n            threads_per_inch=row["threads_per_inch"],\n            pitch_mm=None,\n            drive_size_in=row["hex_socket_across_flats_in"],\n            major_dia_in=INCH_MAJOR_DIA[size],\n        )\n    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")',
        "tests/test_catalog_standards.py",
        "B",
        "the published #10 flat head is reproduced exactly",
    ),
    Mutation(
        "back-fill a size the standard does not define",
        "domains/industrial/standards.py",
        '    return tuple(row["size"] for row in rows(standard) if row.get("present_in_source"))',
        '    return tuple(row["size"] for row in rows(standard))',
        "tests/test_catalog_standards.py",
        "",
        "a size the standard omits is refused, not invented",
    ),
    # ---- roller chain: the strand count moves the price (#36) ----
    Mutation(
        "roller chain: a double strand chain prices as a single strand one",
        "domains/industrial/product_types/motion/roller_chain.py",
        "STRANDS[2]: 1.9,",
        "STRANDS[2]: 1.0,",
        "tests/test_type_roller_chain.py",
        "more_strands_cost_more_in_every_same_spec_set",
        "more strands cost more in every same-spec set",
    ),
    Mutation(
        "roller chain: a triple strand chain prices under a double strand one",
        "domains/industrial/product_types/motion/roller_chain.py",
        "STRANDS[3]: 2.8}",
        "STRANDS[3]: 1.5}",
        "tests/test_type_roller_chain.py",
        "more_strands_cost_more_in_every_same_spec_set",
        "more strands cost more in every same-spec set",
    ),
    Mutation(
        "type seam: breadth.rows() skips ensure_registered",
        "domains/industrial/breadth.py",
        "    typespec.ensure_registered()\n    return _ROWS\n",
        "    return _ROWS\n",
        "tests/test_type_seam.py::test_the_breadth_rows_include_the_type_modules_rows_on_a_first_read",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: breadth registers the type modules at import again",
        "domains/industrial/breadth.py",
        "\n\nregister()\n\n",
        "\n\nregister()\ntypespec.ensure_registered()\n\n",
        "tests/test_a_type_module_imported_first.py::test_a_type_module_imported_first_still_registers[synthetic_ecommerce_data.domains.industrial.product_types.raw_materials.ball_stock_precision]",
        "",
        "a type module or discovery can be a process's first import",
    ),
    Mutation(
        "type seam: a type module row repeating a YAML row is not refused",
        "domains/industrial/breadth.py",
        "    if any(existing.key == row.key for existing in _ROWS):",
        "    if False:",
        "tests/test_type_seam.py::test_a_type_module_row_that_repeats_a_yaml_row_is_refused",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    # A type states its per-type entries on its TypeSpec, once (#48, #61).
    Mutation(
        "type seam: applicable never reads a type module's CLAIMS rule",
        "domains/industrial/conformance.py",
        "    rule = CLAIMS.get(type_key)",
        "    rule = None",
        (
            "tests/test_type_registration.py::"
            "test_a_planted_type_reaches_every_per_type_table_from_its_spec",
            "tests/test_type_registration.py::"
            "test_an_inch_line_of_the_planted_type_claims_what_its_spec_says",
        ),
        "",
        "a type's spec reaches every per-type table",
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
    # ---- cross-references and near-miss threads ----------------------------
    Mutation(
        "print the key-to-screw table one screw size off",
        "domains/industrial/compat.py",
        "            table[size] = (nominal_key_in(head.drive_size_in, metric), standard)",
        "            table[size] = (nominal_key_in(head.drive_size_in * 1.25, metric), standard)",
        (
            "tests/test_compatibility_text.py -k key_to_screw",
            "tests/test_compatibility_text.py -k every_compatibility_sentence_holds",
        ),
        "A",
        "every compatibility sentence is a fact of a standard's table",
    ),
    Mutation(
        "let a washer claim a socket head cap screw's standard",
        "domains/industrial/conformance.py",
        '        out.extend(("ISO 7089", "DIN 125-A"))',
        '        out.extend(("ISO 7089", "DIN 125-A", "DIN 912"))',
        "tests/test_catalog_facts.py -k claimed_standard_applies",
        "A",
        "every fact a record states is real",
    ),
    Mutation(
        "let an inch R-series bearing claim the metric ABMA 20 again",
        "domains/industrial/conformance.py",
        '        if metric:\n            out.extend(("ISO 15", "ISO 492", "ABMA 20"))',
        '        out.extend(("ISO 15", "ISO 492", "ABMA 20") if metric else ("ABMA 20",))',
        "tests/test_catalog_facts.py -k inch_bearing_claims_no_metric",
        "A",
        "a bearing claims only its own measurement system's standards",
    ),
    Mutation(
        "stop writing the tap drill's threads in parts",
        "domains/industrial/compat.py",
        '    return f"Tap drill for {named} threads{thread_gloss(named)}."',
        '    return f"Tap drill for {named} threads."',
        "tests/test_glued_thread_sizes.py -k m12_is_found_by_m12",
        "",
        "a glued metric size is also written in its parts",
    ),
    # Every name starts "variant bounds doc:", so `--only "variant bounds doc:"`
    # re-runs the rows that hold docs/adding-a-type.md to the build's bounds (#252).
    Mutation(
        "variant bounds doc: the knob's maximum moves off the doc's",
        "domains/industrial/product_split.py",
        "    ceiling = table[-1][0]\n",
        "    ceiling = table[-1][0] + 1\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_maximum_skus_per_product",
        "",
        "the doc states the most SKUs a product may have",
    ),
    Mutation(
        "variant bounds doc: the median bound moves off the doc's",
        "domains/industrial/product_split.py",
        "        if running >= 0.75:\n",
        "        if running >= 0.9:\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_median_bound",
        "",
        "the doc states the largest median of a deep type",
    ),
    Mutation(
        "variant bounds doc: the product floor moves off the doc's",
        "domains/industrial/product_split.py",
        "MEDIAN_MIN_PRODUCTS = 20\n",
        "MEDIAN_MIN_PRODUCTS = 25\n",
        "tests/test_variant_bounds_doc_252.py::test_the_doc_states_the_product_floor_of_the_median_check",
        "",
        "the doc states the product floor of the median check",
    ),
]
