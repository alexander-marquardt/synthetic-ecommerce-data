"""This repository's git hooks and CI's file checks, in one script, with no pre-commit (#1108).

Usage:

    python3 scripts/hooks.py install                      # once per clone: the three git hooks
    python3 scripts/hooks.py run pre-commit               # the commit hook: the staged files
    python3 scripts/hooks.py run pre-commit --all-files   # CI's lint job: every tracked file
    python3 scripts/hooks.py run commit-msg <message-file>
    python3 scripts/hooks.py run pre-push <remote> <url>  # git passes the refs on stdin

The hooks are the ones `.pre-commit-config.yaml` held, under the same ids (see `HOOKS`):

* pre-commit: ``end-of-file-fixer``, ``trailing-whitespace``, ``check-yaml`` and
  ``ruff-check`` on the staged files, then ``file-size-warning``
  (``scripts/file_size_gate.py --warn-at-commit``, docs/file-size-budget.md);
* commit-msg: ``no-ai-attribution`` (``scripts/check_commit_msg.py``);
* pre-push: ``prepush-gate`` (``bash scripts/prepush.sh --hook``, docs/pre-push-gate.md).

The two fixers rewrite a file and fail, so the fixed file is staged again by hand.
``golden-catalog/`` and ``vendor/`` are left alone by both, because those bytes are pinned.
``ruff-check`` runs the ruff that ``uv.lock`` pins, the same one CI's lint job runs.
``--all-files`` runs the four file checks without the file-size warning, because CI's
``file-size`` job runs the whole gate.

A commit or push hook runs with the unstaged edits set aside, so it sees what is being
committed or pushed (``set_aside``). ``SKIP=<id>[,<id>...]`` skips the named hooks; CI
still runs every job. The pre-push hook gives ``scripts/prepush.py`` the
``PRE_COMMIT_*`` variables that pre-commit used to set, so the gate reads the same names.
Exit status: 0 every hook passed or was skipped, 1 a hook failed, 2 usage.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

ZEROS = "0" * 40
MARK = "Written by scripts/hooks.py install"
PINNED = re.compile(r"^(golden-catalog|vendor)/")
# identify's rule for a text file, as pre-commit applied it: no byte outside this set.
TEXT_BYTES = bytes({7, 8, 9, 10, 11, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
SHIM = """#!/bin/sh
# {mark} (#1108): the {stage} hook. Rerun that command to rewrite it.
root="$(git rev-parse --show-toplevel)" || exit 1
exec python3 "$root/scripts/hooks.py" run {stage} "$@"
"""
STAGES = ("pre-commit", "commit-msg", "pre-push")


def git(root: Path, *args: str, check: bool = True) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          check=False)
    if check and done.returncode != 0:
        raise SystemExit(f"hooks: git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def is_text(path: Path) -> bool:
    with path.open("rb") as handle:
        return not handle.read(1024).translate(None, TEXT_BYTES)


def end_of_file(paths: list[Path]) -> tuple[bool, str]:
    """``end-of-file-fixer``: a non-empty file ends in exactly one line ending."""
    fixed = []
    for path in paths:
        data = path.read_bytes()
        body = data.rstrip(b"\r\n")
        ending = data[len(body):]
        if not data or ending in (b"\n", b"\r\n"):
            continue
        path.write_bytes(body + (b"\r\n" if ending.startswith(b"\r\n") else b"\n") if body else b"")
        fixed.append(f"Fixing {path}")
    return not fixed, "\n".join(fixed)


def trailing_whitespace(paths: list[Path]) -> tuple[bool, str]:
    """``trailing-whitespace``: no line ends in spaces or tabs before its line ending."""
    fixed = []
    for path in paths:
        lines = io.BytesIO(path.read_bytes()).readlines()  # split on LF only, as the hook did
        out = []
        for line in lines:
            eol = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(line[: len(line) - len(eol)].rstrip() + eol)
        if out != lines:
            path.write_bytes(b"".join(out))
            fixed.append(f"Fixing {path}")
    return not fixed, "\n".join(fixed)


def check_yaml(paths: list[Path]) -> tuple[bool, str]:
    """``check-yaml``: each YAML file parses, as one document."""
    import yaml  # main() makes sure it imports

    bad = []
    for path in paths:
        try:
            yaml.safe_load(path.read_text("utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError) as error:
            bad.append(f"{path}: {error}")
    return not bad, "\n".join(bad)


def ruff_check(paths: list[Path]) -> tuple[bool, str]:
    """``ruff-check``: the locked ruff, so the hook and CI run one version."""
    beside = Path(sys.executable).parent / "ruff"
    ruff = [str(beside)] if beside.is_file() else ["uv", "run", "-q", "--locked", "ruff"]
    done = subprocess.run([*ruff, "check", "--force-exclude", *map(str, paths)],
                          capture_output=True, text=True, check=False)
    return done.returncode == 0, (done.stdout + done.stderr).strip()


def command(argv: tuple[str, ...], extra: list[str]) -> tuple[bool, str]:
    """A hook that is a command of ours, run from the root with what git passed the hook."""
    done = subprocess.run([*argv, *extra], capture_output=True, text=True, check=False)
    return done.returncode == 0, (done.stdout + done.stderr).strip()


def yaml_file(path: str) -> bool:
    return path.endswith((".yaml", ".yml"))


def python_file(path: str) -> bool:
    return path.endswith((".py", ".pyi", ".ipynb"))


def unpinned_text(path: str) -> bool:
    return not PINNED.match(path)


# The pre-commit stage's file checks: id -> (which tracked paths it reads, the check).
FILE_HOOKS = {
    "end-of-file-fixer": (unpinned_text, end_of_file),
    "trailing-whitespace": (unpinned_text, trailing_whitespace),
    "check-yaml": (yaml_file, check_yaml),
    "ruff-check": (python_file, ruff_check),
}
# The commands of ours: id -> (stage, argv), run from the root after the file checks.
COMMAND_HOOKS = {
    "file-size-warning": ("pre-commit", (sys.executable, "scripts/file_size_gate.py", "--base",
                                         "origin/main", "--warn-at-commit")),
    "no-ai-attribution": ("commit-msg", (sys.executable, "scripts/check_commit_msg.py")),
    "prepush-gate": ("pre-push", ("bash", "scripts/prepush.sh", "--hook")),
}
HOOKS = {**{name: "pre-commit" for name in FILE_HOOKS},
         **{name: stage for name, (stage, _) in COMMAND_HOOKS.items()}}


def report(name: str, ok: bool | None, text: str) -> None:
    status = "Skipped" if ok is None else "Passed" if ok else "Failed"
    print(f"{name}{'.' * max(3, 72 - len(name))}{status}", flush=True)
    if ok is False:
        print(f"- hook id: {name}")
    if text and ok is not None:
        print(text, flush=True)


@contextlib.contextmanager
def set_aside(root: Path) -> Iterator[None]:
    """Unstaged edits to tracked files are off disk while the hooks run, then put back.

    A fixer's change that clashes with them is dropped and the edits win, as with pre-commit.
    """
    # An intent-to-add file (`git add -N`) leaves the index for the run, as pre-commit did:
    # untracked, it is neither in the patch nor emptied by the checkout.
    status = git(root, "status", "--porcelain", "-z", "--untracked-files=no").split("\0")
    ita = [entry[3:] for entry in status if entry.startswith(" A ")]
    if ita:
        git(root, "rm", "--cached", "-q", "--", *ita)
    try:
        patch = subprocess.run(["git", "-C", str(root), "diff", "--binary", "--no-color",
                                "--no-ext-diff"], capture_output=True, check=True).stdout
        if not patch:
            yield
            return
        gitdir = Path(git(root, "rev-parse", "--absolute-git-dir").strip())
        saved = gitdir / "hooks-set-aside.patch"
        saved.write_bytes(patch)
        print(f"[hooks] unstaged edits set aside in {saved}", flush=True)
        git(root, "checkout", "--", ".")
        try:
            yield
        finally:
            put_back(root, saved)
    finally:
        if ita:
            git(root, "add", "-N", "--", *ita)


def put_back(root: Path, saved: Path) -> None:
    def apply() -> bool:
        return subprocess.run(["git", "-C", str(root), "apply", "--whitespace=nowarn",
                               str(saved)], capture_output=True, check=False).returncode == 0
    if not apply():
        print("[hooks] a fix clashed with the unstaged edits: the fix is dropped", flush=True)
        git(root, "checkout", "--", ".")
        if not apply():
            raise SystemExit(f"hooks: the unstaged edits could not be put back; they are in "
                             f"{saved}: run `git apply {saved}`")
    saved.unlink()


def push_env(stdin: str, remote: str) -> dict[str, str]:
    """The ``PRE_COMMIT_*`` refs of a push, from git's pre-push lines: the first non-delete ref."""
    lines = [line.split() for line in stdin.splitlines() if len(line.split()) == 4]
    if not lines:
        return {}
    local_ref, local_sha, remote_ref, remote_sha = next(
        (line for line in lines if line[1] != ZEROS), lines[0])
    return {"PRE_COMMIT_LOCAL_BRANCH": local_ref, "PRE_COMMIT_TO_REF": local_sha,
            "PRE_COMMIT_REMOTE_BRANCH": remote_ref, "PRE_COMMIT_FROM_REF": remote_sha,
            "PRE_COMMIT_REMOTE_NAME": remote}


