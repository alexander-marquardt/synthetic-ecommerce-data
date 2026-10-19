"""Mutation rows for the roller chain strand price and the type seam that registers the type modules.

Moved out of ``mutation_check.py`` without a change to any row (#363): each row keeps its name,
so ``--only`` filters behave as before. ``mutation_row.discover`` finds this file by glob; its
``PREFIX`` only labels the file, because each name below is already the whole name.
"""

from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
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
        "roller chain: one brand's strand counts draw their price noise apart",
        "core/price.py",
        "        and (model is None or attribute.name != model.option_attribute)",
        "        and (model is None or attribute.name != object())",
        "tests/test_type_roller_chain.py",
        "more_strands_cost_more_in_every_same_spec_set",
        "more strands cost more in every same-spec set",
    ),
    # ---- the type seam: a table read registers the type modules (#54) ----
    # Every name starts "type seam:", so `--only "type seam:"` re-runs the
    # review's score. Left out as EQUIVALENT: dropping the ``done`` flag, which
    # ``@cache`` on ``registered()`` already makes a no-op on every later read.
    Mutation(
        "type seam: RegistryTable.__getitem__ skips the registration hook",
        "core/typespec.py",
        "    def __getitem__(self, key: _K) -> _V:\n        ensure_registered()\n",
        "    def __getitem__(self, key: _K) -> _V:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[__getitem__]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.get skips the registration hook",
        "core/typespec.py",
        "    def get(self, key: _K, default: Any = None) -> Any:  # type: ignore[override]\n        ensure_registered()\n",
        "    def get(self, key: _K, default: Any = None) -> Any:  # type: ignore[override]\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[get]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.__contains__ skips the registration hook",
        "core/typespec.py",
        "    def __contains__(self, key: object) -> bool:\n        ensure_registered()\n",
        "    def __contains__(self, key: object) -> bool:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[__contains__]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.__iter__ skips the registration hook",
        "core/typespec.py",
        "    def __iter__(self) -> Iterator[_K]:\n        ensure_registered()\n",
        "    def __iter__(self) -> Iterator[_K]:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[__iter__]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.__len__ skips the registration hook",
        "core/typespec.py",
        "    def __len__(self) -> int:\n        ensure_registered()\n",
        "    def __len__(self) -> int:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[__len__]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.keys skips the registration hook",
        "core/typespec.py",
        "    def keys(self) -> KeysView[_K]:\n        ensure_registered()\n",
        "    def keys(self) -> KeysView[_K]:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[keys]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.values skips the registration hook",
        "core/typespec.py",
        "    def values(self) -> ValuesView[_V]:\n        ensure_registered()\n",
        "    def values(self) -> ValuesView[_V]:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[values]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: RegistryTable.items skips the registration hook",
        "core/typespec.py",
        "    def items(self) -> ItemsView[_K, _V]:\n        ensure_registered()\n",
        "    def items(self) -> ItemsView[_K, _V]:\n",
        "tests/test_type_seam.py::test_every_read_of_a_table_registers_before_it_answers[items]",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: ensure_registered ignores a registration already running",
        "core/typespec.py",
        '    if _REGISTRATION["running"]:\n        raise RegistrationReadError(',
        "    if False:\n        raise RegistrationReadError(",
        "tests/test_type_seam.py::"
        "test_a_table_read_while_registration_runs_is_refused_naming_the_reader",
        "",
        "every read of a type table registers the type modules first",
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
        "type seam: registered() no longer imports breadth",
        "core/typespec.py",
        "        from synthetic_ecommerce_data.domains.industrial import breadth  # noqa: F401, PLC0415\n",
        "",
        "tests/test_type_seam.py::test_registration_brings_in_the_yaml_rows_without_any_type_module",
        "",
        "every read of a type table registers the type modules first",
    ),
    Mutation(
        "type seam: _type_kinds omits the type modules' modelled types",
        "domains/industrial/generate.py",
        '        *((key, "modelled") for key in typespec.modelled()),\n',
        "",
        "tests/test_type_seam.py::test_every_type_is_built_once",
        "",
        "every type module's type is built",
    ),
    Mutation(
        "type seam: a type module's share is not the fallback weight",
        "domains/industrial/generate.py",
        "            weight = cfg.type_weights.get(key, own.share if own else None)",
        "            weight = cfg.type_weights.get(key)",
        "tests/test_type_seam.py::test_a_type_modules_share_sizes_its_type[screw_socket_head]",
        "",
        "every type module's type is built",
    ),
    Mutation(
        "type seam: register skips DRAWING",
        "core/typespec.py",
        "    taxonomy.DRAWING[spec.key] = spec.key\n",
        "",
        "tests/test_type_seam.py::test_a_modelled_module_is_registered_into_every_table[screw_socket_head]",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: register skips STANDARDS_FAMILY",
        "core/typespec.py",
        "    vocab.STANDARDS_FAMILY[spec.key] = spec.standards_family\n",
        "",
        "tests/test_type_seam.py::test_a_modelled_module_is_registered_into_every_table[screw_socket_head]",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: register skips USE_LINES",
        "core/typespec.py",
        "    if spec.use_lines:\n        voice.USE_LINES[spec.key] = spec.use_lines\n",
        "",
        "tests/test_type_seam.py::test_a_modelled_module_is_registered_into_every_table[screw_socket_head]",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: a modelled spec missing a field is not refused",
        "core/typespec.py",
        "    if missing:\n        raise TypeModuleError",
        "    if False:\n        raise TypeModuleError",
        "tests/test_type_seam.py -k missing_a_field_is_refused",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: an unset share is not refused",
        "core/typespec.py",
        '            ("share", spec.share > 0),',
        '            ("share", True),',
        'tests/test_type_seam.py -k "missing_a_field_is_refused and share"',
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: an unset extent is not refused",
        "core/typespec.py",
        '            ("extent", all(side > 0 for side in spec.extent)),',
        '            ("extent", True),',
        'tests/test_type_seam.py -k "missing_a_field_is_refused and extent"',
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        "type seam: a breadth spec whose row has another key is not refused",
        "core/typespec.py",
        "        if spec.breadth.key != spec.key:",
        "        if False:",
        "tests/test_type_seam.py::test_a_breadth_spec_whose_row_has_another_key_is_refused",
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
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
    # The round-2 review's four (#54).
    Mutation(
        "type seam: first_free_block returns start even when it is taken",
        "core/typespec.py",
        "        if block not in taken:\n            return block\n",
        "        if True:\n            return block\n",
        (
            "tests/test_type_seam.py -k first_free_block_is_the_first_unused",
            "tests/test_type_seam.py::test_the_block_command_names_the_owner_and_a_really_free_block",
        ),
        "",
        "ecom-generate block names a block no type uses",
    ),
    Mutation(
        "type seam: ecom-generate block finds no owner of a taken block",
        "generate_cli.py",
        "    owners = sorted(other for other, block in used.items() if block == derived)\n",
        "    owners: list[str] = []\n",
        "tests/test_type_seam.py::test_the_block_command_names_the_owner_and_a_really_free_block",
        "",
        "ecom-generate block names a block no type uses",
    ),
    Mutation(
        "type seam: a half-zero extent is not refused",
        "core/typespec.py",
        '            ("extent", all(side > 0 for side in spec.extent)),',
        '            ("extent", any(side > 0 for side in spec.extent)),',
        'tests/test_type_seam.py -k "missing_a_field_is_refused and extent"',
        "",
        "a type module's spec reaches every table, or is refused naming the gap",
    ),
    Mutation(
        # Was "_discovered_blocks drops the row fallback"; the row's block now
        # reaches DECLARED_BLOCKS with the row, and this is how it is lost.
        "type seam: a breadth module's block on its row is overwritten by the spec's unset one",
        "core/typespec.py",
        "    if spec.part_number_block is not None:\n        DECLARED_BLOCKS[spec.key]",
        "    if True:\n        DECLARED_BLOCKS[spec.key]",
        "tests/test_type_seam.py::test_a_breadth_modules_declared_block_is_its_block[row]",
        "",
        "a type's declared block is its block, wherever it is declared",
    ),
    Mutation(
        "type seam: a table read during registration is answered, not refused",
        "core/typespec.py",
        '    if _REGISTRATION["running"]:\n        raise',
        '    if _REGISTRATION["running"]:\n        return\n        raise',
        (
            "tests/test_type_seam.py::"
            "test_a_table_read_while_registration_runs_is_refused_naming_the_reader",
            "tests/test_type_seam.py::"
            "test_block_of_read_during_registration_is_refused_not_answered_by_import_order",
        ),
        "",
        "a table read during registration is refused, not answered by import order",
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
        "type seam: register leaves a spec's claims out of CLAIMS",
        "core/typespec.py",
        '        "conformance.CLAIMS": (conformance.CLAIMS, spec.claims),\n',
        "        # CLAIMS left out\n",
        "tests/test_type_registration.py::"
        "test_a_planted_type_reaches_every_per_type_table_from_its_spec",
        "",
        "a type's spec reaches every per-type table",
    ),
    Mutation(
        "type seam: register writes no spec field into the shared tables",
        "core/typespec.py",
        "            table[spec.key] = value",
        "            pass",
        "tests/test_type_registration.py::"
        "test_a_planted_type_reaches_every_per_type_table_from_its_spec",
        "",
        "a type's spec reaches every per-type table",
    ),
    *(
        Mutation(
            f"type seam: a {table} entry in both the shared table and the spec is not refused",
            "core/typespec.py",
            "        if value is not None and dict.__contains__(table, spec.key):",
            "        if False:",
            "tests/test_type_registration.py::"
            f"test_a_key_in_a_shared_table_and_in_its_spec_is_refused[{table}]",
            "",
            "a per-type entry is declared once",
        )
        for table in ("CLAIMS", "KEY_ATTRIBUTES", "THREADED", "FASTENERS", "UNIT_PRIMARY")
    ),
    Mutation(
        "type seam: a modelled spec with no key_attributes is not refused",
        "core/typespec.py",
        '            ("key_attributes", bool(spec.key_attributes)),',
        '            ("key_attributes", True),',
        "tests/test_type_registration.py::test_a_modelled_type_without_a_key_dimension_is_refused",
        "",
        "a type's spec reaches every per-type table",
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
    # The facts tests' own refusals (tests/type_facts.py).
    *(
        Mutation(
            f"type seam: type_facts.{read} reads a shared row beside a module's own",
            "tests/type_facts.py",
            "        if key in shared:",
            "        if False:",
            "tests/test_type_facts.py::"
            f"test_a_shared_row_for_a_type_with_its_own_module_is_refused[{read}]",
            "",
            "a type's facts are declared once",
            root=".",
        )
        for read in ("may_claim", "title_key")
    ),
    *(
        Mutation(
            f"type seam: type_facts accepts a module that declares no {field}",
            "tests/type_facts.py",
            old,
            "        if False:",
            "tests/test_type_facts.py::"
            f"test_a_type_module_that_declares_no_fact_is_refused_naming_it[{param}]",
            "",
            "a type's facts are declared once",
            root=".",
        )
        for field, old, param in (
            ("may_claim", "        if value is None:", "may_claim-None-may_claim"),
            ("key_attributes", "        if value is None:", "key_attributes-unset1-title_key"),
        )
    ),
]

# Found by ``mutation_row.discover``: the label of this file; the rows carry their own names.
PREFIX = "area: type seam"


def rows() -> list[Mutation]:
    return MUTATIONS
