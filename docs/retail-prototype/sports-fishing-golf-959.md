# Sports & Outdoors, fishing and golf, slice 1 (gen#959)

The retail `Sports & Outdoors` department held 1,093 SKUs at the ceiling build against the 11,000
of `docs/catalogue-mix-837.md`, and sold no fishing or golf product, so a search for `golf balls`
or a `fishing reel` found nothing. Slice 1 adds two families of three types each, every type a
spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Fishing Rod | `type_specs/fishing_rod.py` | Sports & Outdoors > Fishing > Fishing Rods | spinning, casting, fly | color x length (cm) |
| Fishing Reel | `type_specs/fishing_reel.py` | Sports & Outdoors > Fishing > Fishing Reels | spinning, baitcasting, spincast | color x reel size |
| Tackle Box | `type_specs/tackle_box.py` | Sports & Outdoors > Fishing > Tackle Boxes | cantilever (two), drawer, hip roof | color x size |
| Golf Club | `type_specs/golf_club.py` | Sports & Outdoors > Golf > Golf Clubs | driver, fairway wood, 7 iron, sand wedge, putter | color x handedness |
| Golf Ball | `type_specs/golf_ball.py` | Sports & Outdoors > Golf > Golf Balls | 2-piece, 3-piece (two), 4-piece | color x pack of 3, 12, 24 |
| Golf Glove | `type_specs/golf_glove.py` | Sports & Outdoors > Golf > Golf Gloves | cabretta leather (two), synthetic, hybrid | color x size S to XL |

The paths and the two invented brands of the families (Pennywhistle Angling and Larchmere Golf,
beside the department's own brands) are in `fishing_golf_rows.py`. Every type offers the six main
colors of gen#275 across its templates. A fishing rod's power (light, medium, heavy) exports as
`rod_power`, not as the shared `power` key, which the export publishes as a power source.

**Drawings.** `kit_fishing_golf.py` draws six shapes. `fishing_rod` takes `rod_type`: guides hang
under a spinning blank, sit on a casting blank with a trigger grip, and a fly rod has snake guides
and its reel seat at the end. `fishing_reel` takes `reel_type` (spinning, baitcasting, spincast),
`tackle_box` takes `tackle_type` (cantilever, drawer, hip roof), `golf_club` takes `club_type`
(driver, fairway wood, iron, wedge, putter), `golf_ball` takes `construction`, and `golf_glove`
takes `material` (cabretta leather, synthetic, hybrid). Each param is the lower-cased attribute
value, so a derived style that swaps the value is drawn true (gen#512).

**Breadth.** These are the department's first derivable types: the scaled build draws more styles
from each by the values its title shows (a rod's power, blank material and kind; a reel's body
material, bearings and kind), so the department grows without a hand-written row per style. The
earlier Sports & Outdoors types stay out of the derivation.

**Decoys.** Each type carries two class-8 text-match decoys in
`feature_decoys/fishing_golf_959.py`: a product of another department whose title holds the
shopper's words, such as a `Fishing Rod Print T-Shirt` or a `Golf Club Print Beach Towel`. No
title or description names a color.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. Fitness,
team and racket sports (slice 2) and outdoors and winter sports (slice 3) are later slices of
gen#959. The guards are in `tests/test_retail_sports_959.py`.
