# Jewellery and watches (gen#1113)

Cut 1 is stud earrings, bangles and cufflinks. Cut 2 is pendants, anklets and watch straps, and it
makes the jewellery and watch types derivable. Cut 3 is charms, brooches and jewellery boxes. Cut 4
is jewellery sets, kids' watches, and the sports and dress styles of the analog and digital watches.

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

`tests/test_retail_jewellery_range_1113.py` held a floor of 2,000 SKUs on the range, the axes of
each new type and the fixed build of each derived style.

## Cut 3: charms, brooches and jewellery boxes

| Type | Spec | Path | Styles | SKU axis |
|---|---|---|---|---|
| Charm | `type_specs/charm.py` | Womens > Jewellery > Charms | heart (two), star, moon, cross, four leaf, paw print, barrel bead, six birthstones | metal; a stone style states `stone` and its `birthstone` month |
| Brooch | `type_specs/brooch.py` | Womens > Jewellery > Brooches | flower, bee, bow, leaf, pearl cluster, five oval stones | metal; a stone style states `stone` |
| Jewellery Box | `type_specs/jewellery_box.py` | Womens > Jewellery > Jewellery Boxes | mirror lid (two), drawers (two), case (two), travel case (two) | color of the covering, the six main colors across the styles |

A charm states its `charm_style` and its `fastening`: a lobster clasp, or threaded for a bead. A
brooch states its `brooch_style` and a pin with a safety catch. A jewellery box states its
`box_style`, `material`, `compartments`, `mirror` and `lock`; `mirror` is Yes only on the style
that draws a mirror.

**Drawings.** `charm` takes `motif` (heart, star, moon, cross, clover, paw, bead, stone), plus a
`stone`: a charm hangs from a lobster clasp, and a bead is threaded on a strand. `brooch` takes
`motif` (flower, bee, bow, leaf, pearl, stone), plus a `stone`, drawn over the ends of its pin.
`jewellery_box` takes `style` (case, mirror, drawers, travel). A stone the kit has no color for
is refused. All three stand upright. Charm and Brooch are `main_colors.EXCEPTIONS` entries, as
the other jewellery is; a jewellery box is colored, so it carries the six main colors.

**Derived styles.** The three types are derivable. A derived style keeps its template's motif,
stone, box style, material, compartments, mirror and lock (`scale_text.JEWELLERY_KEYS` gains
`charm_style`, `brooch_style`, `box_style`, `compartments`, `mirror` and `lock`).

**Decoys.** A silver heart charm with a gold tone edge ("gold charm"); one star charm sold to add
to a charm bracelet ("charm bracelet"); a silver bee brooch with gold tone wings ("gold brooch");
a pearl brooch made to match pearl earrings ("pearl earrings"); a black jewellery box with white
stitching ("white jewellery box"); an earring organizer box ("earrings").

