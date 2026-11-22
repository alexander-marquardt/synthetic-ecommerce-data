# Chocolate bars, boxes and bags that fill their picture (gen#1125)

Before gen#1125 every chocolate bar was the grocery kit's generic `bar`: a flat wrapper in the
flavour's color covering about a fifth of the product area at 100g, with the chocolate seen
only in a torn corner. A chocolate box was a closed, shallow box low in the frame (18% of the
product area at 150g), and a sharing bag the generic grocery bag (33% at 150g); neither showed
a chocolate. Slice 1 draws the bars and the multipacks, slice 2 the boxes and the sharing bags.
Hot chocolate, the chocolate orange, peanut butter cups, the advent calendar and the decoy
chocolate box and coated fruit follow in slice 3, and each brand's mark and colors with a before
and after contact sheet in slice 4.

**`kit_chocolate.chocolate_bar`** draws a bar seen from a little above: its wrapper torn back
over gold foil to show the segmented block, the block glossed (a `choc-gloss-<hex>` gradient, a
highlight at the top left and a shade at the foot right), and two broken pieces in front, each
a `<g class="chocolate">`. The bar stands on a `class="ground"` shadow.

- **The wrapper is the flavour's color, the block is chocolate.** The block and the pieces are
  painted the chocolate the flavour is made of (`kit_chocolate.CHOCOLATE`: milk, dark, white),
  so a Mint Dark bar is dark chocolate in a green wrapper and a Chocolate Orange milk chocolate
  in an orange one. `grocery_families.chocolate_of` reads the kind from the flavour, the white
  or dark its name says, else milk when it contains milk; it also files the bar under its
  Chocolate Bars child (gen#298). The grocery build passes it as the drawing's `chocolate`
  param, and the decoy dark and white bars name theirs. With no param the bar reads its kind off
  the base color's luminance.
- **A pale wrapper stays visible.** `kit_chocolate.wrapper_color` moves a wrapper towards a cocoa
  brown just far enough to keep a 3:1 contrast against white paper, so a white chocolate bar's
  cream wrapper does not vanish.
- **A bar shows its own weight.** A bar under 200g is drawn smaller by about the cube root of its
  weight, never under 0.9 of the full bar, and each SKU draws its own pack size
  (`export.drawing_spec`), so a 100g bar is smaller than a 200g one. The pack scale (gen#543)
  gives the shape no factor (`pack_scale.OWN_SIZE`).
- **A multipack is a stack of its bars.** "4 x 35g" draws four bars and "6 x 25g" six, each a
  `<g class="bar">`, the front one opened; pack copies (gen#728) leave it as it is
  (`pack_copies.SELF_DRAWN_SHAPES`). Its broken piece sits high enough on the front bar that
  the stack, the piece and the shadow stay on the 400 x 400 sheet (gen#242).

The cereal bars (`CBR`) keep the generic `bar`.

**Fill is measured against the product area**, the plain sheet's 344 x 334 box
(`house_styles.TURN_AREA`), by `sheet_cover.cover`, as gen#1111 measures produce; the ground
shadow does not count.

| pack | floor | measured |
|---|---|---|
| 100g | 0.50 | 0.60 |
| 175g | 0.50 | 0.66 |
| 200g, or no pack size (a decoy row) | 0.50 | 0.72 |
| 4 x 35g | 0.50 | 0.66 |
| 6 x 25g | 0.50 | 0.68 |

## Boxes and sharing bags (slice 2)

**`kit_chocolate.chocolate_box`** (GRC-CHX) draws an opened gift box seen from a little above:
the lid stands behind it, with a ribbon, a bow and the label panel, and the gold tray holds the
chocolates in brown paper cups. The assortment cycles a round truffle in the box's chocolate, a
square praline in a second one (dark in a milk box, milk in a dark or white one) and a dome
with a drizzle of a third, each a glossed `<g class="chocolate">`. A 150g box holds 4 x 3, a
250g 5 x 3 and a 400g 6 x 4.

**`kit_chocolate.chocolate_bag`** (GRC-CSB) draws a stand-up sharing bag: a crimped top seal, a
sheen down its left side, the label panel, and an oval window showing the pieces it holds,
with five more spilled at its foot. The grocery build passes `piece`: `buttons` (a disc with a
raised rim) when the flavour names buttons, else `bites` (a small block).

Both are drawn about the product area's center, so a house-style turn keeps them large, and
both draw their own weight: a box under 400g or a bag under 250g by the cube root of its
share, never under 0.84 (box) or 0.9 (bag), so `pack_scale.SELF_SIZED` gives them no factor.
The box and the bag are the flavour's color moved towards cocoa as far as white paper needs
(`wrapper_color`), so a white chocolate bag stays visible. The chocolate is the one the flavour
is made of (`grocery_families.chocolate_of`), passed as `chocolate`, as for the bars.

| pack | floor | measured |
|---|---|---|
| box 150g | 0.50 | 0.56 |
| box 250g | 0.50 | 0.58 |
| box 400g, or no pack size | 0.50 | 0.79 |
| sharing bag 150g | 0.50 | 0.59-0.61 |
| sharing bag 250g, or no pack size | 0.50 | 0.72-0.73 |

`tests/test_chocolate_fill_1125.py` pins the floor over every bar, box and bag flavour and pack,
the gloss, the multipack's bar count and a box's chocolates by its size, that every pack stays
on its sheet, the wrapper's contrast, the chocolate of each style, the bag's pieces, and that
each SKU draws its own pack size.
