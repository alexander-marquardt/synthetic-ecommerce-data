# Hand files: a deep type on conventional lengths (gen#836)

`Hand Tools > Files & Rasps > Hand Files` was a breadth row of two SKUs. It is now a modelled type, `product_types/hand_tools/hand_files.py`, and `tests/test_type_hand_files.py` runs the per-type gates over it.

**Titles.** A line is one shape, and its noun names that shape as a distributor titles it: "Flat File", "Half Round File", "Hand File" (`hand_files.item`). "Hand" is itself a shape, so a flat file titled "Hand File" would name the wrong one.

**Price.** The hand files keep the census's 118 prices (`price.DEEPENED_CENSUS`), as the roller chain does. Unlike the roller chain's, their slope on the length is measured: the census has within-page pairs for them (0.947, `hand_files.PRICE`).
