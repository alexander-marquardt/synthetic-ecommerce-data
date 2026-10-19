"""Mutations that plant a defect in the product-type spec seam (``core/typespec.py``) and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    Mutation(
        "let a part number take a letter, the shape every reference SKU has",
        "core/typespec.py",
        '    return f"{block:04d}{(sequence * _PART_STRIDE) % SEQUENCE_SPACE:06d}"',
        '    return f"{block:04d}{(sequence * _PART_STRIDE) % SEQUENCE_SPACE:05d}X"',
        "tests/test_catalog_noncopy.py",
        "",
        "no generated SKU can collide with a real archived one",
    ),
    Mutation(
        "let two types share a part-number block",
        "core/typespec.py",
        "        if block in owner:",
        "        if False:",
        "tests/test_type_seam.py",
        "",
        "two types on one block are refused, naming both",
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
        "type seam: registered() no longer imports breadth",
        "core/typespec.py",
        "        from synthetic_ecommerce_data.domains.industrial import breadth  # noqa: F401, PLC0415\n",
        "",
        "tests/test_type_seam.py::test_registration_brings_in_the_yaml_rows_without_any_type_module",
        "",
        "every read of a type table registers the type modules first",
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
        "make the catalog non-deterministic",
        "core/typespec.py",
        '    return random.Random(f"{seed}:{type_key}")',
        "    return random.Random()",
        "tests/test_catalog_generate.py",
        "",
        "the same seed produces the same catalog",
    ),
]
