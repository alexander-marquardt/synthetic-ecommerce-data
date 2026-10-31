"""The drywall screw kind (#750): one of the plain screws.

Everything it draws is in :mod:`...plain_screws`; this module declares the type.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.industrial import plain_screws

SPEC = plain_screws.spec(plain_screws.DRYWALL)
