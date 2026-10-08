"""The domain-neutral machinery is in ``core/``; the industrial code is a domain (#125).

Step 2 of #125 moves modules without changing what they do: the golden
catalog (``test_catalog_golden.py``) proves the output did not move. This
module pins the layout itself, and the one direction the split must hold:
``core`` does not import a domain, except through the edges listed in
:data:`CORE_TO_INDUSTRIAL`. Those are machinery and industrial data that still
share a module; the list may only shrink, and each removal is a
one-line edit here.

It also pins that a pre-rename import path still resolves after the move,
since the deprecated alias maps module paths, not only the package name.
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "synthetic_ecommerce_data"

CORE_MODULES = (
    "breadth",
    "brands",
    "bundle",
    "cli",
    "config",
    "dimensions",
    "drawing",
    "drawing.model",
    "drawing.sheet",
    "drawing.style",
    "drawing.svg",
    "emit",
    "entry",
    "formats",
    "model",
    "naming",
    "noise",
    "noncopy",
    "price",
    "typespec",
    "voice",
)

INDUSTRIAL_MODULES = (
    "breadth",
    "compat",
    "conformance",
    "data",
    "drawing.breadth_shapes",
    "drawing.figures",
    "generate",
    "measure",
    "muststock",
    "names",
    "newtypes",
    "price_report",
    "product_types",
    "records",
    "render",
    "series",
    "standards",
    "tabletype",
    "taxonomy",
    "vocab",
)

#: ``(core module, industrial module it imports)``: the seams the move-only
#: step could not cut without a redesign. Shrinks only.
CORE_TO_INDUSTRIAL = frozenset(
    {
        ("brands", "vocab"),
        ("cli", "breadth"),
        ("cli", "generate"),
        ("cli", "measure"),
        ("drawing", "drawing.figures"),
        ("drawing", "render.marking"),
        ("drawing.style", "render.marking"),
        ("emit", "render.kinds"),
        ("emit", "taxonomy"),
        ("entry", "series"),
        ("noise", "compat"),
        ("noise", "conformance"),
        ("noise", "standards"),
        ("price", "breadth"),
        ("price", "newtypes"),
        ("typespec", "breadth"),
        ("typespec", "conformance"),
        ("typespec", "drawing.figures"),
        ("typespec", "taxonomy"),
        ("typespec", "vocab"),
    }
)

CORE = "synthetic_ecommerce_data.core"
INDUSTRIAL = "synthetic_ecommerce_data.domains.industrial"


def test_the_core_modules_are_in_core():
    missing = [m for m in CORE_MODULES if not _is_module(f"{CORE}.{m}")]
    assert missing == []


def test_the_industrial_modules_are_in_the_industrial_domain():
    missing = [
        m for m in INDUSTRIAL_MODULES if not _is_module(f"{INDUSTRIAL}.{m}")
    ]
    assert missing == []


def test_the_dissolved_catalog_package_is_gone():
    assert not (PACKAGE / "catalog").exists()


def _imported(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
    return names


def _is_module(name: str) -> bool:
    """Whether ``name`` is a module, rather than a name imported from one."""
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


def _module_of(path: Path) -> str:
    parts = path.relative_to(PACKAGE / "core").with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def test_core_imports_a_domain_only_through_the_listed_edges():
    edges = set()
    for path in sorted((PACKAGE / "core").rglob("*.py")):
        for name in _imported(path):
            if not name.startswith(f"{INDUSTRIAL}."):
                continue
            target = name[len(INDUSTRIAL) + 1 :]
            if _is_module(name):
                edges.add((_module_of(path), target))
    assert edges == CORE_TO_INDUSTRIAL


def test_a_pre_rename_path_resolves_to_the_moved_module():
    done = subprocess.run(
        [
            sys.executable,
            "-W",
            "ignore::DeprecationWarning",
            "-c",
            "import synthetic_industrial_products.catalog.emit as old_emit\n"
            "from synthetic_industrial_products.catalog import generate as old_generate\n"
            "import synthetic_ecommerce_data.core.emit as emit\n"
            "import synthetic_ecommerce_data.domains.industrial.generate as generate\n"
            "print(old_emit is emit, old_generate is generate)\n",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.stdout.split() == ["True", "True"], done.stderr
