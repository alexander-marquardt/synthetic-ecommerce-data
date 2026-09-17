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
