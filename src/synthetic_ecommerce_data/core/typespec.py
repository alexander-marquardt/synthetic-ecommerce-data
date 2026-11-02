"""The type seam: what makes one product type's output its own (#48, #27).

Several builders add types in parallel, so a type's SKUs, product ids and
drawn values must depend on nothing but the seed and that type's own key and
code. Three things here make that hold, each a pure function of the key:

* :func:`type_rng` -- the type's random stream. A stream shared by every type
  and walked in type order would make each type's draws depend on every type
  built before it.
* :func:`block_of` -- the type's four-digit part-number block, which leads
  every SKU and product id the type issues, so two types can never issue the
  same identifier and no global sequence is needed to keep them apart.
* :func:`discover` -- the per-type modules under each registered domain's
  types package (:attr:`.domain.Domain.types_package`, #128), found
  by walking the package rather than by a hand-kept list that every new type
  would have to edit.

A derived block can land on another type's: about one chance in 135 per new
type at today's 67 types, and better than even odds that at least one of a
hundred new types does. :func:`check_collisions` refuses that build, names
both types and where each would declare a block of its own (its YAML row, or
its type module), and names the first free block (:func:`first_free_block`);
``ecom-generate block <type_key>`` prints the block a new type should declare
before it is built. The fix goes on the newly added type, because re-blocking
a type that already shipped renumbers every SKU it published.
"""

from __future__ import annotations

