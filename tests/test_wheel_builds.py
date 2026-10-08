"""This repo must be installable as a WHEEL, not only as an editable checkout.

``uv sync`` and ``uv pip install -e .`` -- the two installs the README
documents -- never build a wheel. So for as long as those were the only ways
anybody installed this repo, the wheel build was unexercised, and it was
broken: ``[tool.hatch.build.targets.wheel.force-include]`` re-declared
``src/prism_synthetic_industrial/data``, which the ``packages`` entry already
ships, and hatchling refuses to add the same archive path twice::

    ValueError: A second file is being added to the wheel archive at the same
    path: `prism_synthetic_industrial/data/customization.yaml`

The failure is invisible from inside this repo and total from outside it: a
consumer depending on ``synthetic-ecommerce-data @ git+https://...@<sha>``
cannot install the package at all.

The build runs through hatchling's own builder rather than ``python -m build``
so it needs no network and no isolated environment -- the same backend
``pyproject.toml`` declares, driven in-process.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: Files that MUST be inside the wheel. The customization is nothing but data,
#: so a wheel that builds and drops them is no better than one that refuses.
REQUIRED_MEMBERS = (
    "prism_synthetic_industrial/data/customization.yaml",
    "prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml",
    "synthetic_ecommerce_data/core/emit.py",
    "synthetic_ecommerce_data/prism/derive.py",
)


@pytest.fixture(scope="module")
def wheel(tmp_path_factory) -> Path:
    builder = pytest.importorskip(
        "hatchling.builders.wheel",
        reason="hatchling is in the dev group; install it to run the wheel gate",
    )
    out = tmp_path_factory.mktemp("wheel")
    built = next(builder.WheelBuilder(str(ROOT)).build(directory=str(out), versions=["standard"]))
    return Path(built)


def test_the_wheel_builds_at_all(wheel: Path) -> None:
    """Reds on the duplicate-path ValueError that made this repo uninstallable."""
    assert wheel.exists() and wheel.suffix == ".whl", wheel


def test_the_wheel_carries_both_packages_and_the_customization_data(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        members = set(archive.namelist())
    missing = sorted(name for name in REQUIRED_MEMBERS if name not in members)
    assert not missing, (
        f"the wheel builds but omits {missing}. PRISM reads the customization from "
        f"these files; a wheel without them installs a package it cannot load."
    )


def test_no_archive_path_is_written_twice(wheel: Path) -> None:
    """The property the duplicate declaration violated, stated directly.

    hatchling happens to raise on it today. Asserting the property rather than
    the exception means a future backend that silently kept the last writer
    would still be caught here.
    """
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    duplicates = sorted({name for name in names if names.count(name) > 1})
    assert not duplicates, f"the wheel writes these paths more than once: {duplicates}"
