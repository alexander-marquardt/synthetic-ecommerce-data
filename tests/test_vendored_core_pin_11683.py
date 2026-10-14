"""The vendored core gate is core's, byte for byte, at the pinned commit (elastic/prism#11683).

``vendor/prism/PIN.txt`` lists each vendored file as core's ``git ls-tree``
prints it: mode, blob id, path. A git blob id is the hash of the file's bytes,
so a vendored file that hashes to the listed id IS core's file at that commit,
and this check needs no access to the private core repository. Whether the
listed ids are core's is checked against a core clone when
``PRISM_CORE_CHECKOUT`` names one (CI cannot read core).
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "prism"


def _gate():
    path = ROOT / "scripts" / "file_size_gate.py"
    spec = importlib.util.spec_from_file_location("file_size_gate", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(*args: str, cwd: Path = ROOT) -> str:
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout


def test_every_vendored_file_is_the_pinned_blob() -> None:
    pinned = _gate().pinned_files()
    wrong = {}
    for path, (_mode, blob) in pinned.items():
        actual = _git("hash-object", str(VENDOR / path)).strip()
        if actual != blob:
            wrong[path] = actual
    assert wrong == {}, (
        f"vendored files differ from core at the pinned commit: {wrong}. Change "
        "core, then resync (docs/file-size-budget.md)."
    )


def test_every_vendored_file_keeps_its_pinned_mode() -> None:
    pinned = _gate().pinned_files()
    staged = {}
    for line in _git("ls-files", "-s", "--", "vendor/prism").splitlines():
        meta, path = line.split("\t", 1)
        staged[path.removeprefix("vendor/prism/")] = meta.split()[0]
    assert {path: staged.get(path) for path in pinned} == {
        path: mode for path, (mode, _blob) in pinned.items()
    }


def test_nothing_under_vendor_prism_is_unlisted() -> None:
    pinned = set(_gate().pinned_files())
    present = {
        str(path.relative_to(VENDOR))
        for path in VENDOR.rglob("*")
        if path.is_file() and path.name != "PIN.txt" and "__pycache__" not in path.parts
    }
    assert present == pinned


@pytest.mark.skipif(
    not os.environ.get("PRISM_CORE_CHECKOUT"),
    reason="PRISM_CORE_CHECKOUT names no core clone (CI cannot read core)",
)
def test_the_pin_is_core_ls_tree_at_its_commit() -> None:
    gate = _gate()
    core = Path(os.environ["PRISM_CORE_CHECKOUT"])
    pinned = gate.pinned_files()
    listed = _git("ls-tree", gate.pinned_commit(), "--", *sorted(pinned), cwd=core)
    in_core = {}
    for line in listed.splitlines():
        meta, path = line.split("\t", 1)
        mode, _kind, blob = meta.split()
        in_core[path] = (mode, blob)
    assert in_core == pinned
