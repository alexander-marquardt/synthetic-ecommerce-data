"""The orientation of every retail shape, one module per module that registers it (#1045).

:mod:`..orientation` held the four tuples every shape is filed in. A PR that added a shape
inserted its name into one of them, so PRs from different departments edited the same lines
and five rebase rounds in two days went to that one file (#994, #1011, #1020, #1033). Now
each shape's orientation sits in a module named after the module that registers the shape:

* ``kit_<owner>.py`` -> ``<owner>.py`` (``kit_health.py`` -> ``health.py``);
* ``kit.py`` itself -> ``kit.py``;
* ``type_specs/<name>.py`` -> ``spec_<name>.py``.

A module exposes any of ``ANY``, ``SLIGHT``, ``UPRIGHT`` and ``LEVEL``, each a tuple of shape
names (the sets are :mod:`..orientation`'s). A PR that adds a ``kit_<owner>.py`` adds
``<owner>.py`` here, and edits no line another department's PR touches. :mod:`..orientation`
finds each module by walking this package, in the order of their names. It refuses a module
that names no shape, and a shape that two modules name.
"""
