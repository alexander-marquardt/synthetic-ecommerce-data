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
        "ecom-generate": "synthetic_ecommerce_data.catalog.cli:main",
        "ecom-render": "synthetic_ecommerce_data.cli:main",
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
        "import synthetic_ecommerce_data.catalog.generate as new\n"
        "print(old is new, old_fixtures is synthetic_ecommerce_data.FIXTURES)\n"
        "print(sum(issubclass(w.category, DeprecationWarning)\n"
        "          and 'synthetic_ecommerce_data' in str(w.message) for w in caught))\n"
    )
    assert done.stdout.split() == ["True", "True", "1"], done.stderr


def test_an_old_name_import_leaves_the_real_module_spec_in_place():
    """Importing through the alias must not rewrite the real module's ``__spec__``.

    The import system sets ``__spec__`` on whatever ``create_module`` returns,
    so a naive alias leaves ``synthetic_ecommerce_data.X.__spec__`` naming the
    alias, with the alias as its loader. ``resources.files`` then cannot find
    the data package's files, and ``importlib.reload`` runs nothing.
    """
    done = _python(
        "import importlib, warnings\n"
        "from importlib import resources\n"
        "warnings.simplefilter('ignore')\n"
        "import synthetic_industrial_products.data as data\n"
        "import synthetic_industrial_products.catalog.emit as emit\n"
        "print(data.__spec__.name == data.__name__, emit.__spec__.name == emit.__name__)\n"
        "text = resources.files('synthetic_ecommerce_data.data')"
        ".joinpath('reference_fingerprints.json').read_text('utf-8')\n"
        "print(len(text) > 0)\n"
        "emit.IMAGE_ROOT = 'patched'\n"
        "importlib.reload(emit)\n"
        "print(emit.IMAGE_ROOT)\n"
    )
    assert done.stdout.split() == ["True", "True", "True", "industrial"], done.stderr


def test_an_old_command_still_runs_and_says_it_is_deprecated():
    done = _python(
        "import sys\n"
        "from synthetic_industrial_products import sip_generate\n"
        "sys.argv = ['sip-generate', '--help']\n"
        "sip_generate()\n"
    )
    assert done.returncode == 0, done.stderr
    assert "usage:" in done.stdout
    assert "sip-generate is deprecated; use ecom-generate" in done.stderr
