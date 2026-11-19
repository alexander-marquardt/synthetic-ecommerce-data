"""Step 2 of gen#1022: products of our own, written around a manifest of pictures.

The pictures are drawn elsewhere (step 1, in elastic/prism-wands, through the public
``synthetic_ecommerce_data.drawings.render``). Step 2 sees only the picture manifest: the spec each
picture was drawn from, in the generator's own drawing vocabulary, under an opaque image id. It
never reads an image file, a catalogue or anything named for the benchmark. :mod:`.manifest`
checks the manifest against its closed schema, and :mod:`.writer` makes one product per picture.
The two paths share the renderer and nothing else: ``drawings`` does not import this package, and
this package imports nothing under the benchmark's name (``tests/test_picture_products_1022.py``).

Run it::

    uv run python -m synthetic_ecommerce_data.picture_products MANIFEST OUT_DIR

It writes ``OUT_DIR/products.jsonl`` and one ``OUT_DIR/images/<product id>.svg`` per product.
"""

from __future__ import annotations

from synthetic_ecommerce_data.picture_products.manifest import Picture, load, load_file
from synthetic_ecommerce_data.picture_products.writer import Product, write

__all__ = ["Picture", "Product", "load", "load_file", "write"]
