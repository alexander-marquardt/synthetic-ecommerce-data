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

RD = "src/synthetic_ecommerce_data/domains/retail"
#: One concrete path for every glob the guard names, and the ones that were committed.
PLANTED = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    "docs/retail-product-word-decoys-table.md",
    "docs/retail-text-match-decoys-table.md",
    "docs/feature-pages.md",
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

import ast  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import socket  # noqa: E402

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


def test_the_release_builds_both_assets_and_prints_the_pins() -> None:
    steps = RELEASE["jobs"]["release"]["steps"]
    runs = "\n".join(str(step.get("run", "")) for step in steps)
    for want in (
        "retail.scale --skus",
        "retail.image_release --skus",
        "gh release create",
        "scripts/open_pin_bump_pr.py",
        ".content-sha256",
    ):
        assert want in runs, want


#: What a workflow reads a repository secret with, or opens a pull request with (gen#1246). The
#: run's own ``github.token`` writes to this repository alone, so it is not one of them.
CROSSES = re.compile(
    r"\$\{\{[^}]*\bsecrets\b|\bsecrets:\s*inherit\b|\bgh\s+pr\s+create\b|/pulls\b"
    r"|create-pull-request|PIN_BUMP_TOKEN"
)


@pytest.mark.parametrize(
    "line",
    [
        "PIN_BUMP_TOKEN: ${{ secrets.PIN_BUMP_TOKEN }}",
        "GH_TOKEN: ${{ secrets['OTHER'] }}",
        "    secrets: inherit",
        "gh pr create -R elastic/other --title x",
        "gh api repos/elastic/other/pulls -f head=x",
        "uses: peter-evans/create-pull-request@v7",
    ],
)
def test_the_release_check_names_a_line_that_reads_a_secret_or_opens_a_pull_request(line) -> None:
    assert CROSSES.search(line), line


def test_the_release_reads_no_secret_and_opens_no_pull_request_in_another_repository() -> None:
    """v3's catalogue load publishes and pins the images (agent-ops#917), so a tag needs no secret:
    a tag that published two releases and then failed for a missing token left no pin (gen#1246)."""
    text = (ROOT / ".github" / "workflows" / "release.yaml").read_text("utf-8")
    found = [line for line in text.splitlines() if CROSSES.search(line)]
    assert found == [], "release.yaml crosses to another repository"
    assert RELEASE["permissions"] == {"contents": "write"}
    assert all("permissions" not in job for job in RELEASE["jobs"].values())
    run = _release_run("The pins")
    assert run.count("open_pin_bump_pr.py") == 1, "the pins are printed once, and nothing is opened"


def test_a_pin_the_script_refuses_stops_the_tag_before_anything_is_uploaded(tmp_path) -> None:
    """The step pipes the script into ``tee``, and GitHub runs a step with ``bash -e`` and no
    ``pipefail``: a refusal would be hidden by ``tee`` and the tag would publish (gen#1246)."""
    out, bin_dir, called = tmp_path / "release", tmp_path / "bin", tmp_path / "called"
    (out / "catalog").mkdir(parents=True)
    (out / "catalog" / "catalog.ndjson").write_bytes(b"{}\n")
    (out / "images.tar.gz.content-sha256").write_text("nothex 3\n", encoding="utf-8")
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(f'#!/bin/sh\necho "$@" >> {called}\n', encoding="utf-8")
    fake.chmod(0o755)
    done = subprocess.run(
        ["bash", "-e", "-c", _release_run("The pins").replace("build/release", str(out))],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "TAG": "v0.0.0-test",
             "DRY_RUN": "false", "GITHUB_SHA": "0" * 40},
    )  # fmt: skip
    assert "is not '<sha256>  <file count>'" in done.stderr
    assert done.returncode != 0
    assert not called.exists(), "nothing is uploaded after a refused pin"


NETWORK = {"urllib", "http", "socket", "ssl", "requests", "httpx", "subprocess"}