def run(root: Path, stage: str, extra: list[str], all_files: bool) -> int:
    skip = {name.strip() for name in os.environ.get("SKIP", "").split(",") if name.strip()}
    failed = False
    if stage == "pre-commit":
        listing = (git(root, "ls-files", "-z") if all_files else
                   git(root, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"))
        files = [name for name in listing.split("\0") if name and Path(name).is_file()]
        text = [name for name in files if is_text(Path(name))]
        for name, (wanted, check) in FILE_HOOKS.items():
            chosen = [Path(path) for path in text if wanted(path)]
            if name in skip or not chosen:
                report(name, None, "")
                continue
            ok, out = check(chosen)
            report(name, ok, out)
            failed |= not ok
        if all_files:
            return int(failed)
    if stage == "pre-push":
        os.environ.update(push_env(sys.stdin.read(), extra[0] if extra else ""))
        extra = []
    for name, (hook_stage, argv) in COMMAND_HOOKS.items():
        if hook_stage != stage:
            continue
        if name in skip:
            report(name, None, "")
            continue
        ok, out = command(argv, extra)
        report(name, ok, out)  # verbose: a passing hook's output is printed too
        failed |= not ok
    return int(failed)


def install(root: Path, force: bool) -> int:
    hooks = root / git(root, "rev-parse", "--git-path", "hooks").strip()
    hooks.mkdir(parents=True, exist_ok=True)
    for stage in STAGES:
        path = hooks / stage
        old = path.read_text("utf-8", errors="replace") if path.exists() else ""
        if old and MARK not in old and "File generated by pre-commit" not in old and not force:
            print(f"hooks: {path} is not ours or pre-commit's; keep it, or rerun with --force",
                  file=sys.stderr)
            return 1
        path.write_text(SHIM.format(mark=MARK, stage=stage), encoding="utf-8")
        path.chmod(0o755)
        print(f"hooks: wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = parser.add_subparsers(dest="action", required=True)
    put = sub.add_parser("install", help="write the pre-commit, commit-msg and pre-push hooks")
    put.add_argument("--force", action="store_true", help="replace a hook that is not ours")
    go = sub.add_parser("run", help="run one stage's hooks")
    go.add_argument("stage", choices=STAGES)
    go.add_argument("--all-files", action="store_true", help="every tracked file (CI)")
    go.add_argument("extra", nargs="*", help="what git passes the hook")
    args = parser.parse_args(argv)
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
    os.chdir(root)  # paths print as git names them, and the commands run from the root
    if args.action == "install":
        return install(root, args.force)
    if args.stage == "pre-commit" and not os.environ.get("HOOKS_UV"):
        try:
            import yaml  # noqa: F401  # check-yaml's parser
        except ImportError:  # the system python3 has no pyyaml: rerun in the locked env
            os.environ["HOOKS_UV"] = "1"
            os.execvp("uv", ["uv", "run", "-q", "--locked", "python", __file__,
                             *(argv if argv is not None else sys.argv[1:])])
    if args.all_files or args.stage == "commit-msg":
        return run(root, args.stage, args.extra, args.all_files)
    with set_aside(root):
        return run(root, args.stage, args.extra, False)


if __name__ == "__main__":
    sys.exit(main())
