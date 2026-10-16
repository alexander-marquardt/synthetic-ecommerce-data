"""The 100K catalog is built once and read by every worker (#140).

Each xdist worker used to build its own 100K catalog (about 1.9 GB resident), so a
``-n 2`` run held two and the swap watchdog killed workers. ``shared_builds`` builds it
once, under one lock, keeps only what the tests read, and writes that to a file keyed on
the generator's own source. These tests hold the three promises that makes: a worker that
finds the file holds under 500 MB, two processes asking at once build once, and a changed
source is never served the old file. The last test keeps a new module from building a
100K catalog of its own.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent

#: What one worker may hold for a 100K fixture it reads from the shared file. The
#: unshared build was about 1,900 MB (``/usr/bin/time -v`` on tests/test_price.py).
PER_WORKER_PEAK_MB = 500

#: The child reports its own memory's high-water mark (``VmHWM``), not ``ru_maxrss``: a
#: child forked from the big pytest process starts with the parent's peak in ``ru_maxrss``
#: (Linux keeps the pre-exec mm's high-water mark), so the rusage figure reads the parent.
_PEAK_PROBE = """
import json, resource, sys
import shared_builds
rows, kits = shared_builds.hundred_k_prices()
try:
    status = open("/proc/self/status").read()
    peak_mb = int(status.split("VmHWM:")[1].split()[0]) / 1024
except (OSError, IndexError):
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (
        1024 * 1024 if sys.platform == "darwin" else 1024
    )
print(json.dumps({"rows": len(rows), "peak_mb": peak_mb}))
"""


def _run(code: str, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    environ = {**os.environ, "PYTHONPATH": str(TESTS), **(env or {})}
    return subprocess.run(
        [sys.executable, "-c", code, *args],
        capture_output=True,
        text=True,
        check=True,
        env=environ,
        timeout=550,
    )


@pytest.mark.timeout(600)
def test_a_worker_that_reads_the_shared_100k_file_holds_under_500_mb():
    _run(_PEAK_PROBE)  # the first worker to ask builds the file; its peak is not the claim
    reading = json.loads(_run(_PEAK_PROBE).stdout.splitlines()[-1])
    assert reading["rows"] > 0
    assert reading["peak_mb"] < PER_WORKER_PEAK_MB, reading


_TOY = textwrap.dedent(
    """
    import sys, time
    from pathlib import Path
    import shared_builds

    cache, source, counter = (Path(p) for p in sys.argv[1:4])

    def build():
        with counter.open("a") as handle:
            handle.write("built\\n")
        time.sleep(1.5)
        return source.read_text()

    print(shared_builds.cached("toy", build, roots=[source], cache_dir=cache))
    """
)


def _toy(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    script = tmp_path / "toy.py"
    script.write_text(_TOY)
    source = tmp_path / "source.txt"
    source.write_text("one")
    return script, tmp_path / "cache", source, tmp_path / "counter.txt"


def _spawn(script: Path, cache: Path, source: Path, counter: Path) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(script), str(cache), str(source), str(counter)],
        stdout=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONPATH": str(TESTS)},
    )


def test_two_processes_asking_at_once_build_once(tmp_path):
    script, cache, source, counter = _toy(tmp_path)
    procs = [_spawn(script, cache, source, counter) for _ in range(2)]
    answers = [p.communicate(timeout=60)[0].strip() for p in procs]
    assert answers == ["one", "one"]
    assert counter.read_text().splitlines() == ["built"]


def test_a_second_ask_for_unchanged_inputs_reads_the_file(tmp_path):
    script, cache, source, counter = _toy(tmp_path)
    for _ in range(2):
        _spawn(script, cache, source, counter).communicate(timeout=60)
    assert counter.read_text().splitlines() == ["built"]


def test_a_changed_source_is_never_served_the_old_file(tmp_path):
    script, cache, source, counter = _toy(tmp_path)
    _spawn(script, cache, source, counter).communicate(timeout=60)
    source.write_text("two")
    answer = _spawn(script, cache, source, counter).communicate(timeout=60)[0].strip()
    assert answer == "two"
    assert counter.read_text().splitlines() == ["built", "built"]


#: Modules that may name the 100K size: the shared builds and this guard.
_MAY_ASK = {"shared_builds.py", Path(__file__).name}


def test_no_test_module_builds_a_whole_100k_catalog_of_its_own():
    """A module that builds its own copy is a copy per worker again."""
    asking = sorted(
        path.name
        for path in TESTS.glob("*.py")
        if path.name not in _MAY_ASK
        and re.search(r"HUNDRED_K_LINES", path.read_text(encoding="utf-8"))
    )
    assert asking == [], f"build through shared_builds instead: {asking}"


def test_the_default_dist_mode_keeps_a_module_on_one_worker():
    """What a worker still holds after the shared file is the flat documents of the 100K build
    (the brand-voice module: about 1.4 GB, against 2.1 GB when it built them). Two copies of
    those never meet because a plain ``-n 2`` honours the module groups ``conftest.py`` marks:
    the default ``--dist load`` scatters a module's tests over both workers."""
    import tomllib
    import types

    import xdist_groups

    options = tomllib.loads((TESTS.parent / "pyproject.toml").read_text(encoding="utf-8"))
    addopts = options["tool"]["pytest"]["ini_options"]["addopts"]
    assert "--dist loadgroup" in addopts, addopts
    module = types.ModuleType("test_catalog_brands_voice")
    assert xdist_groups.group_for(module) == "test_catalog_brands_voice"
