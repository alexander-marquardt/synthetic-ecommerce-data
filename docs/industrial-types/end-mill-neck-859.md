# An end mill states its neck only when it has a reduced neck (#859)

A reduced neck belongs to a long-reach end mill. Behind the flutes, the body is ground below the cutting diameter for a stated length, so the tool can reach into a pocket without rubbing. A catalogue prints that length, `Neck Length`, on those tools only. It prints a standard size, in the unit of the tool's other lengths.

Until #859, every end mill computed a neck as `length of cut × uniform(1.05, 1.4)`, and the sparsity draw published it on 27% of them. The default build had 560 distinct values on 668 SKUs, such as `0.3164"` and `15.09mm`, and the served catalogue had 6,124.

- **Which tools have one.** A line is a reduced-neck line when a digest of its type and series falls under `series.REDUCED_NECK_LINE_SHARE` (0.42). A digest is used so that no random draw moves. Each tool of such a line that a reach fits states its neck, and no other tool does. The published share lands near the census's 27% of end mills: 600 of 2,324 on the default build, and 13,157 of 51,409 on an end-mill build at `--lines 39000`.
- **Which reach.** `series.neck_lengths` keeps the standard sizes that fit the tool. The inch list, `NECK_LENGTHS_IN`, runs from 1/4" to 3" on the 1/16" grid. The metric list, `NECK_LENGTHS_MM`, runs from 3 to 50 mm. A size fits when it is longer than the length of cut, at most ten cutting diameters, and short enough to leave 1.5 shank diameters to clamp, so it is always shorter than the overall length. Only cutters up to 1/2" or 12 mm qualify. The tool's own draw (the one `uniform(1.05, 1.4)` took) picks among the sizes that fit. A line of several lengths (#850) takes the next reach past the length of cut instead, so the neck follows that axis and is no third choice on the product page. Where one length of cut fits a neck on one SKU and not on another, such as a cutter past the range beside one in it, that length of cut states no neck.
- **How it is spelled.** It is spelled the way `Length of Cut` is, in the same unit: `5/8"`, `1-1/4"`, `25mm`. The unit defects that respell any length in the other system respell a neck too.
- **What it is to the facet rule.** The neck is `tabled`, a list of sizes. The catalogue now has no `drawn` quantity. `MIN_PRESENCE` still keeps it off the sidebar, because it is on 26% of end mills.

Distinct values: 22 on the default build and 38 on an end-mill build at `--lines 39000`. Without the unit defects, the bound is 24, the two lists together. `tests/test_end_mill_neck_859.py` holds the rule.

A tool with no reduced neck lists the neck as a retired attribute (#497) that does not tell two SKUs apart. Its sparsity draw is still taken, so no later draw moves.
