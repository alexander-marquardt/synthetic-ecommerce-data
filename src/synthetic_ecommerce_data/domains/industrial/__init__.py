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


_domain.register(
    _domain.Domain("industrial", _product_types, _brand_families, _figures, _pack_types)
)
