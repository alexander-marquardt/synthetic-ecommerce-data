"""Six plain, fixed geometric shapes for the breadth categories.

alexander-marquardt/synthetic-industrial-products#34: the breadth categories
exist to fill out category BREADTH cheaply -- "just something to fill up the
image" (maintainer, 2026-09-30) -- not to be exercised in the demo, so their
drawings are not read from the record at all. Every function here returns
IDENTICAL geometry whatever it is called with: the shape says "this is
roughly a sphere / a bar / a box / a disc / a tube / a bracket" and nothing
more specific. That is the opposite of every other drawing in this package,
which reads its geometry from the record's own published values -- and it is
deliberate here: a breadth SKU's dimensions are cheap filler, and a drawing
that scaled to them would assert a precision the record does not have.

Colour and section hatch still come from the record's own Material/Finish
(:mod:`.style`), through the same :func:`.draw_sku` pipeline every other type
uses -- only the GEOMETRY is fixed. ``tests/test_breadth.py`` proves that two
records of one breadth type draw byte-for-byte identical bytes whatever their
published dimensions, the same property ``tests/test_generic.py`` proves for
the twelve original types' drawings.
"""

from __future__ import annotations

from .figures import Drawn, Record
from .model import Figure


def sphere(record: Record) -> Drawn:
    """A ball: one disc."""
    del record
    fig = Figure(size_in=1.0)
    fig.disc((0.0, 0.0), 0.5)
    return Drawn(fig, "nominal")


def cylinder(record: Record) -> Drawn:
    """A round bar, rod or pin: a body with rounded ends."""
    del record
    length, dia = 2.4, 0.5
    half = length / 2
    fig = Figure(size_in=length)
    fig.rect(-half + dia / 2, -dia / 2, half - dia / 2, dia / 2)
    fig.disc((-half + dia / 2, 0.0), dia / 2)
    fig.disc((half - dia / 2, 0.0), dia / 2)
    return Drawn(fig, "nominal")


def block(record: Record) -> Drawn:
    """A rectangular part, drawn with a shallow isometric offset."""
    del record
    w, h, skew = 1.8, 1.2, 0.5
    fig = Figure(size_in=w + skew)
    fig.poly(((0.0, skew), (w, skew), (w, skew + h), (0.0, skew + h)))
    fig.poly(((0.0, skew), (skew, 0.0), (w + skew, 0.0), (w, skew)), "plain")
    fig.poly(((w, skew), (w + skew, 0.0), (w + skew, h), (w, skew + h)), "plain")
    return Drawn(fig, "nominal")


def disc(record: Record) -> Drawn:
    """A flat ring or plate: a disc with a bore."""
    del record
    od, bore = 1.6, 0.5
    fig = Figure(size_in=od)
    fig.disc((0.0, 0.0), od / 2)
    fig.disc((0.0, 0.0), bore / 2, "hole")
    return Drawn(fig, "nominal")


def tube(record: Record) -> Drawn:
    """A hollow cylinder: a body with a bore visible at each end."""
    del record
    length, od, wall = 2.2, 0.6, 0.12
    half = length / 2
    # The end discs sit INSET by their own radius, the same way ``cylinder``'s
    # rounded ends do: a disc of radius ``od / 2`` centred at
    # ``half - od / 2`` reaches exactly to ``half``, so the total extent is
    # ``length`` -- not ``length + od``, which a disc centred AT the rect's
    # edge would draw (the bug this shape shipped with once, caught by
    # ``tests/test_sku_drawings.py::test_no_product_exceeds_its_types_extent``).
    inset = half - od / 2
    fig = Figure(size_in=length)
    fig.rect(-inset, -od / 2, inset, od / 2)
    fig.disc((-inset, 0.0), od / 2)
    fig.disc((-inset, 0.0), od / 2 - wall, "hole")
    fig.disc((inset, 0.0), od / 2)
    fig.disc((inset, 0.0), od / 2 - wall, "hole")
    return Drawn(fig, "nominal")


def bracket(record: Record) -> Drawn:
    """An L-shaped angle bracket, with two mounting holes."""
    del record
    a, b, t = 1.6, 1.6, 0.3
    fig = Figure(size_in=max(a, b))
    fig.poly(((0.0, 0.0), (a, 0.0), (a, t), (t, t), (t, b), (0.0, b)))
    fig.disc((t / 2 + 0.12, b - 0.3), 0.06, "hole")
    fig.disc((a - 0.3, t / 2 + 0.12), 0.06, "hole")
    return Drawn(fig, "nominal")


#: One entry per fixed shape: its drawing function, and the extent
#: (:func:`..drawing.product_scale_for`) it is scaled at. Not derived from
#: any SKU's own dimensions -- these are the same six numbers whatever the
#: breadth row -- so every breadth product of one shape shares one scale by
#: construction, the same guarantee :data:`..catalog.taxonomy.DRAWING` gives
#: the twelve original types.
BREADTH_SHAPES: dict[str, tuple] = {
    "sphere": (sphere, (1.0, 1.0)),
    "cylinder": (cylinder, (2.4, 0.6)),
    "block": (block, (2.3, 1.7)),
    "disc": (disc, (1.6, 1.6)),
    "tube": (tube, (2.2, 0.6)),
    "bracket": (bracket, (1.6, 1.6)),
}