def test_the_pin_script_prints_without_a_token_and_imports_no_network(
    tmp_path, monkeypatch, capsys
) -> None:
    tree = ast.parse((ROOT / "scripts" / "open_pin_bump_pr.py").read_text("utf-8"))
    imported = {
        name.split(".")[0]
        for node in ast.walk(tree)
        for name in (
            [alias.name for alias in node.names] if isinstance(node, ast.Import)
            else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
        )
    }  # fmt: skip
    assert not imported & NETWORK
    assert not hasattr(pins, "TOKEN_ENV") and not hasattr(pins, "open_pull_request")

    def refuse(*_args, **_kw):
        raise AssertionError("the pin script opened a socket")

    monkeypatch.setattr(socket, "socket", refuse)
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b"{}\n")
    argv = ["--tag", "v1", "--catalog", str(catalog), "--images-sidecar", str(_sidecar(tmp_path))]
    assert pins.main(argv) == 0
    assert pins.TARGET_REPO in capsys.readouterr().out


def _sidecar(tmp_path: Path) -> Path:
    path = tmp_path / "images.tar.gz.content-sha256"
    path.write_text("ab" * 32 + "  12\n", encoding="utf-8")
    return path


def test_the_pin_bump_prints_the_body_and_both_pins(tmp_path, capsys) -> None:
    catalog = tmp_path / "catalog.ndjson"
    catalog.write_bytes(b'{"a": 1}\n{"a": 2}\n')
    code = pins.main([
        "--tag", "v1.0.0", "--repository", "o/r", "--catalog", str(catalog),
        "--images-sidecar", str(_sidecar(tmp_path)),
    ])  # fmt: skip
    out = capsys.readouterr().out
    assert code == 0
    assert "https://github.com/o/r/releases/tag/v1.0.0" in out
    assert pins.CATALOG_PIN in out and pins.IMAGES_PIN in out
    assert '"documents": 2' in out and '"file_count": 12' in out
    assert hashlib.sha256(catalog.read_bytes()).hexdigest() in out


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
        for n in (
            "Build the retail ceiling",
            "Build the industrial catalog",
            "Compose the one catalog",
            "Build the image bundle",
            "The pins",
        )
    ).replace("build/release", str(out))  # fmt: skip
    env = {**os.environ, "RELEASE_SKUS": "300", "RELEASE_INDUSTRIAL_LINES": "60",
           "TAG": "v0.0.0-test", "DRY_RUN": "true"}  # fmt: skip
    done = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr[-800:]
    for asset in (
        "catalog.ndjson.gz",
        "catalog.ndjson.gz.content-sha256",
        "images.tar.gz",
        "images.tar.gz.content-sha256",
        "pin-bump-body.txt",
        "catalog/provenance.json",
    ):
        assert (out / asset).stat().st_size > 0, asset
    count = (out / "images.tar.gz.content-sha256").read_text("utf-8").split()[1]
    body = (out / "pin-bump-body.txt").read_text("utf-8")
    assert re.search(rf'"tag": "images-{count}-\d{{8}}"', body), "the image pin names its release"


def test_skus_ceiling_is_never_short_and_reports_what_the_build_made(tmp_path, monkeypatch) -> None:
    from synthetic_ecommerce_data.domains.retail import scale  # noqa: PLC0415

    real = scale.build
    monkeypatch.setattr(scale, "build", lambda skus, seed=0: real(300, seed))
    report = tmp_path / "report.json"
    assert scale.main(["--skus", "ceiling", "--report", str(report)]) == 0
    data = json.loads(report.read_text("utf-8"))
    assert data["reached_target"] is True and 300 <= data["target_skus"] < 10_000
    assert scale.main(["--skus", "10000000"]) == 2, "a number past the ceiling is still refused"


@pytest.mark.parametrize("step", ["Build the retail ceiling", "Build the image bundle"])
def test_the_release_build_defaults_to_the_ceiling_not_a_number(step) -> None:
    """With no ``RELEASE_SKUS`` the tag build asks for ``ceiling`` (gen#536 review): a number past
    the frozen catalogue is refused with exit 2, so a default of 10000000 fails every ``v*`` tag
    while the test above, which always sets ``RELEASE_SKUS``, stays green."""
    assert '--skus "${RELEASE_SKUS:-ceiling}"' in _release_run(step)


def test_the_release_draws_the_industrial_large_build() -> None:
    """The one image set carries the industrial half too (gen#706), at the large build's line
    count, named once in ``config``."""
    from synthetic_ecommerce_data.core.config import LARGE_BUILD_LINES  # noqa: PLC0415

    build = _release_run("Build the industrial catalog")
    assert f'--lines "${{RELEASE_INDUSTRIAL_LINES:-{LARGE_BUILD_LINES}}}"' in build
    assert "--industrial-catalog build/release/industrial" in _release_run("Build the image bundle")
