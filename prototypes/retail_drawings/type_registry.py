"""The registry of retail type specs: one declarative file per product type (gen#351).

A type is one module under ``type_specs/``, named for its key, that declares ``SPEC =
TypeSpec(...)``: its rows (a style is a :class:`~breadth_rows.Row`, or an
:class:`~lowerbody_rows.LRow` with a third SKU axis), its hand-authored text-match decoys, whether
the scaled build may derive styles from the rows, and the owners of any brand the shop does not
already state. :func:`specs` finds the modules by walking the package, so the scaled build
(:func:`scale.templates`, :func:`scale.derivable`), the measured figures
(:mod:`retail_figures`) and the tests read the registry and nothing else is edited to add a type.

``scripts/new_type.py <key> --kind clothing|beauty`` writes a spec that already validates.
``tests/test_retail_type_specs_351.py`` holds every spec to :func:`validate` and fails a type that
is registered anywhere but a spec file or the :func:`legacy_types` list, which only shrinks (a
type moves from the list into a spec; nothing is added to it): :func:`registration_problems` holds
the list to :data:`LEGACY_CEILING`. A clothing, footwear or lingerie spec also carries its
apparel decoy plan (:class:`ApparelPlan`) or an exemption, and :mod:`decoy_apparel` reads it here.

A type that needs a drawing shape the kit lacks defines it in the spec module with
``kit.register`` (see ``docs/new-type-quick-path.md``); the common case reuses a shape.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
import re
from dataclasses import dataclass
from pathlib import Path

import departments
import type_specs
from breadth_rows import OWNERS, Row
from class_model import BRAND_OWNER
from lowerbody_rows import LRow
from variants import cw

__all__ = [
    "ApparelPlan", "BRAND_OWNER", "Decoy", "LRow", "Row", "SpecError", "TypeSpec", "a",
    "check_unique_ids", "count", "cw", "decoy_ids", "docs", "left_out_ids", "legacy_types",
    "registration_problems", "sizes", "specs", "validate",
]  # fmt: skip

LEGACY_FILE = Path(__file__).resolve().parent / "type_specs" / "legacy_types.txt"
KEY = re.compile(r"[a-z][a-z0-9_]*")
#: The text-match decoy classes of gen#294 (``decoy_rows``): a color part, a category word, an
#: audience word, an absent feature, a shade in the description, an incidental word, a brand.
DECOY_CLASSES = range(1, 8)
#: The departments whose Womens, Mens and Kids types carry the apparel decoys of gen#311
#: (:mod:`decoy_apparel`), and the word families a plan may name there.
APPAREL_DEPARTMENTS = ("Clothing", "Footwear", "Lingerie & Nightwear")
APPAREL_FAMILIES = "abusk"
#: The most types the legacy list may hold. A migration lowers it by the types it moves, so the
#: list is exact: an appended line (a type registered the old way) is over it, and a shorter list
#: leaves room to append the difference. Eight footwear styles (gen#216) are the one rise: a
#: shoe is a ``FootwearStyle`` (size charts, an upper per color), which a spec's ``Row`` cannot
#: carry; the footwear types leave the list when footwear moves to specs.
LEGACY_CEILING = 336


class SpecError(ValueError):
    """A spec the registry refuses."""


@dataclass(frozen=True)
class Decoy:
    """A hand-authored text-match decoy: its class, the query it targets, the policy that repairs
    it, and the row (whose structured fields tell the truth)."""

    cls: int
    query: str
    policy: str
    row: Row


@dataclass(frozen=True)
class ApparelPlan:
    """How many text-match decoys a clothing, footwear or lingerie type carries (gen#311)."""

    family: str = "a"
    per_class: int = 3


@dataclass(frozen=True)
class TypeSpec:
    """Everything one product type declares.

    ``derivable`` True lets the scaled build draw derived styles from ``rows`` (a breadth type
    that grows with the build); False keeps them as templates only. A decoy is never derived.
    ``owners`` states ``brand -> "own" | "third_party"`` for a brand no other module has stated.
    A clothing, footwear or lingerie type carries ``apparel`` (its :class:`ApparelPlan` of
    text-match decoys, gen#311) or ``apparel_exempt`` (the reason it carries none); a type of any
    other department carries neither. :mod:`decoy_apparel` reads the plan from the registry.
    """

    key: str
    department: str
    product_type: str
    rows: tuple[Row, ...]
    decoys: tuple[Decoy, ...] = ()
    derivable: bool = False
    owners: tuple[tuple[str, str], ...] = ()
    apparel: ApparelPlan | None = None
    apparel_exempt: str = ""

    def docs(self) -> list[dict]:
        """The catalog documents: the rows, then the decoys."""
        OWNERS.update({b: o for b, o in self.owners if b not in OWNERS})
        return [r.doc() for r in self.rows] + [d.row.doc() for d in self.decoys]


def a(key: str, name: str, value: str) -> tuple[str, str, str]:
    """One attribute entry of a row: ``(key, name, value)``."""
    return (key, name, value)


def count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    """A counted attribute entry (``C62``, unit)."""
    return (key, name, str(n), "C62")


def sizes(price: float, names: tuple[str, ...]) -> tuple[tuple[str, float], ...]:
    """One ``(size, price)`` pair per size name, all at ``price``."""
    return tuple((n, price) for n in names)


def _ids(rows: list[Row]) -> frozenset[str]:
    return frozenset(f"BRD-{r.code}" for r in rows)


def ids_of(spec: TypeSpec) -> frozenset[str]:
    """Every product id the spec adds."""
    return _ids([*spec.rows, *(d.row for d in spec.decoys)])


def decoy_ids_of(spec: TypeSpec) -> frozenset[str]:
    """The ids of the spec's decoys: ``main_colors.complete`` leaves them as authored."""
    return _ids([d.row for d in spec.decoys])


def validate(spec: TypeSpec) -> None:
    """Raise :class:`SpecError` for a spec the build cannot take as it stands."""
    if not KEY.fullmatch(spec.key):
        raise SpecError(f"{spec.key!r}: a key is lower-case words joined by underscores")
    try:
        departments.check([spec.department], spec.key)
    except ValueError as exc:
        raise SpecError(str(exc)) from exc
    if not spec.rows:
        raise SpecError(f"{spec.key}: a type needs at least one row")
    rows = [*spec.rows, *(d.row for d in spec.decoys)]
    codes = [r.code for r in rows]
    for code in sorted({c for c in codes if codes.count(c) > 1}):
        raise SpecError(f"{spec.key}: row code {code} is used twice")
    known = {**OWNERS, **dict(spec.owners)}
    for r in rows:
        if (r.department, r.product_type) != (spec.department, spec.product_type):
            raise SpecError(
                f"{spec.key}: {r.code} is a {r.department}/{r.product_type}, not "
                f"{spec.department}/{spec.product_type}"
            )
        if r.brand not in known:
            raise SpecError(f"{spec.key}: {r.code} sells {r.brand!r}, a brand with no owner")
    for d in spec.decoys:
        if d.cls not in DECOY_CLASSES:
            raise SpecError(f"{spec.key}: {d.row.code} has decoy class {d.cls}, not 1 to 7")
    _validate_apparel(spec)


def _validate_apparel(spec: TypeSpec) -> None:
    plan = spec.apparel
    if plan is None and not spec.apparel_exempt:
        return
    if spec.department not in APPAREL_DEPARTMENTS:
        raise SpecError(f"{spec.key}: apparel decoys are for {', '.join(APPAREL_DEPARTMENTS)}")
    if plan is not None and spec.apparel_exempt:
        raise SpecError(f"{spec.key}: it has an apparel plan and an apparel exemption: pick one")
    if plan is not None and plan.family not in APPAREL_FAMILIES:
        raise SpecError(f"{spec.key}: apparel family {plan.family!r} is not one of a, b, u, s, k")
    if plan is not None and plan.per_class < 3:
        raise SpecError(f"{spec.key}: an apparel plan holds at least 3 decoys per class")


@functools.cache
def specs() -> dict[str, TypeSpec]:
    """Every registered spec by key: the modules of ``type_specs``, found by walking the package."""
    found: dict[str, TypeSpec] = {}
    for info in pkgutil.iter_modules(type_specs.__path__):
        spec = getattr(importlib.import_module(f"type_specs.{info.name}"), "SPEC", None)
        if not isinstance(spec, TypeSpec):
            raise SpecError(f"type_specs/{info.name}.py declares no SPEC = TypeSpec(...)")
        if spec.key != info.name:
            raise SpecError(f"type_specs/{info.name}.py declares key {spec.key!r}: name the file")
        validate(spec)
        found[spec.key] = spec
    seen: dict[tuple[str, str], str] = {}
    for spec in found.values():
        other = seen.setdefault((spec.department, spec.product_type), spec.key)
        if other != spec.key:
            raise SpecError(f"{spec.key} and {other} both declare {spec.product_type}")
    owner: dict[str, str] = {}
    for spec in found.values():
        for pid in sorted(ids_of(spec)):
            if (other := owner.setdefault(pid, spec.key)) != spec.key:
                raise SpecError(
                    f"{other} and {spec.key} both build {pid}: give one row another code "
                    "(the scaffold's --code)"
                )
    return dict(sorted(found.items()))


def check_unique_ids(docs: list[dict]) -> None:
    """Raise :class:`SpecError` when two documents of the build share a product id. A spec
    cannot see the rows still outside the registry, so the build asks once it has them all."""
    seen: dict[str, str] = {}
    for d in docs:
        pid = d["product_id"]
        if pid in seen:
            raise SpecError(
                f"{pid} is built twice ({seen[pid]!r} and {d['product_type']!r}): give the "
                "new row another code (the scaffold's --code)"
            )
        seen[pid] = d["product_type"]


def docs() -> list[dict]:
    """Every spec's documents, spec by spec in key order."""
    return [d for spec in specs().values() for d in spec.docs()]


def left_out_ids() -> frozenset[str]:
    """The ids :func:`scale.derivable` leaves out: every non-derivable spec's rows and every
    decoy."""
    out: set[str] = set()
    for spec in specs().values():
        out |= decoy_ids_of(spec) if spec.derivable else ids_of(spec)
    return frozenset(out)


def decoy_ids() -> frozenset[str]:
    """Every spec decoy's id."""
    return frozenset(i for spec in specs().values() for i in decoy_ids_of(spec))


def legacy_types() -> frozenset[tuple[str, str]]:
    """The ``(department, product type)`` pairs still registered outside a spec file."""
    lines = LEGACY_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(
        (dept, ptype)
        for dept, ptype in (ln.split("|", 1) for ln in lines if ln and not ln.startswith("#"))
    )


def registration_problems(built: set[tuple[str, str]]) -> list[str]:
    """What is wrong with how the ``(department, product type)`` pairs of ``built`` are registered:
    a type in no spec file and not on the legacy list, a type on both, a legacy type no longer
    built, and a legacy list that is not exactly :data:`LEGACY_CEILING` long."""
    through = {(s.department, s.product_type) for s in specs().values()}
    legacy = legacy_types()
    out = []
    if elsewhere := sorted(built - through - legacy):
        out.append(f"registered outside a spec file (use scripts/new_type.py): {elsewhere}")
    if both := sorted(legacy & through):
        out.append(f"migrated but still on the legacy list (on both): {both}")
    if stale := sorted(legacy - built):
        out.append(f"on the legacy list but no longer built: {stale}")
    if len(legacy) > LEGACY_CEILING:
        out.append(f"the legacy list holds {len(legacy)} types, over the ceiling {LEGACY_CEILING}")
    if len(legacy) < LEGACY_CEILING:
        out.append(f"lower LEGACY_CEILING to {len(legacy)}: a migration shortened the list")
    if not through <= built:
        out.append(f"a spec type is not built: {sorted(through - built)}")
    return out
