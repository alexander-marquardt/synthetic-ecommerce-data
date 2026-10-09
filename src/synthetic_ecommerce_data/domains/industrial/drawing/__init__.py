"""The industrial figures: one per product kind, plus the breadth rows' plain shapes.

``core.drawing`` imports :data:`.figures.FIGURES` when it loads. Loading it
here, before either submodule, keeps the import order these modules had when
they shared one package: a process whose first import is ``figures`` would
otherwise reach ``core.drawing`` half-way through ``figures`` and find no
``FIGURES`` yet.

It also fills core's mark slot (``core.drawing.brand_mark.use_marks``) with
this domain's brand marks, so core draws them without importing the domain:
this package runs whenever ``core.drawing`` loads, since that loads
``figures``.
"""

import synthetic_ecommerce_data.core.drawing  # noqa: F401
from synthetic_ecommerce_data.core.drawing import brand_mark
from synthetic_ecommerce_data.domains.industrial.drawing import brand_marks

brand_mark.use_marks(brand_marks.mark_of)
