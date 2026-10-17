"""The colours a product type really comes in (gen#448). Stub: nothing is restricted yet."""

from __future__ import annotations

#: path prefix -> (the colours the type comes in, why)
RESTRICTED: dict[tuple[str, ...], tuple[tuple[str, ...], str]] = {}


def allowed_for(path) -> tuple[str, ...] | None:
    return None


def permits(path, color: str) -> bool:
    return True


def base_color(name: str) -> str:
    return name


def not_a_cloth(value: str) -> bool:
    return value.lower() in {"crease resistant", "checked", "recycled"}
