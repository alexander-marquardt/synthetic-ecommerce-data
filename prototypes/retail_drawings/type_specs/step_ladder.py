"""Step ladders and step stools (gen#191, the issue's comment): the steps, the material, the maximum
load in kilograms and the platform height in metres are structured entries; the title states the
steps and the material. :func:`kit_drills.step_ladder` draws one tread per step."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from type_registry import TypeSpec, a


def _row(code, title, brand, price, steps, material, load, height, kind, text):
    return (code, title, brand, price, text,
            (("steps", "Steps", str(steps), "C62"), a("material", "Material", material), ("max_load_kg", "Maximum load", str(load), "KGM", load * 1000.0),
             ("platform_height_m", "Platform height", f"{height:g}", "MTR", height * 1000.0), a("ladder_kind", "Kind", kind)),
            (("steps", str(steps)), ("kind", "stool" if kind == "Step stool" else "ladder")))  # fmt: skip


ROWS = d.styles(
    (
        _row(
            "SLD2ST",
            "2 Step Folding Step Stool, Steel",
            d.BRI,
            18.0,
            2,
            "Steel",
            150,
            0.42,
            "Step stool",
            "A folding step stool with a grip, for a high kitchen shelf.",
        ),
        _row(
            "SLD3AL",
            "3 Step Aluminum Step Ladder",
            d.TOR,
            39.0,
            3,
            "Aluminum",
            150,
            0.65,
            "Step ladder",
            "A light step ladder with wide treads and a tool tray.",
        ),
        _row(
            "SLD4FG",
            "4 Step Fiberglass Step Ladder",
            d.HAR,
            79.0,
            4,
            "Fiberglass",
            150,
            0.85,
            "Step ladder",
            "A step ladder that does not conduct, for jobs near wiring.",
        ),
        _row(
            "SLD5ST",
            "5 Step Steel Step Ladder",
            d.STO,
            69.0,
            5,
            "Steel",
            150,
            1.05,
            "Step ladder",
            "A strong step ladder with a top platform and a safety rail.",
        ),
    ),
    "Step Ladder",
    "step_ladder",
    d.DIY + ("Ladders", "Step Ladders"),
)

SPEC = TypeSpec(
    key="step_ladder",
    department=d.HOME,
    product_type="Step Ladder",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[1], "step ladder", ("DCSLWD", "Step Ladder, Wood Free", "wooden step ladder")
    ),
    owners=d.OWNERS,
)
