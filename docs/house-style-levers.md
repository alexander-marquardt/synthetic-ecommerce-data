# House-style levers and the distinguishability rule (#55)

Text-free ways to tell brands apart on a drawing, beyond the 48 (ink, frame) pairs, and the rule
that says when two brands are visibly different. Code: `core/brands.py` (the levers),
`core/drawing/distinguish.py` (the rule), `core/drawing/sheet.py` (the drawing). Tests:
`tests/test_house_style_levers_55.py`. README: Brands, and Images.

## The levers

A brand row in `core/brands.py` may set, besides its ink, frame and mark:

* `outline`: the outline weight, 2.3 (the floor), 3.0 or 3.7 units (0.4 px a step at the tile);
* `dash`: the dash pattern of the interior lines (flutes, threads, centre lines): solid, dashed
  or a long-short chain. The part's outline stays solid;
* `margin`: the frame's inset, 6 or 3 units (never deeper: the handle-less lens and the plate clear
  a frame at 6 and no further in);
* `texture`: the figure area's background, plain, a grid or dots, in the brand's ink, faint, and
  never under the wordmark's plate;
* the `chamfer` frame (`brands.EXTRA_FRAMES`): a rule with 7-unit cut corners, the third corner
  treatment beside the square rule and the rounded border.

Index 0 of each is the original look, so no brand in the book changes: 6,885 drawings (45 brands
by 153 types) are byte-identical to the ones before the levers. Not done: first- against
third-angle projection (no figure draws the end view the convention needs).

## When two brands are visibly different

Any ONE strong lever differs: the frame, the mark, or an ink at least 15 CIELAB units from the
other under normal vision, protanopia, deuteranopia and tritanopia (15 of the 66 ink pairs are
not, red and green among them: 10.8 for a protanope). Otherwise at least THREE weak levers differ:
paper, outline, dash, margin, texture, or a confusable ink. The ink-to-paper contrast floor (3:1)
holds for every ink on every paper.

## Capacity

Without counting the mark, the space holds 570 pairwise visibly different house styles (a greedy
lower bound, `distinguish.capacity()`); with the 45 marks, 45 x 570. #53 needs 135 brands: three
times the 100K build's 45, for a catalog of several hundred thousand SKUs. The book is checked
pairwise. A brand beyond the 45 marks must share a mark, which the mark-uniqueness test in
`tests/test_brand_marks.py` does not yet allow.
