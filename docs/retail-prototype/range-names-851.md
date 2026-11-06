# Range names with no number, and a color as a SKU (#851)

A derived style of a line-grammar family used to take a model of a lead word, a sub-model and a
generation number. On a cup set that read "Brackenmere Home Supper 6 Set of 4 Porcelain Espresso
Cups in Gift Box, Black", next to "Supper 9 …, Green" from the same brand. No retailer names a cup
set that way. Each of those was also a product of one SKU, split from the brand's grouped
product by a color and a numbered range alone.

**A derived range is a plain word.** Outside the cleaning and beauty families, a derived style's
model is one of its brand's lead words alone, "Larchwood Living Gather Set of 4 Porcelain
Espresso Cups in Gift Box" (`line_grammar.Deal.owned`). A lead word that any template's title,
description, brand or attribute value also uses is not dealt (`line_grammar.text_words`):
without a number, "Toast" would be the range of "for toast, cake or a starter", and "Bright" of
"Bright Orange Crew Neck Tee". So the families gained words no text uses (storage, kitchen,
lighting, sport and tools), and eight words a description used were replaced (Feather, Border,
Patio, Grow, Whisk, Roast, Starter, Smooth). An authored model, and a cleaning or beauty model, may
still carry a sub-model and a number. `line_grammar.is_model` reads a lead word alone as a model.

**A color is a SKU, not a product.** A derived style whose title-shown values its template, or
an earlier sibling, already shows used to carry its hero color alone, with the color named in
its title. It now carries every color of its template, hero first, and its title names none
(`scale._draw`). So it is its brand's one product of the kind. A second one from the same brand
would be a twin (`scale_text.twin_key`), so the build makes none, and different brands stay
separate products. A cleaning or beauty style (a lipstick shade, a scent) keeps the older rule
until those families drop their numbers.

**The report.** `scale --report` has `single_sku_kinds`: each product type where most products
have one SKU although one of its products has two colors or sizes, with its counts.

At the ceiling build the build has fewer products and more SKUs (`scale --report` measures them;
a total is never typed here, `tests/test_retail_figures_162.py`). The numbered ranges left are the
cleaning and beauty models. Cup
sets and travel cups are one product per brand, each with several colors as its SKUs.

**A mug is sold in several glazes.** Each plain mug of the mug print line (`prints.py`, line
`MUG`) had one glaze and each graphic mug one ground, so most mugs were one-SKU products. A plain
style may now carry several colors (`prints._glazes`): each plain mug sells three glazes, hero
first, and each graphic mug two grounds. A derived style with a new title-shown value (a graphic
mug with another motif) takes its hero color and a seeded subset of the rest
(`scale._colors`), and that subset could be empty. It now keeps one more color at least when the
template has two, so no derived style of a two-color template is a one-color product. Mug is no
longer in `single_sku_kinds`; the two one-SKU mugs left are decoys of other queries.

**A set is sold in packs, a single cup in sizes.** Every SKU of a cup set was a set of four, so a
brand's one cup set differed only by color. The cup set (`class_rows.CUPS` `DRKSET`, "Porcelain
Espresso Cup Set in Gift Box") now sells every color in a 2 pack, a 4 pack and an 8 pack
(`Style.packs`, the SKU option `pack_size`, listed on the product too), and each pack draws that
many cups (`pack_copies`, gen#728). The value is `N pack`, not "Set of 4": one `pack_size`
vocabulary (gen#246, `tests/test_pack_size_values_246.py`). A travel cup or a tumbler is not
sold in packs, so the travel cup (`DRKTRV`) and the steel tumbler (`DRKTMB`) sell every color in
350, 470 and 590 ml (12, 16 and 20 oz: `Style.capacities`, the SKU option `capacity_ml`,
exported as Capacity in ml). Their declared size axis (`size_axes.AXES`) draws a larger cup
larger (`size_ladder`). A derived style copies its template's SKUs, so each brand's set or cup
is one product with pack or capacity × color SKUs.

**A plate, bowl or glass set is sold as the cup set is.** Each plate, bowl and glass row sold in
packs (`tableware_rows.PLATES`, `BOWLS`, `GLASSES`) named its own: Single, 4 and 6 for a dinner
plate, 4 and Single for a cereal bowl, 2, 4 and 6 for a wine glass, and none of them an 8 pack.
Each now sells every color in a 2 pack, a 4 pack and an 8 pack (`tableware_rows._sets`), and each
pack draws that many items (`pack_copies`). A derived style copies them. A large single piece (the
serving platter, the salad, serving and mixing bowls) is not sold in packs and has no pack axis.
A brand may still sell two plates of one template when they differ by material or finish
(stoneware, bone china).

**An authored range is a plain word too.** The authored bra, jeans, running shoe and walking
boot rows kept their numbers after the derived ones dropped them: "Bramblewood Comfort Pro 3
Underwired Lace Plunge Bra", "Ottery Denim Original Pro 101 High Rise Cigarette Jeans",
"Stridewell Summit 2 Waterproof Walking Boots". Each authored line is now its lead word alone
(`scale_rows.py`, `variants.py`, `colorgroup_rows.py`, `needs_rows.py`, `footwear_rows.py`). Bramblewood's bras are
"Anytime", not "Comfort": a bare "Comfort" also leads another brand's title ("Comfort
High-Waisted Pants"), so the range review read one range word under two brands. Eight bras would
then share a brand, a wiring and a style with another, though they sell other band and
cup runs and colors, so each takes another word its brand is dealt: Saltmarsh's second
non-wired nursing, full cup, minimiser, post-surgery and mastectomy bras are "Haven" (its third
post-surgery bra "Nimbus"), and Bramblewood's second non-wired plunge and mastectomy bras are
"Harmony". The women's and men's walking boots share one title, as the running shoes already
did; their category paths differ. An appliance, tool or garden model ("Torque Pro") keeps its
sub-model word, with no number after it.

The guards are in `tests/test_retail_scale_range_names_851.py`,
`tests/test_retail_scale_authored_lines_851.py`,
`tests/test_retail_scale_cup_packs_851.py`, `tests/test_retail_scale_mugs_851.py` and
`tests/test_retail_scale_tableware_packs_851.py`.
