# Household tool sets: a homeowner tool for general retail (gen#971, slice 3)

`Tools > Hand tools > Tool sets & kits > Household tool sets` is a new modelled type, `product_types/hand_tools/household_tool_sets.py`, and `tests/test_type_household_tool_sets.py` runs the per-type gates over it. It is the fifth and last of the homeowner tools gen#971 adds to `Tools`, after tape measures, levels, stud finders and utility knives. It sits beside the assortment kits (`kit_assortment`), which are trade kits of one part in many sizes.

**Lines.** A line is one brand's sets in one container, with one tool steel and one container color. The containers are a blow-molded case, a zippered case, a plastic or metal tool box, a roll-up pouch and a canvas tool bag. The steels are chrome vanadium, carbon and alloy steel. Its SKUs are a run of the piece counts homeowner sets are stocked in: 8, 23, 39, 65, 102 and 148. The count is published as `Piece Count`, the name the assortment kits already publish. No standard fixes the counts, and the provenance says so.

**Colors.** The container comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 18 container and steel combinations, so over 108 lines every combination is built in every color.

**Decoys.** Two lines in every six name a power tool before the item ("Drill Series Household Tool Set"). A household set holds no power tool, so a search for that word finds a set that a category policy can remove (gen#294).

**Price.** The price is generated, not measured, because the price census has no household tool sets. It is about the piece count to the 0.45 power, anchored at 35 USD for a 39-piece set.

**Drawing.** The set is drawn open, from the front, with its container filled with the record's color. Each container has its own outline and fittings: a case's latches, a zipper, a box's handle (a metal box also has its tray line and side latches), a pouch's pockets and a bag's handles. Inside, a tray holds one mark per piece, laid out in rows. The container grows with the piece count, so siblings draw differently. The type is drawn `level`, like the other sets and kits (`domains/industrial/orientation.py`).
