"""``drawing/`` is the one way to draw a product; the text renderer is gone (#27).

The catalog's drawings are the text-free per-SKU SVGs in
``domains/industrial/drawing``. ``render/`` was the matplotlib renderer that put
specification tables, stamps and callouts into a picture -- text the maintainer
ruled out of every drawing -- and ``sip-render batch`` still produced such
images for anyone to publish. What the two shared was geometry, and that now
lives in ``domains/industrial/geometry``, which draws nothing.

These checks read the source rather than run the renderer, because the thing to
prove is an absence: nothing left that can draw text, and nothing that
silently grows back.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "synthetic_ecommerce_data"
INDUSTRIAL = "synthetic_ecommerce_data.domains.industrial"
INDUSTRIAL_DIR = SRC / "domains" / "industrial"
GEOMETRY = SRC / "domains" / "industrial" / "geometry"
GEOMETRY_MODULES = ("attrs", "drill", "endmill", "fastener", "flapdisc", "palette", "tap", "washer")


def _imports(path: Path) -> set[str]:
    """Every module name a file imports, as dotted names (``from a.b import c`` gives ``a.b.c``)."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def _py(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_there_is_no_render_package():
    assert not (SRC / "domains" / "industrial" / "render").exists()


def test_no_console_script_renders_a_record():
    scripts = _pyproject()["project"]["scripts"]
    assert not {"sip-render", "ecom-render"} & set(scripts), scripts
    assert not [name for name, target in scripts.items() if "render" in target], scripts
    assert not (SRC / "cli.py").exists()


def test_the_geometry_package_exists_and_draws_nothing():
    missing = [m for m in GEOMETRY_MODULES if not (GEOMETRY / f"{m}.py").is_file()]
    assert missing == [], f"geometry/ lacks {missing}"
    for path in _py(GEOMETRY):
        banned = sorted(
            name
            for name in _imports(path)
            if name.split(".")[0] in {"matplotlib", "numpy", "PIL"}
            or ".render" in name
            or name.endswith(".canvas")
            or ".drawing" in name
        )
        assert banned == [], f"{path.name} imports a drawing dependency: {banned}"


def test_nothing_in_src_imports_matplotlib_or_the_render_package():
    offenders = {}
    for path in _py(ROOT / "src"):
        bad = sorted(
            name
            for name in _imports(path)
            if name.split(".")[0] == "matplotlib"
            or name.endswith(".industrial.render")
            or ".industrial.render." in name
        )
        if bad:
            offenders[str(path.relative_to(ROOT))] = bad
    assert offenders == {}


def test_matplotlib_is_not_a_dependency():
    dependencies = _pyproject()["project"]["dependencies"]
    assert not [d for d in dependencies if d.lower().startswith("matplotlib")], dependencies


def test_the_catalog_has_no_render_output():
    assert not (ROOT / "golden-catalog" / "render.jsonl").exists()
    for relative in ("generate_cli.py", "core/emit.py"):
        source = (SRC / relative).read_text(encoding="utf-8")
        assert "render.jsonl" not in source, relative
        assert "render_records" not in source, relative


def test_records_hold_only_the_observed_records():
    # Read the source: importing the package would pull in the renderer's
    # matplotlib at the commit before the fix, and a test must fail on an
    # assertion there, not on an import error.
    tree = ast.parse((INDUSTRIAL_DIR / "records.py").read_text(encoding="utf-8"))
    assigned = {}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned[node.target.id] = node.value
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned[target.id] = node.value
    for retired in ("BUNDLED", "GENERATED", "NO_IMAGE", "DRAWABLE"):
        assert retired not in assigned, retired
    assert isinstance(assigned["FIXTURES"], ast.Dict)
    assert len(assigned["FIXTURES"].keys) == 5


DRAWING_MODULES = [
    "figures",
    "primitives",
    "compose",
    "brand_marks",
    "breadth_shapes",
    "found_shapes",
]


@pytest.mark.parametrize("module", DRAWING_MODULES)
def test_drawing_reaches_geometry_not_the_renderer(module):
    path = SRC / "domains" / "industrial" / "drawing" / f"{module}.py"
    assert [n for n in _imports(path) if ".industrial.render" in n] == []
