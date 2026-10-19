# Retail babywear and nursery: sleepsuits, bodysuits, snowsuits, puddlesuits, all-in-ones, blankets, mats, caddies, storage (gen#213)

The Baby audience held no babywear basics and no nursery textiles. Nine type specs under
`prototypes/retail_drawings/type_specs/` add them; `kit_baby.py` draws each as a shape of its own
and `babywear_rows.py` holds the shared colors, age sizes, row builders and decoy helper. None is
derived: authored rows only. Every brand is invented.

| Type | Path | SKU axes | Key attributes (structured, in the export) |
|---|---|---|---|
| Sleepsuit | Kids > Baby > Sleepsuits | color x age size x pack (1, 2, 3) | feet, sleeve, fastening, fabric, season, pack size |
| Baby Bodysuit | Kids > Baby > Bodysuits | color x age size x pack (3, 5, 7) | sleeve, neck, fabric, season, pack size |
| Snowsuit | Kids > Baby > Snowsuits & Pramsuits | color x age size | fill, hood, fold-over mitts, fold-over feet, season |
| Puddlesuit | Kids > Baby > Puddlesuits | color x age size | waterproof rating, lining, hood, season |
| All-in-One | Womens, Mens or Kids > Nightwear > All-in-Ones | color x size | fabric, hood, season |
| Baby Blanket | Home > Nursery > Baby Blankets | color | blanket type, blanket size, fabric |
| Changing Mat | Home > Nursery > Changing Mats | color | wipe clean, compartments, mat size |
| Nappy Caddy | Home > Nursery > Nappy Caddies | color | compartments, wipe clean, caddy size |
| Nursery Storage | Home > Nursery > Nursery Storage | color | storage type, fabric |

Age sizes are `Newborn`, `0-3 Mths` to `18-24 Mths` (babywear) and `Yrs` (older children). The
Combined loader does not yet read the months: that is
elastic/prism-industrial-products#592, to merge before this catalog is loaded.

A drawing shows what the record states: feet, sleeve, fastening, neck, hood, mitts, lining, weave,
blanket size, wipe-clean surface, pocket count, storage kind (`tests/test_retail_babywear_213.py`
pairs each attribute with its drawing parameter). No baby drawing prints a size or a pack count.

## Decoys

A clothing type (sleepsuit, bodysuit, snowsuit, puddlesuit, all-in-one) carries the apparel decoy
plan of gen#311 (three compound words, such as a "romper" or "babygrow" sleepsuit; the table is
`retail-apparel-decoys.md`). A nursery type has no apparel plan, so each carries four hand-authored
text-match decoys of gen#294, in the classes where a nursery title can mislead: 1 (a color on the
trim, not the product), 2 (a sibling's word, "changing bag", "nappy bag"), 3 or 4 (a size or a
feature named on a part, not the product: a "cot bed" print on a pram blanket, a "waterproof"
pouch on a mat that is not) and 6 or 7 (a name that is a brand or a range, "Bear Hill",
"Thistle & Wren"). A decoy's trigger word is true of a real part or of the shown name, and its
description never denies its title (gen#404; `tests/test_retail_babywear_213.py`). Four per type puts every class a baby search plausibly hits in the
node without outweighing the three to four real styles.

The checks are `tests/test_retail_babywear_213.py`; the mutation rows are
`scripts/mutation_rows_babywear_213.py` (`--only "babywear:"`).
