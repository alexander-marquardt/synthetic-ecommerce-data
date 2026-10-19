"""A figure declared as primitives plus parameters (#74).

A :class:`Spec` is data: the dimensions a figure reads from the record
(:class:`Dim`), and the parts it is made of (:class:`Part`), each naming a
primitive of :mod:`.primitives` and giving it parameters. A parameter is a
number, a string (a role) or an expression over the named dimensions
(:class:`Ref`, with ``+ - * /``). Nothing in a spec is code, so the declarative
type spec (#72) can name a figure by key and carry its parameters.

Provenance is kept per dimension. A dimension the record publishes is read;
one it does not publish takes its ``nominal`` value, which is an expression
(usually a proportion of a dimension that WAS read), and the figure says so:
``source`` is ``record`` when every dimension was read, ``partial`` when the
first (the primary) was read and some other was not, and ``nominal`` when the
primary itself could not be read. A published value always wins over a
nominal one.

``compose(spec, record)`` returns ``(figure, source)``; a figure module wraps
it as ``Drawn(*compose(spec, record))``. This module does not import
:class:`~.figures.Drawn`, because ``figures`` imports this module.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length, parse_thread
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.domains.industrial.drawing import primitives


def _is_primitive(name: str, fn: object) -> bool:
    """A primitive is a public function of :mod:`.primitives` that draws into a figure
    (its first parameter is ``fig``); a helper such as ``thread_crests`` is not one."""
    if not inspect.isfunction(fn) or fn.__module__ != primitives.__name__ or name.startswith("_"):
        return False
    return next(iter(inspect.signature(fn).parameters), None) == "fig"


#: Every primitive a part can name, by name.
PRIMITIVES: dict[str, Callable[..., None]] = {
    name: fn for name, fn in vars(primitives).items() if _is_primitive(name, fn)
}


class CompositionError(ValueError):
    """A spec that names no such primitive, passes it the wrong parameters, or
    refers to a dimension it does not declare."""


@dataclass(frozen=True)
class Expr:
    """A small arithmetic tree over the spec's named dimensions."""

    op: str
    args: tuple = ()

    def _bin(self, op: str, other: object, swap: bool = False) -> Expr:
        pair = (_wrap(other), self) if swap else (self, _wrap(other))
        return Expr(op, pair)

    def __add__(self, other: object) -> Expr:
        return self._bin("+", other)

    def __radd__(self, other: object) -> Expr:
        return self._bin("+", other, swap=True)

    def __sub__(self, other: object) -> Expr:
        return self._bin("-", other)

    def __rsub__(self, other: object) -> Expr:
        return self._bin("-", other, swap=True)

    def __mul__(self, other: object) -> Expr:
        return self._bin("*", other)

    def __rmul__(self, other: object) -> Expr:
        return self._bin("*", other, swap=True)

    def __truediv__(self, other: object) -> Expr:
        return self._bin("/", other)

    def __rtruediv__(self, other: object) -> Expr:
        return self._bin("/", other, swap=True)

    def __neg__(self) -> Expr:
        return Expr("-", (_wrap(0.0), self))


def Ref(name: str) -> Expr:  # noqa: N802  (a constructor read like a type)
    """The value of the dimension (or derived quantity) called ``name``."""
    return Expr("ref", (name,))


def _wrap(value: object) -> Expr:
    if isinstance(value, Expr):
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CompositionError(f"{value!r} is not a number or an expression")
    return Expr("const", (float(value),))


def evaluate(value: object, values: Mapping[str, float]) -> Any:
    """What a parameter comes to: an expression becomes a number; a number, a string (a
    role) passes through; a tuple or list (a point, a list of holes) is evaluated inside."""
    if isinstance(value, (tuple, list)):
        return tuple(evaluate(item, values) for item in value)
    if isinstance(value, (str, int, float)):
        return value
    if not isinstance(value, Expr):
        raise CompositionError(f"{value!r} is not a number, a role or an expression")
    if value.op == "const":
        return value.args[0]
    if value.op == "ref":
        try:
            return values[value.args[0]]
        except KeyError:
            raise CompositionError(f"no dimension {value.args[0]!r} is declared") from None
    left = evaluate(value.args[0], values)
    right = evaluate(value.args[1], values)
    if value.op == "+":
        return left + right
    if value.op == "-":
        return left - right
    if value.op == "*":
        return left * right
    return left / right


def _major(text: str) -> float:
    return parse_thread(text).major.inches


def _pitch(text: str) -> float:
    return parse_thread(text).pitch_in


#: How a dimension's published text becomes inches.
READERS: dict[str, Callable[[str], float]] = {
    "length": lambda text: parse_length(text).inches,
    "thread_major": _major,
    "thread_pitch": _pitch,
}


