"""One module per numbered family of the line grammar, found by walking this package (gen#513).

``line_grammar.py`` was a registry: a feature that gave a new family of kinds its model names
added a ``FAMILIES`` row, a vocabulary constant and a ``fam == ...`` branch there, so the four
open PRs of 2026-10-25 (synth#671 to #674) conflicted in all 6 pairs. A family whose model is a
lead word, an optional sub-model and a number or a code ("Tempo Pro 3") is now a module here,
``line_grammar_families/<family>.py``, which exposes:

``KINDS``
    The product types of the family. A type another module or a core family of
    :mod:`line_grammar` already holds is refused.
``LEADS``
    The lead words of a model, each dealt to one brand (gen#642). A word another module holds,
    or a name-like word of the dress shoes, is refused: a lead word that reads as a brand
    without its brand in front is what the grammar exists to avoid.
``SUBS``
    The sub-model words that may follow the lead (optional).
``NUMBERS``
    The generations a model is in: a model ends in one of them, or in a code.
``GROCERY_LEADS``
    A second lead half (optional): the grocery build deals it, the scale build deals ``LEADS``,
    so one word belongs to one brand across both builds (gen#642, gen#665). Checked like ``LEADS``.
``BARE``
    True when the lead word alone is a model (optional, gen#665).
``MIXED_BRAND``
    True when a title leads with its brand in two of three draws, not always (optional, gen#665).

The module name is the family's name. Modules are read in the order of their names; a file here
that lacks ``KINDS``, ``LEADS`` or ``NUMBERS`` is refused, because a file the grammar would skip is
a defect nobody sees. A family with its own model shape (dress shoes, appliances) stays in
:mod:`line_grammar`. ``tests/test_line_grammar_families_513.py`` holds the contract, and
``scripts/check_no_registry_append.py`` refuses a line appended to ``line_grammar.py``.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable
from typing import NamedTuple

__all__ = ["Family", "families"]


class Family(NamedTuple):
    name: str
    kinds: tuple[str, ...]
    leads: tuple[str, ...]
    subs: tuple[str, ...]
    numbers: tuple[int, ...]
    grocery_leads: tuple[str, ...] = ()
    bare: bool = False
    mixed_brand: bool = False


def families(core_kinds: Iterable[str] = (), reserved: Iterable[str] = ()) -> dict[str, Family]:
    """Every family of the package by name, in the order of the module names.

    ``core_kinds`` are the product types the core families already hold and ``reserved`` the
    words no family may lead a model with; a module that claims either, or claims a kind or a
    lead word another module holds, is refused with the names of both."""
    taken_kinds = {kind: "a core family of line_grammar" for kind in core_kinds}
    banned = set(reserved)
    lead_owner: dict[str, str] = {}
    found: dict[str, Family] = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{__name__}.{info.name}")
        missing = [n for n in ("KINDS", "LEADS", "NUMBERS") if not hasattr(module, n)]
        if missing:
            raise ValueError(
                f"{module.__name__} defines no {' and '.join(missing)}: the line grammar would"
                " skip it"
            )
        for kind in module.KINDS:
            if kind in taken_kinds:
                raise ValueError(
                    f"kind {kind!r} of {module.__name__} is also in {taken_kinds[kind]}"
                )
            taken_kinds[kind] = module.__name__
        grocery_leads = tuple(getattr(module, "GROCERY_LEADS", ()))
        for lead in (*module.LEADS, *grocery_leads):
            if lead in banned:
                raise ValueError(
                    f"lead word {lead!r} of {module.__name__} is a name-like word: it reads as a"
                    " brand without its brand in front"
                )
            if lead in lead_owner:
                raise ValueError(
                    f"lead word {lead!r} of {module.__name__} is also in {lead_owner[lead]}"
                )
            lead_owner[lead] = module.__name__
        found[info.name] = Family(
            info.name,
            tuple(module.KINDS),
            tuple(module.LEADS),
            tuple(getattr(module, "SUBS", ())),
            tuple(getattr(module, "NUMBERS", ())),
            grocery_leads,
            bool(getattr(module, "BARE", False)),
            bool(getattr(module, "MIXED_BRAND", False)),
        )
    return found
