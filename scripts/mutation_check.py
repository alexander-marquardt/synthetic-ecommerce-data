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
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "synthetic_ecommerce_data"


@dataclass(frozen=True)
class Mutation:
    name: str
    #: Path relative to ``root``.
    file: str
    old: str
    new: str
    #: The test selector expected to go red, or a TUPLE of them when one
    #: mutation is expected to red more than one test.
    #:
    #: A tuple rather than one ``-k "a or b"`` filter, and the difference is
    #: the whole point: this harness's verdict is "pytest went red", so a
    #: disjunction is satisfied by EITHER test and prints ``[ok]`` on the
    #: other one's back. Ten rows were written that way and five of them were
    #: riding on a sibling. Every selector in the tuple is run and judged on
    #: its own, and the row is caught only when ALL of them red.
    tests: str | tuple[str, ...]

    @property
    def selectors(self) -> tuple[str, ...]:
        return (self.tests,) if isinstance(self.tests, str) else tuple(self.tests)

    #: "A" and "B" label the two directions of one property.
    direction: str = ""
    property_name: str = ""
    #: Path relative to the REPO root that ``file`` hangs off. Defaults to the
    #: generator package; the PRISM customization is a second package, and the
    #: committed field map has to be mutable from here too -- a drift test that
    #: is only ever proven from the DERIVATION side is not proven at all.
    root: str = "src/synthetic_ecommerce_data"


