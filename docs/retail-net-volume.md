# Retail net volumes (gen#347)

A **Net volume** facet that offers one option demos nothing, so every retail type that carries
a net volume offers at least three, and a title that states a volume carries it.

How a volume reaches the catalogue, by where it is authored:

| Authored as | Volume | Where |
| --- | --- | --- |
| A grocery family (`grocery_rows.Family.packs`) | One `net_volume` per SKU. A family listed in `PACKS_PER_STYLE` stocks more sizes across its range than any one style sells: each style takes that many packs, the window moving one pack per style, so the family spans every size while each style keeps its SKU count (and so the family's styles, flavors and random draws). | `grocery.stocked` |
| A `class_model.Style` sold in several sizes | `volumes=((ml, price), ...)`: one SKU per color and size, the price following the size. A style sold in one size keeps `unit=(ml, "ml")`. | `class_model.Style` |
| A `breadth_rows.Row` sold in several sizes | `sizes=((ml, price), ...)` with `size_key="net_volume_ml"`. | `breadth_rows.Row` |
| A title that states a volume ("Glass Cleaner 500ml") | The title's volume becomes the record's `unit_size`, in one place. | `net_volume.state_title_volumes` |

The guard is `tests/test_retail_net_volume_347.py`: it counts the distinct volumes per category
path over `scale.templates()` (a derived style keeps its template's volume) and fails below
three unless the path is in its `EXCEPTIONS` with a reason. An exception the catalogue outgrows
is refused, so the list cannot rot. It also fails a title whose volume the record does not carry.

Shampoo, conditioner, perfume and olive oil (gen#356) are `breadth_rows.Row`s with
`size_key="net_volume_ml"`: every product of the four leaves sells three volumes, shampoo and
conditioner at 250/400/500 ml, perfume at 30/50/100 ml and olive oil at 500/750/1000 ml. Their
volume used to be a free-text `size` (`"250ml"`, `"30 ml"`) or absent, which the Net volume facet
cannot read. `tests/test_retail_net_volume_347.py` pins the four leaves: each product carries at
least three `net_volume`s, none as a `size`, and the leaf offers the volumes above.

A new volume-sized type: author it with three sizes across its products or SKUs, and the title
states the size only when the product is sold in that size alone.
