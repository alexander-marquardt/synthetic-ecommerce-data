# Hex bar stock: a deep type on the material pool (gen#830, slice 2)

`Raw Materials > Bar & Rod Stock > Hex Bars` was a breadth row of two SKUs on the fastener pool. It is now a modelled type, `product_types/raw_materials/bar_stock_hex.py`, and `tests/test_type_bar_stock_hex.py` runs the per-type gates over it. It follows the round bar ([bar-stock-round-830.md](bar-stock-round-830.md)).

**Spec space.** A line is one alloy and cut length; its SKUs are sizes. A hex bar's size is its `Width Across Flats`, the census's name for it, which the hex head screw also publishes. A title writes it as `A/F` (`Hex Bar Stock: 1/2" A/F`). There are 27 fractional sizes from 1/4" to 3": sixteenths to 1-1/4", eighths to 2" and quarters to 3". There are 10 alloys under five `Material` names, with `Material Grade` carrying the alloy: 1018, 1045, 12L14, 1215, 4140, 303, 304, 316, 6061-T6 and C360. The bars are 12", 36", 72" and 144" long. That is 10 alloys × 4 lengths × 27 sizes = 1,080 specs a brand can make, or 10,800 over the pool. Hex bar is drawn, not ground, so unlike the round bar it publishes no `Finish`.

**Sources.** The sizes are conventional stocked sizes. ASTM A108 (steel) and ASTM B211 (aluminum) are the specifications such bar is sold to, but neither was read, and neither has a table of stocked sizes. So no record claims a standard, a tolerance or a mechanical property, and `dimension_provenance` says that no standard fixes the values.

**Brands.** The type sells on the `material` family that the round bar introduced. That is ten makers already in the book, and no fastener specialist is among them. Like the round bar, its 42 lines at the default size share almost no spec across brands, so its type test orders the pool's price tiers at `--lines 39000`.

**Price.** The price is generated, not measured: the census has no bar stock (`bar_stock_hex.PRICE`). It is anchored on a 1/2" × 12" steel hex at about 8 USD, a little over the round bar's 7. The material factors and the length model are the round bar's.

**Drawing.** The bar is drawn from the side with a flat towards the eye, broken to fit as the round bar is, beside its hexagonal end.
