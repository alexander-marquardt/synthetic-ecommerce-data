# Stud finders: a homeowner tool for general retail (gen#971, slice 2)

`Tools > Measuring & inspecting > Stud finders` is a new modelled type, `product_types/hand_tools/stud_finders.py`, and `tests/test_type_stud_finders.py` runs the per-type gates over it. It is one of the homeowner tools gen#971 adds to `Tools`, beside tape measures and levels.

**Styles and tiers.** A stud finder is published with its `Style`: `Edge Finding` or `Center Finding` for an electronic scanner, or `Magnetic` for a finder that locates the screws in a stud with a pivoting magnet. An electronic scanner is one of two tiers, named by the scan modes it lists (`Application Modes`): a basic one (`Stud Scan, AC Scan`) or a multi-scan one (`Stud Scan, Deep Scan, Metal Scan, AC Scan`). A magnetic finder lists `Metal Scan`. Its `Indicator` is a single LED, LED arrows or an LCD screen; a magnetic finder's is its pivoting magnet.

**Scan depths.** The SKUs of a line are its tier's scan depths: 3/4 or 1 in for a basic scanner or a magnetic finder, 1-1/2 or 2 in for a multi-scan one. No standard fixes these depths, and the provenance says so. The census names the depth `Scan Depth (In.)`, so a depth is published in inches only, as a bare fraction (`3/4`) with the unit code `INH`.

**Lines.** A line is one brand's finders of one style, indicator and tier, in one body color. The 13 combinations (12 electronic, 1 magnetic) are rotated in an order whose first six lines already hold every style, every indicator and every tier. The title names the scan depth, the style and the color ("Stud Finder: 3/4" Scan Depth, Edge Finding, Red").

**Colors.** The body comes in all six main colors (gen#275). The `j`-th combination of the `k`-th turn takes color `j + k`, so over six turns each combination meets every color. The levels' form, `n + n // len(COMBOS)`, covers every pair only when the combinations are a multiple of six; with 13 it would step two colors a turn and pair each combination with three colors only.

**Decoys.** Two lines in every six name another tool before the item ("Laser Series Stud Finder", "Voltage Tester Series Stud Finder"). A search for that tool's word finds a stud finder (gen#294).

**Distinct specs.** The spec space is 13 combinations, six colors and two depths: 156 specs, all of them built at the large build. Every maker sells the same ones, so `DISTINCT_SPEC_FLOOR` in `tests/test_catalog_brands_voice.py` holds the type at 0.40 (156 of 361 SKUs at 100K, 0.432).

**Price.** The price is generated, not measured, because the price census has no stud finders. It is about the scan depth to the 0.9 power, anchored at 25 USD for a 1 in scanner: a 3/4 in finder near 19 USD, a 2 in multi-scan one near 47.

**Drawing.** The finder is drawn from its face, filled with the record's color. An electronic scanner is a tall body with a dark grip across its lower half and its indicator near the top: one LED, two arrows pointing at each other, or an LCD window; a multi-scan one draws a mode button under it. A magnetic finder is a smaller body with a round window and the magnet across it. Each draws a depth scale on its body, 0.8 in long per inch of scan depth, so two SKUs of a line draw apart. The type is drawn `upright` (`domains/industrial/orientation.py`). The largest drawing, a center-finding scanner, is 2.60 x 5.60 in on both builds, so `extent=(2.7, 5.7)`.

**Size.** The default build holds 21 SKUs over 17 products; the large build (`--lines 39000`) holds 361 over 243.
