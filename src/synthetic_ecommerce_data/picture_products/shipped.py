"""The pictures the retail build makes products of (gen#1093).

``pictures.jsonl`` beside this module is the full picture manifest of the WANDS persona's pictures,
byte for byte the one its pinned image set was drawn from (elastic/prism-wands
``src/prism_wands/data/images_release.json``, drawn by the generator at ``ddade9f3``): 42,994 rows,
13,373 of a drawn type and 29,621 department fallbacks. It is the spec each picture was drawn
from, in the generator's own drawing vocabulary under an opaque image id, and nothing else: the
closed schema of :mod:`..picture_manifest` refuses any other field.

:func:`docs` writes a product of our own for each row of a type the book describes, through
:func:`.writer.docs`, and draws no picture: the build draws each SKU's picture from the
document's ``drawing``. The retail build reads it as its ``picture_products`` source
(:data:`synthetic_ecommerce_data.domains.retail.type_registry.BUILD_SOURCES`).
"""

from __future__ import annotations

import functools
from pathlib import Path

from synthetic_ecommerce_data.picture_manifest import Fallback, Picture, load_file
from synthetic_ecommerce_data.picture_products import writer

PINNED = Path(__file__).with_name("pictures.jsonl")
#: The pinned manifest's sha256, as elastic/prism-wands ``docs/wands-persona.md`` records it.
SHA256 = "42fb7e82cd0ce17c9a1e068e61726220b3d03e8c9a5a4ccc72e993738f8fb467"


@functools.cache
def pictures() -> tuple[Picture | Fallback, ...]:
    """The checked rows of the pinned manifest, read once per process."""
    return tuple(load_file(PINNED))


@functools.cache
def ids() -> frozenset[str]:
    """The product id of every shipped product: the build's passes leave them out by these."""
    return frozenset(d["product_id"] for d in docs())


def docs() -> list[dict]:
    """One product document per described picture, in the manifest's order. Fresh each call:
    the build transforms documents."""
    return writer.docs(pictures())
