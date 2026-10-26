"""A product type declared as one data file, read by a generic builder (#72).

A type is ``product_types/<family>/<key>.yaml``: its attributes, the sizes and
standards it is built from, its price model (the fitted numbers between the
``@fit-begin`` / ``@fit-end`` markers), the figure it names and the relations
the shared tables hold for it. :func:`load` reads one file and returns the
:class:`~synthetic_ecommerce_data.core.typespec.TypeSpec` a code module would
have declared as ``SPEC``; :func:`~synthetic_ecommerce_data.core.typespec.discover`
calls it, so the rest of the build cannot tell the two apart.

Code is written only for a new KIND of builder (:data:`KINDS`) or a new KIND of
geometry (:data:`GEOMETRIES`), never per type: a second hex socket set screw,
a stainless one, a square-head one, is one more data file. A file names its
kind (``kind:``) and its geometry (``figure:``); a field neither the common
schema nor its kind owns is refused, naming the file, so a typo cannot silently
leave a type without a rule.

Why YAML, not a frozen Python literal: the breadth rows already are YAML; a
data file imports nothing, so the import-cycle rule (a type module imports
the generator lazily) does not bind it; and the fitted price numbers stay a
block ``scripts/fit_price_model.py`` rewrites between two markers.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import parse_thread
from synthetic_ecommerce_data.core.price import ENDINGS, PriceModel
from synthetic_ecommerce_data.core.typespec import TypeModuleError, TypeSpec
from synthetic_ecommerce_data.domains.industrial import compat
from synthetic_ecommerce_data.domains.industrial.drafts import retired
from synthetic_ecommerce_data.domains.industrial.newtypes import table_provenance
from synthetic_ecommerce_data.domains.industrial.standards import UNF_THREADS_PER_INCH
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

MM = 25.4

#: Fields every type file may carry, whatever its kind.
COMMON = frozenset({
    "key", "kind", "label", "category", "standards_family", "vocab", "figure", "extent",
    "share", "price", "key_attributes", "threaded", "fastener", "compat", "near_miss_period",
    "use_lines", "unit_primary", "cutting", "part_number_block",
})  # fmt: skip
#: What a file must give, whatever its kind; a kind adds its own.
REQUIRED = (
    "key", "kind", "label", "category", "standards_family", "vocab", "figure", "extent", "share",
    "price",
)  # fmt: skip
#: The fields whose value is a tuple in a TypeSpec and a list in a data file.
_TUPLES = ("category", "extent", "key_attributes", "use_lines", "compat")


class _Loader(yaml.SafeLoader):
    """``yaml.safe_load`` that refuses a key given twice, which PyYAML would let win silently."""


def _mapping(loader: _Loader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    seen: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"the key {key!r} is given twice", key_node.start_mark
            )
        seen.add(key)
    return loader.construct_mapping(node, deep)


_Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


# --------------------------------------------------------------------------- the tables
# The row readers of the set-screw standards table, shared by every type whose
# kind is ``pointed_screw``: they read the library's table by name.


class Row(NamedTuple):
    """One size of one table, in inches: what a SKU of that size publishes."""

    size: str
    #: Millimetres for a metric row, threads per inch for an inch row.
    pitch: float
    key_in: float
    #: The flat point's diameter (dp max, C max) and the dog point's (dp max, P max).
    flat_dia_in: float
    dog_dia_in: float
    lengths_in: tuple[float, ...]


@cache
def _data(table: str) -> dict:
    return library.table(table).data


def _inch(value: str) -> float:
    return float(Fraction(value))


def length_range_mm(table: str, standard: str, size: str) -> tuple[float, float]:
    """The shortest and longest length ``standard``'s Table 1 defines for ``size``, mm."""
    (row,) = (r for r in _data(table)[standard]["rows"] if r["size"] == size)
    return row["length_min_mm"], row["length_max_mm"]


@cache
def metric_rows(table: str, standard: str) -> tuple[Row, ...]:
    """``standard``'s rows (ISO 4026-4029), each with the lengths its range admits."""
    data = _data(table)
    nominal = data[standard]["_meta"]["nominal_lengths_mm"]
    # dp is a column of ISO 4026 and 4028 only; both share it, size for size.
    dp = {r["size"]: r["point_dia_max_mm"] for r in data["ISO 4026"]["rows"]}
    rows = []
    for r in data[standard]["rows"]:
        low, high = r["length_min_mm"], r["length_max_mm"]
        dia = float(dp[r["size"]]) / MM
        rows.append(Row(
            size=r["size"],
            pitch=r["pitch_mm"],
            key_in=float(r["socket_key_mm"]) / MM,
            flat_dia_in=dia,
            dog_dia_in=dia,
            lengths_in=tuple(mm / MM for mm in nominal if low <= mm <= high),
        ))  # fmt: skip
    return tuple(rows)


