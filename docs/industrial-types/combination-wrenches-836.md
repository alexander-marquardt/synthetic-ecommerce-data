# Combination wrenches: prices (gen#836)

The combination wrenches keep their 158 census prices the same way the roller chain keeps its 71 (see the price section of the README), and since the census has within-page pairs for them, their slope on the size is the census's (0.647). What their kind multiplies the price by is GENERATED (`combination_wrenches.PRICE`: ratcheting 1.8x, long pattern 1.3x, stubby 0.9x a standard wrench); the census's prices are not split by kind.

## Sizes (#50)

A line stocks a contiguous run of the hex widths across flats its kind makes. The run's start rotates over the lines of one kind and unit system. On its own, that rotation starts at the short end of the pool, and a key gets only about three lines, so the long sizes depended on how many variants a line drew: 9 of 12 seeds from the default had no 3/4" wrench. So the type's first eight inch lines start their runs at the breadth row's sizes in turn (`combination_wrenches.BREADTH_SIZES`: 1/4" to 3/4"), and the rotation picks the start of every later line. No random draw changes. `test_the_breadth_rows_sizes_are_offered_whatever_the_seed` builds 12 seeds and finds every breadth size on each.
