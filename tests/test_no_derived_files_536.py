"""No file under git is build output (gen#536).

``golden-retail/stats.json``, the sneak-peek samples and previews and the two generated docs
moved with every retail PR, so each PR that committed one conflicted the rest and main went red
whenever a merge did not roll them. CI builds them as artifacts now (``scripts/build_derived.py``).
``scripts/check_no_derived_files.py`` is the guard that keeps them out: these tests plant each one
in a throwaway repository and read the real tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_no_derived_files as guard  # noqa: E402

RD = "prototypes/retail_drawings"
#: One concrete path for every glob the guard names, and the ones that were committed.
PLANTED = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    f"{RD}/samples.ndjson",
    f"{RD}/samples4.ndjson",
    f"{RD}/preview.html",
    f"{RD}/preview4.html",
    f"{RD}/samples_next.ndjson",
)


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True,
        text=True,
    )  # fmt: skip
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


@pytest.mark.parametrize("path", PLANTED)
def test_a_re_added_derived_file_fails_the_check_and_is_named(path, repo, capsys) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "re-add")
    assert guard.main(["--root", str(repo)]) == 1
    out = capsys.readouterr().out
    assert f"\n  {path}\n" in out, "the refusal lists the offender on a line of its own"


def test_a_tree_with_no_derived_file_passes(repo, capsys) -> None:
    (repo / "docs").mkdir()
    (repo / "docs" / "retail-prototype.md").write_text("a doc\n", encoding="utf-8")
    (repo / "golden-retail").mkdir()
    (repo / "golden-retail" / "other.json").write_text("{}\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "docs")
    assert guard.main(["--root", str(repo)]) == 0
    assert capsys.readouterr().out == ""


def test_this_repository_tracks_no_derived_file() -> None:
    tracked = _git(ROOT, "ls-files").split("\n")
    assert guard.offenders(tracked) == []


# -- the build side: what the check holds out of git, the build writes (gen#536) ----------------

import hashlib  # noqa: E402
import os  # noqa: E402

import build_derived  # noqa: E402
import local_ci_jobs  # noqa: E402
import open_pin_bump_pr as pins  # noqa: E402
import yaml  # noqa: E402

CI = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yaml").read_text("utf-8"))
RELEASE = yaml.safe_load((ROOT / ".github" / "workflows" / "release.yaml").read_text("utf-8"))


def test_every_file_the_build_writes_is_one_the_check_keeps_out_of_git() -> None:
    assert build_derived.OUTPUTS
    assert guard.offenders(list(build_derived.OUTPUTS)) == list(build_derived.OUTPUTS)


def test_every_planted_path_but_the_globs_own_example_is_a_build_output() -> None:
    extra = [p for p in PLANTED if p not in build_derived.OUTPUTS]
    assert extra == [f"{RD}/samples_next.ndjson"]


def test_the_ci_job_checks_the_tree_then_builds_and_uploads_the_derived_files() -> None:
    steps = CI["jobs"]["no-derived-files"]["steps"]
    runs = " ".join(str(step.get("run", "")) for step in steps)
    assert "scripts/check_no_derived_files.py" in runs
    assert "scripts/build_derived.py --out build/derived" in runs
    uploads = [s for s in steps if str(s.get("uses", "")).startswith("actions/upload-artifact")]
    assert [u["with"]["name"] for u in uploads] == ["derived"]
    assert uploads[0]["with"]["path"] == "build/derived"


def test_no_workflow_rolls_or_commits_a_derived_file() -> None:
    for name in ("ci.yaml", "release.yaml"):
        text = (ROOT / ".github" / "workflows" / name).read_text("utf-8")
        assert "roll_stats" not in text and "check_no_stats_edit" not in text, name
    assert "stats-roll" not in CI["jobs"]


def test_the_release_runs_on_a_v_tag_and_is_never_a_local_check() -> None:
    triggers = RELEASE.get("on", RELEASE.get(True))
    assert triggers["push"]["tags"] == ["v*"]
    assert "workflow_dispatch" in triggers
    assert "release.yaml" in local_ci_jobs.NOT_A_CHECK
    assert "release" not in local_ci_jobs.load_jobs(ROOT / ".github" / "workflows")


def test_the_release_builds_both_assets_and_opens_the_pin_bump() -> None:
    steps = RELEASE["jobs"]["release"]["steps"]
    runs = "\n".join(str(step.get("run", "")) for step in steps)
    for want in (
        "scale.py --skus",
        "image_release.py --skus",
        "gh release create",
        "scripts/open_pin_bump_pr.py",
        ".content-sha256",
    ):
        assert want in runs, want
    assert "dry-run" in runs, "the workflow prints the pin-bump body before it opens anything"


def _sidecar(tmp_path: Path) -> Path:
    path = tmp_path / "retail-images.tar.gz.content-sha256"
    path.write_text("ab" * 32 + "  12\n", encoding="utf-8")
    return path


def test_the_pin_bump_dry_run_prints_the_body_and_both_pins(tmp_path, capsys) -> None:
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b'{"a": 1}\n{"a": 2}\n')
    code = pins.main([
        "--tag", "v1.0.0", "--repository", "o/r", "--catalog", str(catalog),
        "--images-sidecar", str(_sidecar(tmp_path)), "--dry-run",
    ])  # fmt: skip
    out = capsys.readouterr().out
    assert code == 0
    assert "https://github.com/o/r/releases/tag/v1.0.0" in out
    assert pins.CATALOG_PIN in out and pins.IMAGES_PIN in out
    assert '"documents": 2' in out and '"file_count": 12' in out
    assert hashlib.sha256(catalog.read_bytes()).hexdigest() in out


def test_the_pin_bump_needs_its_token_unless_it_is_a_dry_run(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.delenv(pins.TOKEN_ENV, raising=False)
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b"{}\n")
    code = pins.main([
        "--tag", "v1", "--catalog", str(catalog), "--images-sidecar", str(_sidecar(tmp_path)),
    ])  # fmt: skip
    assert code == 2
    assert pins.TOKEN_ENV in capsys.readouterr().err


def test_a_malformed_image_sidecar_is_refused(tmp_path) -> None:
    bad = tmp_path / "side"
    bad.write_text("nothex 3\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        pins.images_pin(bad, "o/r", "v1")


def _release_run(name: str) -> str:
    steps = RELEASE["jobs"]["release"]["steps"]
    return next(s["run"] for s in steps if s.get("name", "").startswith(name))


def test_the_release_build_commands_exit_zero_and_leave_both_assets(tmp_path) -> None:
    """Run the workflow's own build and dry-run steps (gen#536 review): a build that asks for
    more SKUs than the frozen catalogue holds exits 2 under ``bash -e`` and fails every ``v*``
    tag, which a read of the workflow text never showed. ``RELEASE_SKUS`` shrinks the build."""
    out = tmp_path / "release"
    script = "\n".join(
        _release_run(n)
        for n in ("Build the ceiling export", "Build the image bundle", "The pin-bump")
    ).replace("build/release", str(out))  # fmt: skip
    env = {**os.environ, "RELEASE_SKUS": "300", "TAG": "v0.0.0-test", "DRY_RUN": "true"}
    done = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr[-800:]
    for asset in (
        "catalog.ndjson.gz",
        "catalog.ndjson.gz.content-sha256",
        "retail-images.tar.gz",
        "retail-images.tar.gz.content-sha256",
        "pin-bump-body.txt",
    ):
        assert (out / asset).stat().st_size > 0, asset
