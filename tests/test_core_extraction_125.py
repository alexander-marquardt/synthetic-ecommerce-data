"""The domain-neutral machinery is in ``core/``; the industrial code is a domain (#125).

Step 2 of #125 moves modules without changing what they do: the golden
catalog (``test_catalog_golden.py``) proves the output did not move. This
module pins the layout itself, and the one direction the split must hold:
``core`` reaches nothing outside itself (no domain, and not the commands or
``prism/`` above it) except through the edges listed in :data:`CORE_EDGES`.
Those are machinery and industrial data that still share a module; the list
may only shrink, and each removal is a one-line edit here.

It also pins that a pre-rename import path still resolves after the move,
since the deprecated alias maps module paths, not only the package name.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "synthetic_ecommerce_data"

CORE_MODULES = (
    "breadth",
    "brands",
    "bundle",
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

_I = "domains.industrial"

#: ``(core module, what it reaches outside core)``, relative to the package:
#: the seams the move-only step could not cut without a redesign. Shrinks
#: only. 18 edges: 16 imports, and 2 module paths named in a string. The
#: ``ecom-generate`` command's 3 imports (breadth, generate, measure) and its
#: prism imports left core with it, to ``generate_cli``.
CORE_EDGES = frozenset(
    {
        ("brands", f"{_I}.vocab"),
        ("drawing", f"{_I}.drawing.figures"),
        ("drawing", f"{_I}.render.marking"),
        ("drawing.style", f"{_I}.render.marking"),
        ("emit", f"{_I}.render.kinds"),
        ("emit", f"{_I}.taxonomy"),
        ("noise", f"{_I}.compat"),
        ("noise", f"{_I}.conformance"),
        ("noise", f"{_I}.standards"),
        ("price", f"{_I}.breadth"),
        ("price", f"{_I}.newtypes"),
        ("typespec", f"{_I}.breadth"),
        ("typespec", f"{_I}.conformance"),
        ("typespec", f"{_I}.drawing.figures"),
        ("typespec", f"{_I}.taxonomy"),
        ("typespec", f"{_I}.vocab"),
        # Strings: resources.files() on the data package, and the package
        # the type registry scans (TYPES_PACKAGE).
        ("noncopy", f"{_I}.data"),
        ("typespec", f"{_I}.product_types"),
    }
)

PACKAGE_NAME = "synthetic_ecommerce_data"
CORE = f"{PACKAGE_NAME}.core"
INDUSTRIAL = f"{PACKAGE_NAME}.domains.industrial"


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


#: A string literal that is nothing but a dotted module path, as
#: ``resources.files`` and a package scan take one.
DOTTED = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")


def _is_module(name: str) -> bool:
    """Whether ``name`` is a module, rather than a name imported from one."""
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


def _reached(path: Path, package: str) -> set[str]:
    """Every module that ``path``, a module in ``package``, imports or names.

    A relative import is resolved by its level. ``from P import N`` reaches
    ``P.N`` when that is a module, else ``P`` itself, so a name imported from
    a domain package counts as reaching the package. A string literal that is
    a dotted path under :data:`PACKAGE_NAME` counts too.
    """
    reached: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.rsplit(".", node.level - 1)[0]
                source = f"{base}.{node.module}" if node.module else base
            else:
                source = node.module or ""
            for alias in node.names:
                full = f"{source}.{alias.name}"
                reached.add(full if _is_module(full) else source)
        elif isinstance(node, ast.Import):
            reached.update(alias.name for alias in node.names)
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and DOTTED.fullmatch(node.value)
            and node.value.startswith(f"{PACKAGE_NAME}.")
        ):
            reached.add(node.value)
    return reached


def _core_edges(core: Path) -> set[tuple[str, str]]:
    """``(core module, what it reaches outside core)``, for every module under ``core``.

    ``core`` is read as the package :data:`CORE`; a target is named relative
    to :data:`PACKAGE_NAME`.
    """
    edges = set()
    for path in sorted(core.rglob("*.py")):
        rel = path.relative_to(core).with_suffix("").parts
        is_package = rel[-1] == "__init__"
        inner = ".".join(rel[:-1] if is_package else rel)
        module = f"{CORE}.{inner}" if inner else CORE
        package = module if is_package else module.rpartition(".")[0]
        for name in _reached(path, package):
            inside = name == CORE or name.startswith(f"{CORE}.")
            if inside or not (name == PACKAGE_NAME or name.startswith(f"{PACKAGE_NAME}.")):
                continue
            edges.add((inner, name.removeprefix(f"{PACKAGE_NAME}.")))
    return edges


def test_core_reaches_outside_itself_only_through_the_listed_edges():
    assert _core_edges(PACKAGE / "core") == CORE_EDGES


def test_the_edge_scan_sees_every_way_core_can_reach_outside_itself(tmp_path):
    """Each plant is a way to depend on a domain that a prefix match misses."""
    core = tmp_path / "core"
    core.mkdir()
    plants = {
        # A relative import, and the domain package itself rather than a module in it.
        "relative": "from ..domains import industrial\n",
        # A name imported from the domain package, not a module.
        "package_level": "from synthetic_ecommerce_data.domains.industrial import SOMETHING\n",
        # Another domain than the industrial one.
        "other_domain": "import synthetic_ecommerce_data.domains.retail.catalog\n",
        # A module named in a string, as resources.files() and a package scan take it.
        "string": 'PACKAGE = "synthetic_ecommerce_data.domains.industrial.data"\n',
        # The application layer above core.
        "app": "from synthetic_ecommerce_data.prism import field_map\n",
        # Core importing core is no edge, by either spelling.
        "inside": "from . import noise\nfrom synthetic_ecommerce_data.core import emit\n",
    }
    for name, text in plants.items():
        (core / f"{name}.py").write_text(text, encoding="utf-8")
    assert _core_edges(core) == {
        ("relative", "domains.industrial"),
        ("package_level", "domains.industrial"),
        ("other_domain", "domains.retail.catalog"),
        ("string", "domains.industrial.data"),
        ("app", "prism.field_map"),
    }


def test_the_generate_command_composes_the_domains_outside_core():
    """``ecom-generate`` wires a domain to core, so it cannot live in core."""
    assert _is_module("synthetic_ecommerce_data.generate_cli")
    assert not (PACKAGE / "core" / "cli.py").exists()
    done = subprocess.run(
        [
            sys.executable,
            "-W",
            "ignore::DeprecationWarning",
            "-c",
            "import synthetic_industrial_products.catalog.cli as old\n"
            "print(old.__name__)\n",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.stdout.split() == ["synthetic_ecommerce_data.generate_cli"], done.stderr


def test_the_moved_generate_command_still_writes_the_tracked_field_map():
    """Moving ``core/cli.py`` up a level must not move the field map it writes.

    ``field_map_target`` climbs from its own file, so the climb shrinks by one
    when the module does; the default build then wrote outside ``src/``.
    """
    from synthetic_ecommerce_data.generate_cli import field_map_target

    src = PACKAGE.parent
    want = src / "prism_synthetic_industrial" / "data" / "field_weights"
    assert field_map_target() == want / "synthetic_industrial_flat.yaml"
    assert field_map_target().is_file()


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
