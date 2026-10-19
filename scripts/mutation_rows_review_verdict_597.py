"""Mutation rows for the review-verdict check (gen#597).

Each row plants one defect in ``.github/scripts/check_review_binding.py`` and names the test
file that must go red. Found by ``mutation_row.discover``; ``--only "review verdict:"``
re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "review verdict"

_FILE = "check_review_binding.py"
_ROOT = ".github/scripts"
_TESTS = ("tests/test_review_verdict_check.py",)

_MUTANTS = [
    ('if not _is_bot(entry["login"]) and (verdict', "if (verdict", "bot-verdicts-count"),
    (
        "max(parsed, key=lambda item: item[:2])[2]",
        "min(parsed, key=lambda item: item[:2])[2]",
        "oldest-verdict-wins",
    ),
    ("default=len(tiers) - 1,", "default=0,", "unmapped-path-is-shallow"),
    (
        "if tiers.index(verdict.tier) < tiers.index(needed):",
        "if tiers.index(verdict.tier) <= tiers.index(needed):",
        "equal-tier-refused",
    ),
    (
        "if tiers.index(verdict.tier) < tiers.index(needed):",
        "if tiers.index(verdict.tier) > tiers.index(needed):",
        "tier-comparison-flipped",
    ),
    ('if verdict.kind != "ARM":', "if False:", "fix-and-block-pass"),
    ("if verdict.head == head.lower():", "if False:", "head-match-ignored"),
    (
        'return self.kind in ("same-diff", "generated-only")',
        'return self.kind in ("same-diff",)',
        "generated-only-never-carries",
    ),
    (
        'and _git(git_dir, "cat-file", "-e", f"{rev}:{path}")[0] == 0',
        "and True",
        "generated-need-not-exist",
    ),
    ("        and bool(paths)\n        and all(", "        and all(", "empty-diff-exempt"),
    (
        '_STRIP = re.compile(r"[*`#_ -]*")',
        '_STRIP = re.compile(r"[>*`#_ -]*")',
        "quoted-verdict-counts",
    ),
    ("kind if kind in KINDS else None,", "kind,", "unknown-kind-kept"),
    (
        "head.lower() if head and FULL_SHA.fullmatch(head) else None,",
        "head.lower() if head else None,",
        "short-sha-accepted",
    ),
    (
        '"diff", "--name-only", "--no-renames", "-z", first, second',
        '"diff", "--name-only", "--no-renames", first, second',
        "paths-read-without-z",
    ),
    (
        '"diff", "--name-only", "--no-renames", "-z", first, second',
        '"diff", "--name-only", "-z", first, second',
        "renames-detected",
    ),
    ('["git", "--literal-pathspecs", "-C"', '["git", "-C"', "pathspec-magic-honoured"),
    ("    if not differing:\n", "    if False:\n", "unexplained-diff-reads-generated"),
    (
        'return Delta("unreadable", "git could not list the changed paths")',
        "continue",
        "delta-path-list-failure-ignored",
    ),
    (
        "if paths is None:\n        raise CannotJudge",
        "if False:\n        raise CannotJudge",
        "load-path-list-failure-ignored",
    ),
    (
        '(entry["created_at"] or "", n, verdict)',
        '(entry["created_at"] or "z", n, verdict)',
        "none-timestamp-sorts-newest",
    ),
    ('select(.state != "PENDING")', "select(true)", "pending-review-counts"),
    ("comments + reviews, base)", "reviews + comments, base)", "review-order-flipped"),
    ('(.submitted_at // "")', "(.submitted_at)", "review-time-may-be-null"),
]


def rows() -> list[Row]:
    return [
        Row(name, _FILE, old, new, _TESTS, f"the check stays honest: {name}", _ROOT)
        for old, new, name in _MUTANTS
    ] + registry_rows()


def registry_rows() -> list[Row]:
    return [
        Row(
            "the workflow is not registered as not-a-check",
            "local_ci_jobs.py",
            '"release.yml", "review-verdict.yaml", "review-verdict.yml")',
            '"release.yml")',
            "tests/test_merge_pr.py::test_every_job_of_the_real_workflows_has_a_local_equivalent",
            "the local job list reads every workflow",
            "scripts",
        )
    ]
