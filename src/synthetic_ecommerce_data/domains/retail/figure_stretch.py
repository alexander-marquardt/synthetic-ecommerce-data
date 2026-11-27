"""The figure wrapper: a drawing scaled to its product's own proportions (gen#1022)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthetic_ecommerce_data.domains.retail.kit import Fill


def figure_at(draw, stretch: tuple[float, float], defs: str):
    """``draw`` with its parts in one ``<g class="figure">``, scaled ``stretch`` (x, y) about the
    bottom center of the box they cover (gen#1022): a 90-inch sideboard draws longer for its
    height than a 60-inch one, and stands on the same floor. The box leaves out a ground shadow
    (``class="ground"``), which reaches below the floor and is drawn again outside the figure
    (gen#1214). ``defs`` holds what the parts refer to, so they can be measured."""

    def drawn(paint: str, fill: Fill, label: str | None, **params) -> list[str]:
        parts = draw(paint, fill, label, **params)
        sx, sy = stretch
        if (sx, sy) == (1.0, 1.0):
            return ['<g class="figure">', *parts, "</g>"]
        # deferred: these measure what the kit draws
        from synthetic_ecommerce_data.domains.retail import (
            ground_shadow,
            sheet_extent,
        )

        body = ground_shadow.GROUND.sub("", "".join(parts))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{body}</svg>'
        box = sheet_extent.reach(svg)
        if box is None:
            return ['<g class="figure">', *parts, "</g>"]
        x, y = (box[0] + box[2]) / 2, box[3]
        move = f"translate({x:g} {y:g}) scale({sx:.4f} {sy:.4f}) translate({-x:g} {-y:g})"
        return [f'<g class="figure" transform="{move}">', *parts, "</g>"]

    return drawn
