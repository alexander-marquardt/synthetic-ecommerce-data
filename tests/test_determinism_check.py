"""``scripts/check_determinism.py``: two builds of one seed and commit are byte-identical.

elastic/prism-industrial-products#129 requires the 100K build to be
deterministic, checked by two builds with identical digests. The script is that
check at any ``--lines``. Here it runs at a small size, and a planted one-byte
difference proves the comparison bites.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_determinism.py"


def _module():
    spec = importlib.util.spec_from_file_location("check_determinism", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_two_small_builds_are_byte_identical():
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--lines", "160"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "DETERMINISTIC" in done.stdout
    # every emitted file was compared, not an empty set
    assert done.stdout.count(" same ") >= 6, done.stdout


def test_a_one_byte_difference_is_reported(tmp_path):
    left, right = tmp_path / "a", tmp_path / "b"
    for side in (left, right):
        side.mkdir()
        (side / "flat.jsonl").write_text('{"sku": "1"}\n', encoding="utf-8")
        (side / "stats.json").write_text("{}\n", encoding="utf-8")
    (right / "flat.jsonl").write_text('{"sku": "2"}\n', encoding="utf-8")
    differing = _module().compare(left, right)
    assert differing == ["flat.jsonl"]


def test_a_file_only_one_build_wrote_is_reported(tmp_path):
    left, right = tmp_path / "a", tmp_path / "b"
    left.mkdir()
    right.mkdir()
    (left / "flat.jsonl").write_text("x\n", encoding="utf-8")
    assert _module().compare(left, right) == ["flat.jsonl"]


# --- fake builds: the check's own verdicts, with no real catalog build ---------

CATALOG_FILES = (
    "nested.jsonl",
    "flat.jsonl",
    "images.jsonl",
    "render.jsonl",
    "stats.json",
    "mapping.nested.json",
    "mapping.flat.json",
)


def _fake_build(module, monkeypatch, tmp_path, *, skip=(), field_map=lambda seed: "same\n"):
    """Replace the child builds with a writer that honours the same CLI shape."""
    target = tmp_path / "src-tree" / "field_map.yaml"
    target.parent.mkdir()
    monkeypatch.setattr(module, "field_map_target", lambda: target, raising=False)

    def fake(args, hash_seed):
        if args[0] == "build":
            out = Path(args[args.index("--out") + 1])
            out.mkdir(parents=True)
            for name in CATALOG_FILES:
                if name not in skip:
                    (out / name).write_text("x\n", encoding="utf-8")
            if "--lines" not in args:
                target.write_text(field_map(hash_seed), encoding="utf-8")
        else:
            archive = Path(args[args.index("--archive") + 1])
            archive.parent.mkdir(parents=True)
            for suffix in ("", ".sha256", ".content-sha256"):
                archive.with_name(archive.name + suffix).write_text("x\n", encoding="utf-8")

    monkeypatch.setattr(module, "_sip_generate", fake)


def test_a_build_that_writes_nothing_is_refused(monkeypatch, capsys):
    module = _module()
    monkeypatch.setattr(module, "_sip_generate", lambda args, hash_seed: None)
    assert module.main(["--lines", "160"]) == 1
    assert "NOT DETERMINISTIC" in capsys.readouterr().out


def test_a_missing_expected_file_is_refused_even_when_both_builds_miss_it(
    tmp_path, monkeypatch, capsys
):
    module = _module()
    _fake_build(module, monkeypatch, tmp_path, skip=("stats.json",))
    assert module.main(["--lines", "160"]) == 1
    assert "stats.json" in capsys.readouterr().out


def test_identical_default_config_field_maps_pass(tmp_path, monkeypatch):
    module = _module()
    _fake_build(module, monkeypatch, tmp_path)
    assert module.main([]) == 0


def test_a_seed_dependent_field_map_is_reported(tmp_path, monkeypatch, capsys):
    module = _module()
    _fake_build(module, monkeypatch, tmp_path, field_map=lambda seed: f"order {seed}\n")
    assert module.main([]) == 1
    assert "field_map.yaml" in capsys.readouterr().out


def test_images_are_compared_at_a_small_size():
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--lines", "160", "--images"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    for name in ("images.tar.gz", "images.tar.gz.sha256", "images.tar.gz.content-sha256"):
        assert f"images/{name}" in done.stdout, done.stdout
    assert done.stdout.count(" same ") >= 10, done.stdout
