"""A SKU's manufacturer part number (#937).

The reference catalogue's description ends with the brand, the product line and the
manufacturer's part number, and a part number is not the distributor's SKU. Each SKU gets its
own: the line's series, a dash, and six characters read from a hash of the seed and the SKU.
A hash, not a draw from the build's random stream, so no later draw of the build moves.
"""

from __future__ import annotations

import hashlib

#: The part number's characters: digits and capitals without the look-alikes I and O.
_ALPHABET = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"

#: How many characters follow the series.
_LENGTH = 6


def mfr_part_number(seed: int, series: str, sku: str) -> str:
    """``<series>-<six characters>``, fixed by the seed and the SKU, e.g. ``FD360-7K2Q9M``."""
    number = int(hashlib.sha256(f"{seed}:mfr-part-number:{sku}".encode()).hexdigest(), 16)
    code = ""
    for _ in range(_LENGTH):
        number, digit = divmod(number, len(_ALPHABET))
        code += _ALPHABET[digit]
    part = f"{series}-{code}"
    if part == sku:
        raise ValueError(f"part number {part!r} equals its SKU")
    return part
