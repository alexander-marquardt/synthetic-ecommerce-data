# Sports & Outdoors (gen#368)

Every Sports & Outdoors type carries at least two decoys: a product
of another department, an existing type of the catalog, whose title holds the shopper's word for the
sports product (a block-heel shoe for "yoga block", a lantern-sleeve blouse for "camping lantern", a
crystal tennis bracelet for "tennis racket"). A row names its sports type in `target`, holds no
color word in its title or description, and is fixed by the department policy (the `Sports & Outdoors`
department drops it). `tests/test_retail_sports_decoys_368.py` walks the live catalog's Sports &
Outdoors types, so a new type reds until it has two decoys or an entry in `SPORTS_EXEMPT` that names
its follow-up issue. `SPORTS_EXEMPT` has been empty since gen#375 gave the seven first-increment types
(tents, sleeping bags, camping chairs, yoga mats, dumbbells, kettlebells, foam rollers) their two
decoys each, in `feature_decoys/sports_first_increment.py` (a tent dress and a tent stitch cushion,
a sleeping cat cushion and a sleeping beauty doll, camping club and camping trip rows, yoga leggings
and a yoga candle, dumbbell and kettlebell prints, a foam hand wash and foam sole sandals), and a test
pins it empty. The prototype's plural strip reads
"tennis" as "tenni", so the noun of those two rows is `tenni`. The picnic blanket of gen#217 (Camping)
carries two rows of its own (`picnic`), beside the two decoys of `decor_rows.py`.
