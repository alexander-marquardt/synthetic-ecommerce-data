"""A department's derived-style rate is a module in ``department_rates/`` (gen#1044).

The rates were one ``DEPARTMENT_RATE`` table in ``scale.py``, and 8 PRs in 7 days conflicted on it,
since each PR that adds product types recomputes one department's rate. No test here names a
rate: a pin of every value would put the conflict point back in this file. The tests hold that
``scale.py`` reads its table from the package and binds no table of its own, and the package
contract, with a probe package planted in a throwaway directory. The same holds for each
department's fixed share and invented brands (``SHARE`` and ``EXTRA_BRANDS``, slice 3), which
``scale.DEPARTMENT_SHARE`` and ``scale.EXTRA_BRANDS`` are built from.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest

from synthetic_ecommerce_data.domains.retail import department_rates, departments, scale


def test_scale_reads_the_table_the_package_builds() -> None:
    assert department_rates.rates() == scale.DEPARTMENT_RATE
    assert scale.DEFAULT_RATE == 0.008


def test_scale_reads_the_shares_and_the_brands_the_package_builds() -> None:
    assert department_rates.shares() == scale.DEPARTMENT_SHARE
    assert department_rates.extra_brands() == scale.EXTRA_BRANDS


def _names(node: ast.AST, table: str) -> bool:
    return isinstance(node, ast.Name) and node.id == table


_TABLES = [("DEPARTMENT_SHARE", "shares"), ("EXTRA_BRANDS", "extra_brands")]
_MUTATORS = {
    "update",
    "setdefault",
    "pop",
    "popitem",
    "clear",
    "__setitem__",
    "__delitem__",
    "__ior__",
}


def _package_table_writes(tree: ast.AST, table: str, builder: str) -> list[str]:
    """Each place ``tree`` binds or changes ``table`` other than its one
    ``table = department_rates.<builder>()``; a missing or repeated call is one too."""
    call = f"{table} = department_rates.{builder}()"
    writes, calls = [], 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if _names(target, table):
                    if ast.unparse(node) == call:
                        calls += 1
                    else:
                        writes.append(f"line {node.lineno}: {ast.unparse(node)}")
                elif isinstance(target, ast.Subscript) and _names(target.value, table):
                    writes.append(f"line {node.lineno}: {table}[...] assigned")
        elif isinstance(node, ast.Delete):
            writes += [
                f"line {node.lineno}: del {table}[...]"
                for t in node.targets
                if isinstance(t, ast.Subscript) and _names(t.value, table)
            ]
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and _names(node.func.value, table)
            and node.func.attr in _MUTATORS
        ):
            writes.append(f"line {node.lineno}: {table}.{node.func.attr}(...)")
    if calls != 1:
        writes.append(f"{call} appears {calls} times, not once")
    return writes


@pytest.mark.parametrize(("table", "builder"), _TABLES)
def test_scale_binds_the_shares_and_the_brands_only_to_the_package_call(
    table: str, builder: str
) -> None:
    tree = ast.parse(Path(scale.__file__).read_text())
    assert _package_table_writes(tree, table, builder) == []


@pytest.mark.parametrize(("table", "builder"), _TABLES)
@pytest.mark.parametrize(
    "source",
    [
        '{t} = {{"Pets": 0.05}}\n',
        "{t}: dict = {{}}\n",
        "{t} = department_rates.{b}()\n{t} = dict({t})\n",
        "{t} = department_rates.{b}()\n{t} = department_rates.{b}()\n",
        "import x\n{t} = x.{b}()\n",
        "PLACEHOLDER = 1\n",
        '{t} = department_rates.{b}()\n{t}["Pets"] = 0.05\n',
        '{t} = department_rates.{b}()\n{t}.update({{"Pets": 0.05}})\n',
        '{t} = department_rates.{b}()\n{t}.setdefault("Pets", 0.05)\n',
        '{t} = department_rates.{b}()\n{t} |= {{"Pets": 0.05}}\n',
        '{t} = department_rates.{b}()\ndel {t}["Home"]\n',
        '{t} = department_rates.{b}()\n{t}.pop("Home")\n',
    ],
)
def test_a_share_or_brand_table_put_back_in_scale_is_seen(
    table: str, builder: str, source: str
) -> None:
    tree = ast.parse(source.format(t=table, b=builder))
    assert _package_table_writes(tree, table, builder)


@pytest.mark.parametrize(("table", "builder"), _TABLES)
def test_the_one_package_call_is_not_a_write(table: str, builder: str) -> None:
    source = f"{table} = department_rates.{builder}()\nx = {table}.get('Home')\n"
    assert _package_table_writes(ast.parse(source), table, builder) == []


def _is_rates_call(node: ast.expr | None) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "rates"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "department_rates"
    )


def _names_table(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "DEPARTMENT_RATE"


def _table_writes(tree: ast.AST) -> list[str]:
    """Each place ``tree`` binds or changes ``DEPARTMENT_RATE`` other than by a rates() call."""
    writes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if _names_table(target) and not (
                    not isinstance(node, ast.AugAssign) and _is_rates_call(node.value)
                ):
                    writes.append(f"line {node.lineno}: DEPARTMENT_RATE bound to a non-call")
                if isinstance(target, ast.Subscript) and _names_table(target.value):
                    writes.append(f"line {node.lineno}: DEPARTMENT_RATE[...] assigned")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and _names_table(node.func.value)
            and node.func.attr in {"update", "setdefault", "__setitem__", "__ior__"}
        ):
            writes.append(f"line {node.lineno}: DEPARTMENT_RATE.{node.func.attr}(...)")
    return writes


def test_scale_binds_department_rate_only_to_the_package_call() -> None:
    tree = ast.parse(Path(scale.__file__).read_text())
    binds = [
        node
        for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(
            _names_table(t)
            for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
        )
    ]
    assert len(binds) == 1, [b.lineno for b in binds]
    assert _is_rates_call(binds[0].value), ast.unparse(binds[0])
    assert _table_writes(tree) == []


@pytest.mark.parametrize(
    "source",
    [
        'DEPARTMENT_RATE = {"Pets": 0.004}\n',
        'DEPARTMENT_RATE = department_rates.rates()\nDEPARTMENT_RATE = {"Home": 8.35e-3}\n',
        "DEPARTMENT_RATE: dict[str, float] = dict(Home=0.009)\n",
        'DEPARTMENT_RATE = department_rates.rates()\nDEPARTMENT_RATE["Electronics"] = 0.002\n',
        'DEPARTMENT_RATE = department_rates.rates()\nDEPARTMENT_RATE.update({"Toys": 0.006})\n',
        'DEPARTMENT_RATE = department_rates.rates()\nDEPARTMENT_RATE |= {"Gifts": 0.005}\n',
    ],
)
def test_a_table_put_back_in_scale_is_seen(source: str) -> None:
    assert _table_writes(ast.parse(source))


def test_each_module_names_one_department_and_its_docstring_says_why() -> None:
    for module in department_rates.modules():
        assert (module.__doc__ or "").strip(), module.__name__
        assert module.DEPARTMENT in departments.DEPARTMENTS, module.__name__


def _probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, files: dict[str, str]) -> ModuleType:
    """A fresh copy of the package whose path is a throwaway directory holding ``files``."""
    root = tmp_path / "probe_rates"
    root.mkdir()
    (root / "__init__.py").write_text(Path(department_rates.__file__).read_text())
    for name, body in files.items():
        (root / f"{name}.py").write_text(body)
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in [n for n in sys.modules if n == "probe_rates" or n.startswith("probe_rates.")]:
        monkeypatch.delitem(sys.modules, name)
    importlib.invalidate_caches()
    return importlib.import_module("probe_rates")


def test_a_new_department_is_one_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pkg = _probe(tmp_path, monkeypatch, {
        "pets": 'DEPARTMENT = "Pets"\nRATE = 0.004\n',
        "home": 'DEPARTMENT = "Home"\nRATE = 0.00835\n',
    })  # fmt: skip
    assert pkg.rates() == {"Home": 0.00835, "Pets": 0.004}


@pytest.mark.parametrize(
    ("body", "refusal"),
    [
        ("RATE = 0.004\n", "has no DEPARTMENT"),
        ('DEPARTMENT = ""\nRATE = 0.004\n', "has no DEPARTMENT"),
        ('DEPARTMENT = "Pets"\n', "is not a positive number"),
        ('DEPARTMENT = "Pets"\nRATE = 0\n', "is not a positive number"),
        ('DEPARTMENT = "Pets"\nRATE = -0.1\n', "is not a positive number"),
        ('DEPARTMENT = "Pets"\nRATE = "0.004"\n', "is not a positive number"),
        ('DEPARTMENT = "Pets"\nRATE = True\n', "is not a positive number"),
    ],
)
def test_a_malformed_module_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str, refusal: str
) -> None:
    pkg = _probe(tmp_path, monkeypatch, {"pets": body})
    with pytest.raises(ValueError, match=refusal):
        pkg.rates()


def test_a_department_named_twice_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pkg = _probe(tmp_path, monkeypatch, {
        "home": 'DEPARTMENT = "Home"\nRATE = 0.00835\n',
        "home_again": 'DEPARTMENT = "Home"\nRATE = 0.009\n',
    })  # fmt: skip
    refusal = "'Home' of probe_rates.home_again is also in probe_rates.home"
    with pytest.raises(ValueError, match=refusal):
        pkg.rates()


def test_a_new_department_with_a_share_and_brands_is_one_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pkg = _probe(tmp_path, monkeypatch, {
        "pets": 'DEPARTMENT = "Pets"\nRATE = 0.004\nSHARE = 0.05\nEXTRA_BRANDS = ("Kibblewick",)\n',
        "home": 'DEPARTMENT = "Home"\nRATE = 0.00835\nSHARE = 0.20\n',
        "toys": 'DEPARTMENT = "Toys"\nRATE = 0.005\n',
    })  # fmt: skip
    assert pkg.shares() == {"Home": 0.20, "Pets": 0.05}
    assert pkg.extra_brands() == {"Pets": ("Kibblewick",)}


@pytest.mark.parametrize(
    ("bodies", "builder", "refusal"),
    [
        (["SHARE = 0"], "shares", "is not a number in"),
        (["SHARE = 1"], "shares", "is not a number in"),
        (['SHARE = "0.1"'], "shares", "is not a number in"),
        (["SHARE = True"], "shares", "is not a number in"),
        (["SHARE = 0.6", "SHARE = 0.4"], "shares", "the shares sum to 1"),
        (["EXTRA_BRANDS = ()"], "extra_brands", "is not a tuple of brand names"),
        (['EXTRA_BRANDS = "Kibblewick"'], "extra_brands", "is not a tuple of brand names"),
        (['EXTRA_BRANDS = ["Kibblewick"]'], "extra_brands", "is not a tuple of brand names"),
        (['EXTRA_BRANDS = ("Kibblewick", "")'], "extra_brands", "is not a tuple of brand names"),
        (["RATE = 0"], "shares", "is not a positive number"),
        (["RATE = 0"], "extra_brands", "is not a positive number"),
    ],
)
def test_a_malformed_share_or_brand_list_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bodies: list[str], builder: str, refusal: str
) -> None:
    files = {
        f"dept{i}": f'DEPARTMENT = "Dept {i}"\nRATE = 0.004\n{body}\n'
        for i, body in enumerate(bodies)
    }
    pkg = _probe(tmp_path, monkeypatch, files)
    with pytest.raises(ValueError, match=refusal):
        getattr(pkg, builder)()
