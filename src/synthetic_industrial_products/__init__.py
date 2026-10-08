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


def new_name(fullname: str) -> str:
    """The module that the pre-rename ``fullname`` now lives at."""
    return NEW + fullname[len(OLD) :]


class _Alias(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Resolve ``synthetic_industrial_products.X`` to the module ``synthetic_ecommerce_data.X``."""

    def find_spec(self, fullname: str, path: Any = None, target: Any = None):
        if not fullname.startswith(OLD + "."):
            return None
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
    from synthetic_ecommerce_data.catalog.cli import main  # noqa: PLC0415

    _deprecated_command("sip-generate", "ecom-generate")
    return main(argv)


def sip_render(argv: list[str] | None = None) -> int:
    """The pre-rename ``sip-render``: ``ecom-render`` with a deprecation note."""
    from synthetic_ecommerce_data.cli import main  # noqa: PLC0415

    _deprecated_command("sip-render", "ecom-render")
    return main(argv)
