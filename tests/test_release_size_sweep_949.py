"""The release sweeps ``ecom-generate build`` across sizes and checks each writes every file (#949).

A material only a larger build draws (``420 Stainless Steel``, first at 4000 lines) stopped
``ecom-generate build --lines 4000`` while it wrote ``images.jsonl``, and the default build never
showed it. CI keeps the per-material test (``tests/test_material_styles_949.py``); the full sweep
is too slow for it, so the release workflow runs it on every ``v*`` tag and on the dry run. These
tests run the workflow's own step text at small sizes, and with a stand-in ``uv`` that leaves a
file out, so a step that builds but checks nothing cannot pass.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

from synthetic_ecommerce_data.core.config import LARGE_BUILD_LINES

ROOT = Path(__file__).resolve().parents[1]
RELEASE = yaml.safe_load((ROOT / ".github" / "workflows" / "release.yaml").read_text("utf-8"))
SWEEP_STEP = "Sweep the industrial build sizes"
BUILD_STEP = "Build the industrial catalog"
EVERY_FILE = ("nested.jsonl", "flat.jsonl", "images.jsonl", "stats.json")


def _run_text(name: str) -> str:
    steps = RELEASE["jobs"]["release"]["steps"]
    found = [s["run"] for s in steps if s.get("name", "") == name]
    assert found, f"release.yaml has no step named {name!r}"
    return found[0]


def _run(script: str, tmp_path: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    script = script.replace("build/release", str(tmp_path / "release"))
    script = script.replace("build/sweep", str(tmp_path / "sweep"))
    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script],
        cwd=ROOT, env={**os.environ, **env}, capture_output=True, text=True,
    )  # fmt: skip


def _fake_uv(tmp_path: Path, writes: tuple[str, ...]) -> str:
    """A ``uv`` on PATH that exits 0 and writes only ``writes`` into its ``--out``."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        "#!/usr/bin/env bash\n"
        'while [ $# -gt 0 ]; do if [ "$1" = --out ]; then out=$2; fi; shift; done\n'
        'mkdir -p "$out"\n'
        f'for f in {" ".join(writes)}; do echo x > "$out/$f"; done\n',
        "utf-8",
    )
    uv.chmod(0o755)
    return f"{bin_dir}{os.pathsep}{os.environ['PATH']}"


def test_the_sweep_names_the_sizes_below_the_release_size() -> None:
    """The sweep builds 2600 (the default), 4000 and 10000 lines; the release size,
    ``LARGE_BUILD_LINES``, is the industrial build the release already makes, and the sweep
    checks that build's files rather than building it twice."""
    sweep = _run_text(SWEEP_STEP)
    assert 'for lines in ${RELEASE_SWEEP_LINES:-2600 4000 10000}; do' in sweep
    assert "check build/release/industrial" in sweep
    assert f'--lines "${{RELEASE_INDUSTRIAL_LINES:-{LARGE_BUILD_LINES}}}"' in _run_text(BUILD_STEP)
    steps = [s.get("name", "") for s in RELEASE["jobs"]["release"]["steps"]]
    assert steps.index(BUILD_STEP) < steps.index(SWEEP_STEP), "the sweep checks a finished build"


def test_the_sweep_step_writes_every_file_at_each_size(tmp_path) -> None:
    script = _run_text(BUILD_STEP) + "\n" + _run_text(SWEEP_STEP)
    env = {"RELEASE_INDUSTRIAL_LINES": "60", "RELEASE_SWEEP_LINES": "40 80"}
    done = _run(script, tmp_path, env)
    assert done.returncode == 0, done.stdout[-800:] + done.stderr[-800:]
    sweep, release = tmp_path / "sweep", tmp_path / "release"
    for build in (sweep / "40", sweep / "80", release / "industrial"):
        for name in EVERY_FILE:
            assert (build / name).stat().st_size > 0, f"{build.name}: {name}"


def test_a_size_that_leaves_a_file_out_fails_the_sweep(tmp_path) -> None:
    path = _fake_uv(tmp_path, EVERY_FILE[:3])
    done = _run(_run_text(SWEEP_STEP), tmp_path, {"PATH": path, "RELEASE_SWEEP_LINES": "40"})
    assert done.returncode != 0
    assert "stats.json" in done.stdout + done.stderr


def test_a_release_build_that_leaves_a_file_out_fails_the_sweep(tmp_path) -> None:
    path = _fake_uv(tmp_path, EVERY_FILE)
    (tmp_path / "release" / "industrial").mkdir(parents=True)
    done = _run(_run_text(SWEEP_STEP), tmp_path, {"PATH": path, "RELEASE_SWEEP_LINES": "40"})
    assert done.returncode != 0
    assert "industrial" in done.stdout + done.stderr
