"""The 100K builds the tests read, built once and shared across xdist workers (#140).

A 100K catalog is about 1.9 GB resident (``/usr/bin/time -v`` on ``tests/test_price.py``,
which also holds the default build). Left to each module's fixture, every xdist worker
built its own, so ``-n 2`` held two, and on a busy host the swap watchdog killed workers.

Here a module asks for what it READS from a 100K build, not for the build:

* the build runs in at most ONE process at a time, whatever it is asked for: one lock
  for all of them, so two workers that both miss the file build one after the other,
  never together;
* only what the tests read is kept and written to a file, so the catalog is freed when
  the build returns and a worker that finds the file holds a few hundred MB, not 1.9 GB;
* the file is named by a digest of the generator's own source (``src/``, which holds
  every YAML and JSON table the build reads) and the dependency lock, of the code that
  reduces the build, and of this file. A changed generator reads a different name, so a
  stale file is never read, and the files of older digests are removed when a new one is
  written.

The files live in ``.pytest_cache/shared_builds``, which the repository already ignores
through pytest's own ``.gitignore`` there (and holds a ``.gitignore`` of its own).
``SHARED_BUILDS_DIR`` names another directory.
"""

from __future__ import annotations

import fcntl
import gc
import hashlib
import inspect
import os
import pickle
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data.core.config import LARGE_BUILD_LINES, GeneratorConfig
from synthetic_ecommerce_data.core.model import Attribute, Catalog
from synthetic_ecommerce_data.domains.industrial.generate import Generator, generate

REPO = Path(__file__).resolve().parents[1]

#: What the generator is made of: every file under ``src/`` and the dependency lock.
GENERATOR_INPUTS = [REPO / "src", REPO / "uv.lock"]

_LOCK = "build.lock"


def default_cache_dir() -> Path:
    named = os.environ.get("SHARED_BUILDS_DIR")
    return Path(named) if named else REPO / ".pytest_cache" / "shared_builds"


def inputs_digest(roots: list[Path] | None = None) -> str:
    """A digest of every file under ``roots`` (a file or a directory), by relative path."""
    digest = hashlib.sha256()
    for root in GENERATOR_INPUTS if roots is None else roots:
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in files:
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                digest.update(str(path.relative_to(root.parent)).encode())
                digest.update(b"\0")
                digest.update(path.read_bytes())
                digest.update(b"\0")
    return digest.hexdigest()


def _code_of(build: Callable[[], Any]) -> str:
    try:
        return inspect.getsource(build)
    except (OSError, TypeError):
        return build.__qualname__


@contextmanager
def _one_build_at_a_time(directory: Path) -> Iterator[None]:
    with (directory / _LOCK).open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _read(path: Path) -> Any | None:
    try:
        with path.open("rb") as handle:
            return pickle.load(handle)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return None


