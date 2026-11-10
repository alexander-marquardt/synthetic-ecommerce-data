# Every shoe is one product sold in UK sizes and colors (gen#935)

"blue bull red mens shoes size 10" found no Best match on the Combined demo: the Blue Bull shoes
were single-SKU products with no size, and a size filter cannot match a shoe that has none. On the
ceiling build 95 of the 959 footwear products (517 SKUs) had no `size_uk` axis, 58 of them a single
SKU with no axis at all, and all 405 planted and decoy shoes were sold in one color.

Footwear is a `Mens`, `Womens` or `Kids` path whose second node is `Shoes`. Every footwear product
is now one product whose SKUs are UK size x color, grouped by `product_id`, as the footwear rows
(`footwear_rows.py`) already were. `shoe_grid.apply` runs last over the templates
(`scale.templates`), so a derived style copies its template's sizes and no pass before it moves:

- A row with no UK size (the planted shoe rows of `decoy_rows.py` and `decoy_product_words.py`, and
  the decoys `decoy_apparel.py` clones from them), or with a slipper's letter size whose `size_uk`
  was a range ("7-8"), takes the run of its audience's chart in core's `size_charts`: Womens UK 3
  to 8, Mens UK 6 to 12, Kids 8 Infant to 2 Junior, whole sizes, one inner size left out of about a
  third of the rows, as real ranges have gaps. A slipper keeps its width and material and drops the
  letter size, so "slippers size 7" filters `size_uk: 7`.
- A row sold in one color takes 2 to 5 colors from its type's palette (`shoe_grid.PALETTES`:
  formal shoes and boots, sports shoes, summer shoes, slippers), every SKU of its hero color
  repeated in each. Each SKU draws in its own color and has its own image (gen#706, gen#860).

A decoy keeps its decoy property (gen#294, gen#444): an added color is never a color word its title,
brand, line or description names, so "Brogues with Blue Sole" is never sold in blue and no Blue Bull
shoe in blue. A title that names the hero color names each SKU's own color on that SKU: "Red
Cashmere-Feel Chelsea Boots" in black is "Black Cashmere-Feel Chelsea Boots" (the record's
`color_copy`, which the export reads for the variant's title and description). A color whose title
would be another product's ("White Trainers with Black Sole" in red, beside "Red Trainers with
Black Sole") is not added.

Every product keeps its id and its place, so the change adds SKUs only, no product: the build's
totals are `retail_figures.figures()`'s, and the pull request states the footwear and catalog SKUs
before and after. `tests/test_shoe_grid_935.py` holds it.
