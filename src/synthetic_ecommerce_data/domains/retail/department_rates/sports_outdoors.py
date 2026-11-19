"""Sports & Outdoors' derived-style rate (gen#959).

The fishing and golf types of gen#959 slice 1 are the department's first derivable types. At the
default rate (0.008) the department drew 2.18% of derived styles, against its by-template-count
target of 0.48%; at the 0.002475 the PR first set, 0.68%. The rate is the one that gives the
target with every other rate held: the target share times the other departments' summed rates,
over the department's summed leaf weights (3.545) times one less the target. It is recomputed the
same way when a later slice of gen#959 adds the department's next derivable types.

Slice 2 adds nine (exercise bikes to table tennis bats): the target is 1.09% and the summed leaf
weights 6.289, so the rate is 0.002259; at slice 1's 0.001726 the department drew 0.83%.
"""

DEPARTMENT = "Sports & Outdoors"
RATE = 0.002259
