"""The drawing registry is read only through ``kit.shapes()``, which fills it first (#1039).

``kit.SHAPES`` is filled as each ``kit_*`` module is imported, so a direct read answers with
whatever this interpreter imported first: a CI worker's test files decide it, and main went red
when ``wine_bottle`` was missing on one worker (#1142). ``kit.shapes()`` runs ``register_all()``
before it answers; the lint below refuses a direct read anywhere but ``kit.py``.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = "synthetic_ecommerce_data.domains.retail.kit"
#: The registry's own module: it defines ``SHAPES`` and the accessors that read it.
OWNER = ROOT / "src" / "synthetic_ecommerce_data" / "domains" / "retail" / "kit.py"
SCANNED = ("src", "tests", "scripts")


def _package(path: str) -> list[str]:
    """The dotted package a file under ``src/`` sits in (empty for a test or a script)."""
    parts = Path(path).parts
    return list(parts[parts.index("src") + 1 : -1]) if "src" in parts else []


def _imported(node: ast.ImportFrom, path: str) -> str:
    """The absolute module an ``ImportFrom`` names, a relative one resolved from ``path``."""
    if not node.level:
        return node.module or ""
    package = _package(path)
    base = package[: len(package) - node.level + 1]
    return ".".join([*base, *([node.module] if node.module else [])])


def direct_reads(source: str, path: str) -> list[str]:
    """Each ``path:line`` of ``source`` that reads ``kit.SHAPES`` without ``kit.shapes()``."""
    tree = ast.parse(source)
    names = {KIT}
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.asname for a in node.names if a.name == KIT and a.asname}
        elif isinstance(node, ast.ImportFrom):
            module = _imported(node, path)
            if module == KIT and any(a.name == "SHAPES" for a in node.names):
                found.append(f"{path}:{node.lineno}: imports kit.SHAPES")
            if f"{module}.kit" == KIT:
                names |= {a.asname or a.name for a in node.names if a.name == "kit"}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "SHAPES"
            and ast.unparse(node.value) in names
        ):
            found.append(f"{path}:{node.lineno}: reads kit.SHAPES")
    return sorted(found)


def _fresh(code: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)


def test_no_module_reads_kit_shapes_directly() -> None:
    files = [p for d in SCANNED for p in sorted((ROOT / d).rglob("*.py")) if p != OWNER]
    found = [r for p in files for r in direct_reads(p.read_text(), str(p.relative_to(ROOT)))]
    assert found == []


def test_the_lint_names_an_injected_direct_read() -> None:
    source = (
        "from synthetic_ecommerce_data.domains.retail import kit as k\n"
        "from synthetic_ecommerce_data.domains.retail.kit import SHAPES, Fill\n"
        "drawn = 'wine_bottle' in k.SHAPES\n"
        "fine = 'wine_bottle' in k.shapes()\n"
    )
    assert direct_reads(source, "tests/test_x.py") == [
        "tests/test_x.py:2: imports kit.SHAPES",
        "tests/test_x.py:3: reads kit.SHAPES",
    ]


def test_the_lint_resolves_a_relative_import_to_its_own_kit() -> None:
    """``from .kit import SHAPES`` in the retail package is the registry; in ``orientations/``
    it names that package's own ``kit`` module, which is not."""
    source = "from .kit import SHAPES\n"
    retail = "src/synthetic_ecommerce_data/domains/retail/kit_x.py"
    other = "src/synthetic_ecommerce_data/domains/retail/orientations/x.py"
    assert direct_reads(source, retail) == [f"{retail}:1: imports kit.SHAPES"]
    assert direct_reads(source, other) == []


def test_shapes_holds_a_shape_whose_module_was_never_imported() -> None:
    run = _fresh(
        "import sys\n"
        "from synthetic_ecommerce_data.domains.retail import kit\n"
        "early = sorted(m for m in sys.modules if m.endswith('.kit_drinks'))\n"
        "print(early, 'wine_bottle' in kit.shapes())\n"
    )
    assert (run.returncode, run.stdout.strip()) == (0, "[] True"), run.stderr[-2000:]


def test_a_motif_resolves_whatever_was_imported_first() -> None:
    run = _fresh(
        "import sys\n"
        "from synthetic_ecommerce_data.domains.retail import motifs\n"
        "early = sorted(m for m in sys.modules if m.endswith('.kit_drinks'))\n"
        "print(early, motifs.motif('wine_bottle').name)\n"
    )
    assert (run.returncode, run.stdout.strip()) == (0, "[] wine_bottle"), run.stderr[-2000:]
