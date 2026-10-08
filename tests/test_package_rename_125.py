"""The package is ``synthetic_ecommerce_data``; the old name is a deprecated alias (#125).

Step 1 of #125 renames the generator so that it can hold more than the
industrial catalog. Downstream pins import the old name, so for one release
cycle ``synthetic_industrial_products`` still imports, as the SAME module
objects (a monkeypatch through either name is seen through both), with a
:class:`DeprecationWarning` naming the new package. The old ``sip-*`` commands
keep working too, with a note on stderr, which no catalog byte depends on.

The old-name checks run in a fresh interpreter: the warning fires once per
process, and another test may already have imported the package.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _project() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def _python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT, check=False
    )


def test_the_distribution_is_synthetic_ecommerce_data():
    assert _project()["name"] == "synthetic-ecommerce-data"


def test_the_new_commands_and_the_deprecated_old_ones_are_installed():
    assert _project()["scripts"] == {
        "sed-generate": "synthetic_ecommerce_data.core.cli:main",
        "sed-render": "synthetic_ecommerce_data.cli:main",
        "sip-generate": "synthetic_industrial_products:sip_generate",
        "sip-render": "synthetic_industrial_products:sip_render",
    }


def test_the_package_imports_under_its_new_name():
    assert importlib.util.find_spec("synthetic_ecommerce_data") is not None


def test_an_old_import_path_is_the_same_module_and_warns():
    done = _python(
        "import warnings\n"
        "with warnings.catch_warnings(record=True) as caught:\n"
        "    warnings.simplefilter('always')\n"
        "    from synthetic_industrial_products.catalog import generate as old\n"
        "    from synthetic_industrial_products import FIXTURES as old_fixtures\n"
        "import synthetic_ecommerce_data\n"
        "import synthetic_ecommerce_data.domains.industrial.generate as new\n"
        "print(old is new, old_fixtures is synthetic_ecommerce_data.FIXTURES)\n"
        "print(sum(issubclass(w.category, DeprecationWarning)\n"
        "          and 'synthetic_ecommerce_data' in str(w.message) for w in caught))\n"
    )
    assert done.stdout.split() == ["True", "True", "1"], done.stderr


def test_an_old_command_still_runs_and_says_it_is_deprecated():
    done = _python(
        "import sys\n"
        "from synthetic_industrial_products import sip_generate\n"
        "sys.argv = ['sip-generate', '--help']\n"
        "sip_generate()\n"
    )
    assert done.returncode == 0, done.stderr
    assert "usage:" in done.stdout
    assert "sip-generate is deprecated; use sed-generate" in done.stderr
