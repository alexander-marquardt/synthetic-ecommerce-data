# Flowers and plants: cut flowers, letterbox flowers, house plants and plant food (gen#1115)

The ceiling build held 5 bouquets and no house plant. The 368 `Plant` SKUs were garden plants,
so a search for `roses` or a `pet safe house plant` found nothing live. The maintainer's ruling
of 2026-11-21 asks for the live side of flowers and plants. The artificial side is the WANDS
`faux_floral` (#1073, in Home). This page covers three types, all derivable and drawn by
`kit_flowers.py`:

| Type | Spec | Path | Templates | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|---|---|
| Bouquet | `type_specs/bouquet.py` | Garden > Flowers > Bouquets / Letterbox Flowers | Hand-Tied Rose, Long-Stem Rose, Spring Tulip, Scented Lily, Carnation, Gerbera, Seasonal Mixed Flower (bouquets); Rose, Tulip, Lily, Mixed Flower (letterbox) | flower (in the title) | bloom color x stem count | flower, occasion, delivery |
| House Plant | `type_specs/house_plant.py` | Garden > Plants > House Plants | Phalaenopsis Orchid, Echeveria Succulent, Christmas Cactus, Monstera Deliciosa, Peace Lily, Snake Plant, Golden Pothos, Calathea Prayer Plant, Spider Plant, Aloe Vera | pot color, brand | pot color x pot size (cm) | plant, pot material, light needs, pet safe |
| Plant Food | `type_specs/plant_food.py` | Garden > Plants > Plant Food | House Plant, Orchid and Tomato Liquid Feed; Rose and Citrus Tree Feed Granules; Cactus and House Plant Feed Sticks | plant (in the title) | ml, g or sticks per pack | for (the plant), form |

The legacy bouquets (`samples`, `decor_rows`) stay where they were. Bouquet's own rows are new.

**Facts that never swap.** A derived style takes another value only for a key the scale may
vary. A house plant's `plant_kind`, `light_needs`, `pet_safe` and `pot_material` are in
`scale_text.FROZEN_KEYS`, so a derived monstera is never pet safe and a text that says "in a
ceramic pot" stays true. `pet_safe` follows the ASPCA's list of plants toxic and non-toxic to
cats and dogs. A plant food's `feed_form` is frozen, since it decides the SKU field (a liquid is
sold by the millilitre, granules by the gram and sticks by the count). Its plant varies, so each
template's text names its plant and nothing true only of it: "a liquid feed for a tomato" becomes
"a liquid feed for an orchid" on a derived orchid feed. A bouquet's flower varies too, so its
text names the flower in the singular ("each rose stem") and the word swap reads true.

**Colors.** A bouquet's color is the bloom's own (`main_colors.EXCEPTIONS`). A house plant's is
its pot's, and every house plant offers the six main colors (gen#275). Plant food is colorless.

**Brands.** Bouquet is a type of the gifts family of the line grammar (`line_grammar_families/
gifts.py`), whose 26 lead words leave 16 free of any template's text. The family's brands may
not outnumber them, so the new bouquets come from two brands: Goldfield Farms and Thistle &
Wren, which the family already deals. Five Garden brands would have made 17.

**Drawings.** `cut_flowers` takes `flower` (rose, tulip, lily, carnation, gerbera, mixed
flower) and `pack` (bouquet, letterbox). `house_plant` takes `kind` (the ten plants) and `pot`
(ceramic, plastic, metal). `plant_food` takes `form` (liquid, feed sticks, granules) and `plant`
(house plant, orchid, rose, cactus, tomato, citrus tree). Each param is the lower-cased attribute
value (gen#512), and each value draws apart
(`tests/test_retail_flowers_plants_1115.py::test_a_param_changes_the_drawing`).

**Count.** At the ceiling build the three types hold 1,343 SKUs, against 5 before: +1,338 against
the issue's target of about +1,200 (floor 1,140). That is Bouquet 653 (103 styles), House Plant
588 (49) and Plant Food 102 (42).

**Titles and sizes.** House Plant and Plant Food are kinds of the garden family of the line
grammar (`line_grammar_families/garden.py`), so a derived style's model is a garden lead word
and not an invented range name. `size_axes.AXES` declares a bouquet's `stem_count` and a house
plant's `pot_size_cm`, so the larger bouquet and the larger pot are drawn larger. The bouquet
texts say a stem is sent closed, not "in bud": a word in a template's text is no derived model,
and "Bud" is a baby gear lead word, so using it would re-deal that family's models and change
the stroller, car seat and high chair titles.

**Decoys.** House Plant joins the nursery types in `tests/test_retail_garden_203.py`'s
exemption (a plant bought by variety). So does Plant Food, a feed bought by the plant it feeds.

## Demo queries

- **`roses`**: cut roses (Hand-Tied and Long-Stem Rose Bouquets, Rose Letterbox Flowers, and
  derived rose styles) compete in Garden with Rose Feed Granules, and with rose-scented Beauty
  (the Rose & Geranium Hand Wash) and products sold in the color Rose. The catalogue holds no
  rose bush yet, so the Garden competitor is the feed. A good ranking puts the bouquets first and
  the feed and the hand wash below them.
- **`pet safe house plants`**: the `pet_safe` attribute (Yes or No) filters House Plants. The
  orchid, echeveria, Christmas cactus, calathea and spider plant are Yes. The monstera, peace
  lily, snake plant, pothos and aloe vera are No, and their text says "Keep away from cats and
  dogs", so a text-only match on "pet" or "safe" cannot tell the two apart.
