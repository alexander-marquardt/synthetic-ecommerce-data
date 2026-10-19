"""The `review-verdict` check: a PR merges only on an ARM verdict bound to its head (agent-ops#111).

The same check elastic/prism runs (``.github/scripts/check_review_binding.py``, prism#10107),
trimmed for a repository with no review-rules map: the tier routes and the generated-file list
are data in ``.github/review_verdict_tiers.json``. The file is byte for byte the same in every
repository that carries it; ``git hash-object`` on it prints one id.

The verdict comment
-------------------
The review agent posts, on the PR (an issue comment or a ``gh pr review --comment``), three
lines of its verdict::

    Review-Verdict: ARM|FIX|BLOCK
    Reviewed-Head: <full 40-character sha>
    Tier: <a tier of .github/review_verdict_tiers.json: docs ... production-runtime>

``*``, backticks and ``#`` around a line are ignored, so a bold heading reads. The newest
verdict by a non-bot author decides.

What passes
-----------
All of these:

1. the newest verdict says ARM (a FIX or a BLOCK fails);
2. its ``Reviewed-Head`` is the PR head, or the PR's own diff is unchanged since it: the
   patch-id of ``merge-base..head`` is equal (a rebase, also a force-pushed one: the reviewed
   head is fetched by its full sha when no ref holds it), or every path whose patch differs is a
   generated file (a ``generated`` pattern of the tiers file that exists at the base). Any other
   change to the diff invalidates the verdict, and a delta review posts a new one at the new head;
3. its ``Tier`` is at least the tier the changed paths require. ``tiers`` is ordered shallow to
   deep; a path takes the deepest tier of any route that names it, and a path no route names is
   charged the deepest tier. A docs-only PR needs a verdict at ``docs``.

The exemptions are data, ``.github/review_verdict_exemptions.json``: an author whose every changed
path matches its listed patterns needs no verdict (Dependabot, on dependency manifests). One path
outside the list ends the exemption.

What it does not do
-------------------
It stops a FORGOTTEN review, not a forged one: every comment comes from the same account. The tier
mapping is only as good as the routes. It does not read the findings.

Exit status: 0 pass, 1 fail (the reason is printed), 3 could not judge (a read failed), which is
never reported as a pass.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess  # noqa: S404  # `git` and `gh` with argv lists, no shell
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXEMPTIONS_PATH = ".github/review_verdict_exemptions.json"
TIERS_PATH = ".github/review_verdict_tiers.json"
KINDS = ("ARM", "FIX", "BLOCK")
FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")
_FIELD = re.compile(r"^(Review-Verdict|Reviewed-Head|Tier)\s*:\s*(\S+)", re.IGNORECASE)
# No ``>``: a quoted block is someone repeating a verdict, not posting one.
_STRIP = re.compile(r"[*`#_ -]*")
NO_VERDICT = (
    "no review verdict on this pull request. The reviewer posts a comment with the lines "
    "`Review-Verdict: ARM`, `Reviewed-Head: <full sha>` and `Tier: <tier>`"
)


@dataclass(frozen=True)
class Verdict:
    kind: str | None
    head: str | None
    tier: str | None


@dataclass(frozen=True)
class Delta:
    """What changed in the PR's own diff between the reviewed head and the head."""

    kind: str  # same-diff | generated-only | changed | unreadable
    detail: str

    @property
    def carries(self) -> bool:
        return self.kind in ("same-diff", "generated-only")


@dataclass(frozen=True)
class Judgement:
    ok: bool
    reason: str


def parse_verdict(body: str) -> Verdict | None:
    """The three fields of the first ``Review-Verdict:`` line's comment, or ``None``."""
    found: dict[str, str] = {}
    for line in body.splitlines():
        matched = _FIELD.match(_STRIP.sub("", line, count=1))
        if matched:
            found.setdefault(matched.group(1).lower(), matched.group(2).strip("*`"))
    if "review-verdict" not in found:
        return None
    head = found.get("reviewed-head")
    kind = found["review-verdict"].upper()
    return Verdict(
        kind if kind in KINDS else None,
        head.lower() if head and FULL_SHA.fullmatch(head) else None,
        found.get("tier"),
    )


def _is_bot(login: str) -> bool:
    return not login or login == "github-actions" or login.endswith("[bot]")


def newest_verdict(entries: Sequence[Mapping[str, str]]) -> Verdict | None:
    """The newest verdict by a non-bot author; ``entries`` carry body, created_at, login."""
    parsed = [
        (entry["created_at"], n, verdict)
        for n, entry in enumerate(entries)
        if not _is_bot(entry["login"]) and (verdict := parse_verdict(entry["body"]))
    ]
    return max(parsed, key=lambda item: item[:2])[2] if parsed else None


