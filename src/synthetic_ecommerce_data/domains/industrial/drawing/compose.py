"""Stub for the red commit."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from synthetic_ecommerce_data.core.dimensions import parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.domains.industrial.drawing import primitives


def _is_primitive(name: str, fn: object) -> bool:
    pass


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
        return self

    def __add__(self, other: object) -> Expr:
        return self

    def __radd__(self, other: object) -> Expr:
        return self

    def __sub__(self, other: object) -> Expr:
        return self

    def __rsub__(self, other: object) -> Expr:
        return self

    def __mul__(self, other: object) -> Expr:
        return self

    def __rmul__(self, other: object) -> Expr:
        return self

    def __truediv__(self, other: object) -> Expr:
        return self

    def __rtruediv__(self, other: object) -> Expr:
        return self

    def __neg__(self) -> Expr:
        return self


def Ref(name: str) -> Expr:
    return Expr("ref", (name,))


def _wrap(value: object) -> Expr:
    pass


def evaluate(value: object, values: Mapping[str, float]) -> Any:
    return 0.0


def _major(text: str) -> float:
    pass


def _pitch(text: str) -> float:
    pass


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
    return Part(primitive, ())


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


def check(spec: Spec) -> None:
    pass


def _check_refs(value: object, declared: set[str]) -> None:
    pass


def _read(dim: Dim, record: Mapping[str, str]) -> float | None:
    pass


def build(spec: Spec, values: Mapping[str, float]) -> Figure:
    return Figure()


def compose(spec: Spec, record: Mapping[str, str]) -> tuple[Figure, str]:
    return (Figure(), "nominal")