def cached(
    name: str,
    build: Callable[[], Any],
    *,
    roots: list[Path] | None = None,
    cache_dir: Path | None = None,
) -> Any:
    """What ``build()`` returns, read from the file of this name and digest when it exists.

    On a miss the caller takes the one build lock, looks again (another process may have
    written it while this one waited), and only then builds. ``build`` returns the small
    thing the tests read; the catalog it built is out of scope when it returns.
    """
    directory = cache_dir or default_cache_dir()
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ".gitignore").write_text("*\n", encoding="utf-8")
    # pytest writes the ``.gitignore`` of ``.pytest_cache`` only when it makes the directory
    # itself; one made here first would show as untracked in ``git status``.
    if directory.parent.name == ".pytest_cache":
        ignore = directory.parent / ".gitignore"
        if not ignore.exists():
            ignore.write_text(
                "# Created by shared_builds.py, as pytest would.\n*\n", encoding="utf-8"
            )
    digest = hashlib.sha256(
        (inputs_digest(roots) + _code_of(build) + Path(__file__).read_text("utf-8")).encode()
    ).hexdigest()[:20]
    path = directory / f"{name}-{digest}.pickle"
    found = _read(path)
    if found is not None:
        return found[0]
    with _one_build_at_a_time(directory):
        found = _read(path)
        if found is not None:
            return found[0]
        value = build()
        gc.collect()
        fd, temp = tempfile.mkstemp(dir=directory, prefix=f"{name}-", suffix=".part")
        with os.fdopen(fd, "wb") as handle:
            pickle.dump((value,), handle, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(temp, path)
        for old in directory.glob(f"{name}-*.pickle"):
            if old != path:
                old.unlink(missing_ok=True)
    return value


# --- the builds, and what each reduces to --------------------------------------------

KIT = "kit_assortment"

#: One kit SKU as its price was drawn: its shown price, the facts it was drawn from, and
#: its brand.
KitSku = tuple[float, dict[str, Attribute], str]


def recorded_build(config: GeneratorConfig) -> tuple[Catalog, list[KitSku]]:
    """A build, and each kit SKU with the facts its price was drawn from.
    Those are read as the draw reads them, not off the published record:
    sparsity may drop a kit's ``Material`` or ``Sizes Included``, and never
    moves its price."""
    drawn: dict[str, tuple[dict[str, Attribute], str]] = {}
    original = Generator._price_draw

    def recording(self, type_key, brand, attributes, line_attributes, sku, sku_u):
        if type_key == KIT:
            drawn[sku] = ({a.name: a for a in attributes}, brand)
        return original(self, type_key, brand, attributes, line_attributes, sku, sku_u)

    Generator._price_draw = recording  # type: ignore[method-assign]
    try:
        catalog = generate(config)
    finally:
        Generator._price_draw = original  # type: ignore[method-assign]
    shown = {child.sku: child.price_usd for _, child in catalog.all_skus()}
    kits = [(shown[sku], *drawn[sku]) for sku in sorted(drawn) if sku in shown]
    return catalog, kits


def realistic_only(docs: list[dict]) -> list[dict]:
    """The documents a catalog has apart from its ``fast_and_cheap`` ones."""
    return [doc for doc in docs if doc.get("spec_quality") != "fast_and_cheap"]


def _hundred_k_prices_build() -> tuple[dict, list[KitSku]]:
    from synthetic_ecommerce_data.domains.industrial import price_report

    catalog, kits = recorded_build(GeneratorConfig(lines=LARGE_BUILD_LINES))
    return {row.name: row for row in price_report.price_comparisons(catalog)}, kits


def hundred_k_prices() -> tuple[dict, list[KitSku]]:
    """The 100K build's price rows by name, and its kit SKUs: all that the price tests read."""
    return cached("hundred_k_prices", _hundred_k_prices_build)


WHEEL = "wheel_depressed_center"


def _hundred_k_quiet_wheel_build() -> tuple[Any, dict[tuple, tuple[str, ...]]]:
    from dataclasses import replace
    from unittest import mock

    from synthetic_ecommerce_data.core import price
    from synthetic_ecommerce_data.domains.industrial import price_report

    quiet = replace(price.MODELS[WHEEL], group_sigma=0.0, sku_sigma=0.0, size_sigma=0.0)
    with mock.patch.dict(price.MODELS, {WHEEL: quiet}):
        catalog = generate(GeneratorConfig(lines=LARGE_BUILD_LINES))
        (row,) = [
            row
            for row in price_report.price_comparisons(catalog)
            if row.name == price_report.BRAND_ROW.format(WHEEL)
        ]
        specs = {
            spec: tuple(sorted(by))
            for spec, by in price_report.collect(catalog).specs.items()
            if spec[0] == WHEEL and len(by) > 1
        }
    return row, specs


def hundred_k_quiet_wheel() -> tuple[Any, dict[tuple, tuple[str, ...]]]:
    """The wheel's brand-spread row of a 100K build whose wheel prices carry no noise, and the
    brands of each wheel spec two or more brands make: all that the wheel pin test reads."""
    return cached("hundred_k_quiet_wheel", _hundred_k_quiet_wheel_build)


def _hundred_k_flat_build() -> list[dict]:
    from synthetic_ecommerce_data.core import emit

    return realistic_only(list(emit.iter_flat(generate(GeneratorConfig(lines=LARGE_BUILD_LINES)))))


def hundred_k_flat() -> list[dict]:
    """The 100K build's realistic flat documents, as the brand-voice tests read them."""
    return cached("hundred_k_flat", _hundred_k_flat_build)
