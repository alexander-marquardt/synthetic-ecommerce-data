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
* :func:`discover` -- the per-type modules under :data:`TYPES_PACKAGE`, found
  by walking the package rather than by a hand-kept list that every new type
  would have to edit.

A derived block can land on another type's: about one chance in 135 per new
type at today's 67 types, and better than even odds that at least one of a
hundred new types does. :func:`check_collisions` refuses that build, names
both types and where each would declare a block of its own (its YAML row, or
its type module), and names the first free block (:func:`first_free_block`);
``sip-generate block <type_key>`` prints the block a new type should declare
before it is built. The fix goes on the newly added type, because re-blocking
a type that already shipped renumbers every SKU it published.
"""

from __future__ import annotations

import hashlib
import importlib
import pkgutil
import random
from collections.abc import (
    Callable,
    Collection,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from dataclasses import dataclass, replace
from functools import cache
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from .breadth import BreadthRow
    from .vocab import AttrSpec

#: The package type modules are discovered under: one directory per family,
#: one module per type, each exposing ``SPEC``.
TYPES_PACKAGE = "synthetic_industrial_products.product_types"

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


@dataclass(frozen=True)
class TypeSpec:
    """What a type module declares about itself as ``SPEC``.

    A type is one of two kinds, and declares the fields of its kind only:

    * a **modelled** type names its category path, its standards family, its
      attribute vocabulary, its drawing (``figure`` and ``extent``), its
      builder (``make``) and its ``share`` of ``lines``. The builder and the
      vocabulary are usually a family's, shared with sibling types; what is
      the type's own is this declaration.
    * a **breadth** type declares one :class:`.breadth.BreadthRow` as
      ``breadth``, and everything else follows from that row, exactly as it
      does for a row of ``data/breadth_categories.yaml``.

    :func:`register` writes either kind into the shared, type-keyed tables
    (``taxonomy.LEAVES``, ``vocab.VOCAB``, ``drawing.figures.FIGURES`` and the
    rest), so the code that reads those tables is unchanged by where a type is
    declared.

    ``part_number_block`` is only for the rare type whose derived block
    collides with another's; every other type leaves it unset.
    """

    key: str
    part_number_block: int | None = None
    #: A modelled type's category path, root first; the leaf is the type.
    category: tuple[str, ...] = ()
    #: Which pool of standards designations and brands the type draws from
    #: (``vocab.STANDARDS_FAMILY``).
    standards_family: str = ""
    #: Every attribute the type may publish (``vocab.VOCAB``).
    vocab: tuple[AttrSpec, ...] = ()
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
    #: A breadth type's row, in place of every modelled field above.
    breadth: BreadthRow | None = None
    #: The dotted module the spec was found in, filled in by :func:`discover`.
    module: str = ""


def discover(package: str = TYPES_PACKAGE) -> dict[str, TypeSpec]:
    """Every type module under ``package``, by type key.

    A module that fails to import is reported by its dotted path, because the
    underlying error (a typo in a table, a bad import) rarely says which of
    many type files it came from.
    """

    def refuse(name: str) -> None:
        raise TypeModuleError(f"type package {name} failed to import")

    try:
        root = importlib.import_module(package)
    except Exception as exc:  # noqa: BLE001 - re-raised, naming the package
        raise TypeModuleError(f"type package {package} failed to import: {exc!r}") from exc
    specs: dict[str, TypeSpec] = {}
    for found in pkgutil.walk_packages(root.__path__, prefix=f"{package}.", onerror=refuse):
        if found.ispkg:
            continue
        try:
            module = importlib.import_module(found.name)
        except Exception as exc:  # noqa: BLE001 - re-raised, naming the module
            raise TypeModuleError(f"type module {found.name} failed to import: {exc!r}") from exc
        spec = getattr(module, "SPEC", None)
        if not isinstance(spec, TypeSpec):
            raise TypeModuleError(f"type module {found.name} declares no SPEC = TypeSpec(...)")
        if found.name.rsplit(".", 1)[1] != spec.key:
            raise TypeModuleError(
                f"type module {found.name} declares {spec.key!r}; a type module is named "
                "after its type key, so the key can be found from the file and back"
            )
        if spec.key in specs:
            raise TypeCollisionError(
                f"type {spec.key!r} is declared by both {specs[spec.key].module} and {found.name}"
            )
        specs[spec.key] = replace(spec, module=found.name)
    return specs


def register(spec: TypeSpec) -> None:
    """Write ``spec`` into the shared, type-keyed tables every reader uses.

    The same tables :func:`.breadth.register` fills for a YAML row, so the
    code that reads them cannot tell a type declared in its own module from
    one declared in a shared table.
    """
    # Imported here: each of these modules imports this one.
    from ..drawing.figures import FIGURES  # noqa: PLC0415
    from . import breadth, taxonomy, vocab, voice  # noqa: PLC0415

    if spec.breadth is not None:
        if spec.breadth.key != spec.key:
            raise TypeModuleError(
                f"type module {spec.module} declares {spec.key!r} with a breadth row "
                f"for {spec.breadth.key!r}"
            )
        breadth.add_row(spec.breadth)
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
        )
        if not declared
    ]
    if missing:
        raise TypeModuleError(f"type module {spec.module} declares no {', '.join(missing)}")
    taxonomy.LEAVES[spec.key] = (spec.category,)
    taxonomy.DRAWING[spec.key] = spec.key
    vocab.VOCAB[spec.key] = spec.vocab
    vocab.STANDARDS_FAMILY[spec.key] = spec.standards_family
    FIGURES[spec.key] = (spec.figure, spec.extent)
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


#: Set while :func:`registered` runs, so a table read during registration does
#: not start it again; then set for good once it has finished.
_REGISTRATION = {"running": False, "done": False}


def ensure_registered() -> None:
    """Register the type modules, unless that has already happened (or is underway)."""
    if not (_REGISTRATION["done"] or _REGISTRATION["running"]):
        registered()


_K = TypeVar("_K")
_V = TypeVar("_V")


class RegistryTable(dict[_K, _V]):
    """A shared, type-keyed table that registers the type modules before its first read.

    A type declared in its own module joins the tables only when
    :func:`registered` runs. Every read here runs it first, so no reader
    (a script, a test, the image bundle) has to remember to call it, and one
    that forgets cannot see a migrated type as missing. Writes are untouched:
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
    """Every type module under :data:`TYPES_PACKAGE`, registered once per process.

    Runs on the first read of any :class:`RegistryTable`, so no caller has to
    call it before reading the tables.
    """
    _REGISTRATION["running"] = True
    try:
        # The YAML breadth rows register when breadth is imported; a reader
        # that never imported it would otherwise see none of them.
        from . import breadth  # noqa: F401, PLC0415

        specs = discover()
        for spec in specs.values():
            register(spec)
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
    refusal (or ``sip-generate block``) names is the one every builder of
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
    module = found.module if found else f"{TYPES_PACKAGE}.<family>.{key}"
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
            "`sip-generate block <type_key>` prints the block to declare."
        )


def part_number(block: int, sequence: int) -> str:
    """``4127046271``: the type's block, then its scrambled per-type sequence."""
    if not 0 <= sequence < SEQUENCE_SPACE:
        raise ValueError(f"block {block:04d} has used all {SEQUENCE_SPACE} part numbers")
    return f"{block:04d}{(sequence * _PART_STRIDE) % SEQUENCE_SPACE:06d}"


def type_rng(seed: int, type_key: str) -> random.Random:
    """The type's own random stream, from the seed and its key alone."""
    return random.Random(f"{seed}:{type_key}")
