"""The geometry of a product, read off its record. Nothing here draws.

Each module turns one product's published attributes into a frozen dataclass of
measurements (``geometry_from_record``), or refuses with an error from
:mod:`.attrs`. :mod:`..drawing` reads these to build the per-SKU SVG; the
text-free drawings are the only renderer, so nothing in this package imports a
drawing library.

``palette`` holds the brand inks, the finish tints and the published attribute
spellings the drawings read.
"""
