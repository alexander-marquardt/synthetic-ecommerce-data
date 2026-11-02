# Grouped sofas and sofa cushions (gen#808)

A search for `blue sofa cushion` or `sofa` with grouping on showed no grouped card. The catalog's
cushions came in no blue, and `sofa_rows.py` sells each seat count of a sofa as a style of its
own. `sofa_groups.py` adds six products, each sold in several versions of the same product:

| Product | Brand | SKUs | Varies on |
| --- | --- | --- | --- |
| Elmsworth Velvet Sofa Cushion | Hearth & Table | 9 | color (Blue, Teal, Mustard) x size |
| Quenby Linen Sofa Cushion | Lanternby | 9 | color (Blue, Sage, Natural) x size |
| Harrowden Chenille Sofa Cushion | Calderby & Lune | 9 | color (Blue, Grey, Rust) x size |
| Maddox Velvet Sofa | Brackenmere Home | 3 | configuration (Blue) |
| Wexley Chenille Sofa | Emberly Home | 3 | configuration (Grey) |
| Ellery Boucle Sofa | Larchwood Living | 3 | configuration (Oat) |

**Cushions.** A cushion is sold in 40 x 40, 45 x 45 and 50 x 50 cm, stored as `size`, the axis
`size_axes.AXES` declares for a Cushion. The SKUs of one cushion share its brand, title and
fabric, and `variant_axes` is `["color", "size"]`. Each size draws at its own scale on the size
ladder (`size_ladder.py`, gen#339). That scale shows the order of the sizes (smaller and larger)
but not their true proportions. Each color draws in its own swatch. The three cushions draw
different edges (plain, a light piping and a dark piping), so the same color and size of two
cushions are two pictures.

**Sofas.** A sofa is sold as a `2 Seater`, a `3 Seater` and a `Corner` sofa (left-hand L-shape,
five seats), in one fabric and one color. The version is the SKU's `configuration`. The seat
count, the width (`item_width`) and the depth (`item_depth`) are SKU attributes that follow it, so
`variant_axes` is `["configuration"]` alone. The Sofa spec declares the three options. The drawing
`kit_seating.sofa_version` reads the SKU's own configuration. A 2 or 3 seater draws as the straight
sofa of that seat count, and the corner draws as `corner_sofa`.

**Where a grouped sofa sits.** `Home/Furniture/Sofas` holds `Corner Sofas` (gen#283), so the product
sits at `Sofas`, and a filter on `Sofas` takes all three of its versions. A sofa with a corner
version is also filed at `Sofas > Corner Sofas` (`multi_path.py`, gen#602), so a shopper who
narrows to corner sofas finds it too. The product type is `Sofa`, and the title names no corner.
That keeps tree rule (c) (`tree_guard.py`) satisfied: a title that names a more specific node sits
in that node.

**Titles.** A product name states no axis value (no color, size, seat count or "Corner"). Every SKU
of a product carries the product's title and states its own version as an attribute.

The rows are templates only: `sofa_rows.py` lists the sofas among its `ROWS` and the cushions in
its `docs()`, and the Sofa and Cushion specs name `sofa_rows` as a home that is not derivable. The
seeded derivation is therefore unchanged. `tests/test_retail_grouped_sofas_808.py` checks the
groups.
