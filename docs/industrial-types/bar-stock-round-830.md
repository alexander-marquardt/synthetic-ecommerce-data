# Round bar stock: a deep type on its own brand pool (gen#830)

`Raw Materials > Bar & Rod Stock > Round Bars` was a breadth row of two SKUs. It is now a modelled type, `product_types/raw_materials/bar_stock_round.py`, and `tests/test_type_bar_stock_round.py` runs the per-type gates over it.

**Spec space.** A line is one alloy, finish and cut length; its SKUs are diameters. There are 27 fractional diameters from 1/8" to 3", 13 alloys under five `Material` names (`Material Grade` carries the alloy: 1018, 12L14, 4140, 303, 6061-T6, C360, ...), and 12", 36", 72" and 144" bars. Each alloy comes `Bright` (cold drawn), and the steels and stainless also come `Ground` (centerless ground). That is 20 alloy-finish pairs × 4 lengths × 27 diameters = 2,160 specs a brand can make, or 21,600 over the pool.

**Sources.** The sizes are conventional stocked sizes. ASTM A108 (steel) and ASTM B211 (aluminum) are the specifications such bar is sold to, but neither was read and neither has a table of stocked diameters. So no record claims a standard, a tolerance or a mechanical property, and `dimension_provenance` says that no standard fixes the values.

**Brands.** Bar stock has its own brand family, `material` (`core/brands.py`), not the fastener pool it used as a breadth row, because screw makers rarely sell bar stock. Ten makers already in the book carry it:

- the three broad-line houses;
- Varnstrom, Iron Heron, Vellinhorst and Crennick Works, four multi-family metal houses;
- Quennick, a bearing maker (a bearing house sells precision shafting);
- Ashcombe Forge and Salt Meadow Works.

No fastener specialist is in the pool. Its economy makers are Tervasko and Salt Meadow Works, and its premium makers Ashcombe Forge and Quennick. At the default size its 42 lines share almost no spec across brands, so `test_price` orders this family's tiers at `--lines 39000`, in the type's test (`TIERS_ORDERED_LARGE`).

Salt Meadow Works is the book's smallest maker. On main it sat at the 0.3%-of-100K floor (530 SKUs), and this type's SKUs would push it under; it now makes about 40 bars there.

No new name was invented for the pool. A new name would need the README's real-company check, and with one type to sell it would fall under the book's 0.3%-of-100K floor. The new family draws its title qualifier after every other draw of a brand's voice (`voice.voice_for`), so no other type's text moves. The hex and square bars join the pool in their own slices of #830.

**Price.** The price is generated, not measured: the census has no bar stock (`bar_stock_round.PRICE`). Stainless and brass cost about three times plain steel, and a ground bar costs 1.6 times a drawn one.
