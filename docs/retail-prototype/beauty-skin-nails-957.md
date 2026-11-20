# Beauty: facial cleansers, deodorants and nail polish (gen#957)

The 500K mix ([catalogue-mix-837.md](../catalogue-mix-837.md)) plans 14,000 `Beauty` SKUs, and
gen#957's Done when asks for at least 13,300 at the ceiling build. After hair care
([beauty-hair-957.md](beauty-hair-957.md)) and oral care and shaving
([beauty-oral-shave-957.md](beauty-oral-shave-957.md)), main's ceiling build held 11,191. The
department had no facial cleanser, deodorant or nail polish, so a search for `foaming face wash`,
`roll-on deodorant` or `red nail polish` found nothing. This slice adds `Beauty > Skincare >
Cleansers`, `Beauty > Body Care > Deodorants` and `Beauty > Nails > Nail Polish`.

## The three new types

Each type is a spec of its own and is derivable. The shared paths and brands are in
`skin_rows.py`. A nail polish is built by `hair_rows.row()` and sold in the six main colors
(gen#275). A cleanser and a deodorant are colorless, like a toothpaste: the bottle, tube, can or
jar is the pack.

| Type | Spec | Title-shown values (the derived pools) | SKU option |
|---|---|---|---|
| Facial Cleanser | `type_specs/facial_cleanser.py` | texture (Foaming, Gel, Oil, Micellar, Balm, Clay) and skin type (Oily, Dry, Sensitive, Combination, Normal, Blemish-Prone) | `net_volume_ml`: 100, 150, 200 |
| Deodorant | `type_specs/deodorant.py` | scent (Unscented, Citrus, Sandalwood, Aloe Vera, Sea Breeze, Cedarwood) and applicator (Roll-On, Stick, Spray, Gel) | `units_per_pack`: 1, 2, 3 |
| Nail Polish | `type_specs/nail_polish.py` | wear (Quick Dry, Long Wear, Chip Resistant, Strengthening) and finish (Gloss, Matte, Shimmer, Glitter, Metallic, Gel Effect) | `net_volume_ml`: 5, 10, 15, times the six colors |

A derived style keeps its template's description, so no description names a texture, an
applicator, a finish or a wear: a derived `Gel` cleanser never reads as an oil. No key is
`form`, a key the said-value gate (`SAID_ATTRIBUTES` in `tests/test_retail_scale.py`) holds for
other types. No value is a color word (`colorwords.COLOR_WORDS`): the textures leave out
`Cream`, and the scents leave out `Lavender` and `Rose`.

Each type has two text-match decoys (gen#309). The class 4 decoy names a color its fields do not
hold (`Gel Facial Cleanser with Pink Grapefruit`, in a pale blue pack; `No White Marks Gel
Deodorant`, in black; `Quick Dry Gloss Nail Polish with a Red Brush Tip`, in blue). The class 6
decoy has a color word in its range name (`Green Fern`, `Blue Ridge`, `Pink Lagoon`). Each decoy
is sold under one of the department's invented brands (gen#720), so it needs no new house style.

## Drawings

`kit_skin.py` draws three shapes: `facial_cleanser`, `deodorant` and `nail_polish`. A
cleanser's or deodorant's pack color fills its bottle; a polish's SKU color fills the glass. Each
title-shown value changes the figure, so a derived style that swaps a value is drawn the way its
title reads (gen#512):

- a cleanser's `texture` draws the pack (a foam pump bottle, a tube on its flip cap, a slim oil
  pump bottle, a tall bottle with a flip cap, a low jar, a tall jar with grains); its `skin_type`
  is printed under the product word;
- a deodorant's `applicator` draws the pack (a domed roll-on, an oval stick on its twist base, a
  can under its actuator, a clear gel stick with a window); its `scent` colors the band and is
  printed on it;
- a polish's `finish` draws the glass's sheen (a gloss streak, a flat coat, sparkles, glitter
  flecks, metal bands, a domed gel top); its `wear` draws the cap (short and wide, tall and slim,
  ribbed, ringed).

## Measured

The department's SKU and style counts at the ceiling build (seed 0) are read from the build
(`retail_figures`), never typed here (`test_retail_figures_162`). This slice adds about 3,500
Beauty SKUs, most of them derived nail polish, and no other department's count moves.

`tests/test_retail_beauty_skin_nails_957.py` holds the slice's Done-when: a floor of 13,300
Beauty SKUs (the issue's Done when), each type under its own leaf, unique ids, titles, twin keys
and SKU ids, determinism, the six main colors on every polish, a figure per param value, drawings
that match the title, and a golden slice.

The next slice is left: wider Serum, Mascara and Body Mist by authored styles (they stay
non-derivable, as `tests/test_retail_beauty_214.py` holds them).
