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
* the `chamfer` frame (`brands.EXTRA_FRAMES`): a rule with 7-unit cut corners, the third corner
  treatment beside the square rule and the rounded border.

Index 0 of each is the original look, so no brand in the book changes: 6,885 drawings (45 brands
by 153 types) are byte-identical to the ones before the levers. Not done: first- against
third-angle projection (no figure draws the end view the convention needs).

**The paper and the texture are levers no more (#849).** A brand's paper tint (one of six) and a
background texture were levers until a demo showed a tinted sheet reading as a search signal: a
green sheet looks like a different kind of product from a blue one. Every drawing now sits on
the one paper, `core/drawing/product_look.PAPER`, with no texture, whatever the brand; the
retail house styles lost the same two fields. What does vary by product, not brand, is the
figure's angle (`product_look.angle_of`), so two products of one type no longer draw alike.

## When two brands are visibly different

Any ONE strong lever differs: the frame, the mark, or an ink at least 15 CIELAB units from the
other under normal vision, protanopia, deuteranopia and tritanopia (15 of the 66 ink pairs are
not, red and green among them: 10.8 for a protanope). Otherwise at least THREE weak levers differ:
outline, dash, margin, or a confusable ink. The ink-to-paper contrast floor (3:1) holds for every
ink on the one paper.

## Capacity

Without counting the mark, the space holds 110 pairwise visibly different house styles (a greedy
lower bound, `distinguish.capacity()`; 570 while the paper and the texture were levers); with the
45 marks, 45 x 110. #53 needs 135 brands: three times the 100K build's 45, for a catalog of
several hundred thousand SKUs. The levers alone no longer hold that many; a brand differs from
every other by its own mark, a strong lever. The book is checked
pairwise. A brand beyond the 45 marks must share a mark, which the mark-uniqueness test in
`tests/test_brand_marks.py` does not yet allow.
