# Sports & Outdoors, fitness, team and racket sports, slice 2 (gen#959)

Slice 1 (`docs/retail-prototype/sports-fishing-golf-959.md`) took the retail `Sports & Outdoors`
department to about 3,300 SKUs at the ceiling build, against the 11,000 of
`docs/catalogue-mix-837.md`. Slice 2 adds nine breadth types under the department's existing
Yoga & Fitness and Team & Racket Sports families, every type a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Exercise Bike | `type_specs/exercise_bike.py` | Sports & Outdoors > Yoga & Fitness > Exercise Bikes | magnetic upright, magnetic recumbent, friction folding, air upright | color x maximum load (kg) |
| Weight Plate | `type_specs/weight_plate.py` | Sports & Outdoors > Yoga & Fitness > Weights > Weight Plates | cast iron, rubber coated (two), urethane | color x weight (kg) |
| Weight Bench | `type_specs/weight_bench.py` | Sports & Outdoors > Yoga & Fitness > Weight Benches | flat, adjustable (two), decline | color x maximum load (kg) |
| Basketball | `type_specs/basketball.py` | Sports & Outdoors > Team & Racket Sports > Basketballs | rubber, composite (two), full-grain leather | color x ball size |
| Volleyball | `type_specs/volleyball.py` | Sports & Outdoors > Team & Racket Sports > Volleyballs | synthetic (two), microfiber, rubber | color x ball size |
| Shin Guard | `type_specs/shin_guard.py` | Sports & Outdoors > Team & Racket Sports > Shin Guards | slip-in (two), ankle, sleeve | color x size XS to XL |
| Hockey Stick | `type_specs/hockey_stick.py` | Sports & Outdoors > Team & Racket Sports > Hockey Sticks | ice (two), street (two) | color x handedness |
| Pickleball Paddle | `type_specs/pickleball_paddle.py` | Sports & Outdoors > Team & Racket Sports > Pickleball Paddles | graphite, fiberglass, carbon fiber, wood | color x grip size |
| Table Tennis Bat | `type_specs/table_tennis_bat.py` | Sports & Outdoors > Team & Racket Sports > Table Tennis Bats | control, allround (two), offensive | color x handle shape |

The paths are in `fitness_team_rows.py`. The rows use the department's own brands, so no brand
joins the scale roster and `range_ownership.py` is unchanged. Every type offers the six main
colors of gen#275 across its templates. The gate plan named soccer balls; footballs (gen#368)
already are soccer balls, so hockey sticks take their place.

**Titles.** Each type's title shows three values, the third a word a shopper reads on the shelf:
an exercise bike's console (LCD, Touchscreen), a weight plate's grip (Solid, Tri-Grip, Dual-Grip),
a bench's grade (Home, Commercial), a ball's grade (Official, Training, Recreational), a shin
guard's profile (Low-Profile, Reinforced), a hockey stick's curve (Mid, Heel, Toe), a paddle's
shape (Elongated, Widebody) and a table tennis bat's rubber (Smooth, Pimpled, Tacky). A table
tennis bat's handle shape (flared, straight, anatomic) is its SKU axis, a fit and not a size.

**Drawings.** `kit_fitness_team.py` draws nine shapes, each taking one param, the lower-cased
attribute value, so a derived style that swaps the value is drawn true (gen#512):
`exercise_bike` takes `bike_style`, `weight_plate` `material`, `weight_bench` `bench_type`,
`basketball` `cover`, `volleyball` `play`, `shin_guard` `guard_type`, `hockey_stick`
`hockey_type`, `pickleball_paddle` `face` and `table_tennis_bat` `blade`. A basketball and a
volleyball turn at any angle, an exercise bike and a bench lie level, and the other five stand
upright (`orientations/fitness_team.py`, gen#849 and #1045). A weight plate's weight, a ball's
size and a shin guard's size are size axes (`size_axes.py`, gen#719); a bench's or a bike's maximum load is a
rating, and a paddle's grip, a stick's hand and a bat's handle are fits.

**Breadth.** The scaled build draws more styles from each type by the three values its title
shows. The department's rate is recomputed as `department_rates/sports_outdoors.py` says: 0.002259,
the rate that gives its target share of derived styles (1.09% with the slice's templates) with
every other rate held. At slice 1's 0.001726 it drew 0.83%. The rate moves no style of the ceiling
build, where every template is drawn until it is exhausted.

**Decoys.** Each type carries two class-8 text-match decoys in
`feature_decoys/fitness_team_959.py` (DY9603 to DY9620): a product of another department whose
title holds the shopper's words, such as a `Basketball Print T-Shirt` or a `Hockey Stick Print
Beach Towel`. No title or description names a color. "bat" already names Baseball Bats and
"tennis" Tennis Rackets, so the table tennis bat decoys are found by "table", and the exercise bike
decoys by "exercise" ("bike" is the bicycles' word); `tests/decoy_true_nodes/fitness_team.py` maps
each noun to its node. `fitness_team_959.ids()` keeps them out of the apparel decoys' exemplars and
out of the kids' films neighbours, as slice 1's are.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. Slice 2's
floor is 7,000 SKUs; outdoors and winter sports (slice 3) are the last slice of gen#959. The guards
are in `tests/test_retail_sports_959.py`.
