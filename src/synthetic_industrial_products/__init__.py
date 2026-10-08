"""Deprecated: this generator is now ``synthetic_ecommerce_data`` (#125).

The package was renamed so that it can hold more than the industrial catalog.
This alias keeps every pre-rename import path working for ONE release cycle,
so that a downstream pin can move on its own schedule, and is removed after
it. Import ``synthetic_ecommerce_data`` instead; the module paths under it are
the same.

``synthetic_industrial_products.<path>`` is not a copy: it IS the module
``synthetic_ecommerce_data.<path>``, the same object, so state set or patched
through either name is seen through both. Importing this package warns once
with a :class:`DeprecationWarning`.

``sip_generate`` and ``sip_render`` are the old ``sip-generate`` and
``sip-render`` commands: each prints a deprecation note on stderr and then
runs ``ecom-generate`` or ``ecom-render`` with the same arguments.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys
import warnings
from types import ModuleType
from typing import Any

import synthetic_ecommerce_data

OLD = __name__
NEW = synthetic_ecommerce_data.__name__

warnings.warn(
    f"{OLD} is deprecated and will be removed in the next release; import {NEW} instead",
    DeprecationWarning,
    stacklevel=2,
)

#: No file lookups under the alias: every submodule comes from the finder below.
__path__: list[str] = []


_CORE = (
    "brands bundle cli config emit entry formats model naming noise noncopy price typespec voice"
)
_INDUSTRIAL = (
    "breadth compat conformance generate measure muststock names newtypes price_report "
    "series standards tabletype taxonomy vocab"
)

#: Where each pre-rename module path went when the core was extracted (#125
#: step 2), by longest prefix; a path not listed kept its place.
MOVED: dict[str, str] = {
    **{f"catalog.{name}": f"core.{name}" for name in _CORE.split()},
    **{f"catalog.{name}": f"domains.industrial.{name}" for name in _INDUSTRIAL.split()},
    "dimensions": "core.dimensions",
    "records": "domains.industrial.records",
    "render": "domains.industrial.render",
    "product_types": "domains.industrial.product_types",
    "data": "domains.industrial.data",
    "drawing.figures": "domains.industrial.drawing.figures",
    "drawing.breadth_shapes": "domains.industrial.drawing.breadth_shapes",
    "drawing": "core.drawing",
}

#: Old packages that no longer exist as one package: an empty stand-in holds
#: their submodules, each of which resolves through :data:`MOVED`.
DISSOLVED = frozenset({"catalog"})


def new_name(fullname: str) -> str:
    """The module that the pre-rename ``fullname`` now lives at."""
    parts = fullname[len(OLD) + 1 :].split(".")
    for n in range(len(parts), 0, -1):
        head = ".".join(parts[:n])
        if head in MOVED:
            return ".".join([NEW, MOVED[head], *parts[n:]])
    return ".".join([NEW, *parts])


class _Alias(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Resolve ``synthetic_industrial_products.X`` to the module that X is now."""

    def find_spec(self, fullname: str, path: Any = None, target: Any = None):
        if not fullname.startswith(OLD + "."):
            return None
        if fullname[len(OLD) + 1 :] in DISSOLVED:
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        real = importlib.util.find_spec(new_name(fullname))
        if real is None:
            return None
        return importlib.machinery.ModuleSpec(
            fullname, self, is_package=real.submodule_search_locations is not None
        )

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        """The real module, its own spec parked on the alias spec.

        The import system sets ``__spec__`` on whatever this returns, which
        would leave the real module naming the alias, with this class as its
        loader: ``resources.files`` would then fail on its data and
        ``importlib.reload`` would run nothing. ``exec_module`` puts the real
        spec back.
        """
        if spec.name[len(OLD) + 1 :] in DISSOLVED:
            stand_in = ModuleType(spec.name)
            stand_in.__path__ = []
            return stand_in
        module = importlib.import_module(new_name(spec.name))
        spec.loader_state = module.__spec__
        return module

    def exec_module(self, module: ModuleType) -> None:
        """Nothing to run, only the real ``__spec__`` to restore (see ``create_module``)."""
        real = getattr(module.__spec__, "loader_state", None)
        if isinstance(real, importlib.machinery.ModuleSpec):
            module.__spec__ = real


if not any(isinstance(finder, _Alias) for finder in sys.meta_path):
    sys.meta_path.insert(0, _Alias())


def __getattr__(name: str) -> Any:
    return getattr(synthetic_ecommerce_data, name)


def _deprecated_command(old: str, new: str) -> None:
    print(
        f"{old} is deprecated; use {new}, the same command under the generator's new "
        "name (#125). This alias is removed in the next release.",
        file=sys.stderr,
    )


def sip_generate(argv: list[str] | None = None) -> int:
    """The pre-rename ``sip-generate``: ``ecom-generate`` with a deprecation note."""
    from synthetic_ecommerce_data.core.cli import main  # noqa: PLC0415

    _deprecated_command("sip-generate", "ecom-generate")
    return main(argv)


def sip_render(argv: list[str] | None = None) -> int:
    """The pre-rename ``sip-render``: ``ecom-render`` with a deprecation note."""
    from synthetic_ecommerce_data.cli import main  # noqa: PLC0415

    _deprecated_command("sip-render", "ecom-render")
    return main(argv)
