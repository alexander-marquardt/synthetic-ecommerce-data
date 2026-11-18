"""Health's derived-style figures (gen#968, slice 4).

Slice 4 deepens the nine Health types of slices 1 to 3 toward the 4,750 SKUs the issue asks of
the ceiling build. At the default rate (0.008) its extra templates would draw Health well past
its by-template-count share of a sub-ceiling build; the rate is the one that gives that share
with every other rate held, computed as ``sports_outdoors.py``'s is: the target share times the
other departments' summed rates, over the department's summed leaf weights times one less the
target. It moves no style of the ceiling build, where every template is drawn until it is
exhausted. Recompute it the same way when a later issue adds Health types.

The extra brands sell across every Health type, as a chemist's own label does: Velling
Apothecary and Quellmoor Care already sell first aid and monitors, and Corvane Pharmacy and
Brannock Health are new (their house styles are in ``health_brand_styles.py``). All are invented.
"""

DEPARTMENT = "Health"
RATE = 0.008
#: Invented brands its derived styles may carry, beside its template brands.
EXTRA_BRANDS = (
    "Velling Apothecary", "Quellmoor Care", "Halvering", "Thrennick", "Corvane Pharmacy",
    "Brannock Health",
)