MUTATIONS: list[Mutation] = [
    # ---- the generic images carry no dimension, both directions ----------
    Mutation(
        "put a diameter callout on a generic drawing",
        "domains/industrial/render/generic.py",
        "    _bar(ax, half, body_bottom, cut_top, mark)",
        '    _bar(ax, half, body_bottom, cut_top, mark)\n    cv.diameter_callout(\n        ax, -0.2, half * 2, "Ø1/4\\"", "milling", side=1, overhang=0.02, gap=0.02\n    )',
        "tests/test_generic.py",
        "A",
        "a generic drawing carries no dimension",
    ),
    Mutation(
        "stop DIM being a distinct color, blinding the whole measurement",
        "domains/industrial/render/canvas.py",
        'DIM = "#b03a2e"',
        'DIM = "white"',
        "tests/test_generic.py",
        "B",
        "a generic drawing carries no dimension",
    ),
    # ---- the generic image is not derived from the record, both ways ------
    Mutation(
        "print the SKU on the generic image, as the old fallback did",
        "domains/industrial/render/generic.py",
        "    return render(drawing_for_record(record), path, profile)",
        '    fig, ax = build(drawing_for_record(record), profile)\n    ax.text(0, BOTTOM - 0.04, str(record.get("sku", "")), ha="center", color=cv.MUTED)\n    return cv.save(fig, path, profile)',
        "tests/test_generic.py",
        "A",
        "the generic image is the same file whatever the record says",
    ),
    Mutation(
        "make a dimensioned drawing ignore its diameter, blinding the control",
        "domains/industrial/render/endmill.py",
        '        cut_d=parse_length(require(record, "Milling Dia.")),',
        '        cut_d=parse_length(\'1/4"\') if require(record, "Milling Dia.") else None,',
        "tests/test_generic.py",
        "B",
        "the generic image is the same file whatever the record says",
    ),
    # ---- End Mill Style is read, both directions -------------------------
    Mutation(
        "draw every end mill with a square end, whatever the record says",
        "domains/industrial/render/endmill.py",
        '    published = str(require(record, "End Mill Style")).strip().lower()\n    try:\n        return END_STYLES[published]',
        '    published = str(require(record, "End Mill Style")).strip().lower()\n    try:\n        return "square" if published else END_STYLES[published]',
        "tests/test_endmill.py tests/test_derivation.py",
        "A",
        "the cutting end comes from the record",
    ),
    Mutation(
        "draw every GENERIC end mill with a ball nose, whatever it is of",
        "domains/industrial/render/generic.py",
        "    body_bottom = BOTTOM + (half if ball else 0.0)",
        "    ball = True\n    body_bottom = BOTTOM + (half if ball else 0.0)",
        "tests/test_generic.py",
        "B",
        "the cutting end comes from the record",
    ),
    # ---- a hex head is drawn hexagonal, both directions -------------------
    Mutation(
        "draw a hex head's end view as a circle",
        "domains/industrial/render/fastener.py",
        "    if geom.hex_headed:\n        # Six flats, to the published across-flats dimension.",
        "    if False:\n        # Six flats, to the published across-flats dimension.",
        "tests/test_fastener.py",
        "A",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    Mutation(
        "draw EVERY head's end view as a hexagon",
        "domains/industrial/render/fastener.py",
        'HEX_HEADED = {"hex", "hex head", "hexagon"}',
        "HEX_HEADED = CYLINDRICAL | COUNTERSUNK",
        "tests/test_fastener.py",
        "B",
        "a hex head is drawn hexagonal and a socket head round",
    ),
    # ---- the length dimension spans the published length, both ways -------
    Mutation(
        "measure a cylindrical head's length OVER the head",
        "domains/industrial/render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.total_height\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "A",
        "the length dimension spans the published length",
    ),
    Mutation(
        "measure a countersunk head's length UNDER the head",
        "domains/industrial/render/fastener.py",
        "        return self.length.inches\n\n    @property\n    def length_witness_radius",
        "        return self.shank_length\n\n    @property\n    def length_witness_radius",
        "tests/test_fastener.py",
        "B",
        "the length dimension spans the published length",
    ),
    # ---- the flute slope is the helix, both directions --------------------
    Mutation(
        "draw the flute rise from the diameter, not the circumference",
        "domains/industrial/render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.cut_d.inches / math.tan(math.radians(self.helix_deg))",
        "tests/test_endmill.py",
        "A",
        "one flute rises half a helix lead across the visible face",
    ),
    Mutation(
        "draw the flute rise as a WHOLE lead instead of half of one",
        "domains/industrial/render/endmill.py",
        "        return self.helix_lead / 2.0",
        "        return self.helix_lead",
        "tests/test_endmill.py",
        "B",
        "one flute rises half a helix lead across the visible face",
    ),
    # ---- every published attribute reaches the drawing, both directions ---
    Mutation(
        "ignore which hand the record says the helix is, while still listing it",
        "domains/industrial/render/endmill.py",
        "        hand=HANDS.get(hand_raw, 1),",
        "        hand=1,",
        "tests/test_endmill.py",
        "",
        "the hand of the helix comes from the record",
    ),
    Mutation(
        "drop an attribute from the drawing AND from the sheet",
        "domains/industrial/render/endmill.py",
        '        ("Coolant Fed", record.get("Coolant Fed", "")),\n',
        "",
        "tests/test_derivation.py",
        "A",
        "every published attribute reaches the drawing or is declared",
    ),
    Mutation(
        "declare an attribute NOT DRAWN that the drawing does draw",
        "domains/industrial/render/attrs.py",
        "NOT_DRAWN: dict[str, str] = {\n    # The measurement-system attribute",
        'NOT_DRAWN: dict[str, str] = {\n    "Helix Angle": "a claim that nothing in the drawing depends on it",\n    # The measurement-system attribute',
        "tests/test_derivation.py",
        "B",
        "every published attribute reaches the drawing or is declared",
    ),
    # ---- a renderer refuses rather than defaulting, both directions -------
    Mutation(
        "default a drill's shank diameter to its nominal size",
        "domains/industrial/render/drill.py",
        '        shank_d=parse_length(require(record, "Shank Dia.")),',
        '        shank_d=parse_length(record.get("Shank Dia.") or record["Size"]),',
        "tests/test_refusals.py",
        "A",
        "a dimension is refused, never defaulted",
    ),
    Mutation(
        "clamp a self-contradictory washer instead of refusing it",
        "domains/industrial/render/washer.py",
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
        "make reading a color back resolve to whichever brand comes first",
        "core/drawing/style.py",
        "        if brands.ink_of(brand).lower() == lowered and brands.frame_of(brand) == frame:\n            return brand",
        "        if lowered or brands.ink_of(brand).lower() == lowered and brands.frame_of(brand) == frame:\n            return brand",
        "tests/test_marking.py -k brand",
        "B",
        "the outline color is the brand, and reads back as the brand",
    ),
    Mutation(
        "let a brand stock the same spec twice",
        "domains/industrial/generate.py",
        "            if key in self._drawn_specs or self._differs_only_by_a_drop(",
        "            if False and self._differs_only_by_a_drop(",
        "tests/test_catalog_brands_voice.py -k same_product",
        "A",
        "no two SKUs share (type, brand, every attribute)",
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
    Mutation(
        "let the series walk rewrite any value equal to the series",
        "domains/industrial/generate.py",
        "                if attribute.name in self.IDENTIFIER_ATTRIBUTES and attribute.value == old:",
        "                if attribute.value == old:",
        "tests/test_catalog_brands_voice.py -k series_walk",
        "A",
        "the walk changes no attribute but an identifier",
    ),
    Mutation(
        "leave a product line without an image",
        "domains/industrial/generate.py",
        "            image_id=children[0].image_id,\n            drawing=drawing_for(type_key),\n        )",
        '            image_id="",\n            drawing=drawing_for(type_key),\n        )',
        "tests/test_catalog_generate.py tests/test_catalog_emit.py",
        "A",
        "every product and every variant carries an image that resolves",
    ),
    Mutation(
        "publish a URL for a drawing nothing renders",
        "domains/industrial/taxonomy.py",
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
    # ---- vocab: disjointness, both directions ----------------------------
    Mutation(
        "leak a hammer attribute into the screw vocabulary",
        "domains/industrial/vocab.py",
        '    _spec("Rockwell Hardness", "line", 0.48),',
        '    _spec("Rockwell Hardness", "line", 0.48),\n    _spec("Handle Material", "line", 0.5),',
        "tests/test_catalog_vocab.py tests/test_catalog_generate.py",
        "A",
        "unrelated product types share no vocabulary",
    ),
    Mutation(
        "remove the one name a screw and a hammer legitimately share",
        "domains/industrial/vocab.py",
        'HAMMER_VOCAB = (\n    _spec("Item", "line"),',
        'HAMMER_VOCAB = (\n    _spec("Item ", "line"),',
        "tests/test_catalog_vocab.py",
        "B",
        "unrelated product types share no vocabulary",
    ),
    # ---- series: geometry coherence, both directions ---------------------
    Mutation(
        "let the cut run past the end of the tool",
        "domains/industrial/series.py",
        "        if self.length_of_cut_in >= self.overall_length_in:",
        "        if False:",
        "tests/test_catalog_series.py",
        "A",
        "a tool always has a shank left to hold",
    ),
    Mutation(
        "refuse a tool whose geometry is fine",
        "domains/industrial/series.py",
        "        if self.length_of_cut_in >= self.overall_length_in:",
        "        if self.length_of_cut_in < self.overall_length_in:",
        "tests/test_catalog_series.py",
        "B",
        "a tool always has a shank left to hold",
    ),
    Mutation(
        "reorder the measured flute marginal",
        "domains/industrial/series.py",
        "    (4, 0.42),\n    (2, 0.375),",
        "    (4, 0.375),\n    (2, 0.42),",
        "tests/test_catalog_series.py",
        "",
        "flute counts follow the measured marginal",
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
    # ---- merge_pr.sh merges only a checked tree (#54) ----------------------
    # Every name starts "merge_pr:", so `--only "merge_pr:"` re-runs them. The
    # round-3 review's four survivors are the first four (the fourth, `--ours`
    # turned `--theirs`, is gone with the side-taking: a generated conflict is
    # now left for the rebuild, whose markers guard is its row here).
    *(
        Mutation(name, "scripts/merge_pr.sh", old, new, tests, "", prop, root=".")
        for name, old, new, tests, prop in (
            (
                "merge_pr: no base re-check before a merge attempt",
                '[ "$now_base" = "$base_sha" ] ||\n    die',
                "true ||\n    die",
                (
                    "tests/test_merge_pr.py::"
                    "test_main_that_moves_during_the_checks_is_not_merged_onto",
                    "tests/test_merge_pr.py::"
                    "test_main_that_moves_between_merge_attempts_is_not_merged_onto",
                ),
                "main is the base the checks ran on, at every merge attempt",
            ),
            (
                "merge_pr: every conflict auto-resolved",
                'listed "$path" "${GENERATED[@]}" || by_hand+=',
                "true || by_hand+=",
                (
                    "tests/test_merge_pr.py::"
                    "test_a_conflict_outside_the_generated_files_is_handed_back",
                    "tests/test_merge_pr.py::"
                    "test_a_conflict_in_a_file_the_build_does_not_write_is_handed_back",
                ),
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: no head-moved check after clone",
                '[ "$(git -C "$work" rev-parse HEAD)" = "$head_sha" ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_head_that_moves_while_cloning_is_refused",
                "the tree checked is the head GitHub named",
            ),
            (
                "merge_pr: a generated file the rebuild left conflicted is accepted",
                "    if grep -q '^<<<<<<< ' \"$work/$path\"; then",
                "    if false; then",
                "tests/test_merge_pr.py::"
                "test_a_generated_file_the_rebuild_left_conflicted_is_refused",
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: base re-checked once, not before every attempt",
                '  [ "$now_base" = "$base_sha" ] ||',
                '  [ "$attempt" -gt 1 ] || [ "$now_base" = "$base_sha" ] ||',
                "tests/test_merge_pr.py::"
                "test_main_that_moves_between_merge_attempts_is_not_merged_onto",
                "main is the base the checks ran on, at every merge attempt",
            ),
            (
                "merge_pr: any path under golden-catalog/ counts as generated",
                'listed "$path" "${GENERATED[@]}" || by_hand+=',
                '[[ $path == golden-catalog/* ]] || listed "$path" "${GENERATED[@]}" || by_hand+=',
                "tests/test_merge_pr.py::"
                "test_a_conflict_in_a_file_the_build_does_not_write_is_handed_back",
                "only a conflict the rebuild resolves is resolved by it",
            ),
            (
                "merge_pr: no head re-check before a merge attempt",
                '[ "$now_head" = "$final_sha" ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_head_that_moves_with_nothing_to_push_is_not_merged",
                "the head is the commit that was checked, at every merge attempt",
            ),
            (
                "merge_pr: the push is forced",
                'push -q origin "HEAD:',
                'push -q -f origin "HEAD:',
                "tests/test_merge_pr.py::"
                "test_a_head_that_moves_during_the_checks_is_neither_overwritten_nor_merged",
                "the head is the commit that was checked, at every merge attempt",
            ),
            (
                "merge_pr: the rebuild runs unlocked",
                'uv run -q --locked --directory "$work" ecom-generate',
                'uv run -q --directory "$work" ecom-generate',
                "tests/test_merge_pr.py::test_a_stale_lock_is_refused_not_relocked_and_committed",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: the rebuild stages everything",
                'git -C "$work" add -- "${GENERATED[@]}"',
                'git -C "$work" add -A',
                "tests/test_merge_pr.py::"
                "test_a_change_the_rebuild_makes_outside_the_generated_files_is_refused",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: a change outside the generated files is left behind",
                '[ -z "$stray" ] ||',
                "true ||",
                "tests/test_merge_pr.py::"
                "test_a_change_the_rebuild_makes_outside_the_generated_files_is_refused",
                "the rebuild commits only the generated files",
            ),
            (
                "merge_pr: a check run in which no test passed is green",
                '[ "$passed" -gt 0 ] ||',
                "true ||",
                "tests/test_merge_pr.py::test_a_check_run_in_which_no_test_passed_is_not_green",
                "a check run is green only when a test passed",
            ),
            (
                "merge_pr: CI read on the PR head, not the pushed commit",
                "commits/$final_sha/check-runs",
                "commits/$head_sha/check-runs",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[head-only]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a failed check is green",
                'elif [ "$conclusion" != success ]; then',
                "elif false; then",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[red]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: any skipped check is green",
                'listed "$name" "${SKIPPED_BY_DESIGN_CI[@]}" ||',
                "true ||",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[skipped]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a missing required check is not waited for",
                'listed "$name" ${seen[@]+"${seen[@]}"} || missing+=',
                "true || missing+=",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[missing]",
                "every CI check on the commit that merges is green",
            ),
            (
                "merge_pr: a running check counts as finished",
                'pending+=" $name"',
                ":",
                "tests/test_merge_pr.py::"
                "test_a_merge_waits_for_every_check_on_the_pushed_tree[pending]",
                "every CI check on the commit that merges is green",
            ),
        )
    ),
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
    Mutation(
        "stop injecting the angle-carries-a-length-unit defect",
        "domains/industrial/generate.py",
        "        if self.rng.random() >= self.config.scaled_defect(\n            self.config.defect_angle_carries_length_unit\n        ):\n            return line_attrs",
        "        if True:\n            return line_attrs",
        "tests/test_catalog_generate.py",
        "A",
        "the angle defect occurs at its measured rate",
    ),
    Mutation(
        "inject the angle defect into every line",
        "domains/industrial/generate.py",
        "        if self.rng.random() >= self.config.scaled_defect(\n            self.config.defect_angle_carries_length_unit\n        ):\n            return line_attrs",
        "        if False:\n            return line_attrs",
        "tests/test_catalog_generate.py",
        "B",
        "the angle defect occurs at its measured rate",
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
        "domains/industrial/generate.py",
        "                if middle < cfg.title_token_unlabelled:",
        "                if False:",
        "tests/test_catalog_generate.py",
        "A",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "always leave a title dimension token unlabelled",
        "domains/industrial/generate.py",
        "                if middle < cfg.title_token_unlabelled:",
        "                if True:",
        "tests/test_catalog_generate.py",
        "B",
        "the title token hazards occur at their measured rates",
    ),
    Mutation(
        "use one spelling of the measurement-system attribute everywhere",
        "domains/industrial/generate.py",
        "        system_name = str(_weighted(rng, MEASUREMENT_SYSTEM_NAMES))",
        '        system_name = "Dimension Type"',
        "tests/test_catalog_generate.py",
        "",
        "the measurement-system attribute has more than one spelling",
    ),
    Mutation(
        "let a child redefine a name its line already carries",
        "domains/industrial/generate.py",
        '            keyword_attribute("Item", item),\n            keyword_attribute("End Mill Style", style_name),',
        '            keyword_attribute("Item", item),\n            keyword_attribute("Milling Dia.", "0"),\n            keyword_attribute("End Mill Style", style_name),',
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
        "read the angle defect's inch mark as an inch again",
        "core/entry.py",
        '        unit = UNIT_FOR_NAME.get(name) or UNIT_FOR_SUFFIX[match["suffix"]]',
        '        unit = UNIT_FOR_SUFFIX[match["suffix"]]',
        (
            "tests/test_nested_entry_contract.py -k share_one_unit_dimension",
            "tests/test_nested_entry_contract.py -k hand_worked",
            "tests/test_nested_entry_contract.py -k published_spelling",
        ),
        "",
        "an angle key's entries are angles however the value is spelled (#79)",
    ),
    Mutation(
        "fix the inch-marked Helix Angle but leave Point Angle an inch",
        "core/entry.py",
        '    "Point Angle": "DD",\n',
        "",
        "tests/test_nested_entry_contract.py -k share_one_unit_dimension",
        "",
        "an angle key's entries are angles however the value is spelled (#79)",
    ),
    Mutation(
        "read a length keyed into an angle field as degrees",
        "core/entry.py",
        '        if UNIT_FOR_NAME.get(name) == "DD" and not _within_span(name, match["number"]):\n'
        '            return {"value": published}\n',
        "",
        (
            "tests/test_nested_entry_contract.py -k canonical_lies_within",
            "tests/test_nested_entry_contract.py -k hand_worked",
            "tests/test_nested_entry_contract.py -k published_spelling",
        ),
        "",
        "an angle key's canonical lies within the angles its series offers (#79)",
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
    # ---- PRISM field map: the terms-vs-identifier rule (#31, #28) --------
    Mutation(
        "raise the identifier threshold past 1.0 so identifiers become facets",
        "prism/derive.py",
        "IDENTIFIER_DISPERSION = 0.5",
        "IDENTIFIER_DISPERSION = 1.01",
        (
            "tests/test_prism_field_map_drift.py",
            # Not the rendered List Number entry: the declaration withholds
            # that at any threshold.
            "tests/test_facet_control_rule.py -k identifier_threshold_is_the_midpoint",
        ),
        "A",
        "a terms attribute whose values do not repeat is an identifier, not a facet",
    ),
    Mutation(
        "lower the identifier threshold so real facets are dropped",
        "prism/derive.py",
        "IDENTIFIER_DISPERSION = 0.5",
        "IDENTIFIER_DISPERSION = 0.02",
        (
            "tests/test_prism_field_map_drift.py",
            "tests/test_facet_control_rule.py -k standards_and_thread_size",
        ),
        "B",
        "a terms attribute whose values do not repeat is an identifier, not a facet",
    ),
    Mutation(
        "bring back an absolute cap of 25 terms values",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS\n"
        "            and self.dispersion >= IDENTIFIER_DISPERSION",
        "            not self.is_numeric\n            and self.cardinality > 25",
        "tests/test_facet_control_rule.py -k any_size",
        "",
        "the identifier rule does not move with catalog size",
    ),
    Mutation(
        "call a terms attribute an identifier on a handful of products",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS",
        "            not self.is_numeric",
        (
            "tests/test_facet_control_rule.py -k small_terms_attribute",
            "tests/test_prism_field_map_drift.py",
        ),
        "",
        "below the observation floor a terms attribute is offered",
    ),
    Mutation(
        "count the identifier floor in (product, value) pairs again",
        "prism/derive.py",
        "            not self.is_numeric\n            and self.products >= RANGE_MIN_DOCS",
        "            not self.is_numeric\n            and self.product_values >= RANGE_MIN_DOCS",
        "tests/test_facet_control_rule.py -k multi_valued",
        "",
        "the evidence floor counts products, so a kit's sizes are one product's",
    ),
    Mutation(
        "put the evidence floor back at 50, where small catalogs flip decisions",
        "prism/derive.py",
        "RANGE_MIN_DOCS = 250",
        "RANGE_MIN_DOCS = 50",
        "tests/test_facet_control_rule.py -k every_decision_is_the_same",
        "A",
        "no decision moves with --lines",
    ),
    Mutation(
        "raise the evidence floor past every attribute, so the ratio decides nothing",
        "prism/derive.py",
        "RANGE_MIN_DOCS = 250",
        "RANGE_MIN_DOCS = 100000",
        "tests/test_facet_control_rule.py -k widest_dispersion",
        "B",
        "no decision moves with --lines",
    ),
    Mutation(
        "ignore the generator's identifier declaration",
        "prism/derive.py",
        "    if stats.name in IDENTIFIER_ATTRIBUTES:",
        "    if False:",
        "tests/test_facet_control_rule.py -k declared_identifier",
        "",
        "a declared identifier is withheld whatever its ratio",
    ),
    Mutation(
        "restate the identifier declaration instead of reading the generator's",
        "prism/derive.py",
        "IDENTIFIER_ATTRIBUTES = Generator.IDENTIFIER_ATTRIBUTES",
        'IDENTIFIER_ATTRIBUTES = frozenset({"List Number"})',
        "tests/test_facet_control_rule.py -k reads_the_generators",
        "",
        "a declared identifier is withheld whatever its ratio",
    ),
    Mutation(
        "call an under-floor quantity a standard set below the threshold",
        "prism/derive.py",
        "    if stats.is_numeric and stats.dispersion >= RANGE_DISPERSION:",
        "    if False:",
        "tests/test_facet_control_rule.py -k small_sample",
        "",
        "an under-floor decision names the floor in its reason",
    ),
    Mutation(
        "measure dispersion per SKU document again",
        "prism/derive.py",
        "return self.cardinality / self.product_values if self.product_values else 0.0",
        "return self.cardinality / self.present if self.present else 0.0",
        "tests/test_facet_control_rule.py -k products_not_sku_variants",
        "",
        "dispersion counts products, not SKU variants",
    ),
    Mutation(
        "count every SKU's copy of a product-scope value",
        "prism/derive.py",
        '            product_values[key].update((row["product_id"], value) for value in vals)',
        '            product_values[key].update((row["sku"], value) for value in vals)',
        "tests/test_prism_field_map_drift.py",
        "",
        "dispersion counts products, not SKU variants",
    ),
    # ---- filter_routing.hard must carry every numeric facet -------------
    Mutation(
        "drop the routed range axis, so price loses its slider",
        "data/customization.yaml",
        "    - price\n",
        "",
        "tests/test_prism_field_map_drift.py",
        "A",
        "every derived range facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
    ),
    Mutation(
        # Direction B is the one that is a BOOT REFUSAL rather than a missing
        # slider: a routed name that resolves to no range axis makes Engine and
        # Studio refuse to start (elastic/prism#7114). Since #9285 turned every
        # dimensional attribute into a discrete list, routing one of them is
        # exactly that mistake -- so this plants a real former entry rather
        # than an invented name.
        "route a discrete list as though it were a range axis",
        "data/customization.yaml",
        "    - price\n",
        "    - price\n    - drive_size\n",
        "tests/test_prism_field_map_drift.py",
        "B",
        "every derived range facet is routed as a range axis",
        root="src/prism_synthetic_industrial",
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
        "emit an eighth file the build does not commit",
        "generate_cli.py",
        '    (out / "mapping.flat.json").write_text(',
        '    (out / "mapping.extra.json").write_text("{}\\n", encoding="utf-8")\n'
        '    (out / "mapping.flat.json").write_text(',
        "tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output",
        "B",
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
    # ---- figures: the measured figures are build output (#103) -----------
    # A figure the build miscounts reds the rebuild comparison; a doc that
    # quotes one again reds the docs scan.
    Mutation(
        "figures: brands counted as product types",
        "generate_cli.py",
        '"brands": len({doc["brand"] for doc in flat}),',
        '"brands": len({doc["product_type"] for doc in flat}),',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
    Mutation(
        "figures: the dispersion band's densest end taken over every quantity",
        "prism/derive.py",
        "        densest = max(faceted, key=lambda s: s.dispersion)",
        "        densest = max(quantitative, key=lambda s: s.dispersion)",
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
    Mutation(
        "figures: the README quotes the brand count again",
        "README.md",
        "[breadth categories](#catalog-breadth), one product each, from invented",
        "[breadth categories](#catalog-breadth), one product each, from 45 invented",
        "tests/test_measured_figures.py::test_no_doc_restates_a_figure_the_build_measures",
        "",
        "no doc restates a measured figure",
        root=".",
    ),
    # ---- the headline invariants, mutated in the COMMITTED DATA ----------
    Mutation(
        "blank one card image url in the committed catalog",
        "flat.jsonl",
        '"stock": 191, "image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        '"stock": 191, "image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": ""',
        "tests/test_catalog_golden.py::test_every_flat_document_carries_an_image_url",
        "A",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    Mutation(
        "drop the detail image url from one committed nested variant",
        "nested.jsonl",
        '"stock": 191, '
        '"image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg", '
        '"image_detail_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        '"stock": 191, '
        '"image_id": "abrasive_flap_disc/TAN-FD580-1609-0003/1609171743", '
        '"image_url": "/images/industrial/abrasive_flap_disc/TAN-FD580-1609-0003/1609171743.svg"',
        "tests/test_catalog_golden.py::test_every_nested_line_and_variant_carries_an_image_url",
        "B",
        "every document carries a NON-EMPTY image url at both profiles",
        root="golden-catalog",
    ),
    # THE REPLACEMENT SKU HAS TO EXIST, which is the whole mutation and is
    # what this row got wrong. It rewrote ``97NR28`` as ``80FY44`` -- a sku
    # the catalog does not carry -- so it RENAMED a document instead of
    # duplicating one, every sku stayed distinct, and
    # ``test_flat_holds_one_document_per_sku`` passed for the correct reason
    # while the table read it as proof. ``51RE59`` is CRE-G246-0001's own
    # second variant, so the mutation now really does publish one sku twice.
    # The alexander-marquardt/synthetic-ecommerce-data#39 regeneration
    # (Corner Radius/Neck Length applied once instead of twice) is what took
    # the previous anchor sku, ``6DT18``, out of the catalog.
    # alexander-marquardt/synthetic-ecommerce-data#48 renumbered every
    # sku as a part number, so the golden rows re-anchor on the first committed
    # product line with more than one variant, TAN-FD580-1609-0003; its second
    # variant, ``1609562324``, is the sku this row duplicates.
    Mutation(
        "duplicate a sku in the committed flat catalog",
        "flat.jsonl",
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-0003"',
        '{"sku": "1609562324", "product_id": "TAN-FD580-1609-0003"',
        "tests/test_catalog_golden.py::test_flat_holds_one_document_per_sku",
        "",
        "flat.jsonl is one document per distinct sku",
        root="golden-catalog",
    ),
    Mutation(
        "point one committed document at a product line that does not exist",
        "flat.jsonl",
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-0003"',
        '{"sku": "1609171743", "product_id": "TAN-FD580-1609-9999"',
        "tests/test_catalog_golden.py::test_flat_covers_exactly_the_product_lines",
        "",
        "the catalog spans exactly the committed number of products",
        root="golden-catalog",
    ),
    Mutation(
        "publish a variant_count that disagrees with its own variants array",
        "nested.jsonl",
        '"variant_count": 3, "variants": [{"sku": "1609171743", "title": "Shop Flap Disc',
        '"variant_count": 4, "variants": [{"sku": "1609171743", "title": "Shop Flap Disc',
        "tests/test_catalog_golden.py::test_nested_lines_account_for_every_sku",
        "",
        "the nested lines account for every sku",
        root="golden-catalog",
    ),
    # ---- Length Under Head is DRAWN, both directions ---------------------
    Mutation(
        "draw the length-under-head dimension against the whole screw",
        "domains/industrial/render/fastener.py",
        "        span = geom.length_under_head.inches",
        "        span = geom.total_height",
        (
            "tests/test_fastener.py -k length_under_head",
            "tests/test_fastener.py -k three_published_lengths",
        ),
        "A",
        "the length under head is a span on the drawing, to its published value",
    ),
    Mutation(
        "print the value in the attribute table and draw no dimension for it",
        "domains/industrial/render/fastener.py",
        "    if geom.length_under_head is not None:\n        # The whole shank",
        "    if False:\n        # The whole shank",
        (
            "tests/test_fastener.py -k length_under_head",
            "tests/test_fastener.py -k three_published_lengths",
            "tests/test_fastener.py -k inked_in_the_drawing",
        ),
        "B",
        "the length under head is a span on the drawing, to its published value",
    ),
    # ---- a record whose lengths disagree is refused, both directions ------
    Mutation(
        "draw a screw whose published lengths contradict each other",
        "domains/industrial/render/fastener.py",
        "        if drift > UNDER_HEAD_TOLERANCE_IN:",
        "        if False:",
        "tests/test_fastener.py -k contradict",
        "A",
        "a length under head the other lengths contradict is refused",
    ),
    Mutation(
        "tighten the tolerance past the precision the catalog publishes at",
        "domains/industrial/render/fastener.py",
        "UNDER_HEAD_TOLERANCE_IN = 0.01",
        "UNDER_HEAD_TOLERANCE_IN = 0.0",
        "tests/test_fastener.py -k rounding",
        "B",
        "a length under head the other lengths contradict is refused",
    ),
    # ---- the head style decides the SHAPE, both directions ---------------
    Mutation(
        "draw a button head as the cylinder a socket head cap screw has",
        "domains/industrial/render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return False",
        (
            "tests/test_fastener.py -k each_head_style",
            "tests/test_fastener.py -k button_head",
        ),
        "A",
        "each head style draws the shape its record names",
    ),
    Mutation(
        "dome every head that is not countersunk, so socket and button agree again",
        "domains/industrial/render/fastener.py",
        "    @property\n    def domed(self) -> bool:\n        return self.head_style.strip().lower() in DOMED",
        "    @property\n    def domed(self) -> bool:\n        return not self.countersunk",
        "tests/test_fastener.py -k each_head_style",
        "B",
        "each head style draws the shape its record names",
    ),
    # ---- and it decides which line drawing a LINE gets, both directions ---
    Mutation(
        "give the low head drawing a full socket head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.062",
        "    head_half, head_h = 0.105, 0.115",
        (
            "tests/test_generic.py -k drawn_lower",
            "tests/test_generic.py -k DIFFERENT",
        ),
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
        "domains/industrial/render/generic.py",
        "                dome_profile(head_half, head_h, seat),",
        "                [(-head_half, seat), (-head_half, _HEAD_TOP), "
        "(head_half, _HEAD_TOP), (head_half, seat)],",
        (
            "tests/test_generic.py -k dome",
            "tests/test_generic.py -k head_measurement",
        ),
        "A",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    Mutation(
        "dome the socket head cap screw, so the shape no longer names the style",
        "domains/industrial/render/generic.py",
        "    _bar(ax, head_half, seat, _HEAD_TOP, mark)\n    # The socket, drawn as the opening",
        "    _hatched(\n        ax,\n        ax.add_patch(\n            Polygon(\n"
        "                dome_profile(head_half, head_h, seat),\n                closed=True,\n"
        "                fc=mark.tint or cv.BODY_FILL,\n                ec=mark.ink,\n"
        "                lw=cv.LW_BODY,\n                zorder=5,\n            )\n        ),\n"
        "        mark,\n    )\n    # The socket, drawn as the opening",
        (
            "tests/test_generic.py -k dome",
            "tests/test_generic.py -k head_measurement",
        ),
        "B",
        "a button head is drawn as a dome and a socket head as a bar",
    ),
    # ---- the button head is drawn LOWER than a socket head, both ways -----
    Mutation(
        "draw the button head taller than the socket head cap screw",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.112, 0.200",
        'tests/test_generic.py -k "drawn_lower"',
        "A",
        "a button head is drawn lower than a socket head cap screw",
    ),
    Mutation(
        "flatten the socket head cap screw to the button head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_lower"',
        "B",
        "a button head is drawn lower than a socket head cap screw",
    ),
    # ---- and WIDER than one, both ways -----------------------------------
    Mutation(
        "give the button head the socket head cap screw's own width",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.112, 0.056",
        "    head_half, head_h = 0.105, 0.056",
        'tests/test_generic.py -k "drawn_wider"',
        "A",
        "a button head is drawn wider than a socket head cap screw",
    ),
    Mutation(
        "widen the socket head cap screw past the button head",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.130, 0.115",
        'tests/test_generic.py -k "drawn_wider"',
        "B",
        "a button head is drawn wider than a socket head cap screw",
    ),
    # ---- the dome arc is the cap the two numbers name, both directions ----
    Mutation(
        "take the rim angle with asin, which draws the minor arc on a tall dome",
        "domains/industrial/render/fastener.py",
        "    half_angle = math.atan2(r_head, radius - rise)",
        "    half_angle = math.asin(min(1.0, r_head / radius))",
        'tests/test_fastener.py -k "dome"',
        "A",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "strike the dome about the chord's own half-width instead of the sphere",
        "domains/industrial/render/fastener.py",
        "    radius = (r_head * r_head + rise * rise) / (2 * rise)",
        "    radius = r_head",
        'tests/test_fastener.py -k "dome"',
        "B",
        "the dome is the cap its chord and rise name, at any rise",
    ),
    Mutation(
        "flatten the socket head cap screw to a low head's height",
        "domains/industrial/render/generic.py",
        "    head_half, head_h = 0.105, 0.115",
        "    head_half, head_h = 0.105, 0.062",
        (
            "tests/test_generic.py -k drawn_lower",
            "tests/test_generic.py -k DIFFERENT",
        ),
        "B",
        "the new screw silhouettes are drawn to the proportions their standards give them",
    ),
    # ---- the catalog publishes the attribute at all, both directions ------
    Mutation(
        "publish the length under head on the countersunk line only",
        "domains/industrial/generate.py",
        '                *([] if flat else [self._length("Length under Head", length_in, style)]),',
        '                *([self._length("Length under Head", length_in, style)] if flat else []),',
        "tests/test_catalog_generate.py -k length_under_head",
        "A",
        "every non-countersunk screw and bolt publishes its stocked length under head",
    ),
    Mutation(
        "publish length-less-head-height under the countersunk head again",
        "domains/industrial/generate.py",
        '                *([] if flat else [self._length("Length under Head", length_in, style)]),',
        '                self._length("Length under Head", length_in - (head.head_height_in if flat else 0), style),',  # noqa: E501
        (
            "tests/test_catalog_generate.py -k stocked_length_and_a_countersunk",
            "tests/test_compatibility_text.py -k countersunk",
        ),
        "B",
        "every non-countersunk screw and bolt publishes its stocked length under head",
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
        "name the coarse thread's drill on its fine sibling",
        "domains/industrial/compat.py",
        '    "M12x1.5": 10.5,',
        '    "M12x1.5": 10.2,',
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
    # ---- a record's facts are real (the review of the 100K catalog) -------------
    Mutation(
        "jitter a bearing's rating again",
        "domains/industrial/newtypes.py",
        "    dynamic = int(round(dynamic_kn * LBF_PER_KN, -1))",
        "    dynamic = int(round(dynamic_kn * LBF_PER_KN * rng.uniform(0.9, 1.1), -1))",
        "tests/test_catalog_facts.py -k rated_by_its_table",
        "A",
        "every fact a record states is real",
    ),
    Mutation(
        "give a large-bore bearing an outside diameter ISO 15 does not list",
        "domains/industrial/newtypes.py",
        '    ("6310", 50, 110, 27),',
        '    ("6310", 50, 105, 27),',
        "tests/test_catalog_facts.py -k iso_15_boundary",
        "A",
        "every fact a record states is real",
    ),
    Mutation(
        "narrow the bearing bores back to the 10-35 mm ladder",
        "domains/industrial/newtypes.py",
        "    table = _BEARINGS_INCH if inch else _BEARINGS_METRIC",
        "    table = _BEARINGS_INCH if inch else tuple(r for r in _BEARINGS_METRIC "
        "if 10 <= r[1] <= 35)",
        "tests/test_price.py -k bearing_bores_alone",
        "A",
        "bearing bores span the series miniature through large bore (#64)",
    ),
    Mutation(
        "rate a bearing from a second maker's slower speed basis again",
        "domains/industrial/newtypes.py",
        '    "609": (3.90, 1.66, 43000),',
        '    "609": (3.90, 1.66, 31000),',
        "tests/test_catalog_facts.py -k rating_order_by_bore",
        "A",
        "every metric bearing is rated by one maker, in series order (#64)",
    ),
    Mutation(
        "give a larger bore a higher load rating than the next size up",
        "domains/industrial/newtypes.py",
        '    "6212": (55.3, 36.0, 8000),',
        '    "6212": (60.3, 36.0, 8000),',
        "tests/test_catalog_facts.py -k rating_order_by_bore",
        "A",
        "every metric bearing is rated by one maker, in series order (#64)",
    ),
    Mutation(
        "leave a number the maker rates out of the table again",
        "domains/industrial/newtypes.py",
        '    ("6316", 80, 170, 39),\n',
        "",
        "tests/test_catalog_facts.py -k every_one_the_maker_rates",
        "A",
        "every metric bearing is rated by one maker, in series order (#64)",
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
        "zinc-plate a stainless socket screw",
        "domains/industrial/generate.py",
        '    "18-8 Stainless Steel": (("Plain",), "B80"),',
        '    "18-8 Stainless Steel": (("Plain", "Zinc Plated"), "B80"),',
        "tests/test_catalog_facts.py -k finish_or_hardness",
        "A",
        "every fact a record states is real",
    ),
    Mutation(
        "snap an end mill's shank below its cutter",
        "domains/industrial/series.py",
        "    larger = [s for s in METRIC_SHANKS if s > dia_mm + 1e-9]",
        "    larger = [s for s in METRIC_SHANKS if s > dia_mm * 0.7]",
        "tests/test_catalog_facts.py -k shank_is_thinner",
        "A",
        "every fact a record states is real",
    ),
    Mutation(
        "re-draw the title style per SKU",
        "domains/industrial/generate.py",
        "        return style\n\n    def _dimension_segments",
        "        return self.TITLE_STYLES[int(self.rng.random() * 3)]\n\n    def _dimension_segments",
        "tests/test_catalog_facts.py -k titles_a_type_one_way",
        "A",
        "a brand titles a type one way, naming its key size",
    ),
    Mutation(
        "drop the key dimension from secondary-style titles",
        "domains/industrial/generate.py",
        '        if style == "secondary":\n            # The pair\'s secondary dimension',
        '        if style == "secondary":\n            segments = []\n            # The pair\'s secondary dimension',
        "tests/test_catalog_facts.py -k names_its_key_dimension",
        "B",
        "a brand titles a type one way, naming its key size",
    ),
    Mutation(
        "count the measurement-system spelling as a difference again",
        "domains/industrial/generate.py",
        "    NOT_SUBSTANCE = IDENTIFIER_ATTRIBUTES | METADATA_ATTRIBUTES",
        "    NOT_SUBSTANCE = IDENTIFIER_ATTRIBUTES",
        "tests/test_catalog_brands_voice.py -k no_two_skus_of_the_100k_catalog",
        "A",
        "no two SKUs of a (type, brand) are the same product",
    ),
    # ---- the review of 7dac659: standards, end shape, shanks, title style -----
    Mutation(
        "let a heavy hex nut claim the regular nut's standard again",
        "domains/industrial/newtypes.py",
        '        return flats + (2.0 if metric else 1 / 8), height * 1.1, ""',
        "        return flats + (2.0 if metric else 1 / 8), height * 1.1, "
        "_FINISHED_STANDARD[(system, fine)]",
        "tests/test_catalog_facts.py -k nut_claims_only_the_standard",
        "A",
        "a nut claims only the standard its dimensions are",
    ),
    Mutation(
        "let a fine-pitch metric nut claim the coarse-thread ISO 4032",
        "domains/industrial/newtypes.py",
        '    ("mm", True): "ISO 8673",',
        '    ("mm", True): "ISO 4032",',
        "tests/test_catalog_facts.py -k nut_claims_only_the_standard",
        "A",
        "a nut claims only the standard its dimensions are",
    ),
    Mutation(
        "derive a jam nut's height again while it claims its standard",
        "domains/industrial/newtypes.py",
        "        jam = table.get(_nominal(thread))\n        if jam is None:\n"
        '            return flats, height * 0.6, ""',
        '        jam = height * 0.6\n        if jam is None:\n            return flats, height * 0.6, ""',
        "tests/test_catalog_facts.py -k nut_claims_only_the_standard",
        "B",
        "a nut claims only the standard its dimensions are",
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
        "title every end mill Sq End, ball nose included",
        "domains/industrial/generate.py",
        '                        value=f"{abbreviate_value(end.value)} {END_SHAPE_WORD[shape]} End",',
        '                        value=f"{abbreviate_value(end.value)} Sq End",',
        "tests/test_catalog_facts.py -k mills_own_end_shape",
        "A",
        "a title names the end mill's own end shape",
    ),
    Mutation(
        "let an oversize shank grow to any stocked size again",
        "domains/industrial/series.py",
        "    return max(dia * MAX_SHANK_RATIO, min(larger))",
        "    return max(larger)",
        "tests/test_catalog_facts.py -k shank_is_oversize",
        "A",
        "an end mill's shank is realistic for its cutter",
    ),
    Mutation(
        "let an oversize shank reach four times its cutter",
        "domains/industrial/series.py",
        "MAX_SHANK_RATIO = 3.0",
        "MAX_SHANK_RATIO = 4.0",
        "tests/test_catalog_facts.py -k shank_is_oversize",
        "A",
        "an end mill's shank is realistic for its cutter",
    ),
    Mutation(
        "cap an oversize shank at twice its cutter again",
        "domains/industrial/series.py",
        "MAX_SHANK_RATIO = 3.0",
        "MAX_SHANK_RATIO = 2.0",
        "tests/test_catalog_facts.py -k census_wide_shank_ratios",
        "B",
        "an end mill's shank is realistic for its cutter",
    ),
    Mutation(
        "cap an oversize shank just below the census's 2.667x band",
        "domains/industrial/series.py",
        "MAX_SHANK_RATIO = 3.0",
        "MAX_SHANK_RATIO = 2.5",
        "tests/test_catalog_facts.py -k census_wide_shank_ratios",
        "B",
        "an end mill's shank is realistic for its cutter",
    ),
    Mutation(
        "drop the 6 mm shank for small metric cutters",
        "domains/industrial/series.py",
        "    if dia_mm < SMALL_METRIC_SHANK_MM - 1e-9:\n        return SMALL_METRIC_SHANK_MM\n",
        "",
        "tests/test_catalog_facts.py -k sits_on_6mm",
        "B",
        "an end mill's shank is realistic for its cutter",
    ),
    Mutation(
        "stop writing a glued size's parts in the spec clause",
        "domains/industrial/generate.py",
        "        details.extend(thread_parts(f\"{title.text} {', '.join(details)}\"))\n",
        "",
        "tests/test_glued_thread_sizes.py -k also_written_in_parts",
        "",
        "a glued metric size is also written in its parts",
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
    Mutation(
        "choose labelled or secondary per SKU inside a labelled-or-secondary pair",
        "domains/industrial/generate.py",
        '        if style == "secondary":\n            # The pair\'s secondary dimension',
        '        if style != "unlabelled" and self.rng.random() < 0.5:\n'
        "            # The pair's secondary dimension",
        "tests/test_catalog_facts.py -k secondary_dimension_on_every_title_or_none",
        "A",
        "a brand titles a type one way, naming its key size",
    ),
    Mutation(
        "drop a secondary pair's secondary on some SKUs that publish it",
        "domains/industrial/generate.py",
        '            if attribute is not None:\n                self._bump("title_token_not_primary")',
        "            if attribute is not None and self.rng.random() < 0.7:\n"
        '                self._bump("title_token_not_primary")',
        "tests/test_catalog_facts.py -k secondary_dimension_on_every_title_or_none",
        "B",
        "a brand titles a type one way, naming its key size",
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
    Mutation(
        "let the noise into the title",
        "domains/industrial/generate.py",
        "                    title=title.text,\n                    description=self._build_description(draft, title, attrs, extra),",
        '                    title=title.text + (" " + noise_text if noise_text else ""),\n                    description=self._build_description(draft, title, attrs, extra),',
        "tests/test_noise_text.py -k never_moves_an_attribute",
        "A",
        "noise never moves an attribute or a title",
    ),
    Mutation(
        "count one piece too many in every kit",
        "domains/industrial/newtypes.py",
        "    pieces = kit.per_size * len(contents)",
        "    pieces = kit.per_size * len(contents) + 1",
        "tests/test_noise_text.py -k piece_count_is_its_contents",
        "A",
        "a kit's piece count is its contents",
    ),
    Mutation(
        "publish the socket's toleranced across-flats as its drive size",
        "domains/industrial/generate.py",
        '                child.attrs.append(self._length("Drive Size", key_in, style))',
        '                child.attrs.append(self._length("Drive Size", head.drive_size_in, style))',
        "tests/test_compatibility_text.py -k nominal_key",
        "A",
        "every drive size is a nominal hex key",
    ),
    Mutation(
        "build no fine-pitch line",
        "domains/industrial/generate.py",
        '        if not fine or self._rotate(f"fine:{key}", period) != period - 1:',
        "        if True:",
        "tests/test_compatibility_text.py -k pitch_to_choose",
        "A",
        "a diameter query has a pitch to choose",
    ),
    Mutation(
        "leave a fine-pitch line's thread type saying coarse",
        "domains/industrial/generate.py",
        '            _retype(draft, "Metric Fine" if metric else "UNF")\n            draft.provenance = FINE_PITCH_BOLT_STANDARD[standard]',
        "            draft.provenance = FINE_PITCH_BOLT_STANDARD[standard]",
        "tests/test_compatibility_text.py -k its_thread_type_says_which",
        "B",
        "a diameter query has a pitch to choose",
    ),
    # ---- the sizes the reference distributor asks for exist, both directions ----------
    Mutation(
        "drop 25 mm back out of the metric cutting series",
        "domains/industrial/series.py",
        "    15.0,\n    16.0,\n    20.0,\n    25.0,\n)",
        "    15.0,\n    16.0,\n    20.0,\n)",
        "tests/test_catalog_coverage.py",
        "A",
        "the cutting diameters the reference distributor asks for exist",
    ),
    Mutation(
        "freeze the coverage rotation, so which sizes exist is luck again",
        "domains/industrial/generate.py",
        "        index = self._rotations.get(key, 0)\n        self._rotations[key] = index + 1\n        return index",
        "        self._rotations[key] = self._rotations.get(key, 0) + 1\n        return 0",
        "tests/test_catalog_coverage.py",
        "B",
        "the cutting diameters the reference distributor asks for exist",
    ),
    # ---- 7/16 exists, and its lengths are the standard's, both ways -------
    Mutation(
        "record 7/16 as absent from the hex bolt standard",
        "domains/industrial/data/fastener_standards.json",
        '"size": "7/16",\n        "present_in_source": true,\n        "width_across_flats_in": 0.625,',
        '"size": "7/16",\n        "present_in_source": false,\n        "width_across_flats_in": 0.625,',
        "tests/test_catalog_coverage.py",
        "A",
        "7/16-14 exists, in the standard's own offered lengths",
    ),
    Mutation(
        "offer lengths the standard does not, by scaling the run",
        "domains/industrial/generate.py",
        "        return ordered[start : start + count]",
        "        return [value * 1.5 for value in ordered[start : start + count]]",
        "tests/test_catalog_coverage.py",
        "B",
        "7/16-14 exists, in the standard's own offered lengths",
    ),
    # ---- a grading belongs to one measurement system, both directions ----
    Mutation(
        "grade every bolt on the inch scale, metric ones included",
        "domains/industrial/generate.py",
        'grades = INCH_GRADES if head.published_unit == "in" else METRIC_GRADES',
        "grades = INCH_GRADES",
        "tests/test_catalog_coverage.py",
        "A",
        "a bolt never carries a grading from the other measurement system",
    ),
    Mutation(
        "grade every bolt on the metric scale, inch ones included",
        "domains/industrial/generate.py",
        'grades = INCH_GRADES if head.published_unit == "in" else METRIC_GRADES',
        "grades = METRIC_GRADES",
        "tests/test_catalog_coverage.py",
        "B",
        "a bolt never carries a grading from the other measurement system",
    ),
    # ---- the parametric query resolves, both directions -------------------
    Mutation(
        "take the zinc finish off the hex bolt rotation",
        "domains/industrial/generate.py",
        'HEX_BOLT_FINISHES: tuple[str, ...] = ("Zinc Plated", "Plain", "Hot Dip Galvanized")',
        'HEX_BOLT_FINISHES: tuple[str, ...] = ("Plain", "Hot Dip Galvanized")',
        "tests/test_catalog_coverage.py",
        "A",
        "the reference distributor's parametric query has an answer",
    ),
    Mutation(
        "take Grade 8 off the inch grading rotation",
        "domains/industrial/generate.py",
        'INCH_GRADES: tuple[str, ...] = ("Grade 5", "Grade 8")',
        'INCH_GRADES: tuple[str, ...] = ("Grade 5",)',
        "tests/test_catalog_coverage.py",
        "B",
        "the reference distributor's parametric query has an answer",
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
        "domains/industrial/generate.py",
        "        phase = step + step // len(sizes) + HEX_BOLT_PHASE.index(standard)",
        "        phase = step + step // len(sizes)",
        "tests/test_catalog_coverage.py -k locked",
        "A",
        "one thread size is not locked to one grading or one finish",
    ),
    Mutation(
        "let the size, grading and finish wheels turn in step",
        "domains/industrial/generate.py",
        "        phase = step + step // len(sizes) + HEX_BOLT_PHASE.index(standard)",
        "        phase = step",
        "tests/test_catalog_coverage.py -k locked",
        "B",
        "one thread size is not locked to one grading or one finish",
    ),
    # ---- the control follows CONTINUITY, not numeracy, both directions ----
    # The defect on each side is a real one somebody could write. A restores
    # the old rule -- numbers get a slider -- and publishes a range over 53
    # standard hex-key sizes. B pushes the threshold past every attribute so
    # nothing is ever a range, which would break the grocery catalog this rule
    # has to serve next (elastic/prism#9290) while leaving this catalog's
    # output unchanged -- so it is deliberately a mutation that THIS catalog's
    # data cannot reveal, and the test has to bite on the rule itself.
    Mutation(
        "offer a range over any attribute whose values are numbers",
        "prism/derive.py",
        "            self.is_numeric\n            and self.products >= RANGE_MIN_DOCS\n            and self.dispersion >= RANGE_DISPERSION",
        "            self.is_numeric",
        "tests/test_facet_control_rule.py -k continuity",
        "A",
        "a discrete standard set is not offered as a range",
    ),
    Mutation(
        "put the continuity threshold above 1.0, so nothing is ever continuous",
        "prism/derive.py",
        "RANGE_DISPERSION = 0.5",
        "RANGE_DISPERSION = 1.01",
        "tests/test_facet_control_rule.py -k continuity",
        "B",
        "a discrete standard set is not offered as a range",
    ),
    # ---- every offered fastener size reaches a line, both directions ------
    Mutation(
        "toss a coin for a screw line's measurement system instead of alternating",
        "domains/industrial/generate.py",
        '        metric = self._rotate(f"system:{type_key}", 2) == 0',
        "        metric = rng.random() < 0.5",
        "tests/test_catalog_coverage.py",
        "A",
        "every size a fastener standard offers reaches a document",
    ),
    Mutation(
        "draw a screw line's size at random instead of rotating",
        "domains/industrial/generate.py",
        '        size = sizes[self._rotate(f"size:{type_key}:{standard}", len(sizes))]',
        "        size = rng.choice(sizes)",
        "tests/test_catalog_coverage.py",
        "B",
        "every size a fastener standard offers reaches a document",
    ),
    # ---- no two SKUs of a line share a title, both directions -------------
    Mutation(
        "stop repairing the titles that tell a shopper nothing",
        "domains/industrial/generate.py",
        "        if identifying is None or len(published) < 2:\n            return titles",
        "        return titles",
        "tests/test_catalog_titles.py",
        "A",
        "no two SKUs of one line share a title",
    ),
    Mutation(
        "repair only exact duplicates, the way the first version did",
        "domains/industrial/generate.py",
        "            alone = [\n                value\n                for name, value in mine.items()",
        "            alone = [\n                value\n                for name, value in [*mine.items(), (None, title.text)]",
        "tests/test_catalog_titles.py",
        "B",
        "no two SKUs of one line share a title",
    ),
    # ---- the description is a tier of its own, both directions ------------
    Mutation(
        "put the line title back in the description field",
        "domains/industrial/generate.py",
        "        return f\"{title.text} - {', '.join(details)}. {middle}{tail}\"",
        '        return f"{draft.brand} {draft.series} -- {draft.item}"',
        "tests/test_catalog_titles.py",
        "A",
        "the description names what distinguishes the SKU",
    ),
    Mutation(
        "leave the SKU's own attributes out of the description",
        "domains/industrial/generate.py",
        "        named = title.attribute_names()\n        details: list[str] = []",
        "        named = {a.name for a in attributes}\n        details: list[str] = []",
        "tests/test_catalog_titles.py",
        "B",
        "the description names what distinguishes the SKU",
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
    # ---- a published value is a token, not prose, both directions ---------
    Mutation(
        "let the stamp break a published value at its hyphen",
        "domains/industrial/render/marking.py",
        "        return tuple(textwrap.wrap(text, width=columns, break_on_hyphens=False)) if text else ()",
        "        return tuple(textwrap.wrap(text, width=columns, break_on_hyphens=True)) if text else ()",
        "tests/test_marking.py -k hyphen",
        "A",
        "the card stamp sets every published value and nothing else",
    ),
    # ---- elastic/prism-industrial-products#103: the census name gate ------
    Mutation(
        "let a product noun qualify a generic concept",
        "domains/industrial/names.py",
        "        if noun is not None and name not in TYPE_SPECIFIC:",
        "        if False and noun is not None and name not in TYPE_SPECIFIC:",
        "tests/test_attribute_names.py -k planted",
        "A",
        "no emitted name is a type-qualified spelling of a generic concept",
    ),
    Mutation(
        "publish a name the census and the reference list never saw",
        "domains/industrial/vocab.py",
        '    _spec("Tip Style", "line"),\n    _spec("Material", "line", 0.85),',
        '    _spec("Widget Material", "line"),\n    _spec("Material", "line", 0.85),',
        "tests/test_attribute_names.py -k declared",
        "B",
        "no emitted name is a type-qualified spelling of a generic concept",
    ),
    # ---- the per-SKU drawings carry no text, and every channel is real ----
    Mutation(
        "print the SKU's size on its drawing",
        "core/drawing/svg.py",
        '        tail = "</svg>"',
        '        tail = \'<text x="10" y="290">1/4"</text></svg>\'',
        "tests/test_sku_drawings.py -k no_drawing_carries_any_text",
        "A",
        "no drawing carries any text but its brand's wordmark",
    ),
    # ---- the brand plate (#132): legible, distinct, and the only text -----
    Mutation(
        "plate: hold the name to a 10 px font size, not a 10 px cap height",
        "core/drawing/sheet.py",
        "NAME_MIN = math.ceil(MIN_NAME_PX / (brand_mark.CAP_HEIGHT * TILE_PX_PER_UNIT) * 10) / 10",
        "NAME_MIN = MIN_NAME_PX / TILE_PX_PER_UNIT",
        "tests/test_brand_marks.py -k 10px_cap_height",
        "A",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: claim the face's capitals are taller than Arial Bold's",
        "core/drawing/brand_mark.py",
        "CAP_HEIGHT, DESCENDER = 0.716, 0.21",
        "CAP_HEIGHT, DESCENDER = 0.8, 0.21",
        "tests/test_brand_marks.py -k 10px_cap_height",
        "A",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: take the first layout whatever size it sets the name at",
        "core/drawing/brand_mark.py",
        "        if found is not None and found.size >= min_size:",
        "        if found is not None:",
        (
            "tests/test_brand_marks.py -k no_layout_sets_legibly",
            "tests/test_brand_marks.py -k 10px_cap_height",
        ),
        "B",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "plate: drop the split-under layout",
        "core/drawing/brand_mark.py",
        'LAYOUTS: tuple[str, ...] = ("beside", "two_beside", "split_under", "under")',
        'LAYOUTS: tuple[str, ...] = ("beside", "two_beside", "under")',
        "tests/test_brand_marks.py -k halves_do_not_both_fit",
        "B",
        "no brand name's capitals render under 10 px at the tile",
    ),
    Mutation(
        "let a two-line name's descender hang below the plate",
        "core/drawing/brand_mark.py",
        "        first = min(cy + block / 2 + DESCENDER * size, y1) - DESCENDER * size - block",
        "        first = cy + block / 2 - block",
        "tests/test_brand_marks.py -k inside_the_plate",
        "A",
        "the plate's name stays inside the plate",
    ),
    Mutation(
        "count the pixels either mark inks, not the ones only one inks",
        "core/drawing/brand_mark.py",
        "    return int(np.count_nonzero(mark_bitmap(a, px) ^ mark_bitmap(b, px)))",
        "    return int(np.count_nonzero(mark_bitmap(a, px) | mark_bitmap(b, px)))",
        "tests/test_brand_marks.py -k counts_the_pixels",
        "A",
        "two brands' marks differ visibly",
    ),
    Mutation(
        "draw two brands with one mark",
        "domains/industrial/drawing/brand_marks.py",
        '    "checker": (\n        Poly(((-0.9, -0.9), (0, -0.9), (0, 0), (-0.9, 0))),\n        Poly(((0, 0), (0.9, 0), (0.9, 0.9), (0, 0.9))),\n    ),',
        '    "checker": (Poly(((-0.3, -0.95), (0.3, -0.95), (0.3, -0.3), (0.95, -0.3), (0.95, 0.3), (0.3, 0.3), (0.3, 0.95), (-0.3, 0.95), (-0.3, 0.3), (-0.95, 0.3), (-0.95, -0.3), (-0.3, -0.3))),),',
        "tests/test_brand_marks.py -k differ_visibly",
        "B",
        "two brands' marks differ visibly",
    ),
    Mutation(
        "let the gate pass any words in a <text>",
        "core/drawing/__init__.py",
        '    if words and " ".join(words) not in _wordmarks():',
        "    if False:",
        (
            'tests/test_brand_marks.py -k "gate_refuses and size"',
            'tests/test_brand_marks.py -k "gate_refuses and half"',
        ),
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let a font attribute sit on any element",
        "core/drawing/__init__.py",
        '            if name not in ALLOWED_ATTRIBUTES or (name in _TEXT_ONLY and local != "text"):',
        "            if name not in ALLOWED_ATTRIBUTES:",
        (
            'tests/test_brand_marks.py -k "gate_refuses and font"',
            'tests/test_brand_marks.py -k "gate_refuses and circle"',
        ),
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let a character reference spell the ampersand",
        "core/drawing/__init__.py",
        '    if b"&" in svg.replace(b"&amp;", b""):',
        '    if b"&" in svg.replace(b"&amp;", b"").replace(b"&#38;", b""):',
        'tests/test_brand_marks.py -k "gate_refuses and ampersand"',
        "A",
        "a drawing's only text is a brand's wordmark",
    ),
    Mutation(
        "let the figure area run into the plate",
        "core/drawing/sheet.py",
        "    aw, ah = svg.WIDTH - 2 * MARGIN, FIGURE_HEIGHT - 2 * MARGIN",
        "    aw, ah = svg.WIDTH - 2 * MARGIN, svg.HEIGHT - 2 * MARGIN",
        "tests/test_brand_marks.py -k reaches_the_plate",
        "A",
        "no figure reaches the plate",
    ),
    Mutation(
        "let the handled glass size itself to the whole sheet, plate and all",
        "core/drawing/sheet.py",
        "    by_height = (FIGURE_HEIGHT - 2 * GLYPH_MARGIN - GLYPH_GAP - height) / (-left1 + bottom1)",
        "    by_height = (svg.HEIGHT - 2 * GLYPH_MARGIN - GLYPH_GAP - height) / (-left1 + bottom1)",
        "tests/test_sku_drawings.py -k lens_enlarges_at_least_the_measured_floor",
        "A",
        "no figure reaches the plate",
    ),
    Mutation(
        "draw every brand in one ink",
        "core/drawing/style.py",
        "    ink = brands.ink_of(brand)\n",
        '    ink = brands.ink_of(brand) and "#1b1b1b"\n',
        "tests/test_sku_drawings.py -k brand",
        "A",
        "the brand is the house style",
    ),
    Mutation(
        "draw a screw without reading its length",
        "domains/industrial/drawing/figures.py",
        "    fig = Figure(size_in=visible if broken else total)",
        "    fig = Figure(size_in=visible if broken else total)\n    total = hh + 4 * major",
        "tests/test_sku_drawings.py -k published_length",
        "A",
        "a drawn dimension changes the drawing",
    ),
    Mutation(
        "draw every product at one fixed scale instead of its type's",
        "core/drawing/__init__.py",
        "    return type_scale(extent)",
        "    return 60.0",
        "tests/test_sku_drawings.py -k true_proportion",
        "A",
        "sizes are visible: one scale per type",
    ),
    Mutation(
        "magnify a part that is small in only one dimension",
        "core/drawing/sheet.py",
        "    if width > svg.WIDTH * MAGNIFY_WIDTH_SHARE or height > svg.HEIGHT * MAGNIFY_HEIGHT_SHARE:",
        "    if width > svg.WIDTH * MAGNIFY_WIDTH_SHARE and height > svg.HEIGHT * MAGNIFY_HEIGHT_SHARE:",
        "tests/test_sku_drawings.py -k ONE_dimension",
        "A",
        "the magnifier applies only when both dimensions are small",
    ),
    Mutation(
        "draw the lens's part at true scale instead of enlarged",
        "core/drawing/sheet.py",
        "    _figure_at(page, figure, house, fill, hatch_id, scale * mag.k, mag.lens)",
        "    _figure_at(page, figure, house, fill, hatch_id, scale, mag.lens)",
        "tests/test_sku_drawings.py -k same_part_enlarged",
        "A",
        "the lens shows the same part enlarged",
    ),
    Mutation(
        "draw the magnifier in black",
        "core/drawing/sheet.py",
        "    _glyph(page, mag, house.ink)",
        '    _glyph(page, mag, "#000000")',
        "tests/test_sku_drawings.py -k brand_ink",
        "A",
        "the magnifier is in the brand ink",
    ),
    Mutation(
        "always use the handled glass, even where it cannot reach x2.5",
        "core/drawing/sheet.py",
        "    if k >= MIN_ENLARGEMENT:",
        "    if True:",
        "tests/test_sku_drawings.py -k handle_less_only",
        "A",
        "every lens enlarges at least x2.5; handle-less only when it must be",
    ),
    Mutation(
        "draw outlines at the old hairline weight",
        "core/drawing/sheet.py",
        "MIN_STROKE = 2.3",
        "MIN_STROKE = 1.6",
        "tests/test_sku_drawings.py -k minimum_stroke",
        "A",
        "no outline is thinner than the minimum stroke",
    ),
    Mutation(
        "pin the magnifier to the top instead of balancing the sheet",
        "core/drawing/sheet.py",
        "    top = (FIGURE_HEIGHT - (glyph_h + GLYPH_GAP + height)) / 2",
        "    top = GLYPH_MARGIN",
        "tests/test_sku_drawings.py -k space_above",
        "A",
        "the magnified sheet is vertically balanced",
    ),
    Mutation(
        "let a drawing carry a title element",
        "core/drawing/__init__.py",
        '    {"svg", "rect", "defs", "pattern", "g", "path", "circle", "text"}',
        '    {"svg", "rect", "defs", "pattern", "g", "path", "circle", "text", "title"}',
        "tests/test_sku_drawings.py -k title",
        "A",
        "no drawing carries any text",
    ),
    Mutation(
        "accept a census name in another casing",
        "domains/industrial/names.py",
        "        if canonical is not None and canonical != name:",
        "        if False and canonical is not None and canonical != name:",
        "tests/test_attribute_names.py -k another_casing",
        "A",
        "no emitted name is a casing twin of a census name",
    ),
    Mutation(
        "let a paint reference any url",
        "core/drawing/__init__.py",
        '            elif name != "id" and not (_VALUE_GRAMMAR.get(name) or _NUMERIC).match(value):',
        "            elif False:",
        "tests/test_sku_drawings.py -k paint",
        "A",
        "no drawing carries any text",
    ),
    # ---- price: the model and its census gate (#52) ------------------------
    # Every name starts "price:", so `--only "price:"` re-runs them. A model
    # row plants a defect in what prices a SKU and names the default-size
    # band test; a gate row widens one band and names the plant test that
    # moves prices out of it, so a band that cannot fail is red.
    *(
        Mutation(f"price: {name}", file, old, new, f"tests/test_price.py -k {test}", "A", prop)
        for name, file, old, new, test, prop in [
            (
                "price falls with the key dimension",
                "core/price.py",
                "        log_p += model.slope * math.log(key / model.anchor_key)",
                "        log_p -= model.slope * math.log(key / model.anchor_key)",
                "within_its_band_or_pinned_at_the_default_size",
                "larger costs more",
            ),
            (
                "the roller chain prices at three times its fitted anchor",
                "domains/industrial/product_types/motion/roller_chain.py",
                "    116.0,",
                "    348.0,",
                "within_its_band_or_pinned_at_the_default_size",
                "a deepened breadth category keeps its census level",
            ),
            (
                "a deepened breadth category is scored by no row",
                "domains/industrial/price_report.py",
                "    for type_key, (n, p10, p50, p90) in DEEPENED_CENSUS.items():",
                "    for type_key, (n, p10, p50, p90) in {}.items():",
                "row_names_are_the_rows_the_default_build_scores",
                "a deepened breadth category keeps its census level",
            ),
            (
                "price falls with length",
                "core/price.py",
                "        log_p += model.length_slope * math.log(length / model.anchor_length)",
                "        log_p -= model.length_slope * math.log(length / model.anchor_length)",
                "within_its_band_or_pinned_at_the_default_size",
                "longer costs more",
            ),
            (
                "a pack of more costs less",
                "core/price.py",
                "        log_p += model.pack_slope * math.log(pack / model.pack_ref)",
                "        log_p -= model.pack_slope * math.log(pack / model.pack_ref)",
                "within_its_band_or_pinned_at_the_default_size",
                "a nut's pack price",
            ),
            (
                "the brand tier is dropped",
                "core/price.py",
                "    log_p += math.log(model.tiers[tier])",
                "    log_p += 0.0",
                "tiers_price_in_order",
                "economy < standard < premium",
            ),
            (
                "the brand tier is dropped (band rows)",
                "core/price.py",
                "    log_p += math.log(model.tiers[tier])",
                "    log_p += 0.0",
                "within_its_band_or_pinned_at_the_default_size",
                "economy < standard < premium",
            ),
            (
                "every SKU draws its type's first ending class",
                "core/price.py",
                "    return with_ending(noisy(draw), ending_for(model.endings, ending_u))",
                "    return with_ending(noisy(draw), ending_for(model.endings, 0.0))",
                "within_its_band_or_pinned_at_the_default_size",
                "the census endings mix",
            ),
            (
                "group noise is off",
                "core/price.py",
                "    offset = draw.struct + model.group_sigma * _z(draw.group_u)",
                "    offset = draw.struct + 0.0 * _z(draw.group_u)",
                "within_its_band_or_pinned_at_the_default_size",
                "the fitted noise",
            ),
            (
                "group noise is tripled",
                "core/price.py",
                "    offset = draw.struct + model.group_sigma * _z(draw.group_u)",
                "    offset = draw.struct + 3 * model.group_sigma * _z(draw.group_u)",
                "within_its_band_or_pinned_at_the_default_size",
                "the fitted noise",
            ),
            (
                "SKU noise is off",
                "core/price.py",
                " + model.sku_sigma * _z(draw.sku_u)",
                " + 0.0 * _z(draw.sku_u)",
                "within_its_band_or_pinned_at_the_default_size",
                "the fitted noise",
            ),
            (
                "SKU noise is tripled",
                "core/price.py",
                " + model.sku_sigma * _z(draw.sku_u)",
                " + 3 * model.sku_sigma * _z(draw.sku_u)",
                "within_its_band_or_pinned_at_the_default_size",
                "the fitted noise",
            ),
            (
                "size noise is off",
                "core/price.py",
                "        offset += model.size_sigma * _z(draw.size_u)",
                "        offset += 0.0 * _z(draw.size_u)",
                "within_its_band_or_pinned_at_the_default_size",
                "the fitted noise",
            ),
            (
                "the tap list-price ladder is off",
                "core/price.py",
                "    offset = log_offset(draw)\n    if model.price_step:",
                "    offset = log_offset(draw)\n    if False:",
                "within_its_band_or_pinned_at_the_default_size",
                "the census tap ties",
            ),
            (
                "group noise is drawn per SKU, not per group page",
                "domains/industrial/generate.py",
                "            seed, type_key, brand, (a for a in line_attributes if a.name in always)",
                "            seed, type_key, brand + sku, (a for a in line_attributes if a.name in always)",
                "within_its_band_or_pinned_at_the_default_size",
                "a group page shares one price level",
            ),
            (
                "a breadth curve skips its census p50",
                "core/price.py",
                "        log_p = p10 + (p50 - p10) * position * 2",
                "        log_p = p10 + (p90 - p10) * position",
                "'measured_breadth_categorys_p50 and not foam_ear_plugs'",
                "a breadth category's census p50",
            ),
            (
                "a breadth curve reads its census figures in the wrong order",
                "core/price.py",
                "    p10, p50, p90 = (math.log(v) for v in measured)",
                "    p10, p90, p50 = (math.log(v) for v in measured)",
                "'measured_breadth_categorys_p50 and not foam_ear_plugs'",
                "a breadth category's census p50",
            ),
            (
                "a breadth SKU ignores its brand tier",
                "core/price.py",
                "math.exp(log_p) * TIER_FACTORS[tier]",
                "math.exp(log_p)",
                "breadth_skus_tier_scales",
                "a breadth brand's tier",
            ),
            (
                "the p50 band is x0.1 to x10",
                "domains/industrial/price_report.py",
                "P50_BAND = (0.8, 1.25)",
                "P50_BAND = (0.1, 10.0)",
                "scaling_every_price",
                "the p50 band bites",
            ),
            (
                "the p90/p10 band is x0.1 to x10",
                "domains/industrial/price_report.py",
                "\nSPREAD_BAND = (0.75, 1.33)",
                "\nSPREAD_BAND = (0.1, 10.0)",
                "widening_or_narrowing",
                "the p90/p10 band bites",
            ),
            (
                "the order band is +/-0.8",
                "domains/industrial/price_report.py",
                "MONOTONE_BAND = 0.08",
                "MONOTONE_BAND = 0.8",
                "swapping_a_products_first",
                "the order bands bite",
            ),
            (
                "the order band is +/-0.8 (length rows)",
                "domains/industrial/price_report.py",
                "MONOTONE_BAND = 0.08",
                "MONOTONE_BAND = 0.8",
                "falls_with_length",
                "the order bands bite",
            ),
            (
                "bands span 30 census standard errors",
                "domains/industrial/price_report.py",
                "CENSUS_SES = 3.0",
                "CENSUS_SES = 30.0",
                "dropping_the_99",
                "the ending bands bite",
            ),
            (
                "the equal-price band is 10x wider",
                "domains/industrial/price_report.py",
                "    width = CENSUS_SES * math.sqrt(share * (1 - share) / census.n_pairs)",
                "    width = 10 * CENSUS_SES * math.sqrt(share * (1 - share) / census.n_pairs)",
                "breaking_every_tie",
                "the equal-price band bites",
            ),
            (
                "the brand-spread band is x0.1 to x100",
                "domains/industrial/price_report.py",
                "BRAND_SPREAD_BAND = (0.75, 1.33)",
                "BRAND_SPREAD_BAND = (0.1, 100.0)",
                "brand_spread_band_is_x075_to_x133",
                "the brand-spread band bites",
            ),
            (
                "the economy band is x0.1 to x10",
                "domains/industrial/price_report.py",
                "ECONOMY_BAND = (0.75, 1.33)",
                "ECONOMY_BAND = (0.1, 10.0)",
                "economy_brands_priced_as_dear",
                "the economy band bites",
            ),
            (
                "a pin may worsen by half",
                "core/price.py",
                "PIN_TOLERANCE = 0.02",
                "PIN_TOLERANCE = 0.5",
                "a_pin_whose_shortfall_worsens",
                "a pin may not worsen",
            ),
            (
                "a below-band pin holds wherever it lands",
                "domains/industrial/price_report.py",
                "        return recorded / (1 + PIN_TOLERANCE) <= row.achieved < row.band[0]",
                "        return True",
                "a_pin_whose_shortfall_worsens",
                "a pin may not worsen",
            ),
            (
                "the 2x band floor is 0.5",
                "domains/industrial/price_report.py",
                "TWICE_BAND_FLOOR = 0.02",
                "TWICE_BAND_FLOOR = 0.5",
                "twice_band_floor",
                "the 2x band bites",
            ),
            (
                "the kit p90/p10 pin's 100K record is loosened by hand",
                "core/price.py",
                "    _KIT_SPREAD_ROW: (4.032, 3.917),",
                "    _KIT_SPREAD_ROW: (4.032, 3.5),",
                "figure_its_build_produces",
                "a record is the build's figure",
            ),
            # ---- kit: a kit is priced from what it holds (#71) ----
            # Every name also starts "price: kit:", so `--only "kit:"` re-runs these.
            (
                "kit: a kit draws group noise again",
                "core/price.py",
                '"kit_assortment": _model("kit_assortment", 100.9, 100.0, 0.000, 0.022),',
                '"kit_assortment": _model("kit_assortment", 100.9, 100.0, 0.300, 0.022),',
                "tracks_its_contents_at_both_builds",
                "a kit's price tracks its contents",
            ),
            (
                "kit: a kit is priced on its piece count, not its contents",
                "core/price.py",
                "        return kit_contents(attributes)",
                "        return KEYS[type_key](attributes)",
                "tracks_its_contents_at_both_builds",
                "a kit's price tracks its contents",
            ),
            (
                "kit: a kit's pieces are priced at their part's shown price, packs and all",
                "core/price.py",
                "    return total * pieces.value_num / len(values) * each / shown",
                "    return total * pieces.value_num / len(values)",
                "kits_contents_are_its_pieces",
                "a kit's contents are its pieces' census-worked price",
            ),
            (
                "kit: a kit costs the mean of its pieces, not their sum",
                "core/price.py",
                "    return total * pieces.value_num / len(values) * each / shown",
                "    return total / len(values) * each / shown",
                "holding_more_of_the_same_sizes",
                "a kit holding more of the same sizes costs more",
            ),
            (
                "the wheel pin's 100K record is loosened by hand",
                "core/price.py",
                "    _WHEEL_SPREAD_ROW: (4.303, 2.842),",
                "    _WHEEL_SPREAD_ROW: (4.303, 3.25),",
                "figure_its_build_produces",
                "a record is the build's figure",
            ),
            (
                "a pin reads its default figure at 100K",
                "domains/industrial/price_report.py",
                "    recorded = PINNED_FIGURES[row.name][build]",
                "    recorded = PINNED_FIGURES[row.name][0]",
                "a_pin_may_land_no_further_out",
                "a pin holds each build to its own figure",
            ),
            (
                "a wheel spec reads Material, which a wheel never publishes",
                "core/price.py",
                'MATERIAL_ATTRIBUTES: dict[str, str] = {"wheel_depressed_center": '
                '"Abrasive Material"}',
                "MATERIAL_ATTRIBUTES: dict[str, str] = {}",
                "spec_holds_a_material_or_names_why_not",
                "every brand-census spec holds a material",
            ),
            (
                "a material is read off Material for every type",
                "core/price.py",
                '    name = MATERIAL_ATTRIBUTES.get(type_key, "Material")',
                '    name = "Material"',
                "wheel_spec_holds_its_abrasive",
                "a wheel's material is its abrasive",
            ),
            (
                "the material guard counts an empty material as held",
                "domains/industrial/price_report.py",
                "    held = {spec[0] for spec in collected.specs if spec[2]}",
                "    held = {spec[0] for spec in collected.specs}",
                "never_publishes_is_caught",
                "a type whose specs hold no material is caught",
            ),
            (
                "the wheel pin quotes a tier figure no build measures",
                "core/price.py",
                "the brand tiers alone give 1.49 on the default",
                "the brand tiers alone give 1.39 on the default",
                "tiers_alone_give",
                "a pin's stated cause is measured",
            ),
        ]
    ),
    # ---- table: the table-driven types (#101) ------------------------------
    # Every name starts "table:", so `--only "table:"` re-runs them. A table
    # type's price is a declared ladder nobody measured, so what is planted is
    # a broken ORDER, never a wrong level.
    *(
        Mutation(f"table: {name}", file, old, new, test, direction, prop)
        for name, file, old, new, test, direction, prop in [
            (
                "a larger size costs no more",
                "domains/industrial/tabletype.py",
                "            slope=self.size_slope,",
                "            slope=0.0,",
                "tests/test_tabletype.py -k a_larger_size_costs_more",
                "",
                "a larger size costs more",
            ),
            (
                "a bigger pack costs the same in total",
                "domains/industrial/tabletype.py",
                "            pack_slope=self.pack_slope,",
                "            pack_slope=0.0,",
                "tests/test_tabletype.py -k a_bigger_pack_costs_more",
                "A",
                "a bigger pack costs more in total and less a piece",
            ),
            (
                "a bigger pack costs the same a piece",
                "domains/industrial/tabletype.py",
                "            pack_slope=self.pack_slope,",
                "            pack_slope=1.0,",
                "tests/test_tabletype.py -k a_bigger_pack_costs_more",
                "B",
                "a bigger pack costs more in total and less a piece",
            ),
            (
                "a table's material ladder is not read",
                "core/price.py",
                "    factors = MATERIAL_FACTORS if model.materials is None else model.materials",
                "    factors = MATERIAL_FACTORS",
                "tests/test_tabletype.py -k tables_own_factor",
                "",
                "a material costs the table's own factor",
            ),
            (
                "a table price claims to be measured",
                "domains/industrial/tabletype.py",
                "            measured=False,",
                "            measured=True,",
                "tests/test_tabletype.py -k claims_no_measurement",
                "",
                "a table price claims no measurement",
            ),
            (
                "falling sizes are accepted",
                "domains/industrial/tabletype.py",
                "        (sizes == sorted(set(sizes)) and sizes[0] > 0,",
                "        (sizes[0] > 0,",
                "tests/test_tabletype.py -k would_break_an_order",
                "",
                "a table that breaks an order is refused",
            ),
            (
                "a ladder whose cheapest material is not the base is accepted",
                "domains/industrial/tabletype.py",
                "        (factors == sorted(factors) and factors[0] == 1.0,",
                "        (factors == sorted(factors),",
                "tests/test_tabletype.py -k cheapest_material_is_not_the_base",
                "",
                "a table that breaks an order is refused",
            ),
            (
                "an inch table is read as millimetres",
                "domains/industrial/tabletype.py",
                '        return MM_PER_INCH if self.unit == "mm" else 1.0',
                "        return MM_PER_INCH",
                "tests/test_tabletype.py -k an_inch_tables_rows_are_inches",
                "",
                "an inch table is in inches",
            ),
            (
                "an inch table is published in the metric style",
                "domains/industrial/tabletype.py",
                "        style = gen._style(table.unit)",
                '        style = gen._style("mm")',
                "tests/test_tabletype.py -k an_inch_table_is_built_in_inches",
                "",
                "an inch table is in inches",
            ),
            (
                "a table type is not recorded as one",
                "domains/industrial/tabletype.py",
                "    _MADE.setdefault(table.key, table)",
                '    _MADE.setdefault(table.key + "?", table)',
                "tests/test_tabletype.py -k is_a_recorded_table_type",
                "",
                "the table types are found, not listed",
            ),
            (
                "a missing column is drawn at the row's size, not the SKU's",
                "domains/industrial/tabletype.py",
                "own.get(name, nearest[name] * scale)",
                "own.get(name, nearest[name])",
                "tests/test_tabletype.py -k nearest_rows_proportion",
                "",
                "a drawing is scaled from the record",
            ),
            (
                "a cotter pin's eye is drawn from its diameter, not its row",
                "domains/industrial/product_types/fasteners/cotter_pins.py",
                "    radius = c / 2",
                "    radius = d",
                "tests/test_type_cotter_pins.py -k scaled_from_its_row",
                "",
                "a drawing is scaled from the record",
            ),
            (
                "a retaining ring's edge is drawn at one thickness",
                "domains/industrial/product_types/fasteners/retaining_rings_external.py",
                '    fig.rect(edge, -outer, edge + thickness, outer, "plain")',
                '    fig.rect(edge, -outer, edge + 0.05, outer, "plain")',
                "tests/test_type_retaining_rings_external.py -k scaled_from_its_row",
                "",
                "a drawing is scaled from the record",
            ),
            (
                "a cotter pin row is typed wrong",
                "domains/industrial/product_types/fasteners/cotter_pins.py",
                "    (2.0, 3.6, 4.0),",
                "    (2.0, 3.8, 4.0),",
                "tests/test_type_cotter_pins.py -k every_row_of_the_table_is_built",
                "",
                "every built size is a row of the table",
            ),
            (
                "stainless retaining rings cost what steel ones do",
                "domains/industrial/product_types/fasteners/retaining_rings_external.py",
                '        Variant("Stainless Steel", "Plain", 2.6),',
                '        Variant("Stainless Steel", "Plain", 1.0),',
                "tests/test_type_retaining_rings_external.py -k larger_dearer_material",
                "",
                "a dearer material costs more",
            ),
        ]
    ),
    # ---- retail: scent depth for "lemon" and "honey" (gen#154) ----
    *(
        Mutation(f"scent depth: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a depth family is sized against the whole weight, so every core budget moves",
                "grocery.py",
                "sum(f.weight for f in FAMILIES if not f.depth)",
                "sum(f.weight for f in FAMILIES)",
                "tests/test_grocery_scent_depth_154.py -k core_styles_do_not_move",
                "adding a scent family leaves the core grocery styles as built",
            ),
            (
                "a floor cleaner is too small a family to show a lemon",
                "grocery_rows.py",
                '_HOME_BRANDS, 0.016, axis="scent",\n           department="Cleaning & Janitorial", noun="concentrated',
                '_HOME_BRANDS, 0.001, axis="scent",\n           department="Cleaning & Janitorial", noun="concentrated',
                "tests/test_grocery_scent_depth_154.py -k lemon_is_a_scent",
                "lemon is a scent in dozens of SKUs of each type",
            ),
            (
                "a dish soap holds its scent as a flavor",
                "grocery_rows.py",
                '_HOME_SCENTS, _HOME_BRANDS, 0.01, axis="scent",\n           department="Cleaning & Janitorial", noun="washing-up',
                '_HOME_SCENTS, _HOME_BRANDS, 0.01, axis="flavor",\n           department="Cleaning & Janitorial", noun="washing-up',
                "tests/test_grocery_scent_depth_154.py -k told_apart_by_attribute",
                "a scented SKU carries scent, never flavor",
            ),
            (
                "a depth description falls back to the multi-surface spray",
                "grocery.py",
                "noun = fam.noun or (",
                "noun = (",
                "tests/test_grocery_scent_depth_154.py -k describes_its_own_product",
                "a scent style describes its own product",
            ),
        ]
    ),
    # ---- retail: a jean's fit and a bra's style are facets, not leaves ----
    *(
        Mutation(f"facet leaves: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a jean keeps its fit leaf",
                "facet_leaves.py",
                "        return path[:-1]\n    if product_type",
                "        return path\n    if product_type",
                "tests/test_retail_facet_leaves.py -k end_at_their_kind_node",
                "a fit is not a category leaf",
            ),
            (
                "a purpose bra loses its node",
                "facet_leaves.py",
                "return path if path[-1] in PURPOSE_BRAS else path[:-1]",
                "return path[:-1]",
                "tests/test_retail_facet_leaves.py -k purpose_nodes_are_the_only_children",
                "the purpose nodes stay",
            ),
            (
                "a title's own bra facet is dropped",
                "facet_leaves.py",
                "for key, value in stated_bra_facets(rec[\"title\"])",
                "for key, value in []",
                "tests/test_retail_facet_leaves.py -k every_value_its_title_names",
                "a bra carries what its title says",
            ),
            (
                "leg_style is not folded into leg_fit",
                "facet_leaves.py",
                '        fit = fit or LEG_STYLE_FITS.get(have.get("leg_style", ""))\n',
                "",
                "tests/test_retail_facet_leaves.py -k every_jean_has_a_leg_fit",
                "every jean has a leg_fit",
            ),
            (
                "wide trousers are written Wide",
                "facet_leaves.py",
                '    "wide": "Wide Leg",',
                '    "wide": "Wide",',
                "tests/test_retail_facet_leaves.py -k keeps_the_fit_its_old_leaf_named",
                "the fit is the old leaf's",
            ),
            (
                "bra_style stays beside the split facets",
                "facet_leaves.py",
                'return out, {"bra_style", "fabric"}',
                'return out, {"fabric"}',
                "tests/test_retail_facet_leaves.py -k bra_style_and_leg_style_are_gone",
                "bra_style is gone",
            ),
            (
                "the fibre-content detail is dropped",
                "export.py",
                "        doc[\"fibre_content\"] = blend\n",
                "        pass\n",
                "tests/test_retail_facet_leaves.py -k blend_is_a_detail",
                "the blend is a detail",
            ),
            (
                "one bra spells Lightly Lined with a hyphen",
                "facet_leaves.py",
                '"Spacer Cup Bras": ("T-Shirt", "Lightly Lined", None, None),',
                '"Spacer Cup Bras": ("T-Shirt", "Lightly-Lined", None, None),',
                "tests/test_retail_facet_leaves.py -k differ_only_in_case_or_hyphenation",
                "one spelling per facet value",
            ),
            (
                "a convertible bra is only Multiway",
                "facet_leaves.py",
                '("Multiway", "Halterneck", "Cross Back")',
                '"Multiway"',
                "tests/test_retail_audience.py -k cleaning_root",
                "no text contradicts a bra facet",
            ),
            (
                "a cropped balloon jean is not Cropped",
                "facet_leaves.py",
                "            fits.append(CROPPED)\n",
                "            pass\n",
                "tests/test_retail_facet_leaves.py -k text_says_cropped",
                "a jean whose text says cropped is cropped",
            ),
        ]
    ),
    # ---- retail: the Combined loader takes every authored SKU (gen#279) ----
    # Every name starts "combined loader:", so `--only "combined loader:"` re-runs them.
    *(
        Mutation(f"combined loader: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a crossbody bag is sold in a Mini size, which is no size system",
                "accessory_rows.py",
                '_sizes(("Small", 28.0), ("Medium", 34.0))',
                '_sizes(("Mini", 28.0), ("Small", 34.0))',
                "tests/test_retail_combined_loader_279.py -k has_a_size_the_combined_loader_refuses",
                "every size is in a size system the loader declares",
            ),
            (
                "a skirt's fit axis is the bare length the loader renames onto garment_length",
                "lowerbody_rows.py",
                'axis_key="fit_length", axis=_legs()',
                'axis_key="length", axis=_legs()',
                "tests/test_retail_combined_loader_279.py -k writes_a_renamed_key_twice",
                "no SKU writes a renamed key twice",
            ),
        ]
    ),
    # ---- retail: text-match decoys (gen#294) ----
    *(
        Mutation(f"text-match decoys: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a decoy is color-completed",
                "main_colors.py",
                ' and r["product_id"] not in decoy_rows.IDS',
                "",
                "tests/test_retail_text_match_decoys_294.py -k never_copied_or_color_completed",
                "no color completion gives a decoy the query's color",
            ),
            (
                "a decoy is copied by the derivation",
                "scale.py",
                "| MENS_DEPTH_IDS | decoy_rows.IDS\n",
                "| MENS_DEPTH_IDS\n",
                "tests/test_retail_text_match_decoys_294.py -k never_copied_or_color_completed",
                "a decoy stays a template",
            ),
            (
                "a decoy sells nothing, so it cannot compete",
                "decoy_rows.py",
                "one(color, self.sold)",
                "one(color, 1)",
                "tests/test_retail_text_match_decoys_294.py -k decoys_lead_the_top_10",
                "the decoys reach the baseline top 10",
            ),
            (
                "a class 7 decoy loses its ingredients",
                "decoy_rows.py",
                "        if row.ingredients:\n",
                "        if False:\n",
                "tests/test_retail_text_match_decoys_294.py -k hold_the_word_only_in_the_ingredients",
                "the word is on the label",
            ),
            (
                "a part decoy gets the query's color in its color field",
                "decoy_rows.py",
                '"A blue velvet sofa finished with red piping along the seams.", "Blue", 1',
                '"A blue velvet sofa finished with red piping along the seams.", "Red", 1',
                "tests/test_retail_text_match_decoys_294.py -k decoy_is_a_hit",
                "a decoy's fields tell the truth",
            ),
            (
                "the docs table is not the generated one",
                "decoy_rows.py",
                '"true hit" if d.true_hit else "decoy"',
                '"decoy" if d.true_hit else "true hit"',
                "tests/test_retail_text_match_decoys_294.py -k docs_table_is_generated",
                "the docs table is generated",
            ),
            (
                "a guard loses its color word",
                "decoy_rows.py",
                '"Green Tea, 40 Bags"',
                '"Tea, 40 Bags"',
                "tests/test_retail_text_match_decoys_294.py -k guard_holds_every_word",
                "a guard holds its query's words and ranks first",
            ),
            (
                "a decoy's ingredient has no base row",
                "grocery_ingredients.py",
                "lentils: lentil\n",
                "",
                "tests/test_grocery_ingredient_base_295.py -k scale_build_with_the_decoys",
                "every label of the scale build has a base row",
            ),
        ]
    ),
    # ---- retail: text-match decoys on every clothing type (gen#311) ----
    *(
        Mutation(f"apparel decoys: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "an apparel decoy is color-completed",
                "main_colors.py",
                "decoy_rows.IDS | decoy_apparel.IDS",
                "decoy_rows.IDS",
                "tests/test_retail_apparel_decoys_311.py -k never_copied_or_color_completed",
                "no color completion gives an apparel decoy the query's color",
            ),
            (
                "an apparel decoy is copied by the derivation",
                "scale.py",
                "                | decoy_apparel.IDS)",
                "                )",
                "tests/test_retail_apparel_decoys_311.py -k never_copied_or_color_completed",
                "an apparel decoy stays a template",
            ),
            (
                "a class 4 decoy names a material the style holds",
                "decoy_apparel.py",
                "            if word not in held:\n",
                "            if True:\n",
                "tests/test_retail_apparel_decoys_311.py -k fields_contradict",
                "the absent material is absent from every field",
            ),
            (
                "a class 6 category word is one the path holds",
                "decoy_apparel.py",
                "            if not path_has(name.split()[0].lower()):\n",
                "            if True:\n",
                "tests/test_retail_apparel_decoys_311.py -k fields_contradict",
                "a category-word range is not the product's own category",
            ),
            (
                "the decoy exemption from the text check is removed",
                "scale.py",
                "DECOY_IDS = decoy_rows.IDS | decoy_apparel.IDS\n",
                "DECOY_IDS = frozenset()\n",
                "tests/test_retail_apparel_decoys_311.py -k misleading_color",
                "a decoy naming only another color passes the standard by its id",
            ),
            (
                "the decoy exemption widens to every id",
                "scale.py",
                "DECOY_IDS = decoy_rows.IDS | decoy_apparel.IDS\n",
                'DECOY_IDS = type("All", (frozenset,), {"__contains__": lambda self, x: True})()\n',
                "tests/test_retail_apparel_decoys_311.py -k two_tables",
                "no real product is exempt from the text check",
            ),
            (
                "a part is drawn without its color",
                "details.py",
                '<path d="{d}" fill="{color}" stroke="{INK}" stroke-width="1.6"',
                '<path d="{d}" fill="#ffffff" stroke="{INK}" stroke-width="1.6"',
                "tests/test_retail_apparel_decoys_311.py -k named_part_is_drawn",
                "the named part carries the named color",
            ),
            (
                "a hem band moves to the top of the garment",
                "details.py",
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0), "torso")',
                'TORSO_HEM = band((0.0, 0.0, 1.0, 0.11), "torso")',
                "tests/test_retail_apparel_decoys_311.py -k sits_where_the_part_sits",
                "a hem is drawn at the bottom of the garment",
            ),
            (
                "a sole is drawn across the shoe's upper",
                "details.py",
                '"shoe": {"sole": marked("sole")},',
                '"shoe": {"sole": band((0.0, 0.62, 1.0, 0.92), "all")},',
                "tests/test_retail_apparel_decoys_311.py -k sits_where_the_part_sits",
                "a sole is drawn on the kit's own sole path",
            ),
            (
                "a hem band paints the sleeve cuffs",
                "details.py",
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0), "torso")',
                'TORSO_HEM = band((0.0, 0.89, 1.0, 1.0))',
                "tests/test_retail_apparel_decoys_311.py -k torsos_and_does_not_color",
                "a sleeve's cuff is not part of the hem",
            ),
        ]
    ),
    # ---- pack: bolts and socket screws publish the census pack (#65) ------
    *(
        Mutation(
            f"pack: {name}", file, old, new, f"tests/test_pack_quantity.py -k {test}", "A", prop
        )
        for name, file, old, new, test, prop in [
            (
                "the pack grows with the size",
                "core/price.py",
                "    quantile = 1.0 - (rank + u) / sizes",
                "    quantile = (rank + u) / sizes",
                "never_grows_with_the_size",
                "the pack falls as the size grows",
            ),
            (
                "every line of a size takes one pack",
                "core/price.py",
                "    quantile = 1.0 - (rank + u) / sizes",
                "    quantile = 1.0 - (rank + 0.5) / sizes",
                "even_spread_over_the_sizes",
                "the build publishes the census counts",
            ),
            (
                "the bolt's pack does not enter its price",
                "core/price.py",
                '            pack_slope=PACK_SLOPES["bolt_hex"],',
                "            pack_slope=0.0,",
                "prices_its_pack_on_the_census_slope",
                "the price is the pack's",
            ),
            (
                "a census pack count drifts",
                "core/price.py",
                "        100: 76,",
                "        100: 77,",
                "each_pack_count_is_the_census_count",
                "the counts are the census's",
            ),
        ]
    ),
    # ---- retail: suits and tailoring draw the record's choice (gen#215) ----
    *(
        Mutation(f"suits: {name}", file, old, new, test, "", prop,
                 root="prototypes/retail_drawings")
        for name, file, old, new, test, prop in [
            (
                "a long trouser is drawn as long as a short one",
                "kit_suits.py",
                '_HEM = {"short": 316, "regular": 340, "long": 366}',
                '_HEM = {"short": 340, "regular": 340, "long": 340}',
                "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
                "the leg length changes the hem, not only the stamp",
            ),
            (
                "slim, tailored and regular jackets share one geometry",
                "kit_suits.py",
                '_JACKET = {"slim": (142, 136), "tailored": (134, 126), "regular": (122, 116)}',
                '_JACKET = {"slim": (122, 116), "tailored": (122, 116), "regular": (122, 116)}',
                "tests/test_retail_suits_215.py -k cut_closer_to_the_body",
                "the fit changes the cut of a jacket, not only the stamp",
            ),
            (
                "slim, tailored and regular trousers share one leg width",
                "kit_suits.py",
                '_LEG_W = {"slim": 17, "tailored": 22, "regular": 28}',
                '_LEG_W = {"slim": 22, "tailored": 22, "regular": 22}',
                "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
                "the fit changes the width of a trouser leg, not only the stamp",
            ),
            (
                "the notch lapel is drawn as the shawl",
                "kit_suits.py",
                '    if lapel == "notch":',
                '    if lapel == "notch" and False:',
                "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
                "the lapel changes the path, not only the stamp",
            ),
            (
                "a waistcoat record of four or six buttons is drawn with five",
                "mens_depth_rows.py",
                '("buttons", _BUTTONS[detail])',
                '("buttons", "5")',
                "tests/test_retail_suits_215.py -k draws_what_its_record_states",
                "a waistcoat draws the button count its record states",
            ),
            (
                "a decoy accessory drops its accessory type",
                "mens_depth_rows.py",
                "            if kind.item:",
                "            if False:",
                "tests/test_retail_suits_215.py -k decoy_accessory_states",
                "a decoy accessory states its accessory type",
            ),
            (
                "a three-button jacket is drawn with two buttons",
                "kit_suits.py",
                '        buttons=3 if buttons == "3" else 2,',
                "        buttons=2,",
                "tests/test_retail_suits_215.py -k draws_as_many_buttons",
                "a jacket draws the button count its record states",
            ),
        ]
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


class DisjunctiveSelector(ValueError):
    """A selector's ``-k`` filter names two tests with ``or``.

    This harness's verdict is "pytest went red", so a selector matching two
    tests is caught the moment EITHER of them fails -- and the other one is
    printed ``[ok]`` on its back without ever having been shown to bite.

    Measured: ``-k 'mid_word or sheds'`` reported one mutation caught while
    only the segment-level test was doing the catching; the string-level test
    could have been deleted and the row would have stayed green.

    THE FIX IS TWO ENTRIES, NOT A WIDER FILTER. One mutation may legitimately
    be expected to red two tests; write it as two ``Mutation`` rows with one
    selector each, and the table then says which test caught what. ``and`` is
    not refused -- narrowing to a single test is the point of this rule.
    """


def _selector_names_one_test(selector: str) -> None:
    """Refuse a ``-k`` filter that can be satisfied by either of two tests."""
    argv = shlex.split(selector)
    if "-k" not in argv:
        return
    expression = argv[argv.index("-k") + 1]
    if re.search(r"\bor\b", expression):
        raise DisjunctiveSelector(
            f"{selector!r} is satisfied by EITHER test, so one of them is "
            "never proven to bite. Split it into two Mutation rows with one "
            "selector each."
        )


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
            "one filter, or -- better here -- one Mutation row per test."
        )
    _selector_names_one_test(selector)
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
    for selector in sorted({s for m in mutations for s in m.selectors}):
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
            # EVERY selector is judged on its own. A row naming two tests is
            # only FULLY proven when both red, so one of them can never be
            # carried by the other -- see ``Mutation.tests``.
            survivors = [s for s in mutation.selectors if run(s)]
            if survivors and not _mutation_is_live(path, mutation):
                rows.append((mutation, False, "MUTATION DID NOT REACH THE INTERPRETER"))
                print(f"[!!] {mutation.name}: source changed but the import did not")
                continue
        finally:
            path.write_text(original, encoding="utf-8")
        # THREE STATES, NOT TWO. "Nothing red" is a defect that would ship;
        # "something red, but a named test did not bite" is a defect that is
        # caught by a test other than the one the row credits. Reporting both
        # as one verdict is what the disjunctive selectors used to do.
        caught = not survivors
        if caught:
            note = "red"
        elif len(survivors) < len(mutation.selectors):
            note = "caught, but NOT by " + ", ".join(survivors)
        else:
            note = "GREEN -- NOT CAUGHT"
        rows.append((mutation, caught, note))
        marker = "ok" if caught else ("~ " if len(survivors) < len(mutation.selectors) else "  ")
        print(f"[{marker}] {mutation.name}: {note}")

    print("\nre-checking the suite is green after restoring ...")
    ok = all(run(selector) for selector in sorted({s for m in mutations for s in m.selectors}))
    print("  green" if ok else "  STILL RED -- a mutation was not reverted")

    caught = sum(1 for _, c, _ in rows if c)
    print(f"\n{caught} of {len(rows)} mutations caught by EVERY test they name")
    ships_green = [(m, n) for m, c, n in rows if not c and n.startswith("GREEN")]
    partial = [(m, n) for m, c, n in rows if not c and n.startswith("caught, but")]
    if ships_green:
        print("\nNOT CAUGHT -- these defects would ship green:")
        for mutation, note in ships_green:
            print(f"  - {mutation.name} ({mutation.property_name}): {note}")
    if partial:
        print(
            "\nCAUGHT, BUT BY ANOTHER TEST -- the defect is guarded; the test "
            "named here is not proven to bite by this mutation:"
        )
        for mutation, note in partial:
            print(f"  - {mutation.name}: {note}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
