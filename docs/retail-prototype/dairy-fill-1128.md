# Milk drawn as the jug or carton it is sold in (gen#1128)

Before gen#1128 every milk (`GRC-MLK`, 89 products) and plant milk (`GRC-PLM`, 112 products)
SKU drew the kit's generic `carton`, painted in its line's first flavor, and `pack_scale` shrank
the smaller sizes: a 1 pint covered a fifth of its product area, and a Semi Skimmed SKU of a line
whose first flavor is Whole drew blue.

`kit_dairy.py` now draws:

- **`milk_jug`** (milk): a translucent plastic jug of white milk, seen a little from the side,
  with a handle at the back and a cap and label in the SKU's fat level's color (`FAT_CAPS`:
  whole blue, semi skimmed green, skimmed red, as UK shelves code it, and lactose free
  purple). The 1, 2 and 4 pint jugs are drawn in their own proportions (`JUGS`), the larger
  jug wider and deeper.
- **`milk_carton`** (plant milk): a gable-top carton with a screw cap on its roof, the 500ml,
  1L and 2L in their own proportions (`CARTONS`).

Both read the SKU's own `flavor` and `pack_size` (per-SKU drawing params, as a pizza's are), so
each fat level and size is its own picture. Each carries a gloss (`class="gloss"`) and stands on
a ground shadow (`class="ground"`). Neither takes a `pack_scale` factor
(`pack_scale.SELF_SIZED`): the drawing shows its own size.

**Fill is measured as gen#1111 measures it**: the share of the plain sheet's 344 x 334 product
area (`house_styles.TURN_AREA`) that the pack (`<g class="dairy">`) paints, in
`image_release.render`'s own SVG; the ground shadow does not count.

| pack | before | after |
|---|---|---|
| Milk 1 pint | 0.19 | 0.51 |
| Milk 2 pint | 0.30 | 0.58 |
| Milk 4 pint | 0.48 | 0.66 |
| Plant Milk 500ml | 0.19 to 0.30 | 0.54 |
| Plant Milk 1L | 0.30 to 0.48 | 0.61 |
| Plant Milk 2L | 0.48 | 0.69 |

`tests/test_dairy_fill_1128.py` pins, over every milk and plant milk SKU of the 10K grocery
build: the fill between 0.50 and 0.80, no `pack_scale` factor, a jug cap in its fat level's
color (each SKU of a mixed line its own), a wider jug or carton for a larger size of one
flavor, the gloss and ground shadow, and white milk behind translucent plastic.

![Milk and plant milk before: the generic carton, shrunk by pack_scale](../images/dairy-milk-1128-before.png)

![Milk as jugs with a cap by fat level at 1, 2 and 4 pint, and plant milk as gable-top cartons](../images/dairy-milk-1128-after.png)

No milk line in the catalogue is sold in a glass bottle, so none is drawn. Yoghurt (single pots,
the 4 x 125g sleeve and the 500g tub) follows in its own PR.
