"""The build holds one product type at a time, so its peak does not grow with the catalog (gen#952).

``ecom-generate build`` used to build every type into one catalog before it wrote a line, so its
peak grew with the catalog: on main at seed 7 the peak RSS went from 118 MiB at 2,600 lines to
188 MiB at 5,200. It now builds a type, audits it, writes its lines and drops it before it builds
the next (``iter_types``). What it keeps across types is tallies, per-type summaries and the
price census's per-SKU ids; the figures pass counts a product's (product, value) pairs and drops
them before the next product. The same doubling grows its peak by about 5 MiB, from 65 to 70 MiB.

It writes into a temporary directory beside ``--out`` and moves the files in only once every
audit has passed, so a refusal raised after some types were already written still leaves
``--out`` untouched (gen#253).

The stress catalog (``--stress-keys``, gen#948) streams too (gen#952 slice 3). It used to gather
every nested document into one list, then every expanded one into a second: at seed 7 its peak
went from 203 MiB at 2,600 lines to 346 MiB at 5,200. Each type's documents now go to a spool
file, and the expansion reads it back one document at a time.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import weakref
from pathlib import Path

import pytest

from synthetic_ecommerce_data import generate_cli as cli
from synthetic_ecommerce_data import stress
from synthetic_ecommerce_data.core import emit, standard
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import generate as gen
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.measure import measure
from synthetic_ecommerce_data.prism import derive

#: Not the default seed, so the build writes no field map into the source tree.
SEED = 7
#: The doubling: the golden size, then twice it.
LINES = 2600
#: How much the build's peak RSS may grow when ``--lines`` doubles from :data:`LINES`.
#: Streamed, it grows by about 5 MiB. Holding the catalog whole it grew by 70 MiB.
GROWTH_CEILING_MIB = 25
#: The stress builds' flags: a key target and copies per attribute large enough that the
#: expanded documents dwarf the standard ones.
STRESS_KEYS = 5000
STRESS_COPIES = 3
STRESS = ("--stress-keys", str(STRESS_KEYS), "--stress-copies", str(STRESS_COPIES))
#: The builds the doubling compares: the standard build and the stress build.
MODES = {"standard": (), "stress": STRESS}

#: The files the build writes one type at a time, and the writer each comes from.
WRITERS = {
    "nested.jsonl": emit.iter_nested,
    "flat.jsonl": emit.iter_flat,
    "images.jsonl": emit.iter_image_manifest,
}

#: Runs one build in a fresh interpreter and prints its own peak RSS, in KiB.
PEAK_RSS = """
import resource, sys
from synthetic_ecommerce_data import generate_cli
code = generate_cli.main(sys.argv[1:])
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print("PEAK_KIB", peak // 1024 if sys.platform == "darwin" else peak)
sys.exit(code)
"""


def _digest(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture(scope="module")
def doubled(tmp_path_factory: pytest.TempPathFactory) -> dict[tuple[str, int], tuple[int, Path]]:
    """The standard and the stress build at :data:`LINES` and twice it, each in its own
    interpreter, side by side: ``{(mode, lines): (peak RSS in KiB, --out)}``."""
    root = tmp_path_factory.mktemp("doubled")
    runs = {}
    for mode, extra in MODES.items():
        for lines in (LINES, 2 * LINES):
            out = root / f"{mode}-{lines}"
            argv = ["build", "--lines", str(lines), "--seed", str(SEED), "--out", str(out), *extra]
            process = subprocess.Popen(
                [sys.executable, "-c", PEAK_RSS, *argv],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            runs[mode, lines] = (process, out)
    peaks = {}
    for (mode, lines), (process, out) in runs.items():
        stdout, stderr = process.communicate(timeout=540)
        failed = f"the {mode} --lines {lines} build failed:\n{stderr[-2000:]}"
        assert process.returncode == 0, failed
        peak = next(line for line in stdout.splitlines() if line.startswith("PEAK_KIB"))
        peaks[mode, lines] = (int(peak.split()[1]), out)
    return peaks


@pytest.mark.parametrize("mode", list(MODES))
def test_the_peak_does_not_grow_with_the_catalog(doubled, mode) -> None:
    """Twice the lines, about the same peak: no structure the build keeps grows with the rows,
    in the standard build or the stress one."""
    small, _ = doubled[mode, LINES]
    large, _ = doubled[mode, 2 * LINES]
    growth = (large - small) / 1024
    assert growth < GROWTH_CEILING_MIB, (
        f"The {mode} build at --lines {LINES} peaked at {small // 1024} MiB and at --lines "
        f"{2 * LINES} at "
        f"{large // 1024} MiB: {growth:.0f} MiB more for twice the catalog, over the "
        f"{GROWTH_CEILING_MIB} MiB ceiling. Something the build keeps across types grows with "
        "the rows."
    )


def test_the_streamed_build_writes_what_the_whole_catalog_does(doubled) -> None:
    """At twice the golden size: the files and figures are those of the whole catalog, built in
    one piece and written by the same writers (the golden size is ``test_catalog_golden``)."""
    lines = 2 * LINES
    _, out = doubled["standard", lines]
    config = GeneratorConfig(seed=SEED, lines=lines)
    catalog = generate(config)
    base_url = emit.DEFAULT_IMAGE_BASE_URL
    for name, rows in WRITERS.items():
        # strict: a file with a line more or fewer than the catalog raises.
        with (out / name).open(encoding="utf-8") as written:
            pairs = zip(written, rows(catalog, base_url), strict=True)
            for number, (line, row) in enumerate(pairs, 1):
                assert line == json.dumps(row, ensure_ascii=False) + "\n", f"{name}:{number}"
    stats = json.loads((out / "stats.json").read_text(encoding="utf-8"))
    measured = cli.round_floats(cli._serialisable(measure(catalog, config)))
    assert {key: stats[key] for key in measured} == json.loads(json.dumps(measured))
    authored = json.loads((out / "authored_names.json").read_text(encoding="utf-8"))
    assert authored == emit.authored_name_map(catalog)


def _whole_list_stress(config: GeneratorConfig) -> dict[str, bytes]:
    """The stress files as main wrote them before it streamed: every nested document of the whole
    catalog in one list, every expanded one in another, each file written from those lists."""
    catalog = generate(config)
    docs = list(emit.iter_nested(catalog, emit.DEFAULT_IMAGE_BASE_URL))
    bases = stress.base_keys(docs)
    copies = stress.copies_per_attribute(STRESS_KEYS, len(bases))
    expanded = [stress.expand_product(doc, copies, STRESS_COPIES) for doc in docs]

    def lines(rows) -> bytes:
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()

    run = {"target_keys": STRESS_KEYS, "max_copies": STRESS_COPIES}
    run |= {"base_keys": len(bases), "copies_per_attribute": copies}
    figures = {"config": run, "census": stress.census(expanded)}
    return {
        "flat.jsonl": lines(row for doc in expanded for row in standard.flat_documents(doc)),
        "mapping.flat.json": (json.dumps(emit.FLAT_MAPPING, indent=1) + "\n").encode(),
        "mapping.nested.json": (json.dumps(emit.NESTED_MAPPING, indent=1) + "\n").encode(),
        "nested.jsonl": lines(expanded),
        stress.CENSUS: (json.dumps(figures, indent=1) + "\n").encode(),
    }


def _files(root: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in sorted(root.iterdir())}


def test_the_streamed_stress_build_writes_what_the_whole_list_does(doubled) -> None:
    """At twice the golden size, every file the stress build writes, and no other, is the one the
    whole-list path writes."""
    _, out = doubled["stress", 2 * LINES]
    expected = _whole_list_stress(GeneratorConfig(seed=SEED, lines=2 * LINES))
    written = _files(out)
    assert sorted(written) == sorted(expected)
    for name, content in expected.items():
        assert written[name] == content, name


def test_the_stress_build_at_the_golden_seed_writes_what_the_whole_list_does(tmp_path) -> None:
    """At the golden seed and size (the default config): the same files, byte for byte."""
    out = tmp_path / "stress"
    assert cli.main(["build", "--out", str(out), *STRESS]) == 0
    expected = _whole_list_stress(GeneratorConfig())
    written = _files(out)
    assert sorted(written) == sorted(expected)
    for name, content in expected.items():
        assert written[name] == content, name


def test_no_earlier_type_is_held_while_the_next_is_built(tmp_path, monkeypatch) -> None:
    """Each type's products are freed before the next type is built, and a finished build leaves
    no temporary directory beside ``--out``."""
    built = weakref.WeakSet()
    held: list[int] = []
    real = gen.Generator.build

    def build(self):
        held.append(len(built))
        lines = real(self)
        built.update(lines)
        return lines

    monkeypatch.setattr(gen.Generator, "build", build)
    out = tmp_path / "catalog"
    assert cli.main(["build", "--lines", "200", "--seed", str(SEED), "--out", str(out)]) == 0
    assert len(held) > 100, "the build made too few types to show anything"
    assert max(held) == 0, (
        f"products of earlier types were still held when a later type was built: {max(held)}"
    )
    assert [p.name for p in tmp_path.iterdir()] == ["catalog"]


def test_a_refusal_after_types_were_written_leaves_out_untouched(
    tmp_path, monkeypatch, capsys
) -> None:
    """The third type's image audit refuses, after two types' lines were written: ``--out``
    keeps its files and the staging directory is gone."""
    out = tmp_path / "catalog"
    out.mkdir()
    for name in ("flat.jsonl", "nested.jsonl", "images.jsonl", "stats.json"):
        (out / name).write_text(f"previous {name}\n", encoding="utf-8")
    before = _digest(out)
    calls: list[str] = []
    real = cli._check_images

    def check(catalog, referenced):
        calls.append(catalog.lines[0].type_key if catalog.lines else "")
        return ["forced on the third type"] if len(calls) == 3 else real(catalog, referenced)

    monkeypatch.setattr(cli, "_check_images", check)
    assert cli.main(["build", "--lines", "200", "--seed", str(SEED), "--out", str(out)]) == 1
    assert "image audit FAILED: forced on the third type" in capsys.readouterr().err
    assert len(calls) == 3
    assert _digest(out) == before
    assert [p.name for p in tmp_path.iterdir()] == ["catalog"]


def _row(product: str, value: str) -> dict:
    return {
        "product_id": product,
        "product_type": "probe_type",
        "facets": {"probe": [value]},
        "facets_num": {},
        "attributes": [{"name": "Probe", "key": "probe", "value": value}],
    }


def test_the_figures_count_each_product_s_pairs_once() -> None:
    """The (product, value) pairs are counted one product at a time and agree with the sets
    they replace: a value repeated on a product's SKUs is one pair."""
    rows = [_row("P1", "a"), _row("P1", "a"), _row("P1", "b"), _row("P2", "a"), _row("P3", "c")]
    stats = derive.measure(rows)["probe"]
    assert (stats.present, stats.cardinality, stats.products) == (5, 3, 3)
    assert stats.product_values == len({(r["product_id"], r["facets"]["probe"][0]) for r in rows})
    assert stats.product_magnitudes == stats.product_values == 4


def test_the_figures_refuse_a_product_met_again_after_another() -> None:
    """Counted one product at a time, a product split across the rows would be counted twice:
    refused rather than miscounted."""
    with pytest.raises(ValueError, match="met again after another product"):
        derive.measure([_row("P1", "a"), _row("P2", "a"), _row("P1", "b")])