**No other record changes.** A model name a template's text already uses is never a derived
range name (`line_grammar.deals`, #851). The first draft's "four leaf clover" and "six petal"
took Clover and Petal from the baby monitor, crib and bra range names, and 469 records of those
types were renamed. The rows say "lucky four leaf" and "six rounded lobes" instead. A diff of
every ceiling record against main now shows 99 records added, all of the three types, and none
lost or changed.

### The count after cut 3

Retail ceiling build, seed 0, main 76558518 against this cut.

| Type | Before | After |
|---|---:|---:|
| Charm | 0 | 128 |
| Brooch | 0 | 89 |
| Jewellery Box | 0 | 64 |
| The other 16 types | 2,028 | 2,028 |
| **The range** | **2,028** | **2,309** |

`tests/test_retail_jewellery_range_1113.py` holds a floor of 2,300 SKUs on the range.
`tests/test_retail_jewellery_cut3_1113.py` holds each new type's axes, its drawing params and
"charm", "birthstone charm", "brooch", "pearl brooch", "jewellery box" and "travel jewelry case"
ranking the type first.

## Cut 4: jewellery sets, kids' watches, sports and dress watches

| Type | Spec | Path | Styles | SKU axis |
|---|---|---|---|---|
| Jewellery Set | `type_specs/jewellery_set.py` | Womens > Jewellery > Jewellery Sets | polished disc, heart (three), pearl (two), five stone sets; a necklace and earrings, or a set of three with a bracelet | metal; a stone set states `stone` |
| Kids Watch | `type_specs/kids_watch.py` | Kids > Watches | time teacher and digital faces, Unisex | strap color, the six main colors across the styles; `case_mm` is the one size of a style |

A jewellery set states `set_contents` (Necklace and Earrings, or Necklace, Earrings and Bracelet),
`piece_count` and `set_style`. A kids' watch states `watch_type`, `display`, a silicone `strap`
and `water_resistance`.

**Sports and dress watches** are styles, not types. Every Analog Watch and Digital Watch row now
states `watch_style`. Analog Watch: Dress (9 records, a thin case on leather or mesh), Sports (14:
8 chronographs, 6 dive watches), Field (3) and Everyday (16). Digital Watch: Sports (11) and
Everyday (14). A sports style is water resistant to at least 100 m.

**Drawings.** `jewellery_set` takes `pieces` (2 or 3) and `motif` (plain, heart, pearl, stone),
plus a `stone`; each piece shows the motif. `kids_watch` takes `face` (teacher, digital).
`analog_watch` gains `dial` (plain, chrono, dive) and a `silicone` strap drawn with its holes. A
chronograph or dive title draws that dial. A plain dial is left out of the params, so the
existing records keep theirs. Jewellery Set is a `main_colors.EXCEPTIONS` entry, as the other
metal jewellery is. Both new shapes stand upright.

**Derived styles.** Both new types are derivable. A derived style keeps its template's pieces,
motif, stone, face, watch style and water resistance (`scale_text.JEWELLERY_KEYS` gains
`set_contents`, `set_style`, `watch_style` and `water_resistance`).

**Decoys.** A silver heart set with gold tone edges ("gold jewellery set"); a disc pendant
and earrings set made to match a bracelet that is not included ("bracelet"); a kids' watch with pink
numbers on another strap color ("pink kids watch"); a kids' watch with no alarm ("kids watch with
alarm").

**Necklace weight.** The sets put "necklace" in many more titles, and each extra title lowers the
word's weight on the text baseline. With "necklace" in each set's description too, a sterling
silver keyring ranked first for "silver necklace" (`tests/test_retail_jewellery_watches_423.py`).
A set's description now says "a pendant on a fine chain", and only the 2-piece titles say
"necklace". A Necklace ranks first again, but by a margin of 0.18 (20.35 against 20.17), so a
later cut that adds necklace text should run that test.

**Other record changes.** A diff of every ceiling record against main shows 91 records added
(38 Jewellery Set, 26 Kids Watch, 21 Analog Watch, 6 Digital Watch) and none lost. 40 existing
Analog Watch and Digital Watch records gain the `watch_style` attribute. Three of them also take
another brand or range name. The new rows bring new brands into each watch type's pool, so these
derived styles draw differently: a woven fabric strap watch, a sports digital watch and a leather
strap watch.

### The count after cut 4

Retail ceiling build, seed 0, main 301759df against this cut.

| Type | Before | After |
|---|---:|---:|
| Jewellery Set | 0 | 110 |
| Kids Watch | 0 | 74 |
| Analog Watch | 165 | 336 |
| Digital Watch | 134 | 170 |
| The other 17 types | 2,010 | 2,010 |
| **The range** | **2,309** | **2,700** |

The range now counts the Kids path too, where only Kids Watch sits.
`tests/test_retail_jewellery_range_1113.py` holds a floor of 2,690 SKUs on the range.
`tests/test_retail_jewellery_cut4_1113.py` holds each new type's axes, its drawing params, every
watch's style, and "jewellery set", "necklace and earrings set", "kids watch", "time teacher
watch", "dress watch", "sports watch" and "chronograph watch" each ranking its type or style
first.

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

Nothing: the range's types are all built, and its count is recorded on gen#837. Before gen#1113 the
range held 367 SKUs on the ceiling build; after its four cuts it holds 2,700 (+2,333). The SKUs
each type added are rows of the table in
[catalogue-mix-837.md](../catalogue-mix-837.md#counts-added-by-the-gap-issues), which
`tests/test_retail_jewellery_range_1113.py` holds against the build.