import hashlib
import importlib
import os
import pkgutil
import random
import sys
from collections.abc import (
    Callable,
    Collection,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from synthetic_ecommerce_data.core import domain

if TYPE_CHECKING:
    from synthetic_ecommerce_data.core.price import PriceModel

#: Part-number blocks are four digits, so a block always prints the same width.
BLOCK_LOW = 1000
BLOCK_HIGH = 9999

#: The scrambled sequence after the block: six digits per type.
SEQUENCE_SPACE = 10**6

#: A stride coprime to 10**6, so consecutive products do not read as a counter.
_PART_STRIDE = 390_581


class TypeModuleError(ImportError):
    """A type module that cannot be imported, named by its dotted path."""


class TypeCollisionError(ValueError):
    """Two types that derive the same part-number block or id."""


class RegistrationReadError(RuntimeError):
    """A type-keyed table read while the type modules are being registered.

    Mid-registration a table holds only the types registered so far, so any
    answer would depend on import order: a sibling's vocabulary missing, or
    :func:`block_of` giving the derived block of a type whose declared one is
    not recorded yet. A type module reads the tables inside its functions,
    never at import.
    """


@dataclass(frozen=True)
class TypeSpec:
    """What a type module declares about itself as ``SPEC``.

    A type is one of two kinds, and declares the fields of its kind only:

    * a **modelled** type names its category path, its standards family, its
      attribute vocabulary, its drawing (``figure`` and ``extent``), its
      builder (``make``) and its ``share`` of ``lines``. The builder and the
      vocabulary are usually a family's, shared with sibling types; what is
      the type's own is this declaration. It also states the per-type
      entries the shared tables register from it (its claims, key
      dimension and noise roles) and what the tests hold its records to:
      the standards a record may claim and its default size.
    * a **breadth** type declares one :class:`.breadth.BreadthRow` as
      ``breadth``, and everything else follows from that row, exactly as it
      does for a row file in ``data/breadth_categories/``.

    :func:`register` writes either kind into the shared, type-keyed tables
    (core's own, and through its domain's ``register_type`` the domain's:
    ``taxonomy.LEAVES``, ``vocab.VOCAB``, ``drawing.figures.FIGURES`` and the
    rest for industrial), so the code that reads those tables is unchanged by
    where a type is declared.

    ``part_number_block`` is only for the rare type whose derived block
    collides with another's; every other type leaves it unset.
    """

    key: str
    #: The shopper-readable name every product of the type carries as
    #: ``product_type_label`` (singular, plain English, capitalised, no ``_``,
    #: unique). Required: a type without one stops the build (#331). A type
    #: whose label is still in ``type_labels.PRODUCT_TYPE_LABELS`` leaves this
    #: unset; declaring it in both places is refused. Declared here, two PRs
    #: that each add a type edit no line in common (#103).
    label: str = ""
    part_number_block: int | None = None
    #: A modelled type's category path, root first; the leaf is the type.
    category: tuple[str, ...] = ()
    #: Which pool of standards designations and brands the type draws from
    #: (``vocab.STANDARDS_FAMILY``).
    standards_family: str = ""
    #: Every attribute the type may publish (``vocab.VOCAB``).
    #: Each is the domain's own attribute spec (industrial: ``vocab.AttrSpec``).
    vocab: tuple[Any, ...] = ()
    #: The drawing function and the extent every SKU of the type is drawn at
    #: (``drawing.figures.FIGURES``).
    figure: Callable[..., Any] | None = None
    extent: tuple[float, float] = (0.0, 0.0)
    #: The builder: ``make(generator, type_key, category)`` drafts one line.
    make: Callable[..., Any] | None = None
    #: Lines drafted, as a share of ``GeneratorConfig.lines``; a
    #: ``type_weights`` entry for the key overrides it.
    share: float = 0.0
    #: What every product of the type is for (``voice.USE_LINES``); empty
    #: falls back to the generic lines.
    use_lines: tuple[str, ...] = ()
    #: How the type's SKUs are priced (:class:`.price.PriceModel`): its
    #: census slope and endings, and its fitted anchor and noise.
    price: PriceModel | None = None
    #: In place of ``price``: the census type whose model the type prices
    #: with (``price.BORROWS``), for a type the census has no prices for. A
    #: module cannot read that model at import (``price.MODELS`` refuses a
    #: read mid-registration), so it names the type instead.
    borrows: str = ""
    #: The sizes each standard the type builds to offers, for a standard with
    #: no extraction in the standards library's ``fastener_standards`` table. Declared apart from
    #: the type's own table on purpose: the coverage sweep holds every size
    #: here to reaching a document, so a row dropped from the table reds it.
    sizes: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    #: The standard a published record was built to, read from its published
    #: attributes, for a type whose ``dimension_provenance`` is a sentence
    #: rather than a bare standard name. ``None`` reads the provenance itself.
    line_standard: Callable[[Mapping[str, str]], str] | None = None
    #: The standards a line may claim (:func:`.conformance.applicable`):
    #: ``claims(facts, metric=..., provenance=..., standard=...)`` returns
    #: them in order. A rule whose claim has a size scope also declares
    #: ``sizes=()`` and is passed each child's thread size (the hex nut).
    #: ``None`` claims none.
    claims: Callable[..., Iterable[str]] | None = None
    #: Every standard a record of the type may claim, which the facts tests
    #: hold each published ``Standards`` value to. Nothing in the build reads
    #: it, so it checks ``claims`` rather than restating it. An empty set
    #: claims nothing; ``None`` is undeclared, which the facts tests refuse.
    may_claim: frozenset[str] | None = None
    #: The type's key dimension: the attribute names the price census keys it
    #: on (:data:`.price.KEY_ATTRIBUTES`, the first one carried wins), which
    #: every title also names.
    key_attributes: tuple[str, ...] = ()
    #: The attribute every title names, for a type whose title names another
    #: than its price key (an O-ring is priced on its cross-section and titled
    #: by its nominal size). Empty reads ``key_attributes``.
    title_attributes: tuple[str, ...] = ()
    #: The thread-size attribute of a type sold by one thread designation,
    #: for the near-miss thread sentence (:data:`.noise.THREADED`).
    threaded: str | None = None
    #: Whether the type is a fastener that publishes ``Material`` and
    #: ``Finish``, for the "what it is not" sentence (:data:`.noise.FASTENERS`).
    fastener: bool = False
    #: The length attribute a unit equivalent is written for
    #: (:data:`.noise.UNIT_PRIMARY`).
    unit_primary: str | None = None
    #: The type's cross-reference sentence (:data:`.compat.RELATIONS`): the
    #: relation kind and the attribute it is written from, for example
    #: ``("nut", "Thread Size")``. ``False`` states the type has none; unset
    #: is refused, so a type cannot go without one by saying nothing (#75).
    compat: tuple[str, str] | bool | None = None
    #: A type whose builder offers a fine-pitch near miss of a diameter: every
    #: Nth line of it is built to one (:data:`.compat.NEAR_MISS_PERIOD`).
    near_miss_period: int | None = None
    #: Whether the type is a cutting tool, for the "suitable for" sentence
    #: (:data:`.noise.CUTTING`).
    cutting: bool = False
    #: Whether the type is one of the newer types: built by its ``make`` as
    #: ``round(lines * share)`` products, a share of them with zero axes
    #: (``config.new_type_share``), rather than as ``max(1, round(lines *
    #: share))`` drafted lines (``config.type_weights``). A kind of its own so
    #: each type's count and random draws, and so the golden catalog, are
    #: what they were when the two kinds were built from different tables.
    newer: bool = False
    #: A breadth type's row, in place of every modelled field above.
    #: The domain's own row type (industrial: ``breadth.BreadthRow``); core reads its ``key``.
    breadth: Any = None
    #: The dotted module the spec was found in, filled in by :func:`discover`.
    module: str = ""


#: The loader of a type FILE (#72), named as a string because core imports no domain:
#: ``module:function``, called ``load(path, module)`` and returning the :class:`TypeSpec`
#: the file declares. It raises :class:`TypeModuleError` naming the file.
TYPE_FILE_LOADER = "synthetic_ecommerce_data.domains.industrial.typefile:load"
TYPE_FILE_SUFFIX = ".yaml"


def _entries(package: str, paths: Iterable[str]) -> list[tuple[str, str, str | None]]:
    """What sits in one package directory: ``(short name, dotted name, file or None)``.

    A module or subpackage has no file; a type file has its path. Sorted by short
    name, as :func:`pkgutil.walk_packages` sorts a directory, so a data file and a
    code module are found in one order.
    """
    found: dict[str, tuple[str, str, str | None]] = {}
    for info in pkgutil.iter_modules(list(paths)):
        found[info.name] = (info.name, f"{package}.{info.name}", None)
    for directory in paths:
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            stem, suffix = os.path.splitext(name)
            if suffix != TYPE_FILE_SUFFIX:
                continue
            if stem in found:
                raise TypeCollisionError(
                    f"type {stem!r} is declared by both {found[stem][1]} and "
                    f"{os.path.join(directory, name)}"
                )
            found[stem] = (stem, f"{package}.{stem}", os.path.join(directory, name))
    return [found[name] for name in sorted(found)]


def types_packages() -> list[str]:
    """Each registered domain's types package, in the order the domains registered."""
    return [d.types_package for d in domain.domains() if d.types_package]


def discover(package: str | None = None) -> dict[str, TypeSpec]:
    """Every type under ``package``, by type key: a code module or a data file.

    With no ``package``, every registered domain's types package
    (:func:`types_packages`); a key two of them declare is refused like two
    modules of one. A module that fails to import is reported by its dotted
    path, because the underlying error (a typo in a table, a bad import) rarely
    says which of many type files it came from. A ``<key>.yaml`` data file is
    read by the generic builder named in :data:`TYPE_FILE_LOADER` (#72); a file
    that is wrong is refused naming the file.
    """
    specs: dict[str, TypeSpec] = {}
    loaders: list[Callable[[Path, str], TypeSpec]] = []

    def read_file(file: str, dotted: str) -> TypeSpec:
        if not loaders:
            module_name, _, attr = TYPE_FILE_LOADER.partition(":")
            loaders.append(getattr(importlib.import_module(module_name), attr))
        return loaders[0](Path(file), dotted)

    def read_module(short: str, dotted: str) -> TypeSpec | None:
        try:
            module = importlib.import_module(dotted)
        except Exception as exc:  # noqa: BLE001 - re-raised, naming the module
            raise TypeModuleError(f"type module {dotted} failed to import: {exc!r}") from exc
        if hasattr(module, "__path__"):
            walk(dotted, list(module.__path__))
            return None
        spec = getattr(module, "SPEC", None)
        if not isinstance(spec, TypeSpec):
            raise TypeModuleError(f"type module {dotted} declares no SPEC = TypeSpec(...)")
        if short != spec.key:
            raise TypeModuleError(
                f"type module {dotted} declares {spec.key!r}; a type module is named "
                "after its type key, so the key can be found from the file and back"
            )
        return spec

    def walk(name: str, paths: list[str]) -> None:
        for short, dotted, file in _entries(name, paths):
            spec = read_file(file, dotted) if file else read_module(short, dotted)
            if spec is None:
                continue
            if spec.key in specs:
                raise TypeCollisionError(
                    f"type {spec.key!r} is declared by both {specs[spec.key].module} and {dotted}"
                )
            specs[spec.key] = replace(spec, module=dotted)

    for name in [package] if package else types_packages():
        try:
            root = importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 - re-raised, naming the package
            raise TypeModuleError(f"type package {name} failed to import: {exc!r}") from exc
        walk(name, list(root.__path__))
    return specs


def owner(spec: TypeSpec) -> domain.Domain:
    """The registered domain whose types package holds ``spec``'s module.

    Raises :class:`TypeModuleError` for a spec no domain's package holds: core
    would not know whose tables it fills.
    """
    held = domain.owner_of(spec.module)
    if held is None or held.register_type is None:
        raise TypeModuleError(
            f"type module {spec.module or '(none)'} declaring {spec.key!r} is in no registered "
            f"domain's types package ({', '.join(types_packages()) or 'none registered'}); "
            "a type module sits under its domain's types package"
        )
    return held


def refuse_redeclared(spec: TypeSpec, own: Mapping[str, tuple[dict[str, Any], Any]]) -> None:
    """Refuse a spec field whose key its shared table already holds.

    ``own`` maps a table's name to the table and the value ``spec`` gives it,
    ``None`` for none. Each entry is declared once: a key in the shared table
    AND on its spec is refused, since which one won would depend on
    registration order.
    """
    for name, (table, value) in own.items():
        if value is not None and dict.__contains__(table, spec.key):
            raise TypeCollisionError(
                f"{spec.key!r} is declared both in {name} and by type module {spec.module}; "
                "keep the declaration on its TypeSpec"
            )


def register(spec: TypeSpec, into: domain.Domain | None = None) -> None:
    """Write ``spec`` into the shared, type-keyed tables every reader uses.

    Core's tables (price, noise, voice) are written here, and the domain's own
    through its :attr:`.domain.Domain.register_type`: the domain ``into``, else
    the one whose types package holds the spec (:func:`owner`). Industrial's are
    the same tables :func:`.breadth.register` fills for a YAML row, so the code
    that reads them cannot tell a type declared in its own module from one
    declared in a shared table.
    """
    # Imported here: each of these modules imports this one.
    from synthetic_ecommerce_data.core import noise, price, voice

    held = into or owner(spec)
    if held.register_type is None:
        raise TypeModuleError(f"domain {held.name!r} registers no types through core")
    if spec.breadth is not None:
        if spec.breadth.key != spec.key:
            raise TypeModuleError(
                f"type module {spec.module} declares {spec.key!r} with a breadth row "
                f"for {spec.breadth.key!r}"
            )
        held.register_type(spec)
        _declare_block(spec)
        return
    # ``share`` and ``extent`` are refused when left at their defaults too: a
    # zero share would build one line (``max(1, ...)``) and a zero extent
    # would draw every SKU at no size, both silently.
    missing = [
        name
        for name, declared in (
            ("category", bool(spec.category)),
            ("standards_family", bool(spec.standards_family)),
            ("vocab", bool(spec.vocab)),
            ("figure", spec.figure is not None),
            ("extent", all(side > 0 for side in spec.extent)),
            ("make", spec.make is not None),
            ("share", spec.share > 0),
            ("price", spec.price is not None or bool(spec.borrows)),
            # Every modelled SKU is priced off its key dimension (``price.KEYS``).
            ("key_attributes", bool(spec.key_attributes)),
            # A relation, or ``False`` for none: a gap the author must see (#75).
            ("compat", spec.compat is not None),
        )
        if not declared
    ]
    if missing:
        raise TypeModuleError(f"type module {spec.module} declares no {', '.join(missing)}")
    if spec.near_miss_period is not None and spec.near_miss_period < 2:
        raise TypeModuleError(
            f"type module {spec.module} declares near_miss_period={spec.near_miss_period}; "
            "every line would be a near miss, and none would be the product itself"
        )
    if spec.price is not None and spec.borrows:
        raise TypeModuleError(
            f"type module {spec.module} declares both a price model and borrows "
            f"{spec.borrows!r}; a type prices by one model"
        )
    # The per-type entries a type used to add to one of core's tables by hand.
    own = {
        "price.KEY_ATTRIBUTES": (price.KEY_ATTRIBUTES, spec.key_attributes),
        "noise.THREADED": (noise.THREADED, spec.threaded),
        "noise.FASTENERS": (noise.FASTENERS, spec.fastener or None),
        "noise.UNIT_PRIMARY": (noise.UNIT_PRIMARY, spec.unit_primary),
        "noise.CUTTING": (noise.CUTTING, spec.cutting or None),
    }
    refuse_redeclared(spec, own)
    # The domain refuses what its own tables refuse before it writes any, so a
    # refusal there leaves core's tables unwritten too.
    held.register_type(spec)
    for table, value in own.values():
        if value is not None:
            table[spec.key] = value
    # A borrower's key is held to its model's fitted span (``price.bounded``).
    price.KEYS[spec.key] = price.bounded(spec.key, price.key_reader(*spec.key_attributes))
    if spec.borrows:
        price.BORROWS[spec.key] = spec.borrows
    else:
        price.MODELS[spec.key] = spec.price  # type: ignore[assignment]
    if spec.use_lines:
        voice.USE_LINES[spec.key] = spec.use_lines
    _declare_block(spec)


def _declare_block(spec: TypeSpec) -> None:
    """Record the block ``spec`` declares, over any its breadth row declared.

    A row's own block is recorded with the row (:func:`.breadth.register`), so
    a spec that leaves its block unset must not overwrite it.
    """
    if spec.part_number_block is not None:
        DECLARED_BLOCKS[spec.key] = spec.part_number_block


#: Set while :func:`registered` runs, so a table read during registration is
#: refused rather than answered from a half-filled table; then set for good
#: once it has finished.
_REGISTRATION = {"running": False, "done": False}


def ensure_registered() -> None:
    """Register the type modules, unless that has already happened.

    Raises :class:`RegistrationReadError` when called while registration is
    underway, naming the line that read.
    """
    if _REGISTRATION["done"]:
        return
    if _REGISTRATION["running"]:
        raise RegistrationReadError(
            f"a type-keyed table was read at {_reader()} while the type modules are being "
            "registered, so it would answer from the types registered so far; read it "
            "inside a function, not at import"
        )
    registered()


def _reader() -> str:
    """``file:line`` of the nearest caller outside this module."""
    frame = sys._getframe(1)
    while frame.f_back is not None and frame.f_code.co_filename == __file__:
        frame = frame.f_back
    return f"{frame.f_code.co_filename}:{frame.f_lineno}"


_K = TypeVar("_K")
_V = TypeVar("_V")


class RegistryTable(dict[_K, _V]):
    """A shared, type-keyed table that registers the type modules before its first read.

    A type declared in its own module joins the tables only when
    :func:`registered` runs. Every read here runs it first, so no reader
    (a script, a test, the image bundle) has to remember to call it, and one
    that forgets cannot see a migrated type as missing. A read made while
    registration runs (a type module reading a table at import) is refused,
    because the table is only half filled then. Writes are untouched:
    registration itself writes through them.
    """

    def __getitem__(self, key: _K) -> _V:
        ensure_registered()
        return super().__getitem__(key)

    def get(self, key: _K, default: Any = None) -> Any:  # type: ignore[override]
        ensure_registered()
        return super().get(key, default)

    def __contains__(self, key: object) -> bool:
        ensure_registered()
        return super().__contains__(key)

    def __iter__(self) -> Iterator[_K]:
        ensure_registered()
        return super().__iter__()

    def __len__(self) -> int:
        ensure_registered()
        return super().__len__()

    def keys(self) -> KeysView[_K]:
        ensure_registered()
        return super().keys()

    def values(self) -> ValuesView[_V]:
        ensure_registered()
        return super().values()

    def items(self) -> ItemsView[_K, _V]:
        ensure_registered()
        return super().items()


@cache
def registered() -> dict[str, TypeSpec]:
    """Every type module of every registered domain, registered once per process.

    Runs on the first read of any :class:`RegistryTable`, so no caller has to
    call it before reading the tables. Each domain loads its table-declared
    types first (:attr:`.domain.Domain.load_types`): a reader that never
    imported the industrial ``breadth`` would otherwise see none of its YAML
    rows. A key two domains declare is refused.
    """
    _REGISTRATION["running"] = True
    specs: dict[str, TypeSpec] = {}
    try:
        for held in domain.domains():
            if not held.types_package:
                continue
            held.load_types()
            for key, spec in discover(held.types_package).items():
                if key in specs:
                    raise TypeCollisionError(
                        f"type {key!r} is declared by both {specs[key].module} and {spec.module}"
                    )
                register(spec, held)
                specs[key] = spec
    finally:
        _REGISTRATION["running"] = False
    _REGISTRATION["done"] = True
    return specs


def modelled() -> dict[str, TypeSpec]:
    """The registered type modules that are modelled types, by key."""
    return {key: spec for key, spec in registered().items() if spec.breadth is None}


#: Every block a type declares, by key: a YAML row's or a type module row's
#: (:func:`.breadth.register`) and a ``TypeSpec``'s (:func:`register`). A
#: :class:`RegistryTable`, so its first read registers both sources: a plain
#: dict was filled only once something had imported ``breadth``.
DECLARED_BLOCKS: RegistryTable[str, int] = RegistryTable()


def part_number_block(type_key: str) -> int:
    """The block a type's key derives: a hash, so no list hands blocks out."""
    digest = int(hashlib.sha256(type_key.encode("utf-8")).hexdigest(), 16)
    return digest % (BLOCK_HIGH - BLOCK_LOW + 1) + BLOCK_LOW


def first_free_block(start: int, used: Collection[int]) -> int:
    """The first block at or after ``start`` that no type uses, wrapping past 9999.

    Deterministic for a given set of used blocks, so the block a collision
    refusal (or ``ecom-generate block``) names is the one every builder of
    that tree would be told.
    """
    span = BLOCK_HIGH - BLOCK_LOW + 1
    taken = set(used)
    for step in range(span):
        block = (start - BLOCK_LOW + step) % span + BLOCK_LOW
        if block not in taken:
            return block
    raise TypeCollisionError(f"all {span} part-number blocks are in use")


def block_of(type_key: str) -> int:
    """The block a type's identifiers carry: its own declared one, else the derived one."""
    declared = DECLARED_BLOCKS.get(type_key)
    return part_number_block(type_key) if declared is None else declared


def module_fix_site(key: str) -> str:
    """Where a code type declares its own block: ``SPEC`` in its type module."""
    found = discover().get(key)
    module = (
        found.module
        if found
        else " or ".join(f"{package}.<family>.{key}" for package in types_packages())
    )
    return f"part_number_block=<block> in SPEC = TypeSpec({key!r}, ...) in {module}"


def check_collisions(blocks: Mapping[str, int], fix_sites: Mapping[str, str] | None = None) -> None:
    """Refuse two types on one block, naming both, in key order.

    ``fix_sites`` says, per type, where that type would declare its own block
    (a YAML row, or a type module); a type missing from it gets
    :func:`module_fix_site`.
    """
    sites = fix_sites or {}
    owner: dict[int, str] = {}
    clashes: list[str] = []
    for key in sorted(blocks):
        block = blocks[key]
        if isinstance(block, bool) or not isinstance(block, int):
            raise TypeCollisionError(
                f"{key}'s part-number block {block!r} is not an integer; declare it unquoted, "
                f"as {sites.get(key) or module_fix_site(key)}"
            )
        if not BLOCK_LOW <= block <= BLOCK_HIGH:
            raise TypeCollisionError(f"{key}'s part-number block {block} is not four digits")
        if block in owner:
            first = owner[block]
            clashes.append(
                f"{first} and {key} both use block {block:04d}, and the first free block "
                f"after it is {first_free_block(block, blocks.values()):04d} "
                f"(to re-block {first}: {sites.get(first) or module_fix_site(first)}; "
                f"to re-block {key}: {sites.get(key) or module_fix_site(key)})"
            )
        else:
            owner[block] = key
    if clashes:
        raise TypeCollisionError(
            "part-number blocks collide: "
            + "; ".join(clashes)
            + ". Give the NEWLY ADDED type of each pair a free block of its own: re-blocking "
            "a type that already shipped renumbers every SKU and product id it has published. "
            "`ecom-generate block <type_key>` prints the block to declare."
        )


def part_number(block: int, sequence: int) -> str:
    """``4127046271``: the type's block, then its scrambled per-type sequence."""
    if not 0 <= sequence < SEQUENCE_SPACE:
        raise ValueError(f"block {block:04d} has used all {SEQUENCE_SPACE} part numbers")
    return f"{block:04d}{(sequence * _PART_STRIDE) % SEQUENCE_SPACE:06d}"


def type_rng(seed: int, type_key: str) -> random.Random:
    """The type's own random stream, from the seed and its key alone."""
    return random.Random(f"{seed}:{type_key}")