@cache
def inch_rows(table: str, inch_table: str) -> tuple[Row, ...]:
    """The inch rows, each with the lengths its range admits."""
    data = _data(table)[inch_table]
    nominal = [_inch(v) for v in data["_meta"]["nominal_lengths_in"]]
    rows = []
    for r in data["rows"]:
        low, high = _inch(r["length_min_in"]), _inch(r["length_max_in"])
        rows.append(Row(
            size=r["size"],
            pitch=r["threads_per_inch"],
            key_in=_inch(r["socket_key_in"]),
            flat_dia_in=_inch(r["cup_flat_point_dia_max_in"]),
            dog_dia_in=_inch(r["dog_point_dia_max_in"]),
            lengths_in=tuple(v for v in nominal if low - 1e-9 <= v <= high + 1e-9),
        ))  # fmt: skip
    return tuple(rows)


# --------------------------------------------------------------------------- the kinds


@dataclass(frozen=True)
class Kind:
    """A kind of builder: the fields of a file of this kind, and how they become the
    spec's builder and rules. Adding a kind is code; using one is data."""

    fields: frozenset[str]
    build: Callable[[Mapping[str, Any], dict[str, Any]], dict[str, Any]]


_POINT_FIELDS = frozenset({"metric", "inch", "diameter"})
_DIAMETERS = ("flat", "dog", "none")