@dataclass(frozen=True)
class Dim:
    """One dimension a figure reads: the record's ``attr`` read as ``reader``, or
    ``nominal`` (an expression over dimensions declared before it) when the record
    does not publish it.

    ``above`` names a dimension this one must exceed (an outside diameter over a
    bore): a pair that contradicts itself falls to ``nominal`` rather than draw an
    impossible part.
    """

    name: str
    attr: str
    nominal: object
    reader: str = "length"
    above: str | None = None


@dataclass(frozen=True)
class Part:
    """One primitive and its parameters, in the order the primitive's signature names
    them (``fig`` is supplied)."""

    primitive: str
    params: tuple[tuple[str, object], ...] = ()


def part(primitive: str, **params: object) -> Part:
    """``part("shank", r=..., y0=..., y1=...)``: a :class:`Part` written as a call."""
    return Part(primitive, tuple(params.items()))


@dataclass(frozen=True)
class Spec:
    """A figure as data: dimensions read, quantities derived from them, and parts.

    ``size`` is the figure's characteristic size in inches (the sheet's size cue).
    ``derived`` are named expressions, evaluated after the dimensions in order, for
    a quantity several parts share.
    """

    dims: tuple[Dim, ...]
    parts: tuple[Part, ...]
    size: object
    derived: tuple[tuple[str, object], ...] = field(default=())
    #: Names the caller supplies to :func:`build` (a kind's geometry reader gives them).
    inputs: tuple[str, ...] = field(default=())


def check(spec: Spec) -> None:
    """Refuse a spec that names no such primitive, or passes it the wrong parameters.

    Called by :func:`compose` and by the tests, so a typo in a declared figure is
    refused when the spec is checked, not when one record happens to reach it.
    """
    declared = {d.name for d in spec.dims} | {name for name, _ in spec.derived} | set(spec.inputs)
    earlier: set[str] = set(spec.inputs)
    for dim in spec.dims:
        if dim.reader not in READERS:
            raise CompositionError(f"dimension {dim.name!r}: no reader {dim.reader!r}")
        if dim.above is not None and dim.above not in earlier:
            raise CompositionError(
                f"dimension {dim.name!r}: {dim.above!r} is not declared before it"
            )
        _check_refs(dim.nominal, earlier)
        earlier.add(dim.name)
    for p in spec.parts:
        fn = PRIMITIVES.get(p.primitive)
        if fn is None:
            raise CompositionError(f"no primitive {p.primitive!r}; known: {sorted(PRIMITIVES)}")
        try:
            inspect.signature(fn).bind(None, **dict(p.params))
        except TypeError as exc:
            raise CompositionError(f"primitive {p.primitive!r}: {exc}") from None
        for _, value in p.params:
            _check_refs(value, declared)
    _check_refs(spec.size, declared)


def _check_refs(value: object, declared: set[str]) -> None:
    if isinstance(value, (tuple, list)):
        for item in value:
            _check_refs(item, declared)
    elif isinstance(value, Expr):
        if value.op == "ref":
            if value.args[0] not in declared:
                raise CompositionError(f"no dimension {value.args[0]!r} is declared")
        elif value.op != "const":
            for arg in value.args:
                _check_refs(arg, declared)


def _read(dim: Dim, record: Mapping[str, str]) -> float | None:
    try:
        return READERS[dim.reader](record[dim.attr])
    except (KeyError, DimensionParseError):
        return None


def build(spec: Spec, values: Mapping[str, float]) -> Figure:
    """Draw ``spec`` from dimensions already known: ``values`` by name.

    For a figure whose dimensions come from somewhere other than the record's
    attributes (a kind's geometry reader, which also checks the record is
    consistent); its spec then declares no :class:`Dim`.
    """
    check(spec)
    missing = [n for n in spec.inputs if n not in values]
    if missing:
        raise CompositionError(f"the spec needs {missing} and was not given them")
    known = dict(values)
    for name, expr in spec.derived:
        known[name] = float(evaluate(expr, known))
    fig = Figure(size_in=float(evaluate(spec.size, known)))
    for p in spec.parts:
        args = {key: evaluate(value, known) for key, value in p.params}
        PRIMITIVES[p.primitive](fig, **args)
    return fig


def compose(spec: Spec, record: Mapping[str, str]) -> tuple[Figure, str]:
    """Draw ``spec`` for ``record``: ``(figure, source)``.

    Each dimension is read from the record, or takes its nominal value (and the
    source says so). A dimension that must exceed another and does not takes its
    nominal value too.
    """
    check(spec)
    values: dict[str, float] = {}
    read: list[bool] = []
    for dim in spec.dims:
        got = _read(dim, record)
        if got is not None and dim.above is not None and got <= values[dim.above]:
            got = None
        if got is None:
            values[dim.name] = float(evaluate(dim.nominal, values))
        else:
            values[dim.name] = got
        read.append(got is not None)
    fig = build(spec, values)
    if all(read):
        source = "record"
    elif read and read[0]:
        source = "partial"
    else:
        source = "nominal"
    return fig, source
