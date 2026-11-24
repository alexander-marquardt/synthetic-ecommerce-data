# Jewellery and watches, cut 1: stud earrings, bangles and cufflinks (gen#1113)

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

**Templates only.** These rows are templates that the scaled build does not derive from, like
gen#423's jewellery. A derived stone style would rewrite the stone in a stud's title but not its
pearl drawing, so deriving the jewellery types is a later cut. That later cut is the one that
reaches the issue's count.

**Decoys.** Each type has two in-department text-match decoys whose fields contradict a query
word. One is a silver stud on a gold tone back for "gold stud earrings". Another is a glass bead
in a pearl effect for "pearl stud earrings". The bangle decoys are a silver bangle with a gold
tone band for "gold bangle" and a single wide bangle for "stacking bangles". The cufflink decoys
are gold cufflinks on a silver tone bar for "silver cufflinks" and an enamel inlay for "onyx
cufflinks".

## The demo queries

Each query of the issue is held in `tests/test_retail_jewellery_1113.py`, on the family it should
find:

| Query | Expected family | Held by |
|---|---|---|
| gold hoop earrings | Hoop Earrings (and the legacy Earrings) with a gold metal SKU | the text rank, and the `metal` of a hoop SKU |
| silver necklace 18 inch | Necklace, a Sterling Silver or Stainless Steel SKU of `length_cm` 45 (18 inches is 45.7 cm) | the fields: the words alone rank a pedestal fan of 18 inches first, so a policy reads the unit |
| ring size N | Ring, a SKU of `ring_size_uk` N (US 7) | the fields: the letter is a size, which a policy reads |
| watch | Analog Watch, Digital Watch or Watch, ahead of the Smartwatch styles | the text rank |

## What comes next

These types and axes are still to come:

- pendants, anklets, charms, brooches, jewellery sets and jewellery boxes;
- kids', sports and dress watches and watch straps (case size, strap material and water
  resistance are axes already);
- deriving the jewellery types, so the range reaches the issue's +2,000 SKUs;
- the count on gen#837 once the range is built.