def _matches(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def required_tier(paths: Sequence[str], rules: Mapping[str, object]) -> str:
    """The deepest tier the changed paths imply; an unmapped path is charged the deepest."""
    tiers: list[str] = list(rules["tiers"])  # type: ignore[call-overload]
    routes: list[Mapping[str, object]] = list(rules["routes"])  # type: ignore[call-overload]
    needed = 0
    for path in paths:
        depth = max(
            (
                tiers.index(str(route["tier"]))
                for route in routes
                if _matches(path, list(route["paths"]))  # type: ignore[call-overload]
            ),
            default=len(tiers) - 1,
        )
        needed = max(needed, depth)
    return tiers[needed]


def _exempt(
    author: str, paths: Sequence[str], exemptions: Mapping[str, list[str]]
) -> bool:
    patterns = exemptions.get(author)
    return (
        bool(patterns)
        and bool(paths)
        and all(_matches(path, patterns or []) for path in paths)
    )


def judge(
    *,
    author: str,
    head: str,
    paths: Sequence[str],
    entries: Sequence[Mapping[str, str]],
    needed: str,
    tiers: Sequence[str],
    delta: Callable[[str], Delta],
    exemptions: Mapping[str, list[str]],
) -> Judgement:
    if _exempt(author, paths, exemptions):
        return Judgement(
            True, f"exempt: every changed path is one {author} may change unreviewed"
        )
    verdict = newest_verdict(entries)
    if verdict is None:
        return Judgement(False, NO_VERDICT)
    if verdict.kind is None:
        return Judgement(
            False,
            f"the newest verdict's Review-Verdict is not one of {'|'.join(KINDS)}",
        )
    if verdict.kind != "ARM":
        return Judgement(
            False,
            f"the newest verdict is {verdict.kind}, not ARM: fix, then post a new verdict",
        )
    if verdict.head is None:
        return Judgement(
            False,
            "the newest verdict has no Reviewed-Head, or it is not a full 40-character sha",
        )
    if verdict.tier not in tiers:
        return Judgement(
            False,
            f"the verdict's Tier {verdict.tier!r} is not one of {', '.join(tiers)}",
        )
    if tiers.index(verdict.tier) < tiers.index(needed):
        return Judgement(
            False,
            f"the verdict's tier {verdict.tier} is below {needed}, which the changed paths require",
        )
    if verdict.head == head.lower():
        return Judgement(True, f"ARM at the head, tier {verdict.tier} (needs {needed})")
    moved = delta(verdict.head)
    if not moved.carries:
        return Judgement(
            False,
            f"the ARM verdict reviewed {verdict.head[:12]}, not the head {head[:12]}, and the "
            f"diff changed since ({moved.kind}: {moved.detail}): a delta review must post a new "
            "verdict",
        )
    return Judgement(
        True,
        f"ARM at {verdict.head[:12]} carries to {head[:12]} ({moved.kind}), tier {verdict.tier}",
    )


def _git(git_dir: Path, *args: str, stdin: str | None = None) -> tuple[int, str]:
    done = subprocess.run(  # noqa: S603  # `git` and `args` built here from shas and paths, no shell
        ["git", "-C", str(git_dir), *args],  # noqa: S607  # `git` resolved on PATH
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    return done.returncode, done.stdout


def _patch_id(git_dir: Path, base: str, tip: str, *path: str) -> str | None:
    code, patch = _git(git_dir, "diff", base, tip, *(["--", *path] if path else []))
    if code != 0:
        return None
    if not patch.strip():
        return ""
    code, out = _git(git_dir, "patch-id", "--stable", stdin=patch)
    return out.split()[0] if code == 0 and out.split() else None


def is_generated(git_dir: Path, rev: str, path: str, patterns: Sequence[str]) -> bool:
    """Whether ``path`` is listed as generated and exists at ``rev``.

    A path absent at ``rev`` is never generated: no drift gate stands behind a file no
    generator wrote.
    """
    return (
        _matches(path, patterns)
        and _git(git_dir, "cat-file", "-e", f"{rev}:{path}")[0] == 0
    )


def delta_state(
    git_dir: Path, base: str, old: str, head: str, generated: Sequence[str] = ()
) -> Delta:
    """Whether the PR's own diff (``merge-base(base, x)..x``) is the same at ``old``/``head``."""
    has_old = ("cat-file", "-e", f"{old}^{{commit}}")
    if _git(git_dir, *has_old)[0] != 0 and (
        # After a force-pushed rebase the reviewed head is in no ref of the CI clone;
        # GitHub serves it by full sha.
        _git(git_dir, "fetch", "--quiet", "origin", old)[0] != 0
        or _git(git_dir, *has_old)[0] != 0
    ):
        return Delta(
            "unreadable", f"the reviewed head {old[:12]} is not in the repository"
        )
    bases = [_git(git_dir, "merge-base", base, tip) for tip in (old, head)]
    if any(code != 0 for code, _ in bases):
        return Delta(
            "unreadable", f"no merge base of {base} with the reviewed head or the head"
        )
    base_old, base_new = (out.strip() for _, out in bases)
    before, after = (
        _patch_id(git_dir, base_old, old),
        _patch_id(git_dir, base_new, head),
    )
    if before is None or after is None:
        return Delta("unreadable", "git could not diff the reviewed head or the head")
    if before == after:
        return Delta("same-diff", "")
    names: set[str] = set()
    for first, second in ((base_old, old), (base_new, head)):
        names.update(
            _git(git_dir, "diff", "--name-only", first, second)[1].splitlines()
        )
    differing = sorted(
        path
        for path in names
        if _patch_id(git_dir, base_old, old, path)
        != _patch_id(git_dir, base_new, head, path)
    )
    hand = [p for p in differing if not is_generated(git_dir, base_new, p, generated)]
    if hand:
        return Delta("changed", ", ".join(hand[:5]) + (" ..." if len(hand) > 5 else ""))
    return Delta("generated-only", ", ".join(differing[:5]))


@dataclass(frozen=True)
class Facts:
    author: str
    head: str
    paths: list[str]
    entries: list[dict[str, str]]
    base: str


class CannotJudge(Exception):
    """A read failed, so the check cannot say pass or fail."""


def _gh_lines(*argv: str) -> list[dict[str, str]]:
    done = subprocess.run(  # noqa: S603  # `gh` with the repo and PR number this script was given, no shell
        ["gh", "api", "--paginate", *argv],  # noqa: S607  # `gh` resolved on PATH
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        raise CannotJudge(f"gh api {argv[0]}: {done.stderr.strip()[:200]}")
    return [json.loads(line) for line in done.stdout.splitlines() if line.strip()]


def load_facts(repo: str, number: int, root: Path) -> Facts:
    pull = _gh_lines(
        f"repos/{repo}/pulls/{number}",
        "--jq",
        "{head: .head.sha, author: .user.login, base: .base.ref}",
    )[0]
    comments = _gh_lines(
        f"repos/{repo}/issues/{number}/comments",
        "--jq",
        '.[] | {body: (.body // ""), created_at, login: (.user.login // "")}',
    )
    reviews = _gh_lines(
        f"repos/{repo}/pulls/{number}/reviews",
        "--jq",
        '.[] | {body: (.body // ""), created_at: .submitted_at, login: (.user.login // "")}',
    )
    base = f"origin/{pull['base']}"
    for ref in (pull["base"], pull["head"]):
        if _git(root, "fetch", "--quiet", "origin", ref)[0] != 0:
            raise CannotJudge(f"git fetch origin {ref} failed")
    code, merge_base = _git(root, "merge-base", base, pull["head"])
    if code != 0:
        raise CannotJudge(f"no merge base of {base} and {pull['head']}")
    # `--no-renames`: a rename is two paths, so a move out of a deep tier is still seen.
    paths = _git(
        root, "diff", "--name-only", "--no-renames", merge_base.strip(), pull["head"]
    )[1].splitlines()
    return Facts(pull["author"], pull["head"], paths, comments + reviews, base)


def main(
    argv: Sequence[str] | None = None, load: Callable[..., Facts] = load_facts
) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else ""
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        facts = load(args.repo, args.pr, args.root)
    except CannotJudge as error:
        print(f"review-verdict: COULD NOT JUDGE #{args.pr}: {error}")
        return 3
    rules = json.loads((args.root / TIERS_PATH).read_text())
    exemptions = json.loads((args.root / EXEMPTIONS_PATH).read_text())
    needed = required_tier(facts.paths, rules)
    result = judge(
        author=facts.author,
        head=facts.head,
        paths=facts.paths,
        entries=facts.entries,
        needed=needed,
        tiers=rules["tiers"],
        delta=lambda old: delta_state(
            args.root, facts.base, old, facts.head, rules.get("generated", [])
        ),
        exemptions=exemptions,
    )
    scanned = (
        f"{len(facts.entries)} comment/review bodies, {len(facts.paths)} changed paths, "
        f"needs tier {needed}"
    )
    print(
        f"review-verdict: {'PASS' if result.ok else 'FAIL'} #{args.pr} head {facts.head[:12]}: "
        f"{result.reason} ({scanned})"
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
