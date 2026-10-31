"""Hardware nails (gen#751): three table types under ``Fasteners > Nails``.

Each kind (:mod:`.product_types.fasteners.nail_framing`, ``nail_finishing``, ``nail_masonry``) is a
table type (#101) over one supplier chart, so it shares the size, price and drawing gates of every
table type. What they share lives here: the columns and the drawing.

The charts name no standard, so a nail claims none: ``TableType.source`` says where the rows came
from, in place of ``standard``. The range stays small: one material per kind, the one the chart's
rows are for, and two packs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.tabletype import TableType, spec

#: The published name of each chart column, the size first. A nail's size is its length.
COLUMNS = ("Length", "Shank Dia.", "Head Dia.")
#: How long the point is and how thick the head, in shank diameters: the charts give neither.
POINT = 2.0
HEAD = 0.5


def draw(values: Mapping[str, float]) -> Figure:
    """The nail standing on its point: the point, the shank, and the head across the top, ``Length``
    tall in all."""
    length, shank, head = values["Length"], values["Shank Dia."], values["Head Dia."]
    point = POINT * shank
    under_head = length - HEAD * shank
    fig = Figure(size_in=shank)
    fig.poly([(-shank / 2, point), (0.0, 0.0), (shank / 2, point)])
    fig.rect(-shank / 2, point, shank / 2, under_head)
    fig.rect(-head / 2, under_head, head / 2, length)
    return fig


def nail_spec(table: TableType, label: str) -> TypeSpec:
    """The table's spec, with the label a table does not state."""
    return replace(spec(table), label=label)
