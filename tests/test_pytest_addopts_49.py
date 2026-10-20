"""The test runner's own options leave the caller's ``-q`` its pass/fail line (#49).

``pyproject.toml`` had ``addopts = "-q"``. A caller who also passed ``-q`` (the
merge script does) got ``-qq``, and pytest at that level prints no
``N passed in Xs`` line: a green run and a run that collected nothing look alike
on the terminal. The option is the caller's to give, so it is not in ``addopts``.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYPROJECT = REPO / "pyproject.toml"


def _addopts() -> list[str]:
    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return shlex.split(config["tool"]["pytest"]["ini_options"].get("addopts", ""))


def test_addopts_carries_no_quiet_flag() -> None:
    quiet = [a for a in _addopts() if a == "--quiet" or (a.startswith("-") and set(a[1:]) == {"q"})]
    assert quiet == [], f"addopts holds {quiet}: it stacks with the caller's -q into -qq"


def test_a_callers_single_q_still_prints_the_summary_line(tmp_path: Path) -> None:
    """Run the repository's own configuration on a one-test file, as the merge script does."""
    (tmp_path / "test_one.py").write_text("def test_one():\n    assert True\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            str(PYPROJECT),
            "--rootdir",
            str(tmp_path),
            "-p",
            "no:cacheprovider",
            "-q",
            str(tmp_path / "test_one.py"),
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 passed" in done.stdout, f"no pass line under the repository's addopts:\n{done.stdout}"


def test_the_rounding_rule_is_cited_to_its_source() -> None:
    """``value_canonical``'s one rounding is prism's rule, named where this repository states it."""
    from synthetic_ecommerce_data.core.entry import canonical

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for where, text in (("README.md", readme), ("entry.canonical", canonical.__doc__ or "")):
        assert "measurement_values.py" in text, f"{where} does not cite prism's measurement_values"
        assert "nested.py" in text, f"{where} does not cite the deployment's nested.py"
