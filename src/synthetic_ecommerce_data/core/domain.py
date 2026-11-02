"""The domain registry: a domain hands core its tables, so core never imports a domain (#128).

Core used to read the industrial tables directly: emit's image-id check asked
``domains.industrial.taxonomy`` whether a type exists, :meth:`.brands.Brand.makes`
looked a type's family up in ``domains.industrial.vocab``, and :mod:`.drawing` drew
a type from ``domains.industrial.drawing.figures``. Each refused any type of a
second domain. :mod:`.typespec` found types in the industrial package alone and
wrote each into industrial tables. Here a domain registers a :class:`Domain` when
its package is imported, and core asks every registered domain.

A domain's tables are passed as functions, not as the tables themselves. A
domain's package ``__init__`` registers it, and importing the table modules there
would run them while the package is half imported.
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from synthetic_ecommerce_data.core.typespec import TypeSpec


class DomainError(Exception):
    """Two different domains registered under one name."""


class ImageIdError(Exception):
    """An image id is not ``<product type>/<product id>/<sku>``.

    Raised rather than patched up. The id is a directory in a published URL:
    an id repaired here would move every image under it and break every link to
    it, silently and long after the change that caused it.
    """


@dataclass(frozen=True)
class Domain:
    """One domain's tables, as core reads them."""

    name: str
    #: Every product type the domain publishes. An image id's first segment is one of them.
    product_types: Callable[[], Collection[str]]
    #: Each of its types' brand family (:attr:`.brands.Brand.families`).
    brand_families: Callable[[], Mapping[str, str]]
    #: Each of its drawn types' figure function and largest extent, in inches
    #: (:func:`.drawing.draw_sku`). A domain that draws through core gives one per type.
    figures: Callable[[], Mapping[str, tuple[Callable[..., Any], tuple[float, float]]]] = field(
        default=lambda: {}
    )
    #: Its types whose card draws the published pack, an item a unit (:func:`.drawing.model.fan`).
    pack_types: Callable[[], Collection[str]] = field(default=lambda: frozenset())
    #: The package its type modules sit under, which :func:`.typespec.discover` walks.
    #: Empty for a domain that declares no type through core.
    types_package: str = ""
    #: Run before its types package is walked, for the types its tables declare
    #: rather than a type module (the industrial YAML breadth rows).
    load_types: Callable[[], None] = field(default=lambda: None)
    #: Writes one spec into the domain's own type-keyed tables, refusing what they
    #: refuse; :func:`.typespec.register` writes core's around it.
    register_type: Callable[[TypeSpec], None] | None = None


_DOMAINS: dict[str, Domain] = {}


def register(domain: Domain) -> None:
    """Add ``domain``. The same one again does nothing; another under its name is refused."""
    held = _DOMAINS.get(domain.name)
    if held is not None and held is not domain:
        raise DomainError(f"a domain named {domain.name!r} is already registered")
    _DOMAINS[domain.name] = domain


def domains() -> tuple[Domain, ...]:
    """The registered domains, in the order they registered."""
    return tuple(_DOMAINS.values())


def is_product_type(type_key: str) -> bool:
    """Whether a registered domain publishes ``type_key``."""
    return any(type_key in d.product_types() for d in _DOMAINS.values())


def brand_family(type_key: str) -> str:
    """The brand family of ``type_key``. Raises ``KeyError`` when no domain gives it one."""
    for d in _DOMAINS.values():
        families = d.brand_families()
        if type_key in families:
            return families[type_key]
    raise KeyError(type_key)


def figure(type_key: str) -> tuple[Callable[..., Any], tuple[float, float]]:
    """The figure function and extent of ``type_key``. ``KeyError`` when no domain draws it."""
    for d in _DOMAINS.values():
        figures = d.figures()
        if type_key in figures:
            return figures[type_key]
    raise KeyError(type_key)


def is_pack_type(type_key: str) -> bool:
    """Whether a registered domain draws ``type_key``'s card as its published pack."""
    return any(type_key in d.pack_types() for d in _DOMAINS.values())


def owner_of(module: str) -> Domain | None:
    """The domain whose types package holds the dotted ``module``, else ``None``."""
    for d in _DOMAINS.values():
        if d.types_package and (
            module == d.types_package or module.startswith(f"{d.types_package}.")
        ):
            return d
    return None


def product_type_for_image(image_id: str) -> str:
    """The product type an image is published under: the first segment of its id.

    Read off the id rather than looked up, because the id was built from the
    line's own product type. A malformed id, or a type no domain registers,
    raises: a guess here would file a drawing under a category nothing else
    agrees with.
    """
    parts = image_id.split("/")
    if len(parts) != 3 or not all(parts) or not is_product_type(parts[0]):
        known = sorted(t for d in _DOMAINS.values() for t in d.product_types())
        raise ImageIdError(
            f"{image_id!r} is not an image id. One reads "
            "<product type>/<product id>/<sku>, and the product type must be one of "
            f"{known}."
        )
    return parts[0]
