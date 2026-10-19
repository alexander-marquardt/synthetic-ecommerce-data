"""Mutation rows for the compatibility relation, near-miss period and noise roles (#75).

Each row plants one defect in how the spec's declarations reach their tables or the copy, and
names the test that must go red. ``mutation_check.py`` finds the file by glob and names the rows
``declared roles: ...`` (``--only "declared roles:"`` re-runs them).
"""

from __future__ import annotations

from mutation_row import GENERATOR, Row

PREFIX = "declared roles"

T = "tests/test_declared_copy_roles_75.py"
INDUSTRIAL = "domains/industrial"


def rows() -> list[Row]:
    return [
        Row(
            "a declared relation writes no sentence",
            f"{INDUSTRIAL}/compat.py",
            "    return KINDS[kind](published.get(attribute))",
            "    return None",
            f"{T} -k writes_its_sentence_for_a_planted_type",
            "a declared relation writes its sentence",
            GENERATOR,
            "A",
        ),
        Row(
            "a spec's relation never reaches the table",
            "core/typespec.py",
            '"compat.RELATIONS": (compat.RELATIONS, spec.compat or None)',
            '"compat.RELATIONS": (compat.RELATIONS, None)',
            f"{T} -k writes_its_sentence_for_a_planted_type",
            "a spec's relation joins compat.RELATIONS",
            GENERATOR,
            "B",
        ),
        Row(
            "a spec's near-miss period never reaches the table",
            "core/typespec.py",
            "(compat.NEAR_MISS_PERIOD, spec.near_miss_period)",
            "(compat.NEAR_MISS_PERIOD, None)",
            f"{T} -k near_miss_period_and_cutting_reach_their_tables",
            "a spec's near-miss period joins compat.NEAR_MISS_PERIOD",
            GENERATOR,
            "A",
        ),
        Row(
            "a cutting spec never joins the cutting table",
            "core/typespec.py",
            "(noise.CUTTING, spec.cutting or None)",
            "(noise.CUTTING, None)",
            f"{T} -k near_miss_period_and_cutting_reach_their_tables",
            "a cutting spec joins noise.CUTTING",
            GENERATOR,
            "B",
        ),
        Row(
            "an unset compat is accepted",
            "core/typespec.py",
            '("compat", spec.compat is not None),',
            '("compat", True),',
            f"{T} -k declares_no_compat_is_refused",
            "a modelled type that declares no compat is refused",
            GENERATOR,
            "A",
        ),
        Row(
            "the set screw reads another type's near-miss period",
            f"{INDUSTRIAL}/product_types/fasteners/set_screws_hex_socket.py",
            "period = compat.NEAR_MISS_PERIOD[type_key]",
            "period = compat.NEAR_MISS_PERIOD['bolt_hex']",
            f"{T} -k reads_its_declared_period_for_the_fine_pitch",
            "a type reads its own near-miss period",
            GENERATOR,
            "B",
        ),
        Row(
            "a period of one is accepted",
            "core/typespec.py",
            "spec.near_miss_period < 2",
            "spec.near_miss_period < 1",
            f"{T} -k malformed_declaration_is_refused",
            "a near-miss period under two is refused",
            GENERATOR,
            "A",
        ),
        Row(
            "an unknown relation kind is accepted",
            "core/typespec.py",
            "spec.compat[0] not in compat.KINDS",
            "spec.compat[0] not in (*compat.KINDS, 'sprocket')",
            f"{T} -k malformed_declaration_is_refused",
            "an unknown relation kind is refused",
            GENERATOR,
            "B",
        ),
        Row(
            "a socket screw is never rebuilt to a fine pitch",
            f"{INDUSTRIAL}/generate.py",
            "period = compat.NEAR_MISS_PERIOD.get(self.type_key)",
            "period = 0",
            "tests/test_compatibility_text.py -k a_diameter_query_has_a_pitch_to_choose",
            "a type reads its own near-miss period",
            GENERATOR,
            "A",
        ),
    ]
