"""The numbers a tap's drawing is built from, read off a product record.

This module draws nothing; the text-free SKU drawing in :mod:`..drawing.figures`
reads :func:`geometry_from_record`.

* The **thread** is the 60-degree form at the pitch the designation states.
  ``Thread Size`` is the only place a tap record carries a diameter for its
  threaded end, so a record whose designation cannot be read is refused.
* The **drive square** does not follow from any attribute unless the record
  publishes ``Square Size`` (a SKU carries it at the vocabulary's presence,
  0.46, from the ASME B94.9 / ISO 529 row of its thread size). Where it does,
  it is carried at its true across-flats.
* The **chamfer** at the entering end is not carried. ``Chamfer Style`` says
  plug, bottoming or taper; how many threads that is, is a table this record
  does not carry.
* The **flutes** are carried when ``Number of Flutes`` is published, at that
  count. Their width is not published.
"""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import (
    Length,
    Thread,
    parse_count,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.domains.industrial.geometry.attrs import (
    ImpossibleGeometryError,
    require,
)


@dataclass(frozen=True)
class TapGeometry:
    """Every number the drawing uses, and nothing else."""

    thread: Thread
    shank_d: Length
    thread_len: Length
    oal: Length
    #: Present only when the record publishes it; the elevation never uses it.
    square: Length | None
    #: Present only when the record publishes it; the end view uses it.
    flutes: int | None

    @property
    def max_d(self) -> float:
        return max(self.thread.major.inches, self.shank_d.inches)


def _optional_length(record: dict, key: str) -> Length | None:
    raw = record.get(key)
    return parse_length(raw) if raw else None


def geometry_from_record(record: dict) -> TapGeometry:
    flutes_raw = record.get("Number of Flutes")
    geom = TapGeometry(
        thread=parse_thread(require(record, "Thread Size")),
        shank_d=parse_length(require(record, "Shank Dia.")),
        thread_len=parse_length(require(record, "Thread Length")),
        oal=parse_length(require(record, "Overall Length")),
        square=_optional_length(record, "Square Size"),
        flutes=parse_count(flutes_raw) if flutes_raw else None,
    )
    if geom.thread_len.inches >= geom.oal.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: thread length {geom.thread_len.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    if geom.square is not None and geom.square.inches > geom.shank_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a {geom.square.display()} square will not fit "
            f"on a {geom.shank_d.display()} shank"
        )
    return geom
