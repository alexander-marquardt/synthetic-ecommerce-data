"""Move the default seed in a scratch worktree and name each test still pinned by hand (#50).

    uv run python scripts/reseed_proof.py              # the default seed + 1, the catalog readers
    uv run python scripts/reseed_proof.py --seed N     # another seed
    uv run python scripts/reseed_proof.py --all        # the whole suite, not the catalog readers
    uv run python scripts/reseed_proof.py --keep       # leave the worktree for a look

The suite half of #50's planted proof. A regeneration of ``golden-catalog/`` is meant to restate
every pinned figure with one command, the one ``rebuild_generated`` runs in
``scripts/merge_pr/tree.sh``. This checks HEAD out in a throwaway worktree, moves
``GeneratorConfig.seed`` there, runs that rebuild, and runs the tests that read what it rewrote
(``scripts/ci_select.py`` over the rewritten paths). Each test that goes red pins a figure the
fixture ``tests/data/golden_pins.json`` does not carry: it prints one id per line, or ``green``.

Exit 0 when green, 1 with a red test, 2 when the proof could not run (a rebuild refused the seed,
a measure rule nothing on the new catalog fits, or pytest stopped before its summary). It takes
minutes: three builds and the catalog readers on ``--workers`` processes. Committed work only:
the worktree is HEAD's, so an uncommitted edit is not in the proof.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG = Path("src/synthetic_ecommerce_data/core/config.py")

#: ``rebuild_generated`` of scripts/merge_pr/tree.sh, its arrays in scripts/merge_pr/config.sh:
#: the build, the measured builds (gen#85) and the golden pins. tests/test_reseed_proof_50.py
#: pins them to the merge script's.
REBUILD: tuple[tuple[str, ...], ...] = (
    ("ecom-generate", "build", "--out", "golden-catalog"),
    ("python", "-m", "synthetic_ecommerce_data.domains.industrial.measured_builds"),
    ("python", "scripts/measure_pins.py"),
)

SEED_LINE = re.compile(r"^(    seed: int = )(\d+)$", re.MULTILINE)
#: A red in pytest's ``-rfE`` summary: the id (a parameter id may hold blanks), without the
#: `` - <message>`` after it.
RED_LINE = re.compile(r"^(?:FAILED|ERROR) ([^\s\[]+(?:\[[^\]]*\])?)", re.MULTILINE)


class ProofError(Exception):
    """The proof could not run; the message says which step refused."""


def reseed(text: str, seed: int | None = None) -> tuple[str, int]:
    """``config.py``'s text with the default seed moved to ``seed`` (default: one more)."""
    found = SEED_LINE.findall(text)
    if len(found) != 1:
        raise ProofError(
            f"{CONFIG} has {len(found)} seed lines (`    seed: int = <n>`), not one: "
            "the seed cannot be moved, and a run on the old one would prove nothing"
        )
    new = int(found[0][1]) + 1 if seed is None else seed
    return SEED_LINE.sub(rf"\g<1>{new}", text), new


def red_tests(output: str) -> list[str]:
    """The ids pytest's summary names red, each once, in its order."""
    return list(dict.fromkeys(RED_LINE.findall(output)))


def _env() -> dict[str, str]:
    # The caller's `uv run` points VIRTUAL_ENV at its own checkout's environment.
    return {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}


def _run(tree: Path, argv: list[str] | tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "-q", "--locked", "--directory", str(tree), *argv],
        capture_output=True,
        text=True,
        env=_env(),
        check=False,
    )


def _rewritten(tree: Path) -> list[str]:
    status = subprocess.run(
        ["git", "-C", str(tree), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line[3:] for line in status.splitlines() if line[3:] != str(CONFIG)]


def prove(tree: Path, seed: int | None, every: bool, workers: str) -> tuple[int, list[str]]:
    """Reseed, rebuild and test the worktree at ``tree``: the seed and the red ids."""
    config = tree / CONFIG
    text, new = reseed(config.read_text("utf-8"), seed)
    config.write_text(text, "utf-8")
    print(f"reseed_proof: seed {new}; rebuilding in {tree}", file=sys.stderr)
    for step in REBUILD:
        done = _run(tree, step)
        if done.returncode:
            raise ProofError(f"`{' '.join(step)}` refused seed {new}:\n{done.stderr.strip()}")
    tests: list[str] = []
    if not every:
        rewritten = _rewritten(tree)
        if not rewritten:
            raise ProofError(f"the rebuild on seed {new} rewrote nothing: the seed reaches no file")
        tests = _run(
            tree, ("python", "scripts/ci_select.py", "--changed", *rewritten)
        ).stdout.split()
        if not tests:
            raise ProofError(f"no test reads the files the rebuild rewrote: {rewritten}")
    # The run takes minutes: its log is a file, so a slow one can be watched with `tail -f`.
    log = tree.parent / "pytest.log"
    print(f"reseed_proof: running {len(tests) or 'every'} test file(s); log {log}", file=sys.stderr)
    with log.open("w", encoding="utf-8") as out:
        code = subprocess.run(
            ["uv", "run", "-q", "--locked", "--directory", str(tree), "pytest", "-v", "-rfE"]
            + ["-p", "no:cacheprovider", "-n", workers, "--", *tests],
            stdout=out,
            stderr=subprocess.STDOUT,
            env=_env(),
            check=False,
        ).returncode
    output = log.read_text("utf-8")
    reds = red_tests(output)
    # 0 is green and 1 is a red test; anything else (an interrupt, a usage or internal error,
    # nothing collected) stopped before the verdict.
    if code not in (0, 1) or (code == 1 and not reds):
        tail = "\n".join(output.strip().splitlines()[-20:])
        raise ProofError(f"pytest stopped with {code} before a verdict:\n{tail}")
    return new, reds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--seed", type=int, help="the seed to build (default: the default + 1)")
    parser.add_argument("--all", action="store_true", help="run the whole suite")
    parser.add_argument("--workers", default="8", help="pytest-xdist workers (default 8)")
    parser.add_argument("--keep", action="store_true", help="leave the worktree in place")
    args = parser.parse_args(argv)
    scratch = Path(tempfile.mkdtemp(prefix="reseed-proof-"))
    tree = scratch / "tree"
    subprocess.run(
        ["git", "-C", str(REPO), "worktree", "add", "-q", "--detach", str(tree), "HEAD"], check=True
    )
    try:
        seed, reds = prove(tree, args.seed, args.all, args.workers)
    except ProofError as error:
        print(f"reseed_proof: {error}", file=sys.stderr)
        return 2
    finally:
        if args.keep:
            print(f"reseed_proof: the worktree stays at {tree}", file=sys.stderr)
        else:
            subprocess.run(
                ["git", "-C", str(REPO), "worktree", "remove", "--force", str(tree)], check=False
            )
            shutil.rmtree(scratch, ignore_errors=True)
    if not reds:
        print("green")
        return 0
    print(
        f"reseed_proof: {len(reds)} test(s) red on seed {seed}, each a pin typed by hand:",
        file=sys.stderr,
    )
    print("\n".join(reds))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
