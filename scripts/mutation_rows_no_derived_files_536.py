"""Mutation rows for the build-output guard and the build that writes it (gen#536).

Each row plants one defect on a changed line of ``check_no_derived_files.py``,
``build_derived.py``, ``open_pin_bump_pr.py`` or the workflows, and names the test that must go
red. Found by ``mutation_row.discover``; ``--only "no derived files:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "no derived files"

_T = "tests/test_no_derived_files_536.py"
_RE_ADD = f"{_T}::test_a_re_added_derived_file_fails_the_check_and_is_named"
_NO_CROSSING = (
    f"{_T}::test_the_release_reads_no_secret_and_opens_no_pull_request_in_another_repository"
)
_GUARD = "check_no_derived_files.py"


def _row(name, file, old, new, test, prop, root="scripts") -> Row:
    return Row(name, file, old, new, test, prop, root)


def rows() -> list[Row]:
    return [
        _row(
            "the stats file is no longer build output",
            _GUARD,
            '    "golden-retail/stats.json",\n    "docs/figures.md",',
            '    "docs/figures.md",',
            f"{_RE_ADD}[golden-retail/stats.json]",
            "a re-added retail stats file fails the check",
        ),
        _row(
            "a numbered samples file is not matched",
            _GUARD,
            '"src/synthetic_ecommerce_data/domains/retail/samples*.ndjson"',
            '"src/synthetic_ecommerce_data/domains/retail/samples.ndjson"',
            f"{_RE_ADD}[src/synthetic_ecommerce_data/domains/retail/samples4.ndjson]",
            "a re-added samples4.ndjson fails the check",
        ),
        _row(
            "a glob is compared as a literal path",
            _GUARD,
            "fnmatch.fnmatchcase(p, glob)",
            "p == glob",
            f"{_RE_ADD}[src/synthetic_ecommerce_data/domains/retail/preview4.html]",
            "a glob matches the paths it names",
        ),
        _row(
            "the check passes whatever the tree tracks",
            _GUARD,
            "    if not files:\n        return 0\n    print(refusal(files))\n    return 1",
            "    return 0",
            f"{_RE_ADD}[docs/figures.md]",
            "a tree that tracks build output exits 1",
        ),
        _row(
            "the refusal does not name the offender",
            _GUARD,
            '            *(f"  {path}" for path in files),',
            "",
            f"{_RE_ADD}[docs/retail-apparel-decoys.md]",
            "the refusal names each tracked build-output file",
        ),
        _row(
            "the build forgets one output",
            "build_derived.py",
            '    "docs/figures.md",\n    "docs/retail-apparel-decoys.md",',
            '    "docs/retail-apparel-decoys.md",',
            f"{_T}::test_every_planted_path_but_the_globs_own_example_is_a_build_output",
            "every planted derived path is one the build writes",
        ),
        _row(
            "the CI job stops uploading the artifact",
            "ci.yaml",
            "          name: derived\n",
            "          name: other\n",
            f"{_T}::test_the_ci_job_checks_the_tree_then_builds_and_uploads_the_derived_files",
            "CI builds the derived files once per run and uploads them",
            ".github/workflows",
        ),
        _row(
            "the release runs on every tag",
            "release.yaml",
            'tags: ["v*"]',
            'tags: ["*"]',
            f"{_T}::test_the_release_runs_on_a_v_tag_and_is_never_a_local_check",
            "a release is a v* tag",
            ".github/workflows",
        ),
        _row(
            "the catalog pin over-counts its documents",
            "open_pin_bump_pr.py",
            '        "documents": data.count(b"\\n"),',
            '        "documents": data.count(b"\\n") + 1,',
            f"{_T}::test_the_pin_bump_prints_the_body_and_both_pins",
            "the catalog pin counts its documents",
        ),
        _row(
            "the release reads a repository secret again",
            "release.yaml",
            "          GH_TOKEN: ${{ github.token }}\n",
            "          GH_TOKEN: ${{ secrets.PIN_BUMP_TOKEN }}\n",
            _NO_CROSSING,
            "a tag needs no repository secret",
            ".github/workflows",
        ),
        _row(
            "the release opens a pull request in another repository",
            "release.yaml",
            "            | tee build/release/pin-bump-body.txt\n",
            "            | tee build/release/pin-bump-body.txt\n"
            "          gh pr create -R elastic/prism-retail-and-industrial --fill\n",
            _NO_CROSSING,
            "a tag opens no pull request elsewhere",
            ".github/workflows",
        ),
        _row(
            "a refused pin is hidden by tee",
            "release.yaml",
            "          set -o pipefail  # a refused pin",
            "          true  # a refused pin",
            f"{_T}::test_a_pin_the_script_refuses_stops_the_tag_before_anything_is_uploaded",
            "a refused pin stops the tag before it uploads",
            ".github/workflows",
        ),
        _row(
            "the pin script can open a connection again",
            "open_pin_bump_pr.py",
            "import re\n",
            "import re\nimport urllib.request  # noqa: F401\n",
            f"{_T}::test_the_pin_script_prints_without_a_token_and_imports_no_network",
            "the pin script imports no network module",
        ),
    ]
