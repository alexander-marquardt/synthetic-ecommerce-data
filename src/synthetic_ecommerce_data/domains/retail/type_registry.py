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
is built but has no spec (:func:`registration_problems`). A type whose rows still sit in the
shared row modules names them as its ``homes`` (:class:`Home`): the spec of such a type holds no
rows of its own, and ``scale`` reads from its homes which rows the scaled build leaves out
(gen#537). A clothing, footwear or lingerie spec also carries its apparel decoy plan
(:class:`ApparelPlan`) or an exemption, and :mod:`decoy_apparel` reads it here.

A type that needs a drawing shape the kit lacks defines it in the spec module with
``kit.register`` (see ``docs/new-type-quick-path.md``); the common case reuses a shape.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
import re
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from typing import NamedTuple

from synthetic_ecommerce_data.domains.retail import departments, type_specs
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS, Row
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.lowerbody_rows import LRow
from synthetic_ecommerce_data.domains.retail.variants import cw

__all__ = [
    "ApparelPlan", "BRAND_OWNER", "Decoy", "LRow", "Option", "Row", "SpecError", "TypeSpec", "a",
    "check_unique_ids", "checked_options", "count", "cw", "decoy_ids", "docs", "left_out_ids",
    "registration_problems", "sizes", "specs", "text_match_decoy_ids", "validate",
]  # fmt: skip

KEY = re.compile(r"[a-z][a-z0-9_]*")
#: The text-match decoy classes of gen#294 (``decoy_rows``): a color part, a category word, an
#: audience word, an absent feature, a shade in the description, an incidental word, a brand, and
#: class 8 (gen#326), a product word in the title of another type's product.
DECOY_CLASSES = range(1, 9)
#: The departments whose Womens, Mens and Kids types carry the apparel decoys of gen#311
#: (:mod:`decoy_apparel`), and the word families a plan may name there.
APPAREL_DEPARTMENTS = ("Clothing", "Footwear", "Lingerie & Nightwear")
APPAREL_FAMILIES = "abusk"


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
    #: Class 2 (#444): the type's real compounds as (the word it targets, the phrase), such as
    #: ("vest", "Knitted Vest Top"): the phrase keeps the head noun and holds the word. An
    #: invented compound is a decoy no shopper reads as a product.
    compounds: tuple[tuple[str, str], ...] = ()


class Option(NamedTuple):
    """One SKU option a type's rows carry, and the attribute entry it exports as (gen#413):
    the ``option`` field of the SKU, the entry's ``key`` and ``name``, and its ``unit`` code."""

    option: str
    key: str
    name: str
    unit: str | None = None


#: The shared sources whose rows a spec may name as its home (gen#537), in the order the scaled
#: build reads them: the row modules (``<name>.docs()``), the authored ``samples`` and the
#: ``grocery`` build. ``scale.source_docs`` reads each by this name.
HOME_SOURCES: tuple[str, ...] = (
    "samples", "scale_rows", "breadth_rows", "distractor_rows", "decoy_rows",
    "decoy_product_words", "shirt_rows", "accessory_rows", "school_rows", "sofa_rows",
    "household_rows", "appliance_rows", "underwear_rows", "toys_rows", "lowerbody_rows",
    "lighting_rows", "seasonal_rows", "garden_rows", "decor_rows", "colorgroup_rows",
    "mens_depth_rows", "womens_depth_rows", "kids_depth_rows", "knacks_rows", "knitwear_rows",
    "needs_rows", "color_word_brand_rows", "neckline_rows", "cups_plural_rows",
    "diy_decoy_rows", "grocery",
)  # fmt: skip


class Home(NamedTuple):
    """A shared source that holds rows of a type, and whether ``scale.derivable`` draws them
    (False: the rows stay templates only, as a non-``derivable`` spec's do)."""

    source: str
    derivable: bool


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
    options: tuple[Option, ...] = ()
    homes: tuple[Home, ...] = ()

    def docs(self) -> list[dict]:
        """The catalog documents: the rows, then the decoys."""
        OWNERS.update({b: o for b, o in self.owners if b not in OWNERS})
        return [r.doc() for r in self.rows] + [d.row.doc() for d in self.decoys]


def option_table(
    shared: Mapping[str, tuple[str, str, str | None]], declared: Iterable[TypeSpec] | None = None
) -> tuple[dict[str, tuple[str, str, str | None]], list[str]]:
    """The export's option table (``option -> (key, name, unit)``): the ``shared`` options of
    ``export.py`` and every option a spec declares, and what is wrong with it (gen#413).

    A problem is an option a spec declares that the shared table already holds, an option two
    specs declare differently, and a key that two entries name differently. Two specs may declare
    one option the same way, and one key may carry two units (a hose is cut in metres, a knife's
    blade is in centimetres: ``item_length``); a key has one name.
    """
    table = dict(shared)
    problems: list[str] = []
    seen: dict[str, tuple[str, Option]] = {}
    for spec in specs().values() if declared is None else declared:
        for o in spec.options:
            if o.option in shared:
                problems.append(
                    f"{spec.key}: option {o.option!r} is already in the shared table of "
                    "export.py: declare it once"
                )
                continue
            first = seen.setdefault(o.option, (spec.key, o))
            if first[1] != o:
                problems.append(
                    f"{first[0]} and {spec.key} declare option {o.option!r} differently: "
                    f"{tuple(first[1][1:])} and {tuple(o[1:])}"
                )
                continue
            table[o.option] = (o.key, o.name, o.unit)
    names: dict[str, dict[str, str]] = {}
    for option, (key, name, _unit) in sorted(table.items()):
        names.setdefault(key, {}).setdefault(name, option)
    for key, named in sorted(names.items()):
        if len(named) > 1:
            problems.append(
                f"key {key!r} is named {sorted(named)} (options {sorted(named.values())}): "
                "one key has one name"
            )
    return table, problems


def checked_options(
    shared: Mapping[str, tuple[str, str, str | None]], declared: Iterable[TypeSpec] | None = None
) -> dict[str, tuple[str, str, str | None]]:
    """:func:`option_table`'s table, or :class:`SpecError` naming every problem: the build never
    runs on an option declared with two meanings."""
    table, problems = option_table(shared, declared)
    if problems:
        raise SpecError("; ".join(problems))
    return table


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
    return frozenset(r.product_id for r in rows)


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
    if not spec.rows and not spec.homes:
        raise SpecError(f"{spec.key}: a type needs at least one row, or a home that holds them")
    for home in spec.homes:
        if home.source not in HOME_SOURCES:
            raise SpecError(
                f"{spec.key}: home {home.source!r} is not a source the build reads "
                f"({', '.join(HOME_SOURCES)})"
            )
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
            raise SpecError(f"{spec.key}: {d.row.code} has decoy class {d.cls}, not 1 to 8")
    named = [o.option for o in spec.options]
    for option in sorted({n for n in named if named.count(n) > 1}):
        raise SpecError(f"{spec.key}: option {option!r} is declared twice")
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
    if plan is not None and not plan.compounds:
        raise SpecError(f"{spec.key}: an apparel plan names its class 2 compounds (#444)")
    for word, phrase in plan.compounds if plan is not None else ():
        if not word or word.lower() not in phrase.lower():
            raise SpecError(f"{spec.key}: apparel compound word {word!r} is not in {phrase!r}")


@functools.cache
def specs() -> dict[str, TypeSpec]:
    """Every registered spec by key: the modules of ``type_specs``, found by walking the package."""
    found: dict[str, TypeSpec] = {}
    for info in pkgutil.iter_modules(type_specs.__path__):
        spec = getattr(importlib.import_module(f"{type_specs.__name__}.{info.name}"), "SPEC", None)
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


def docs(skip: Collection[str] = ()) -> list[dict]:
    """Every spec's documents, spec by spec in key order, but those of the ids in ``skip``.

    The footwear styles are also the preview's authored samples, which come first in the build: the
    caller that has them already skips them here, so each is built once and the seeded derivation
    sees them where it always did (gen#427)."""
    return [d for spec in specs().values() for d in spec.docs() if d["product_id"] not in skip]


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


def text_match_decoy_ids(department: str | None = None) -> frozenset[str]:
    """The ids of the spec decoys of classes 1 to 7, of one department or (``None``) of every
    department: they name a color or a feature their structured fields lack on purpose, so the
    output standard's text check leaves them out (the class-8 decoys of gen#326 are checked like
    any product). :data:`scale.TEXT_EXEMPT` reads this, so a new type is exempt by registering."""
    return frozenset(
        i
        for spec in specs().values()
        if department is None or spec.department == department
        for d in spec.decoys
        if d.cls != 8
        for i in _ids([d.row])
    )


#: Declared exemptions from the text check for an id no spec owns: id -> why (gen#452). The
#: build checks each against the catalog, and refuses one the registry already knows.
ONE_OFF_TEXT_EXEMPT: dict[str, str] = {
    "PLT-RQHOOP": (
        "a rose gold decoy in the Hoop Earrings node since gen#423: its metals are its text "
        "pool, and Gold Plated names the plating while its color is Yellow Gold"
    ),
}


def homed(*, derivable: bool | None = None) -> frozenset[tuple[str, str, str]]:
    """The ``(source, department, product type)`` triples the specs name as homes, those whose
    rows the scaled build draws (``derivable`` True), leaves out (False), or all (``None``)."""
    return frozenset(
        (h.source, s.department, s.product_type)
        for s in specs().values()
        for h in s.homes
        if derivable is None or h.derivable is derivable
    )


def registration_problems(built: set[tuple[str, str]]) -> list[str]:
    """What is wrong with how the ``(department, product type)`` pairs of ``built`` are registered:
    a type no spec declares, and a spec whose type is not built."""
    through = {(s.department, s.product_type) for s in specs().values()}
    out = []
    if elsewhere := sorted(built - through):
        out.append(f"built but declared by no spec (add type_specs/<key>.py): {elsewhere}")
    if not through <= built:
        out.append(f"a spec type is not built: {sorted(through - built)}")
    return out
