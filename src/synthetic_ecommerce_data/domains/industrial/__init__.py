"""The industrial-supply domain: its types, vocabularies, standards, figures and data.

Importing the package registers the domain with core (:mod:`...core.domain`, #128).
"""

from synthetic_ecommerce_data.core import domain as _domain


def _product_types():
    from synthetic_ecommerce_data.domains.industrial.taxonomy import DRAWING  # noqa: PLC0415

    return DRAWING


def _brand_families():
    from synthetic_ecommerce_data.domains.industrial.vocab import STANDARDS_FAMILY  # noqa: PLC0415

    return STANDARDS_FAMILY


def _figures():
    from synthetic_ecommerce_data.domains.industrial.drawing.figures import FIGURES  # noqa: PLC0415

    return FIGURES


def _pack_types():
    from synthetic_ecommerce_data.domains.industrial.drawing.figures import (  # noqa: PLC0415
        PACK_TYPES,
    )

    return PACK_TYPES


def _orientations():
    from synthetic_ecommerce_data.domains.industrial.orientation import ORIENTATION  # noqa: PLC0415

    return ORIENTATION


#: The package its type modules sit under: one directory per family, one module per
#: type, each exposing ``SPEC`` (:func:`...core.typespec.discover`).
TYPES_PACKAGE = "synthetic_ecommerce_data.domains.industrial.product_types"


def _load_types():
    # The YAML breadth rows register when breadth is imported.
    from synthetic_ecommerce_data.domains.industrial import breadth  # noqa: F401, PLC0415


def _register_type(spec):
    from synthetic_ecommerce_data.domains.industrial.type_tables import (  # noqa: PLC0415
        register_type,
    )

    register_type(spec)


#: The domain as core holds it; a spec registered from outside :data:`TYPES_PACKAGE`
#: (a test's toy type) names it: ``typespec.register(spec, DOMAIN)``.
DOMAIN = _domain.Domain(
    "industrial",
    _product_types,
    _brand_families,
    _figures,
    _pack_types,
    types_package=TYPES_PACKAGE,
    load_types=_load_types,
    register_type=_register_type,
    orientations=_orientations,
)

_domain.register(DOMAIN)
