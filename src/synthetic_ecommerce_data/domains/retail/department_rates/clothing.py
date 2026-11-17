"""Clothing's derived-style rate (gen#1044 moved it here from ``scale.py``).

Raised from 0.01227 to 0.0124 for the coffee makers, air fryers and blenders of gen#963
slice 1, whose Home styles took Clothing's share from 41.2% to 40.9%, past the 3 points (it is
now 41.1%, against its 44%). Recomputed to 0.013232 for the school backpacks, colored pencils
and desk organizers of gen#969 slice 3 (0.0124 times its 44% target over the share it
reached), then merged with main's 0.01405 for the other new types (both dilute Clothing:
0.0124 x 1.067 x 1.133 = 0.01499).
"""

DEPARTMENT = "Clothing"
RATE = 0.01499
