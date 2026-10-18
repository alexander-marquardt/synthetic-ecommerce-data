# Retail neckline depth (gen#181)

"womens boat neck top" must filter or boost the stored `neckline` and bury the other neck types.
The catalog could not show it: two tops were boat and one slash. `prototypes/retail_drawings/neckline_rows.py`
adds the products a ranking needs, and gives every top, dress and knit a neckline. The floors are
pinned by `tests/test_retail_neckline_181.py` over `scale.templates()`, counting products (a style;
its colors times its sizes are its SKUs), not SKUs, and leaving out the text-match decoys that copy
a style's neckline. It builds on #309 (knitwear, which carries its neckline already), #302 and #275
(colors) and #294 (decoys).

## What the build holds

| Neckline | Floor (products) | Where |
|---|---|---|
| boat + slash | 40 tops, at least 15 each | Womens Jersey Tops and Long Sleeve Tops |
| crew, round, v-neck, high, collared | 120 each | tops, dresses, knits, shirts |
| square, halter, cowl | 30, 20, 20 | tops and dresses |
| boat or slash on a near-miss type | 3 each | bodysuits, co-ord sets, dresses |

`high` is the roll, turtle, funnel and half zip neck; `round` is the scoop neck; `slash` is drawn
as a boat. The values are a stored fact (`neckline`) and the drawing shows it: the top kit draws
`halter` and `cowl` now, and a dress takes a `neckline` param (`kit.DRESS_NECKS`). A test fails a
style whose picture and fact differ.

## Words and decoys

- **Title wording.** Six boat and slash tops in ten name the neckline in the title ("Womens Boat
  Neck Everyday Satin Fitted Long Sleeve Top"); the rest carry it as the attribute and a
  description with no `boat` or `slash` in it ("a wide, shallow neckline"). The attribute finds
  all of them, a text match part.
- **Neckline-word decoys.** A boat print, a slash pocket, slashed sleeves, a boathouse stripe, a
  rowing crew slogan: the word is in the title and the stored neckline is true (crew, v-neck,
  square). Top and Dress carry more apparel decoys (`decoy_apparel._MORE`) since they grew.

## Every top, dress and knit has a neckline

`neckline_rows.complete` runs once over the templates: a style that states none takes the one its
title names ("Wrap Dress" is v-neck, "Shirt Dress" collared, "Roll Neck Jumper" high), else the one
its drawing shows, else (a dress) one chosen by its id and drawn to match. Nothing already stated
is changed.

## Not in this slice

Tie neck (two styles name it, stored as `tie-neck` with no drawing), one-shoulder, revere collar
and the `sleeve`, `waistband` and `detail` attributes of the coverage review stay open on #181.
