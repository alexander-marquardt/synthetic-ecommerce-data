# Jewellery and watches (gen#1113)

Cut 1 is stud earrings, bangles and cufflinks. Cut 2 is pendants, anklets and watch straps, and it
makes the jewellery and watch types derivable.

## Cut 1: stud earrings, bangles and cufflinks

gen#1113 asks for a real jewellery and watch range in Womens and Mens accessories. It names the
missing types, each with axes a shopper can filter on, and a target of about +2,000 SKUs. Main
already had four of the axes:

- metal (`metal`, one SKU per metal) on every jewellery row since gen#207;
- stone (`stone`) on the stone rings, necklaces and earrings;
- necklace length (`length_cm`);
- ring size (`ring_size_uk` letters beside `ring_size_us`).

What it lacked was the types. Cut 1 adds three of them. Each is a spec of its own with a
drawing of its own in `kit_jewellery.py`:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Stud Earrings | `type_specs/stud_earrings.py` | Womens > Jewellery > Earrings > Stud Earrings | ball (two), cubic zirconia, pearl, knot, sapphire, amethyst, emerald | metal; a stone style states `stone` |
| Bangle | `type_specs/bangle.py` | Womens > Jewellery > Bracelets > Bangles | plain (two), hammered, twisted (two), stacking set of three | metal x size (Small, Medium, Large) |
| Cufflinks | `type_specs/cufflinks.py` | Mens > Jewellery > Cufflinks | round, square (two), knot, onyx, lapis lazuli | metal; a stone style states `stone` |

**Drawings.** `stud_earrings` takes `stud` (ball, gem, pearl, knot), plus a `stone` for a gem.
`bangle` takes `style` (plain, hammered, twisted, stacked). `cufflinks` takes `face` (round,
square, knot, stone), plus a `stone` for an inlay. All three stand upright
(`orientations/jewellery.py`). The color of each is its metal, so each type is a
`main_colors.EXCEPTIONS` entry, as the hoop and drop earrings are. A bangle's size is its size
axis (`size_axes.py`).

**Decoys.** Each type has two in-department text-match decoys whose fields contradict a query
word. One is a silver stud on a gold tone back for "gold stud earrings". Another is a glass bead
in a pearl effect for "pearl stud earrings". The bangle decoys are a silver bangle with a gold
tone band for "gold bangle" and a single wide bangle for "stacking bangles". The cufflink decoys
are gold cufflinks on a silver tone bar for "silver cufflinks" and an enamel inlay for "onyx
cufflinks".

## Cut 2: pendants, anklets, watch straps, and a derived range

| Type | Spec | Path | Styles | SKU axes |
|---|---|---|---|---|
| Pendant | `type_specs/pendant.py` | Womens > Jewellery > Pendants | heart (two), star, moon, cross (two), disc, pearl, cubic zirconia, nine birthstones | metal x `length_cm` (40, 45, 50); a stone style states `stone`, a birthstone also its month |
| Anklet | `type_specs/anklet.py` | Womens > Jewellery > Anklets | chain (two), beaded (two), disc charms, double chain | metal x `length_cm` (23, 25) |
| Watch Strap | `type_specs/watch_strap.py` | Womens and Mens > Watches > Watch Straps | leather, silicone, woven fabric, mesh, for each audience | color x `lug_mm` (14, 16, 18 in Womens; 18, 20, 22 in Mens) |

**Drawings.** `pendant` takes `charm` (heart, star, moon, cross, disc, pearl, stone), plus a `stone`.
`anklet` takes `style` (chain, beaded, charm, double). `watch_strap` takes `material` (leather,
silicone, fabric, mesh).

**Derived styles.** The scaled build derives styles from the jewellery and watch types: the three
above, cut 1's three, hoop and drop earrings, analog and digital watches, and the necklaces,
bracelets and rings of `accessory_rows.py`. A derived style has another brand, range name and price.
It keeps its template's stone, style, strap and drawing (`scale_text.JEWELLERY_KEYS`), because a
pearl stud with an amethyst title would still draw a pearl. A derivable row may not
carry one of clothing's invented brands (`EXTRA_BRANDS`), so 13 necklace, bracelet and ring rows
moved to the jewellery brands. The fitness band and the legacy Earrings and Watch are unchanged.

**The color is the metal.** Necklace, Bracelet and Ring are `main_colors.EXCEPTIONS` entries now, as
the other jewellery is. Before, the main-color pass added SKUs in black, blue, green, red,
white and yellow to 18 of their styles, each with a gold or silver metal. Those SKUs are gone.

### The count

Retail ceiling build, seed 0, main 5ea1291a against this cut. All SKUs are in Womens or Mens.

| Type | Before | After |
|---|---:|---:|
| Pendant | 0 | 492 |
| Watch Strap | 0 | 468 |
| Analog Watch | 63 | 165 |
| Digital Watch | 38 | 134 |
| Ring | 83 | 140 |
| Bangle | 51 | 123 |
| Anklet | 0 | 112 |
| Bracelet | 58 | 102 |
| Necklace | 47 | 80 |
| Stud Earrings | 22 | 54 |
| Hoop Earrings | 15 | 37 |
| Drop Earrings | 15 | 37 |
| Cufflinks | 16 | 36 |
| Fitness Band | 36 | 36 |
| Watch | 8 | 8 |
| Earrings | 4 | 4 |
| **The range** | **456** | **2,028** |

`tests/test_retail_jewellery_range_1113.py` holds a floor of 2,000 SKUs on the range, the axes of
each new type and the fixed build of each derived style.

## The demo queries

Each query of the issue is held in `tests/test_retail_jewellery_1113.py`, on the family it should
find. Cut 2's test file holds "pendant necklace", "anklet" and "watch strap" the same way. It does
not hold "leather watch strap": the words alone rank a "Mens Leather Strap Watch" first, so a policy
reads the type.

| Query | Expected family | Held by |
|---|---|---|
| gold hoop earrings | Hoop Earrings (and the legacy Earrings) with a gold metal SKU | the text rank, and the `metal` of a hoop SKU |
| silver necklace 18 inch | Necklace, a Sterling Silver or Stainless Steel SKU of `length_cm` 45 (18 inches is 45.7 cm) | the fields: the words alone rank a pedestal fan of 18 inches first, so a policy reads the unit |
| ring size N | Ring, a SKU of `ring_size_uk` N (US 7) | the fields: the letter is a size, which a policy reads |
| watch | Analog Watch, Digital Watch or Watch, ahead of the Smartwatch styles | the text rank |

## What comes next

These types are still to come:

- charms, brooches, jewellery sets and jewellery boxes;
- kids', sports and dress watches (case size, strap material and water resistance are axes already);
- the final count on gen#837 once they are built.
