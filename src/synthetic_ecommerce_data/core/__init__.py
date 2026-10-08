"""The domain-neutral machinery every catalog domain builds on (#125).

Schema and model, brands, copy noise, titles, price, emit, the image bundle
and the drawing framework. Some of these modules still hold industrial
tables next to their machinery; the imports that reach into
``domains.industrial`` for them are listed, and only shrink, in
``tests/test_core_extraction_125.py``.
"""
