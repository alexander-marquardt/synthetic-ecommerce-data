# Tape measures: a homeowner tool for general retail (gen#971, slice 1)

`Tools > Measuring & inspecting > Tape measures` is a new modelled type, `product_types/hand_tools/tape_measures.py`, and `tests/test_type_tape_measures.py` runs the per-type gates over it. It is the first of the homeowner tools gen#971 adds to `Tools`.

**Lines.** A line is one brand's tapes with one case material (ABS, rubber-coated ABS or chrome-plated ABS), one lock (slide, auto or push button) and one case color, in inches or metric. Its SKUs are a run of blade lengths: 10 to 35 ft or 3 to 10 m. The blade width goes with the length. No standard fixes either, and the provenance says so.

**Lengths.** A length is published the way a listing writes it ("25 ft", "5 m"). Its value is carried in inches, like every other length.

**Names.** The lock is published as `Lock`, a census name. `Lock Type` is in the census too, but its key `lock_type` was retired by gen#497, so the one-key-per-concept rule refuses it.

**Colors.** The case comes in all six main colors (gen#275). The color rotation steps one further at each full turn of the 18 material, lock and system combinations. Over 108 lines, every combination is built in every color. Without that step, each combination would always get the same color, and only 93 of the 308 large-build SKUs would be distinct specs. With it, 308 of 384 are, and the type's floor is 0.80 (`tests/test_catalog_brands_voice.py`).

**Decoys.** Two lines in every six name another measuring tool before the item ("Level Series Tape Measure"). That way a search for that tool's word finds a tape measure (gen#294).

**Price.** The price is generated, not measured, because the price census has no tape measures. It is about the length to the 0.55 power, anchored at 19 USD for a 25 ft tape.

**Drawing.** The case is drawn from the side, filled with the record's color, with the blade and its hook out of the front. The case grows with both the blade's width and its length, so a 12 ft and a 16 ft tape on the same 3/4 in blade draw differently. The type is drawn `upright` (`domains/industrial/orientation.py`). Its case materials have their own fills and hatches in `core/drawing/style.py`.
