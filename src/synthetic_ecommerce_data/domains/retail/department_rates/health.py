"""Health's derived-style figures (gen#968, slice 4).

Slice 4 deepens the Health types of slices 1 to 3 and adds two (herbal supplements and omega
oils), toward the 4,750 SKUs the issue asks of the ceiling build. At the default rate (0.008) the
department's 102 derivable templates drew 5.89% of derived styles, against its by-template-count
target of 1.85%. The rate is the one that gives the target with every other rate held, computed
as ``sports_outdoors.py``'s is: the target share times the other departments' summed rates
(1.27738), over the department's summed leaf weights (9.9971) times one less the target. It moves
no style of the ceiling build, where every template is drawn until it is exhausted. Recompute it
the same way when a later issue adds Health types.

The six extra brands sell across every Health type, as a chemist's own label does: Velling
Apothecary, Quellmoor Care, Halvering and Thrennick already sell first aid and monitors (slice 2),
and Corvane Pharmacy and Brannock Health are slice 4's own labels (their house styles are in
``health_brand_styles.py``). All are invented.
"""

DEPARTMENT = "Health"
RATE = 0.002402
#: Invented brands its derived styles may carry, beside its template brands.
EXTRA_BRANDS = (
    "Velling Apothecary", "Quellmoor Care", "Halvering", "Thrennick", "Corvane Pharmacy",
    "Brannock Health",
)
