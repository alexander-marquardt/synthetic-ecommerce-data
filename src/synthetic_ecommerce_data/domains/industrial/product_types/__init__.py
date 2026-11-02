"""One directory per product family, one module per product type (#48).

Each type module exposes ``SPEC``, a :class:`...core.typespec.TypeSpec`. The
industrial domain hands this package to core as its types package (#128), and
:func:`...core.typespec.discover` walks it (``pkgutil.iter_modules``, then
``importlib.import_module`` on each module), so adding a type adds a file here
and edits no shared list. ``scripts/ci_select.py`` reads those two names here:
a change to any type module selects every test that reaches this package.
"""
