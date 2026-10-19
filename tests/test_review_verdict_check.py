"""The `review-verdict` check and its workflow (agent-ops#111).

The check is elastic/prism's (`.github/scripts/check_review_binding.py`), trimmed to read its tier
routes from `.github/review_verdict_tiers.json`. These tests pin the grammar, the pass rules, the
tier derivation, the carried-diff rule against a real git repository, and the shape of the workflow
(`review-verdict` on `pull_request` and `merge_group`, a rerun job that holds `actions: write` and
checks out nothing). The file is the same in every repository that carries the check.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_review_binding.py"
WORKFLOW = ROOT / ".github" / "workflows" / "review-verdict.yaml"
SPEC = importlib.util.spec_from_file_location("check_review_binding", SCRIPT)
assert SPEC and SPEC.loader
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check  # a dataclass looks its own module up by name
SPEC.loader.exec_module(check)

A, B = "a" * 40, "b" * 40
TIERS = ["docs", "ui", "gate-or-test", "rulebook", "production-runtime"]
RULES = {
    "tiers": TIERS,
    "routes": [
        {"tier": "docs", "paths": ["docs/*", "*.md"]},
        {"tier": "gate-or-test", "paths": ["tests/*"]},
        {"tier": "rulebook", "paths": ["CLAUDE.md"]},
    ],
}


def comment(body, login="maintainer", at="2026-10-19T10:00:00Z"):
    return {"body": body, "created_at": at, "login": login}


def verdict(kind="ARM", head=A, tier="production-runtime"):
    return f"Review-Verdict: {kind}\nReviewed-Head: {head}\nTier: {tier}\n"


def judge(
    entries, *, head=A, paths=("src/x.py",), needed="docs", delta=None, author="someone"
):
    return check.judge(
        author=author,
        head=head,
        paths=list(paths),
        entries=entries,
        needed=needed,
        tiers=TIERS,
        delta=delta or (lambda old: check.Delta("changed", "src/x.py")),
        exemptions={"dependabot[bot]": ["uv.lock"]},
    )


# --- the grammar ---------------------------------------------------------------------------


def test_a_plain_verdict_parses_to_its_three_fields():
    assert check.parse_verdict(verdict()) == check.Verdict(
        "ARM", A, "production-runtime"
    )


def test_bold_backticks_and_a_heading_around_the_lines_are_ignored():
    body = f"## **Review-Verdict: ARM**\n`Reviewed-Head: {A.upper()}`\n**Tier: docs**\n"
    assert check.parse_verdict(body) == check.Verdict("ARM", A, "docs")


def test_a_comment_with_no_verdict_line_is_not_a_verdict():
    assert check.parse_verdict("looks good to me\nReviewed-Head: " + A) is None


def test_an_unknown_kind_and_a_short_head_parse_to_none_fields():
    parsed = check.parse_verdict(
        "Review-Verdict: MAYBE\nReviewed-Head: abc123\nTier: docs\n"
    )
    assert parsed == check.Verdict(None, None, "docs")


def test_a_quoted_verdict_is_not_a_verdict():
    assert check.parse_verdict("> " + verdict().replace("\n", "\n> ")) is None


def test_the_newest_non_bot_verdict_decides():
    entries = [
        comment(verdict("ARM"), at="2026-10-19T10:00:00Z"),
        comment(verdict("FIX"), at="2026-10-19T11:00:00Z"),
        comment(verdict("ARM"), login="github-actions", at="2026-10-19T12:00:00Z"),
        comment(verdict("ARM"), login="dependabot[bot]", at="2026-10-19T13:00:00Z"),
    ]
    assert check.newest_verdict(entries).kind == "FIX"


def test_an_author_less_entry_is_a_bot():
    assert check.newest_verdict([comment(verdict(), login="")]) is None


def test_the_newest_verdict_is_by_time_not_by_position_in_the_list():
    # `load_facts` appends the reviews after the comments, so a review can sit last yet be older.
    entries = [
        comment(verdict("FIX"), at="2026-10-19T11:00:00Z"),
        comment(verdict("ARM"), at="2026-10-19T10:00:00Z"),
    ]
    assert check.newest_verdict(entries).kind == "FIX"


def test_two_verdicts_at_the_same_second_are_decided_by_position():
    at = "2026-10-19T10:00:00Z"
    assert (
        check.newest_verdict(
            [comment(verdict("ARM"), at=at), comment(verdict("FIX"), at=at)]
        ).kind
        == "FIX"
    )
    assert (
        check.newest_verdict(
            [comment(verdict("FIX"), at=at), comment(verdict("ARM"), at=at)]
        ).kind
        == "ARM"
    )


def test_an_entry_with_no_timestamp_is_the_oldest_not_a_crash():
    entries = [
        comment(verdict("ARM"), at=None),
        comment(verdict("FIX"), at="2026-10-19T10:00:00Z"),
    ]
    assert check.newest_verdict(entries).kind == "FIX"
    assert check.newest_verdict(entries[:1]).kind == "ARM"


def test_the_field_names_are_read_in_any_case():
    body = f"review-verdict: arm\nREVIEWED-HEAD: {A}\ntier: docs\n"
    assert check.parse_verdict(body) == check.Verdict("ARM", A, "docs")


# --- the pass rules ------------------------------------------------------------------------


def test_no_verdict_fails():
    assert not judge([comment("hello")]).ok


def test_arm_at_the_head_with_a_deep_enough_tier_passes():
    assert judge([comment(verdict())], needed="production-runtime").ok


def test_a_fix_and_a_block_fail():
    assert "FIX" in judge([comment(verdict("FIX"))]).reason
    assert not judge([comment(verdict("BLOCK"))]).ok


def test_an_unknown_kind_a_missing_head_and_an_unknown_tier_fail():
    assert not judge([comment(verdict("MAYBE"))]).ok
    assert (
        "Reviewed-Head" in judge([comment("Review-Verdict: ARM\nTier: docs\n")]).reason
    )
    assert "not one of" in judge([comment(verdict(tier="made-up"))]).reason


def test_a_tier_below_what_the_paths_need_fails():
    result = judge([comment(verdict(tier="docs"))], needed="gate-or-test")
    assert not result.ok
    assert "below gate-or-test" in result.reason


def test_a_tier_equal_to_the_need_passes_and_one_shallower_does_not():
    assert judge([comment(verdict(tier="gate-or-test"))], needed="gate-or-test").ok
    assert not judge([comment(verdict(tier="ui"))], needed="gate-or-test").ok


def test_arm_at_an_older_head_fails_when_the_diff_changed():
    result = judge([comment(verdict(head=B))])
    assert not result.ok
    assert "changed" in result.reason


@pytest.mark.parametrize("kind", ["same-diff", "generated-only"])
def test_arm_at_an_older_head_carries_when_the_diff_is_the_same_or_only_generated(kind):
    assert judge([comment(verdict(head=B))], delta=lambda old: check.Delta(kind, "")).ok


def test_arm_at_an_older_head_fails_when_the_delta_is_unreadable():
    unreadable = check.Delta("unreadable", "x")
    assert not judge([comment(verdict(head=B))], delta=lambda old: unreadable).ok


def test_dependabot_on_listed_paths_needs_no_verdict_but_one_other_path_ends_it():
    assert judge([], paths=["uv.lock"], author="dependabot[bot]").ok
    assert not judge([], paths=["uv.lock", "src/x.py"], author="dependabot[bot]").ok
    assert not judge([], paths=["uv.lock"], author="someone").ok
    assert not judge([], paths=[], author="dependabot[bot]").ok


# --- the tier a diff needs -----------------------------------------------------------------


def test_a_docs_only_diff_needs_docs():
    assert check.required_tier(["docs/a.md", "README.md"], RULES) == "docs"


def test_the_deepest_path_decides():
    assert check.required_tier(["docs/a.md", "tests/t.py"], RULES) == "gate-or-test"
    assert check.required_tier(["docs/a.md", "CLAUDE.md"], RULES) == "rulebook"


def test_a_path_no_route_names_is_charged_the_deepest_tier():
    assert check.required_tier(["docs/a.md", "src/x.py"], RULES) == "production-runtime"


def test_a_path_two_routes_name_takes_the_deeper_one():
    assert check.required_tier(["CLAUDE.md"], RULES) == "rulebook"


def test_no_changed_path_needs_the_shallowest_tier():
    assert check.required_tier([], RULES) == "docs"


def test_this_repositorys_tiers_file_is_well_formed():
    rules = json.loads((ROOT / ".github" / "review_verdict_tiers.json").read_text())
    assert rules["tiers"] == TIERS
    assert all(route["tier"] in TIERS and route["paths"] for route in rules["routes"])
    assert isinstance(rules["generated"], list)
    assert check.required_tier(["docs/anything.md"], rules) == "docs"
    assert (
        check.required_tier(["nothing/routes/here.bin"], rules) == "production-runtime"
    )


def test_the_exemptions_file_lists_only_patterns():
    exemptions = json.loads(
        (ROOT / ".github" / "review_verdict_exemptions.json").read_text()
    )
    assert exemptions
    assert all(isinstance(p, str) for patterns in exemptions.values() for p in patterns)


# --- the carried diff, against a real repository -------------------------------------------


def git(repo, *args):
    done = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.com",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


def put(repo, name, text):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    git(repo, "--literal-pathspecs", "add", name)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    put(tmp_path, "src/x.py", "x = 0\n")
    put(tmp_path, "uv.lock", "lock 0\n")
    git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def branch_commit(repo, name, files, base="main"):
    git(repo, "checkout", "-q", "-b", name, base)
    for path, text in files.items():
        put(repo, path, text)
    git(repo, "commit", "-q", "-m", name)
    return git(repo, "rev-parse", "HEAD")


def test_a_rebase_onto_a_moved_main_is_the_same_diff(repo):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    git(repo, "checkout", "-q", "main")
    put(repo, "docs/note.md", "note\n")
    git(repo, "commit", "-q", "-m", "main moves")
    git(repo, "checkout", "-q", "pr")
    git(repo, "rebase", "-q", "main")
    head = git(repo, "rev-parse", "HEAD")
    assert head != old
    assert check.delta_state(repo, "main", old, head) == check.Delta("same-diff", "")


def test_a_second_commit_that_edits_code_is_a_changed_diff(repo):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    put(repo, "src/x.py", "x = 2\n")
    git(repo, "commit", "-q", "-m", "more")
    head = git(repo, "rev-parse", "HEAD")
    moved = check.delta_state(repo, "main", old, head, ["uv.lock"])
    assert (moved.kind, moved.detail) == ("changed", "src/x.py")
    assert not moved.carries


def test_a_delta_of_only_a_listed_generated_file_carries(repo):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n", "uv.lock": "lock 1\n"})
    put(repo, "uv.lock", "lock 2\n")
    git(repo, "commit", "-q", "-m", "relock")
    head = git(repo, "rev-parse", "HEAD")
    moved = check.delta_state(repo, "main", old, head, ["uv.lock"])
    assert (moved.kind, moved.detail) == ("generated-only", "uv.lock")
    assert moved.carries


def test_the_same_delta_does_not_carry_when_the_file_is_not_listed_as_generated(repo):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n", "uv.lock": "lock 1\n"})
    put(repo, "uv.lock", "lock 2\n")
    git(repo, "commit", "-q", "-m", "relock")
    head = git(repo, "rev-parse", "HEAD")
    assert check.delta_state(repo, "main", old, head, []).kind == "changed"


def test_a_generated_pattern_does_not_excuse_a_file_new_in_the_pr(repo):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    put(repo, "golden/new.json", "{}\n")
    git(repo, "commit", "-q", "-m", "adds a file")
    head = git(repo, "rev-parse", "HEAD")
    # The file is absent at the merge base, so no drift gate stands behind it: judged by hand.
    moved = check.delta_state(repo, "main", old, head, ["golden/*"])
    assert (moved.kind, moved.detail) == ("changed", "golden/new.json")
    assert not check.is_generated(repo, "main", "golden/new.json", ["golden/*"])
    assert check.is_generated(repo, "main", "src/x.py", ["src/*"])


def test_a_reviewed_head_that_is_not_in_the_repository_is_unreadable(repo):
    head = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    moved = check.delta_state(repo, "main", "f" * 40, head)
    assert moved.kind == "unreadable"
    assert not moved.carries


def second_commit(repo, files):
    for path, text in files.items():
        put(repo, path, text)
    git(repo, "commit", "-q", "-m", "second")
    return git(repo, "rev-parse", "HEAD")


def test_a_hand_edit_to_a_non_ascii_named_file_is_a_changed_diff(repo):
    # git quotes `caf\303\251` in `--name-only`; the quoted text names no file, so the edit used
    # to vanish and an old ARM verdict passed as "generated only".
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    head = second_commit(repo, {"src/caf\u00e9.py": "y = 1\n"})
    moved = check.delta_state(repo, "main", old, head, ["uv.lock"])
    assert (moved.kind, moved.detail) == ("changed", "src/caf\u00e9.py")
    assert not moved.carries


def test_a_hand_edit_to_a_file_named_like_a_pathspec_is_a_changed_diff(repo):
    # Read as a pathspec, `:(top)notes.txt` means a file `notes.txt` that does not exist: the
    # edit would show as an empty diff on both sides and pass as "generated only".
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    head = second_commit(repo, {":(top)notes.txt": "n = 1\n"})
    moved = check.delta_state(repo, "main", old, head, [])
    assert (moved.kind, moved.detail) == ("changed", ":(top)notes.txt")


def test_the_paths_of_a_diff_are_listed_verbatim_with_both_sides_of_a_rename(repo):
    put(repo, "docs/a.md", "a\n" * 20)
    git(repo, "commit", "-q", "-m", "docs at the base")
    git(repo, "checkout", "-q", "-b", "pr", "main")
    git(repo, "mv", "docs/a.md", "docs/b.md")
    put(repo, "tests/caf\u00e9.py", "t = 1\n")
    git(repo, "commit", "-q", "-m", "rename and add")
    paths = check.changed_paths(repo, "main", "pr")
    assert sorted(paths) == ["docs/a.md", "docs/b.md", "tests/caf\u00e9.py"]


def test_a_move_out_of_a_deep_directory_is_charged_the_deep_tier(repo):
    git(repo, "checkout", "-q", "-b", "pr", "main")
    (repo / "docs").mkdir()
    git(repo, "mv", "src/x.py", "docs/x.md")
    git(repo, "commit", "-q", "-m", "move code into docs")
    paths = check.changed_paths(repo, "main", "pr")
    assert check.required_tier(paths, RULES) == "production-runtime"


def test_changed_paths_is_none_when_git_cannot_say(repo):
    assert check.changed_paths(repo, "main", "f" * 40) is None


def test_a_diff_that_differs_with_no_path_to_show_for_it_is_changed_not_generated(
    repo, monkeypatch
):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    head = second_commit(repo, {"src/x.py": "x = 2\n"})
    monkeypatch.setattr(check, "changed_paths", lambda *args: [])
    moved = check.delta_state(repo, "main", old, head, ["src/*"])
    assert (moved.kind, moved.carries) == ("changed", False)


def test_a_path_list_git_could_not_produce_is_unreadable(repo, monkeypatch):
    old = branch_commit(repo, "pr", {"src/x.py": "x = 1\n"})
    head = second_commit(repo, {"src/x.py": "x = 2\n"})
    monkeypatch.setattr(check, "changed_paths", lambda *args: None)
    moved = check.delta_state(repo, "main", old, head, ["src/*"])
    assert (moved.kind, moved.carries) == ("unreadable", False)


# --- main ---------------------------------------------------------------------------------


def facts(entries, author="someone", paths=("src/x.py",)):
    return lambda repo, number, root: check.Facts(
        author, A, list(paths), entries, "origin/main"
    )


def run_main(load, tmp_path, capsys):
    (tmp_path / ".github").mkdir()
    for name in ("review_verdict_tiers.json", "review_verdict_exemptions.json"):
        (tmp_path / ".github" / name).write_text((ROOT / ".github" / name).read_text())
    code = check.main(
        ["--repo", "o/r", "--pr", "7", "--root", str(tmp_path)], load=load
    )
    return code, capsys.readouterr().out


def test_main_exits_0_on_a_pass_and_1_on_a_fail(tmp_path, capsys):
    code, out = run_main(facts([comment(verdict())]), tmp_path, capsys)
    assert code == 0
    assert "PASS #7" in out


def test_main_exits_1_with_the_reason_when_there_is_no_verdict(tmp_path, capsys):
    code, out = run_main(facts([]), tmp_path, capsys)
    assert code == 1
    assert "FAIL #7" in out
    assert "no review verdict" in out


def test_main_exits_3_and_never_passes_when_a_read_failed(tmp_path, capsys):
    def broken(repo, number, root):
        raise check.CannotJudge("gh api: 502")

    code, out = run_main(broken, tmp_path, capsys)
    assert code == 3
    assert "COULD NOT JUDGE #7" in out
    assert "PASS" not in out


# --- load_facts: a fake `gh` that runs the real jq, and a local origin ----------------------

GH = """#!/bin/sh
# The two forms the check uses: gh api --paginate <endpoint> --jq <expression>
[ "$1" = api ] && [ "$2" = --paginate ] && [ "$4" = --jq ] || { echo "unexpected: $*" >&2; exit 9; }
file="$GH_FIXTURES/$(printf %s "$3" | tr / _).json"
[ -f "$file" ] || { echo "gh: Not Found (HTTP 404)" >&2; exit 1; }
exec jq -c "$5" "$file"
"""
needs_jq = pytest.mark.skipif(
    shutil.which("jq") is None, reason="the fake gh runs the real jq"
)


@pytest.fixture
def pr_world(tmp_path, monkeypatch):
    """A bare origin with `main` and a PR branch, a clone of it, and a fake `gh` on PATH."""
    work, bare, clone = tmp_path / "work", tmp_path / "origin.git", tmp_path / "clone"
    work.mkdir()
    git(work, "init", "-q", "-b", "main")
    put(work, "src/x.py", "x = 0\n")
    put(work, "docs/a.md", "a\n" * 20)
    git(work, "commit", "-q", "-m", "base")
    git(work, "checkout", "-q", "-b", "pr")
    put(work, "src/x.py", "x = 1\n")
    put(work, "tests/caf\u00e9.py", "t = 1\n")
    git(work, "mv", "docs/a.md", "docs/b.md")
    git(work, "commit", "-q", "-m", "pr")
    head = git(work, "rev-parse", "HEAD")
    git(tmp_path, "init", "-q", "--bare", str(bare))
    git(work, "push", "-q", str(bare), "main", "pr")
    git(tmp_path, "clone", "-q", str(bare), str(clone))
    bin_dir, fixtures = tmp_path / "bin", tmp_path / "fixtures"
    bin_dir.mkdir()
    fixtures.mkdir()
    (bin_dir / "gh").write_text(GH)
    (bin_dir / "gh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    monkeypatch.setenv("GH_FIXTURES", str(fixtures))

    def serve(endpoint, doc):
        (fixtures / (endpoint.replace("/", "_") + ".json")).write_text(json.dumps(doc))

    serve(
        "repos/o/r/pulls/7",
        {"head": {"sha": head}, "user": {"login": "someone"}, "base": {"ref": "main"}},
    )
    serve(
        "repos/o/r/issues/7/comments",
        [
            {
                "body": "looks fine",
                "created_at": "2026-10-19T09:00:00Z",
                "user": {"login": "maintainer"},
            },
            {"body": None, "created_at": "2026-10-19T09:30:00Z", "user": None},
        ],
    )
    serve(
        "repos/o/r/pulls/7/reviews",
        [
            {
                "body": verdict(head=head),
                "submitted_at": "2026-10-19T10:00:00Z",
                "user": {"login": "maintainer"},
                "state": "COMMENTED",
            },
            {
                "body": verdict("FIX", head=head),
                "submitted_at": None,
                "user": {"login": "maintainer"},
                "state": "PENDING",
            },
            {
                "body": "note",
                "submitted_at": None,
                "user": {"login": "maintainer"},
                "state": "COMMENTED",
            },
        ],
    )
    return clone, head, serve


@needs_jq
def test_load_facts_reads_the_pr_the_paths_and_the_comments_and_reviews(pr_world):
    clone, head, _ = pr_world
    facts_ = check.load_facts("o/r", 7, clone)
    assert (facts_.author, facts_.head, facts_.base) == ("someone", head, "origin/main")
    assert sorted(facts_.paths) == [
        "docs/a.md",
        "docs/b.md",
        "src/x.py",
        "tests/caf\u00e9.py",
    ]
    assert (
        [(e["login"], e["body"][:6]) for e in facts_.entries]
        == [
            ("maintainer", "looks "),
            ("", ""),
            ("maintainer", "Review"),
            ("maintainer", "note"),
        ]
    )  # a deleted user reads as a bot, a null body as empty, a pending review is not a verdict
    assert all(
        isinstance(e["created_at"], str) for e in facts_.entries
    )  # a null time is ""
    assert check.newest_verdict(facts_.entries) == check.Verdict(
        "ARM", head, "production-runtime"
    )


@needs_jq
def test_load_facts_cannot_judge_when_gh_cannot_answer(pr_world):
    clone, _, _ = pr_world
    with pytest.raises(check.CannotJudge, match="gh api repos/o/r/pulls/8"):
        check.load_facts("o/r", 8, clone)


@needs_jq
def test_load_facts_cannot_judge_when_the_base_cannot_be_fetched(pr_world):
    clone, head, serve = pr_world
    serve(
        "repos/o/r/pulls/7",
        {"head": {"sha": head}, "user": {"login": "someone"}, "base": {"ref": "gone"}},
    )
    with pytest.raises(check.CannotJudge, match="git fetch origin gone"):
        check.load_facts("o/r", 7, clone)


@needs_jq
def test_load_facts_cannot_judge_when_the_paths_cannot_be_listed(pr_world, monkeypatch):
    clone, _, _ = pr_world
    monkeypatch.setattr(check, "changed_paths", lambda *args: None)
    with pytest.raises(check.CannotJudge, match="could not list the paths"):
        check.load_facts("o/r", 7, clone)


# --- the workflow --------------------------------------------------------------------------


def jobs():
    text = WORKFLOW.read_text()
    head, _, rerun = text.partition("\n  rerun-on-verdict:\n")
    _, _, check_job = head.partition("\njobs:\n")
    return text, check_job, rerun


def test_the_job_is_named_review_verdict_and_runs_on_a_pr_and_a_merge_group():
    text, check_job, _ = jobs()
    assert "\n  review-verdict:\n    name: review-verdict\n" in text
    assert (
        "github.event_name == 'pull_request' || github.event_name == 'merge_group'"
        in check_job
    )
    assert "\n  merge_group:\n" in text
    assert "python .github/scripts/check_review_binding.py" in check_job


def test_the_check_job_holds_no_write_scope():
    text, check_job, _ = jobs()
    assert ": write" not in check_job
    top = text.partition("\npermissions:\n")[2].partition("\nconcurrency:")[0]
    assert top.strip() == "contents: read"


def test_the_rerun_job_holds_actions_write_alone_and_checks_nothing_out():
    _, _, rerun = jobs()
    scopes = [
        line.strip() for line in rerun.splitlines() if line.strip().endswith(": write")
    ]
    assert scopes == ["actions: write"]
    assert "actions/checkout" not in rerun
    assert "gh run rerun" in rerun
    assert "Review-Verdict:" in rerun


def test_every_action_is_pinned_to_a_full_sha():
    uses = [line for line in WORKFLOW.read_text().splitlines() if "uses:" in line]
    assert uses, (
        "the check job checks the repository out, so the workflow has a uses: line"
    )
    for line in uses:
        ref = line.split("@", 1)[1].split()[0]
        assert len(ref) == 40, line


def test_two_different_pure_renames_are_a_changed_diff(repo):
    git(repo, "checkout", "-q", "-b", "pr", "main")
    git(repo, "mv", "src/x.py", "src/y.py")
    git(repo, "commit", "-q", "-m", "rename to y")
    old = git(repo, "rev-parse", "HEAD")
    git(repo, "reset", "-q", "--hard", "main")
    git(repo, "mv", "src/x.py", "src/z.py")
    git(repo, "commit", "-q", "-m", "rename to z")
    head = git(repo, "rev-parse", "HEAD")
    moved = check.delta_state(repo, "main", old, head, ["uv.lock"])
    assert moved.kind == "changed"
