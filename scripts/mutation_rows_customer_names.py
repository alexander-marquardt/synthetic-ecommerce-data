"""Mutation rows for the customer-name check (#393), kept out of ``mutation_check.py``.

Each row plants one defect in ``scripts/check_customer_names.py``, the pre-push row that runs it,
the local-CI value its CI job needs or the job itself, and names the test file that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``customer names: ...``
(``--only "customer names:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row's old and new text are source lines, as written)
from __future__ import annotations

from mutation_row import Row

CHECK = "check_customer_names.py"
TEST = "tests/test_customer_name_check_393.py"
GATE = "tests/test_prepush_gate_11677.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        'list cut to one row',
        CHECK,
        'SPECS = core.CUSTOMER_NAME_SPECS\n',
        'SPECS = core.CUSTOMER_NAME_SPECS[:1]\n',
        TEST,
        "the check reads every row of core's list",
        "scripts",
    ),
    (
        'nul byte hides the file',
        CHECK,
        '    try:\n        return data.decode("utf-8")\n',
        '    if b"\\0" in data:\n        return None\n    try:\n        return data.decode("utf-8")\n',
        TEST,
        'one NUL byte does not hide a file',
        "scripts",
    ),
    (
        'binary file not named',
        CHECK,
        '        if b"\\0" in data:\n            return None\n        return data.decode("utf-8", "replace")\n',
        '        return data.decode("utf-8", "replace")\n',
        TEST,
        'a file that is not text is named as not scanned',
        "scripts",
    ),
    (
        'untracked files skipped',
        CHECK,
        '"--cached", "--others", "--exclude-standard"',
        '"--cached"',
        TEST,
        'a file not yet added is scanned',
        "scripts",
    ),
    (
        'ignored files scanned',
        CHECK,
        '"--cached", "--others", "--exclude-standard"',
        '"--cached", "--others"',
        TEST,
        'a file .gitignore hides is not scanned',
        "scripts",
    ),
    (
        'file name not scanned',
        CHECK,
        '        scan.hits.extend(\n            Found(f"{shown} (file name)", label) for label in labels_in(shown)\n        )\n',
        '',
        TEST,
        'a name in a file path is found',
        "scripts",
    ),
    (
        'line numbers from zero',
        CHECK,
        'enumerate(text.split("\\n"), start=1)',
        'enumerate(text.split("\\n"), start=0)',
        TEST,
        'a hit is reported at its 1-based line',
        "scripts",
    ),
    (
        'range not checked',
        CHECK,
        '    if match is None:\n        raise ValueError(',
        '    if False:\n        raise ValueError(',
        TEST,
        'a path handed as a range is refused',
        "scripts",
    ),
    (
        'log ignores the range',
        CHECK,
        '"log", "--format=%H%x1f%B%x1e", spec',
        '"log", "--format=%H%x1f%B%x1e", "HEAD"',
        TEST,
        "only the range's commit messages are judged",
        "scripts",
    ),
    (
        'pr body not scanned',
        CHECK,
        'for part in ("title", "body"):',
        'for part in ("title",):',
        TEST,
        'the PR body is judged as well as its title',
        "scripts",
    ),
    (
        'empty pr number asks gh',
        CHECK,
        '    if args.pr:\n',
        '    if True:\n',
        TEST,
        'an empty PR means gh is not asked',
        "scripts",
    ),
    (
        'could not judge is a pass',
        CHECK,
        'return EXIT_UNJUDGED if unjudged else EXIT_CLEAN',
        'return EXIT_CLEAN',
        TEST,
        'a run that could not judge is not a pass',
        "scripts",
    ),
    (
        'hit exits zero',
        CHECK,
        '    if scan.hits:\n        return EXIT_HIT\n',
        '    if scan.hits:\n        return EXIT_CLEAN\n',
        TEST,
        'a hit exits non-zero',
        "scripts",
    ),
    (
        'gh failure ignored',
        CHECK,
        '    if done.returncode != 0:\n        raise CouldNotJudge(\n            f"gh pr view',
        '    if False:\n        raise CouldNotJudge(\n            f"gh pr view',
        TEST,
        'a gh that failed is not a pass even if it printed an answer',
        "scripts",
    ),
    (
        'report repeats the line',
        CHECK,
        'Found(f"{where}:{number}", label)',
        'Found(f"{where}:{number} {line}", label)',
        TEST,
        'a report names the place, never the matched line',
        "scripts",
    ),
    (
        'text file hit dropped',
        CHECK,
        '    scan.texts += 1\n    scan.hits.extend(scan_lines(text, path))\n',
        '    scan.texts += 1\n',
        TEST,
        'a name in a draft PR body is found',
        "scripts",
    ),
    (
        "the pre-push row asks gh for a PR that does not exist yet",
        "prepush.py",
        '    if "--pr" in argv:\n',
        "    if False:\n",
        GATE,
        "the pre-push row judges the draft body, not a live PR",
        "scripts",
    ),
    (
        "the pre-push row drops the draft PR body",
        "prepush.py",
        '        argv = [*argv, "--text-file", ctx.body_file]\n',
        "        argv = argv\n",
        GATE,
        "a name in the draft PR body fails the pre-push row",
        "scripts",
    ),
    (
        "the local CI run has no value for the job's token",
        "local_ci_jobs.py",
        '        "github.token": "",\n',
        "",
        TEST,
        "merge_pr.sh --local-ci can run the customer-name job",
        "scripts",
    ),
    (
        "the CI job stops reading the PR's live text",
        "ci.yaml",
        '          --pr "${PR_REF:-${GITHUB_HEAD_REF:-$(git rev-parse --abbrev-ref HEAD)}}"\n',
        "",
        TEST,
        "the CI job scans the PR title and body",
        ".github/workflows",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "customer names"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
