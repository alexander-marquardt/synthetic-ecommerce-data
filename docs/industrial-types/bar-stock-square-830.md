# Square bar stock: a deep type on the material pool (gen#830, slice 3)

`Raw Materials > Bar & Rod Stock > Square Bars` was a breadth row of one SKU on the fastener pool. It is now a modelled type, `product_types/raw_materials/bar_stock_square.py`, and `tests/test_type_bar_stock_square.py` runs the per-type gates over it. It follows the round bar ([bar-stock-round-830.md](bar-stock-round-830.md)).

**Spec space.** A line is one alloy and cut length; its SKUs are sizes. A square bar's size is the side of the square, published as `Width`, the name square key stock publishes for the same dimension; a square has one width, so no `Height` is published. A title writes it as `W` (`Square Bar Stock: 1/2" W`). There are 29 fractional widths from 1/8" to 4": sixteenths to 1", eighths to 2", quarters to 3", then 3-1/2" and 4". There are 9 alloys under five `Material` names, with `Material Grade` carrying the alloy: 1018, 1045, 12L14, 4140, 303, 304, 316, 6061-T6 and C360. The bars are 12", 36", 72" and 144" long. That is 9 alloys × 4 lengths × 29 widths = 1,044 specs a brand can make, or 10,440 over the pool. Square bar is drawn, not ground, so unlike the round bar it publishes no `Finish`.

**Sources.** The sizes are conventional stocked sizes. ASTM A108 (steel) and ASTM B211 (aluminum) are the specifications such bar is sold to, but neither was read, and neither has a table of stocked sizes. So no record claims a standard, a tolerance or a mechanical property, and `dimension_provenance` says that no standard fixes the values.

**Brands.** The type sells on the `material` family that the round bar introduced: ten makers already in the book, and no fastener specialist among them. Its lines at the default size share almost no spec across brands, so its type test orders the pool's price tiers at `--lines 39000`.

**Price.** The price is generated, not measured: the census has no bar stock (`bar_stock_square.PRICE`). It is anchored on a 1/2" × 12" steel square at about 9 USD, over the round bar's 7, since a square holds about a quarter more metal than a round of its width. The material factors and the length model are the round bar's.

**Drawing.** The bar is drawn from the side, broken to fit as the round bar is, beside its square end, whose diagonals mark it as a section.
