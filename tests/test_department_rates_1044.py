"""A department's derived-style rate is a module in ``department_rates/`` (gen#1044).

The rates were one ``DEPARTMENT_RATE`` table in ``scale.py``, and 8 PRs in 7 days conflicted on it,
since each PR that adds product types recomputes one department's rate. The move is mechanical: the
first test pins the table the build reads to the one before the move, value for value; the rest
hold the package contract with a probe package planted in a throwaway directory.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest

from synthetic_ecommerce_data.domains.retail import department_rates, scale

#: ``scale.DEPARTMENT_RATE`` on main 2084601b, before the move.
BEFORE = {
    "Clothing": 0.0124, "Lingerie & Nightwear": 0.003558, "Home": 0.00835,
    "Beauty": 0.01665, "Food & Drink": 0.006468, "Toys": 0.005199,
    "Cleaning & Janitorial": 0.007275, "Gifts": 0.0048, "Garden": 0.01059,
    "Footwear": 0.01799,
}  # fmt: skip


def test_the_rates_the_build_reads_are_the_table_before_the_move() -> None:
    assert scale.DEPARTMENT_RATE == BEFORE
    assert scale.DEFAULT_RATE == 0.008


def test_scale_holds_no_department_rate_literal() -> None:
    text = Path(scale.__file__).read_text()
    assert "DEPARTMENT_RATE = department_rates.rates()" in text
    for department, rate in BEFORE.items():
        assert f'"{department}": {rate}' not in text, department


def test_each_module_names_one_department_and_its_docstring_says_why() -> None:
    for module in department_rates.modules():
        assert (module.__doc__ or "").strip(), module.__name__
        assert module.DEPARTMENT in BEFORE, module.__name__


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
