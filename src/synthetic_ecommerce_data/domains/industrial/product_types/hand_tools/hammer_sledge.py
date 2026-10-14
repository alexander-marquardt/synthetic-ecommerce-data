"""The sledge hammer kind (#305): one of the kinds under ``Hand Tools > Hammers``.

Everything it draws is in :mod:`...hammers`; this module declares the type.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.industrial import hammers

SPEC = hammers.spec(hammers.SLEDGE)
