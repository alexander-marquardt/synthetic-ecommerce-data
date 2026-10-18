# A pattern is a `pattern`, not part of a `color` (gen#188)

The authored shades carry pattern words ("Navy Stripe", "Grey Check", "Brown Leopard") and
denim washes ("Light Wash", "Rinse"). A Color facet listing them next to plain colors made a
"navy" filter miss a Navy Stripe shirt. The shades keep their words in the build (swatch names,
image ids, titles, so a text search for "navy stripe shirt" still matches). The exported
documents split them:

| Authored | `color` | `pattern` |
|---|---|---|
| Navy Stripe, Grey Check, Black Polka Dot, Red Gingham, Pink Spot, Cream Print, Brown Leopard, Grey Marl, Ivory Lace, Red Tartan, Pink Floral, Navy Breton Stripe, Multi Patchwork | the word before the pattern | the pattern word: `stripe`, `check`, `polka dot`, `gingham`, `spot`, `print`, `leopard`, `marl`, `lace`, `tartan`, `floral`, `breton stripe`, `patchwork` |
| Light Wash, Mid Wash, Bleach Wash, Rinse | Blue (denim) | the wash: `light wash`, `mid wash`, `bleach wash`, `rinse` |
| Grey Wash | Grey | `grey wash` |
| Washed Black | Black | `washed` |
| Mid Wash and Yellow | Blue and Yellow | `mid wash` |
| Navy, Dark Red, 2N | unchanged | none |

A `pattern` value is lower case (`export.VALUE_CASE`, gen#255), so the table above shows the value
the facet holds, not the authored word.

A product of two colors carries ONE `color` value written in words, `Blue and White`, never
`Blue / White` and never a list of both colors (a list would put a mostly blue product into a
White filter) (gen#514). `tests/test_retail_two_color_514.py` holds it: no `color` value has a
`/` or `&`, and a two-color value reads `<A> and <B>` in title case.

`colorwords.split` is the one splitter; `export._color_entries` writes the two entries. The
`pattern` entry sits on the variant (beside its `color`) and, deduplicated, on the product, where
it joins the style's drawn pattern (`plain`, `stripe`). A pattern attribute is a variant axis
when a style's SKUs differ by it.

In a style where any SKU splits, every variant states its own `pattern` (its split pattern, else
the style's drawn pattern, else `plain`), so no SKU reads a sibling's pattern off the product's
list, and a style whose every SKU splits lists only the patterns its SKUs state (no drawn `plain` or other pattern no SKU carries).

The ceiling build moved from 112,456 to 112,191 SKUs for two reasons: the split pattern entries
are read by the text-contradiction guard (+85 SKUs) and two text edits cleared its refusals (-350
SKUs); derived styles are redrawn from a seed, so the departments shift by hundreds of SKUs.

Those two figures held when the split landed. The ceiling build now holds 166,990 SKUs
(`scale.py --skus ceiling --seed 0` on main at `7f9dd45`). The total moves with every type pull
request, so read the current one from `retail_figures.figures()["ceiling"]["skus"]`.

A document holding a color, a pattern or a wash reads three places: the variant attribute
`color`, the variant attribute `pattern`, and the product-level `pattern` values.

## The four patterns a shopper types before a category (gen#408)

The coverage review of this change asked for tartan, floral, breton stripe and patchwork beside
leopard and polka dot, and the build held none of the four. The product count is frozen, so no
style is added: one colorway of a style main already sold carries each word. "Red Tartan" is the
first colorway of the wool pleated midi skirt (`lowerbody_rows.py`), "Pink Floral" of the jersey
midi dress (`seasonal_rows.py`, drawn with a daisy print), "Navy Breton Stripe" of the ribbed long
sleeve top (`colorgroup_rows.py`) and "Multi Patchwork" of the linen fringed cushion
(`breadth_rows.py`, drawn with the patchwork fill). `colorwords.PATTERN_WORDS` lists the four;
`breton stripe` is one pattern, so a breton colorway is not read as a plain stripe. A patchwork throw is not sold: the Throw type has no
plain color yet, and `main_colors.complete` refuses a type with none.

## Guard

`tests/test_retail_pattern_facet_408.py` asserts the facet holds the six wanted values (the four above, leopard and polka dot), on a product where a shopper types each, with a plain color. `tests/test_retail_color_pattern_188.py` asserts the splitter cases, that no nested or flat
`color` value holds a pattern word, that every split SKU carries its pattern, that every flat SKU of a splitting style states its own pattern, and that a split
color is still a plain color word (the main-color policies of gen#275 keep working).
