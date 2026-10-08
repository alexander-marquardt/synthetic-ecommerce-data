"""The industrial figures: one per product kind, plus the breadth rows' plain shapes.

``core.drawing`` imports :data:`.figures.FIGURES` when it loads. Loading it
here, before either submodule, keeps the import order these modules had when
they shared one package: a process whose first import is ``figures`` would
otherwise reach ``core.drawing`` half-way through ``figures`` and find no
``FIGURES`` yet.
"""

import synthetic_ecommerce_data.core.drawing  # noqa: F401
