# A pattern is a `pattern`, not part of a `color` (gen#188)

The authored shades carry pattern words ("Navy Stripe", "Grey Check", "Brown Leopard") and
denim washes ("Light Wash", "Rinse"). A Color facet listing them next to plain colors made a
"navy" filter miss a Navy Stripe shirt. The shades keep their words in the build (swatch names,
image ids, titles, so a text search for "navy stripe shirt" still matches). The exported
documents split them:

| Authored | `color` | `pattern` |
|---|---|---|
| Navy Stripe, Grey Check, Black Polka Dot, Red Gingham, Pink Spot, Cream Print, Brown Leopard, Grey Marl, Ivory Lace, Red Tartan, Pink Floral, Navy Breton Stripe, Multi Patchwork | the word before the pattern | the pattern word |
| Light Wash, Mid Wash, Bleach Wash, Rinse | Blue (denim) | the wash |
| Grey Wash | Grey | Grey Wash |
| Washed Black | Black | Washed |
| Mid Wash / Yellow | Blue / Yellow | Mid Wash |
| Navy, Dark Red, 2N | unchanged | none |

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

## The four patterns a shopper types before a category (gen#408)

The coverage review of this change asked for tartan, floral, breton stripe and patchwork beside
leopard and polka dot, and the build held none of the four. The product count is frozen, so no
style is added: one colorway of a style main already sold carries each word. "Red Tartan" is the
first colorway of the wool pleated midi skirt (`lowerbody_rows.py`), "Pink Floral" of the jersey
midi dress (`seasonal_rows.py`, drawn with a daisy print), "Navy Breton Stripe" of the ribbed long
sleeve top (`colorgroup_rows.py`) and "Multi Patchwork" of the linen fringed cushion
(`breadth_rows.py`, drawn with the patchwork fill). `colorwords.PATTERN_WORDS` lists the four;
"Breton Stripe" is one pattern, so a breton colorway is not read as a plain stripe. A patchwork throw is not sold: the Throw type has no
plain color yet, and `main_colors.complete` refuses a type with none.

## One spelling per pattern (gen#324)

The facet held `Stripe` (from the colorways) beside `Striped` (authored on the cotton tote bag, the
windproof umbrella, the melamine side plate and the striped wallpaper), `Check` beside `Checked`
and `Spot` beside `Spotted` (both on wallpapers): one pattern, two spellings, so a shopper who
ticked one missed the other. The authored `Pattern` attributes now use the colorway spelling
(`Stripe`, `Check`, `Spot`). Titles keep their words ("Striped Wallpaper"). The count of SKUs and
styles does not move. `tests/test_retail_pattern_spelling_324.py` fails when two pattern values of
any authored template, or of a built catalog, differ only by a plural `s`/`es` or a past `ed`
ending.

## Guard

`tests/test_retail_pattern_facet_408.py` asserts the facet holds the six wanted values (the four above, leopard and polka dot), on a product where a shopper types each, with a plain color. `tests/test_retail_color_pattern_188.py` asserts the splitter cases, that no nested or flat
`color` value holds a pattern word, that every split SKU carries its pattern, that every flat SKU of a splitting style states its own pattern, and that a split
color is still a plain color word (the main-color policies of gen#275 keep working).