class ScrewTables:
    """What a ``pointed_screw`` file declares, validated, with the rules it implies."""

    def __init__(self, data: Mapping[str, Any], refuse: Callable[[str], Exception]) -> None:
        self.table: str = data["table"]
        self.inch_table: str = data["inch_table"]
        self.inch_source: str = data["inch_length_source"]
        self.item: str = data["item"]
        self.item_type: str = data["item_type"]
        self.drive_type: str = data["drive_type"]
        self.points: dict[str, tuple[str, str, str]] = {}
        for name, point in data["points"].items():
            if not isinstance(point, Mapping) or set(point) != _POINT_FIELDS:
                raise refuse(f"point {name!r} must give exactly {sorted(_POINT_FIELDS)}")
            if point["diameter"] not in _DIAMETERS:
                raise refuse(f"point {name!r}: diameter is one of {list(_DIAMETERS)}")
            self.points[name] = (point["metric"], point["inch"], point["diameter"])
        self.metric_sizes = tuple(str(s) for s in data["metric_sizes"])
        self.inch_sizes = tuple(str(s) for s in data["inch_sizes"])
        self.materials: dict[str, tuple[tuple[str, ...], str]] = {}
        for name, material in data["materials"].items():
            finishes = tuple(material["finishes"])
            self.materials[name] = (finishes, material.get("hardness", ""))
        claims = data["claims"]
        self.stainless: str = claims["stainless_marker"]
        self.metric_claims: tuple[str, str] = (
            claims["metric"]["plain"],
            claims["metric"]["stainless"],
        )
        self.inch_standard: str = claims["inch"]["standard"]
        self.inch_claims: tuple[str, str] = (claims["inch"]["plain"], claims["inch"]["stainless"])
        basis = data["price_basis"]
        self.basis: tuple[float, float, float] = (
            basis["base"],
            basis["per_length"],
            basis["per_major"],
        )
        self.period: int = data["near_miss_period"]

    # The standard a point is built to in a system.
    def standard(self, point: str, metric: bool) -> str:
        return self.points[point][0 if metric else 1]

    def sizes(self) -> dict[str, tuple[str, ...]]:
        """The sizes each table offers, stated apart from the data file: the coverage
        sweep holds every one to reaching a document."""
        return {
            **{metric: self.metric_sizes for metric, _, _ in self.points.values()},
            **{inch: self.inch_sizes for _, inch, _ in self.points.values()},
        }

    def line_standard(self, record: Mapping[str, str]) -> str:
        """The standard a published record was built to: its point's, in its thread's system."""
        return self.standard(record["Point Type"], record["Dia./Thread Size"].startswith("M"))

    def provenance(self, standard: str, point: str, metric: bool) -> str:
        """Where each published dimension of a line came from."""
        dimensions = ["Drive Size", *(["Point Dia."] if self.points[point][2] != "none" else [])]
        if metric:
            return table_provenance(*((name, standard) for name in ("Length", *dimensions)))
        return (
            f"{table_provenance(*((name, self.inch_standard) for name in dimensions))}; "
            f"Length from {self.inch_source}"
        )

    def claims(
        self, facts: Mapping[str, str], *, metric: bool, provenance: str, standard: str
    ) -> tuple[str, ...]:
        """The point's metric standard, or the inch standard, then the material's."""
        stainless = self.stainless in facts.get("Material", "")
        if metric:
            return (standard, self.metric_claims[1] if stainless else self.metric_claims[0])
        return (self.inch_standard, self.inch_claims[1] if stainless else self.inch_claims[0])

    def may_claim(self) -> frozenset[str]:
        metric = {metric for metric, _, _ in self.points.values()}
        return frozenset(
            metric | {self.inch_standard} | set(self.metric_claims) | set(self.inch_claims)
        )

    def make(self, gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        """One line of the type: a point, a system, a size, a material, and the lengths offered."""
        # Imported here: generate.py imports the type tables, which discover this file.
        from synthetic_ecommerce_data.core import brands
        from synthetic_ecommerce_data.core.model import keyword_attribute
        from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

        rng = gen.rng
        metric = gen._rotate(f"system:{type_key}", 2) == 0
        points = list(self.points)
        point = points[gen._rotate(f"point:{type_key}:{metric}", len(points))]
        standard = self.standard(point, metric)
        rows = (
            metric_rows(self.table, standard) if metric else inch_rows(self.table, self.inch_table)
        )
        row = rows[gen._rotate(f"size:{type_key}:{standard}", len(rows))]
        size, pitch, lengths = row.size, row.pitch, list(row.lengths_in)
        materials = list(self.materials)
        material = materials[gen._rotate(f"material:{type_key}:{standard}:{size}", len(materials))]
        finishes, hardness = self.materials[material]
        finish = rng.choice(finishes)
        brand = brands.pick_brand(rng, type_key, gen._exhausted)

        if metric:
            thread, thread_type = f"{size}x{pitch:g}", "Metric Coarse"
        else:
            tpi, thread_type = pitch, "UNF" if size == "#0" else "UNC"
            fine = UNF_THREADS_PER_INCH.get(size)
            # The wheel turns per size, not per (point, size): a point type draws a size a
            # line or two, so a wheel kept per point never reached its third line and no
            # set screw was ever built to UNF (#75).
            period = compat.NEAR_MISS_PERIOD[type_key]  # declared on the file: near_miss_period
            # The first line a standard builds to a size is always coarse: a size whose only
            # line landed on the fine turn would leave the standard's own size unreached.
            first = gen._rotation_step(f"visit:{standard}:{size}") == 0
            if fine and not first and gen._rotate(f"fine:{type_key}:{size}", period) == period - 1:
                tpi, thread_type = fine, "UNF"
            thread = f"{size}-{tpi:g}"
        meets = self.inch_standard if not metric else standard
        draft = LineDraft(
            item=self.item,
            brand=brand,
            series=f"{standard.replace(' ', '').replace('.', '')}-{rng.randint(10, 99)}",
            category=category,
            provenance=self.provenance(standard, point, metric),
            standard=standard,
        )
        draft.line_attrs = [
            retired(keyword_attribute("Item", self.item)),  # keeps the stream stable for #497
            retired(keyword_attribute("Type", self.item_type)),  # likewise
            keyword_attribute("Point Type", point),
            keyword_attribute("Drive Type", self.drive_type),
            keyword_attribute("Material", material),
            keyword_attribute("Finish", finish),
            keyword_attribute("Thread Direction", "Right Hand"),
            keyword_attribute("Thread Type", thread_type),
            *([keyword_attribute("Hardness", hardness)] if hardness else []),
            keyword_attribute("Standards", meets),
        ]

        count = min(gen._variant_count(), len(lengths))
        offered = gen._offered_run(f"lengths:{standard}:{size}", lengths, count)
        system = "mm" if metric else "in"
        major_in = parse_thread(thread).major.inches
        # The nominal key, as every other type publishes it: a 5/32 filter must
        # reach the set screws a 5/32 key drives.
        key_in = compat.nominal_key_in(row.key_in, metric)
        diameter = self.points[point][2]
        point_dia_in = row.dog_dia_in if diameter == "dog" else row.flat_dia_in
        base, per_length, per_major = self.basis
        for length_in in offered:
            style = gen._style(system)
            child = ChildDraft(system=system)
            child.primary = keyword_attribute("Dia./Thread Size", thread)
            length_attr = gen._length("Length", length_in, style)
            child.attrs = [child.primary, length_attr, gen._length("Drive Size", key_in, style)]
            if diameter != "none":
                child.attrs.append(gen._length("Point Dia.", point_dia_in, style))
            child.secondary = {"other_length": length_attr}
            child.price_basis = base + length_in * per_length + major_in * per_major
            draft.children.append(child)
        return draft


_PIN_FIELDS = frozenset({
    "item", "item_type", "drive_type", "table", "inch_table", "inch_length_source", "points",
    "metric_sizes", "inch_sizes", "materials", "claims", "price_basis",
})  # fmt: skip


def _pointed_screw(data: Mapping[str, Any], out: dict[str, Any]) -> dict[str, Any]:
    tables = ScrewTables(data, lambda why: ValueError(why))
    return {
        "make": tables.make,
        "sizes": tables.sizes(),
        "line_standard": tables.line_standard,
        "claims": tables.claims,
        "may_claim": tables.may_claim(),
    }


#: Every kind of builder a file may name.
KINDS: dict[str, Kind] = {"pointed_screw": Kind(_PIN_FIELDS, _pointed_screw)}


def _geometries() -> dict[str, Callable[[Sequence[float]], Callable[[Mapping[str, str]], Any]]]:
    # Imported here: the drawing package imports the type tables, which discover this file.
    from synthetic_ecommerce_data.domains.industrial.drawing.headless import headless_screw_figure

    return {"headless_screw": headless_screw_figure}


# --------------------------------------------------------------------------- the loader


def _price(fields: Mapping[str, Any]) -> PriceModel:
    known = {f.name for f in dataclasses.fields(PriceModel)}
    unknown = sorted(set(fields) - known)
    if unknown:
        raise ValueError(f"price: unknown field {unknown[0]!r}; known: {sorted(known)}")
    given = {k: tuple(v) if isinstance(v, list) else v for k, v in fields.items()}
    if "endings" in given:
        name = given["endings"]
        if name not in ENDINGS:
            raise ValueError(f"price: endings {name!r} is not a table of price.ENDINGS")
        given["endings"] = ENDINGS[name]
    return PriceModel(**given)


def _vocab(rows: Sequence[Mapping[str, Any]]) -> tuple[AttrSpec, ...]:
    known = {f.name for f in dataclasses.fields(AttrSpec)}
    for row in rows:
        unknown = sorted(set(row) - known)
        if unknown:
            raise ValueError(f"vocab {row.get('name')!r}: unknown field {unknown[0]!r}")
    return tuple(AttrSpec(**row) for row in rows)


def load(path: Path, module: str) -> TypeSpec:
    """The :class:`TypeSpec` a type file declares; ``module`` is its dotted name.

    Raises :class:`~synthetic_ecommerce_data.core.typespec.TypeModuleError` naming the
    file for text that is not YAML, a file that is not a mapping, a key that is not the
    file's name, a field nobody owns, a missing field, and a value a table refuses.
    """
    name = path.name

    def refuse(why: str) -> TypeModuleError:
        return TypeModuleError(f"type file {name} {why}")

    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_Loader)  # noqa: S506 - SafeLoader
    except yaml.YAMLError as exc:
        raise refuse(f"could not be parsed as YAML: {exc}".replace("\n", " ")) from exc
    if not isinstance(data, dict):
        raise refuse("is not a mapping of fields")
    if data.get("key") != path.stem:
        raise refuse(
            f"declares {data.get('key')!r}; a type file is named after its type key, "
            "so the key can be found from the file and back"
        )
    kind = KINDS.get(data.get("kind"))
    allowed = COMMON | (
        kind.fields if kind else frozenset().union(*(k.fields for k in KINDS.values()))
    )
    for field_name in data:
        if field_name not in allowed:
            raise refuse(f"has an unknown field {field_name!r}; the fields are {sorted(allowed)}")
    if kind is None:
        raise refuse(f"names kind {data.get('kind')!r}; the kinds are {sorted(KINDS)}")
    missing = [f for f in (*REQUIRED, *sorted(kind.fields)) if f not in data]
    if missing:
        raise refuse(f"is missing {missing}")
    geometries = _geometries()
    if data["figure"] not in geometries:
        raise refuse(f"names figure {data['figure']!r}; the geometries are {sorted(geometries)}")
    try:
        built = kind.build(data, data)
        fields: dict[str, Any] = {
            f: tuple(v) if f in _TUPLES and isinstance(v, list) else v
            for f, v in data.items()
            if f in COMMON and f not in {"kind", "figure", "vocab", "price"}
        }
        return TypeSpec(
            **fields,
            **built,
            figure=geometries[data["figure"]](tuple(data["extent"])),
            vocab=_vocab(data["vocab"]),
            price=_price(data["price"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise refuse(f"is not a valid {data['kind']} type: {exc!r}") from exc
