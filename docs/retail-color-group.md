# Near-white shades and bra shape x main color (gen#302)

A color-group demo ("womens cream jumper", "ivory cardigan", "off white dress", "white minimiser
bras") needs products to find. `prototypes/retail_drawings/colorgroup_rows.py` adds them as
templates only: no derived style copies a row, so the seeded derivation of the other styles is
what it was.

## What it holds

- **Near-white shades on apparel.** `APPAREL` has 18 styles that put Cream, Ivory and Off White
  next to White on jumpers, cardigans, midi dresses, long sleeve tops and blouses. "Off White" is
  one color value (`colorwords.is_plain`; "Off" is a half word like "Duck"). No title or
  description names a color, so the text never states a color the style does not carry.
- **Women's jumpers.** Eight of the styles are jumpers: the ceiling holds 185 women's jumper SKUs
  (it held 40), so a page of 10 does not repeat one style.
- **Bra shape x main color.** `BRAS` has one style per shape a shopper names (minimiser, plunge,
  balcony, full cup, t-shirt) in White, Black, Beige, Red and Blue, and a second minimiser, the
  shape that had only Black and Beige.

No attribute carries a color group (gen#186): the group (white includes cream, ivory and off white)
is a vocabulary on the consumer's side.

## Guard

`tests/test_retail_color_group_302.py` pins at least 20 SKUs per shade across 3 or more apparel
types, at least 150 women's jumper SKUs, and each of the 25 shape x main color cells. It counts the
templates, and a derived style only adds, so a count met there is met by the ceiling build. The
styles are counted by `golden-retail/stats.json` under `templates.colorgroup_rows`.
