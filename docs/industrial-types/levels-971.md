# Levels: a homeowner tool for general retail (gen#971, slice 2)

`Tools > Measuring & inspecting > Leveling tools > Spirit levels` is a new modelled type, `product_types/hand_tools/levels.py`, and `tests/test_type_levels.py` runs the per-type gates over it. It is the second of the homeowner tools gen#971 adds to `Tools`, after tape measures.

**Shapes and lengths.** A level is published with its frame `Shape`: a torpedo level in 9 or 12 in (230 or 300 mm), a box-beam level in 24, 48 or 72 in (600, 1200 or 1800 mm), or an I-beam level in 24 or 48 in (600 or 1200 mm). No standard fixes these lengths, and the provenance says so. A length is published the way the catalogue writes every other length (`24"`, `600mm`), and carries its value in inches.

**Lines.** A line is one brand's levels of one shape, one frame material (aluminum, magnesium or plastic), one feature (`Magnetic Edge` or `Non-Magnetic`, published as `Features`) and one frame color, in inches or metric. Its SKUs are a run of the shape's lengths. The 36 (shape, material, feature, system) combinations are rotated in an order whose first six lines already hold every shape, material, feature and system. The title names the length, the shape and the color ("Level: 24" L, Box Beam, Red").

**Colors.** The frame comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 36 combinations, so each combination is built in every color.

**Decoys.** Two lines in every six name another layout tool before the item ("Square Series Level"). A search for that tool's word finds a level (gen#294).

**Price.** The price is generated, not measured, because the price census has no levels. It is about the length to the 0.75 power, anchored at 20 USD for a 24 in level: a 9 in torpedo near 10 USD, a 72 in box beam near 45.

**Drawing.** The level is drawn from its face, filled with the record's color: a frame drawn longer for a longer level, a torpedo tapered to its ends, an I-beam with its two flanges, three vials, and a dark strip along the bottom edge of a magnetic level. The type is drawn `upright` (`domains/industrial/orientation.py`). The magnesium frame has its own fill and hatch in `core/drawing/style.py`. The largest drawing, a 72 in box beam with a magnetic edge, is 6.32 x 0.78 in, so `extent=(6.4, 0.9)`.

**Size.** The default build holds 25 SKUs over 17 products; the large build (`--lines 39000`) holds 388.
