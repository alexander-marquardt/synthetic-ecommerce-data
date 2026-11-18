"""Beauty's derived-style figures (gen#1044 moved them here from ``scale.py``).

Recomputed when gen#957 added the hair tools and four shampoos and conditioners (11.6% of
derived styles at 0.02503, against its 8%).
"""

DEPARTMENT = "Beauty"
RATE = 0.01665
#: Its share of derived styles; a department with no SHARE splits the rest by template count.
SHARE = 0.08
#: Invented brands its derived styles may carry, beside its template brands.
EXTRA_BRANDS = ("Brightwater Botanics", "Orrin Skin")
