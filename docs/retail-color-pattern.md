# A pattern is a `pattern`, not part of a `color` (gen#188)

The authored shades carry pattern words ("Navy Stripe", "Grey Check", "Brown Leopard") and
denim washes ("Light Wash", "Rinse"). A Color facet listing them next to plain colors made a
"navy" filter miss a Navy Stripe shirt. The shades keep their words in the build (swatch names,
image ids, titles, so a text search for "navy stripe shirt" still matches). The exported
documents split them:

| Authored | `color` | `pattern` |
|---|---|---|
| Navy Stripe, Grey Check, Black Polka Dot, Red Gingham, Pink Spot, Cream Print, Brown Leopard, Grey Marl, Ivory Lace | the word before the pattern | the pattern word |
| Light Wash, Mid Wash, Bleach Wash, Rinse | Blue (denim) | the wash |
| Grey Wash | Grey | Grey Wash |
| Washed Black | Black | Washed |
| Mid Wash and Yellow | Blue and Yellow | Mid Wash |
| Navy, Dark Red, 2N | unchanged | none |

A product of two colours carries ONE `color` value written in words, `Blue and White`, never
`Blue / White` and never a list of both colours (a list would put a mostly blue product into a
White filter) (gen#514). `tests/test_retail_two_colour_514.py` holds it: no `color` value has a
`/` or `&`, and a two-colour value reads `<A> and <B>` in title case.

`colorwords.split` is the one splitter; `export._color_entries` writes the two entries. The
`pattern` entry sits on the variant (beside its `color`) and, deduplicated, on the product, where
it joins the style's drawn pattern ("Plain", "Stripe"). A pattern attribute is a variant axis
when a style's SKUs differ by it.

In a style where any SKU splits, every variant states its own `pattern` (its split pattern, else
the style's drawn pattern, else "Plain"), so no SKU reads a sibling's pattern off the product's
list, and a style whose every SKU splits lists only the patterns its SKUs state (no drawn "Plain" or other pattern no SKU carries).

The ceiling build moved from 112,456 to 112,191 SKUs for two reasons: the split pattern entries
are read by the text-contradiction guard (+85 SKUs) and two text edits cleared its refusals (-350
SKUs); derived styles are redrawn from a seed, so the departments shift by hundreds of SKUs.

A document holding a color, a pattern or a wash reads three places: the variant attribute
`color`, the variant attribute `pattern`, and the product-level `pattern` values.

## Guard

`tests/test_retail_color_pattern_188.py` asserts the splitter cases, that no nested or flat
`color` value holds a pattern word, that every split SKU carries its pattern, that every flat SKU of a splitting style states its own pattern, and that a split
color is still a plain color word (the main-color policies of gen#275 keep working).
