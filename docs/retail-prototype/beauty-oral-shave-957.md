# Beauty, oral care and shaving (gen#957, slice 2)

The 500K mix ([catalogue-mix-837.md](../catalogue-mix-837.md)) plans 14,000 `Beauty` SKUs. After
slice 1 ([beauty-hair-957.md](beauty-hair-957.md), hair care), main's ceiling build held 7,792.
The department had no toothbrush, toothpaste or razor, so a search for `toothbrush`, `whitening
toothpaste` or `5 blade razor` found nothing. Aftershave had three styles. Slice 2 of gen#957
adds `Beauty > Dental` and `Beauty > Shaving`, and widens Aftershave.

The node is `Dental`, not `Oral Care`: a third `... Care` sibling beside `Body Care` and `Hair
Care` with no parent that names it fails the tree guard (`tests/test_retail_tree_nesting_283.py`).

## The three new types

Each type is a spec of its own and is derivable. The shared paths and brands are in
`grooming_rows.py`. A toothbrush and a razor are built by `hair_rows.row()` and sold in the six
main colors (gen#275). A toothpaste is colorless, like a shampoo: its tube is its pack.

| Type | Spec | Title-shown values (the derived pools) | SKU option |
|---|---|---|---|
| Toothbrush | `type_specs/toothbrush.py` | bristle (Soft, Medium, Extra Soft, Firm) and power (Manual, Electric, Sonic, Battery) | `units_per_pack`: 1, 2, 4 (drawn as that many brushes by `pack_copies`) |
| Toothpaste | `type_specs/toothpaste.py` | benefit (Whitening, Sensitive, Cavity Protection, Gum Care, Enamel Repair, Fresh Breath) and flavour (Mint, Cool Mint, Spearmint, Peppermint, Herbal, Eucalyptus) | `net_volume_ml`: 75, 100, 125 |
| Razor | `type_specs/razor.py` | handle (Rubber Grip, Weighted, Slim, Ergonomic) and blades (2-Blade to 5-Blade) | `cartridges`: 2, 4, 8 |

`cartridges` is declared by the razor spec (`options=`, gen#413) and listed in
`size_axes.NOT_SIZES`. Each type has two text-match decoys (gen#309). The class 4 decoy names a
color its fields do not hold (`Manual Toothbrush with Blue Bristles`, sold in white). The class 6
decoy has a color word in its range or brand name (`White Cliff Electric Toothbrush`, sold in
blue). The template brands are the department's invented brands (gen#720). A toothpaste
decoy's brand, Red Harbour, is new and also invented. No flavour is a color word: `Charcoal` is
one (`colorwords.COLOR_WORDS`), so the sixth flavour is Eucalyptus.

## Aftershave

Aftershave grows by authored rows only. `tests/test_retail_beauty_214.py` holds the ten beauty
depth types to `derivable=False`. Three styles are added: Rosemary and Cedar Aftershave Balm
(Aromatic), Vetiver and Clove Aftershave (Smoky) and Sea Salt and Juniper Eau de Toilette for Men
(Herbal). None is Citrus, because the type's decoys target `citrus aftershave`. None is
`Fresh`, because `Ocean Fresh Eau de Toilette` would then name a family it does not hold.

## Drawings

`kit_grooming.py` draws three shapes: `toothbrush`, `toothpaste` and `razor`. The SKU's color
fills the handle or the tube. Each title-shown value changes the figure, so a derived style that
swaps a value is drawn the way its title reads (gen#512):

- a toothbrush's `power` draws the body (a slim manual stick, a thick electric body with a round
  head, a tall sonic body with a ring, a battery body with an end cap); its `bristle` colors the
  tufts;
- a toothpaste's `benefit` is printed under the product word, and its `flavour` colors the
  stripe;
- a razor's `handle` draws its form (ribbed, wide with a weight band, slim, curved); its `blades`
  draws one line per blade in the head.

## Measured

At the ceiling build (seed 0), Beauty holds 11,173 SKUs in 1,727 styles, up from 7,792 in 1,335.
Razor has 1,431 SKUs, Toothbrush 1,362, Toothpaste 579 and Aftershave 27. No other department's
count moves.

`tests/test_retail_beauty_oral_shave_957.py` holds the slice's Done-when: a floor of 9,150 Beauty
SKUs, each type under its own leaf, unique ids, titles, twin keys and SKU ids, determinism, a
figure per param value, drawings that match the title, and a golden slice.

Slice 3 is left: facial cleanser, deodorant and nail polish, and wider serum, mascara and body
mist, toward the issue's 13,300.
