"""Catalog domains: one plug-in package per kind of store (#125).

The 2026-10-28 ruling on #125 fixes what a domain is, and this package holds to it:

* **One domain per store.** ``industrial/`` is the industrial supplier and ``retail/`` the
  general retailer. A domain boundary is where the title conventions, the brands, the id
  prefix and the shopper change; a department is not one.
* **Departments live inside a domain.** Apparel, home, food and beauty are departments of
  ``retail/``, not domains of their own: the store's department floors, shared brand pools and
  the decoy rows that cross departments (lemon in food, beauty and cleaning) are one store's
  machinery.
* **A domain never imports another,** and reaches core only (not ``prism/`` or the commands
  above it). ``tests/test_core_extraction_125.py`` refuses a reach from one domain into another,
  as it refuses core reaching a domain past its listed edges.
"""
