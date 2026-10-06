"""One directory per product family, one module per product type (#48).

Each type module exposes ``SPEC``, a :class:`..catalog.typespec.TypeSpec`,
and is found by :func:`..catalog.typespec.discover`; adding a type adds a
file here and edits no shared list.
"""
