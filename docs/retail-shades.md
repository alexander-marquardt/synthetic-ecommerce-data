# Complexion products are sold by shade (gen#345)

A foundation, a concealer and a tinted moisturiser are asked for by the skin they match ("foundation
for medium skin, warm undertone", "6N"), never by a color ("red foundation"). The shade codes
(`1C` to `13N`) used to be written to `color`, the facet clothing queries read, and polluted it.

## What the export writes

For a product of `shades.SOLD_BY_SHADE` (`Foundation`, `Concealer`, `Moisturiser`), each variant and
the style carry three attribute entries and **no `color` entry at all**:

| key | value | from |
| --- | --- | --- |
| `shade` | the code or name as sold: `6N`, `Porcelain` | the authored shade |
| `shade_depth` | `fair`, `light`, `medium`, `tan`, `deep` | the code's depth: 1-2 fair, 3-5 light, 6-8 medium, 9-11 tan, 12+ deep |
| `undertone` | `cool`, `neutral`, `warm` | the code's letter: `C`, `N`, `W` |

A shade that is a name, not a code, states its depth and undertone in `shades.NAMED`; `shades.classify`
refuses a name that is not there, so nothing is guessed from a word. A complexion type is also a
declared exception to the six main colors (`main_colors.EXCEPTIONS`).

`variant_axes` of a foundation is `shade` (the depth and undertone follow it), and the keys are
declared in `export.SHARED_OPTIONS` like every other attribute.

## What stays

- The authored record keeps the shade under its `color` key, the swatch the drawing and the image id
  read, so no image id moves for a coded shade. `export` is the one place that turns it into the
  three entries. A shade sold under its own name is authored with `variants.shade`, which does not
  fold it into a plain color word (`cw("Porcelain", ...)` would give `Cream`).
- Lip, nail and eye products keep their `color`. Their named shade (`shade` beside the color
  family) is not written yet.

## Guards

`tests/test_retail_shade_345.py`: no `color` value of the nested or the flat export matches the shade
code pattern; every complexion variant has one `shade`, `shade_depth` and `undertone`, derived as
above, and no `color`; the lip products still have theirs.
