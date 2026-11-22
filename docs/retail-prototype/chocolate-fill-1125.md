# Chocolate bars that fill their picture (gen#1125)

Before gen#1125 every chocolate bar was the grocery kit's generic `bar`: a flat wrapper in the
flavour's color covering about a fifth of the product area at 100g, with the chocolate seen
only in a torn corner. Slice 1 draws the bars and the multipacks; the boxes, sharing bags, hot
chocolate, chocolate orange, peanut butter cups and advent calendar follow in slice 2, and each
brand's mark and colors with a before and after contact sheet in slice 3.

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

`tests/test_chocolate_fill_1125.py` pins the floor over every bar flavour and pack, the gloss,
the multipack's bar count, that every pack stays on its sheet, the wrapper's contrast, the
chocolate of each style, and that each SKU draws its own pack size.
