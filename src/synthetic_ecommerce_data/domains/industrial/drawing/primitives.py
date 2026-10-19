"""Stub for the red commit."""

from __future__ import annotations

from collections.abc import Sequence

from synthetic_ecommerce_data.core.drawing.model import Figure, Point

PAN_CROWN = 0.5


def shank(fig: Figure, r: float, y0: float, y1: float, role: str = "plain") -> None:
    pass


def round_body(fig: Figure, dia: float, y0: float, y1: float, role: str = "part") -> None:
    pass


def hex_body(fig: Figure, across_flats: float, y0: float, y1: float, role: str = "part") -> None:
    pass


def chamfer(
    fig: Figure,
    r: float,
    y0: float,
    y1: float,
    length: float,
    inset: float | None = None,
    role: str = "part",
    drop: float = 0.0,
) -> None:
    pass


def thread_crests(
    x_half: float, y_from: float, y_to: float, pitch: float
) -> list[tuple[Point, Point]]:
    pass


def thread(
    fig: Figure,
    r: float,
    y0: float,
    y1: float,
    pitch: float,
    chamfer_length: float = 0.0,
    drop: float = 0.0,
) -> None:
    pass


def break_mark(fig: Figure, r: float, y: float, amplitude: float) -> None:
    pass


def conical_end(fig: Figure, r: float, y0: float, y_shoulder: float, y_tip: float) -> None:
    pass


def head_flat(fig: Figure, head_d: float, shank_r: float, height: float, top: float = 0.0) -> None:
    pass


def head_button(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    pass


def head_pan(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    pass


def head_socket(fig: Figure, head_d: float, height: float, top: float = 0.0) -> None:
    pass


def head_hex(fig: Figure, across_flats: float, height: float, top: float = 0.0) -> None:
    pass


def round_face(fig: Figure, centre: Point, radius: float, role: str = "part") -> None:
    pass


def hex_face(fig: Figure, centre: Point, corner_radius: float, role: str = "part") -> None:
    pass


def drive_recess(fig: Figure, centre: Point, key: float) -> None:
    pass


def helix_flutes(
    fig: Figure, dia: float, y0: float, y1: float, flutes: int, helix_deg: float, hand: int = 1
) -> None:
    pass


def flute_end_view(fig: Figure, centre: Point, radius: float, flutes: int, hand: int = 1) -> None:
    pass


def ring(fig: Figure, centre: Point, r_out: float, r_in: float) -> None:
    pass


def tube(fig: Figure, r_out: float, r_in: float, y0: float, y1: float) -> None:
    pass


def plate(
    fig: Figure,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    holes: Sequence[tuple[Point, float]] = (),
    role: str = "part",
) -> None:
    pass
