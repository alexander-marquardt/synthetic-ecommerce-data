# Knacks, the invented sportswear brand (gen#722)

Knacks replaces the real sportswear brand that gen#341 had ruled in on 2026-10-15. The maintainer's
ruling of 2026-10-30: a public catalogue and a commercial demo should not sell invented products
under a real company's name and its model names at invented prices. The issue chose `Knacks`
and `Breeze Max` over the first suggestions: `Knicks` is a registered mark that covers basketball
shoes, and "Cloud" plus "Max" sits on another footwear brand's line names.

## What moved and what did not

The same 22 products, under new names. `tests/test_retail_knacks_722.py` holds each one against
`tests/data/knacks_722_products.json`, recorded from main before the rename: its id, type, category,
price, colors and every SKU are unchanged. The ids keep their `NK` codes for that reason.

| Line | Products |
|---|---|
| Breeze Max | `90`, `270`, `Run`, `Sunup`, `Romp` |
| Courtmark, Roadlark | low trainers; road running shoes |
| Scamperfoot, Bendway | kids running shoes |
| Snugworth, Emberline | fleece joggers and crew sweatshirt; fleece joggers |
| Driftdry | training tees and the sports bra |

The number and `Run` are generic, so they stayed; the other model words were renamed. Each new name
was searched on the web on 2026-10-30 with footwear and sportswear terms. That search dropped three
candidates: `Fireside` and `Daybreak` are real lines, and `Skiprun` sits next to a real one.

## The guard

`src/synthetic_ecommerce_data/domains/retail/real_brands.py` lists `Nike`, `Air Max`, `Pegasus` and
`Dri-FIT` in `KNOWN_REAL`, so `check()` refuses them in the brand, title and description. `ALLOWED`
holds the Electronics exception alone ([retail-electronics.md](retail-electronics.md)). A name inside
an invented word ("Pumaleigh") is not a match.

## What the catalogue holds

`src/synthetic_ecommerce_data/domains/retail/knacks_rows.py` (templates only: `scale.derivable` leaves
them out as `scale.source_ids("knacks_rows")`, and `main_colors.complete` gives none a color):

- 14 trainers and running shoes in the existing leaves of Mens, Womens and Kids, eight of them Breeze
  Max, each in three or more of the six main colors.
- Sportswear: joggers (Mens, Womens), crew sweatshirts and tees (Mens, Kids), a sports bra. The kit
  has no hooded sweatshirt, so there is no hoodie.
- 9 text-match decoys (gen#294): products of other, invented brands in 7 product types whose
  description names Knacks ("safe on Knacks and other trainers") while the title does not.

`decoy_apparel.build()` never clones a Knacks product, so the rename adds none. Knacks draws its own
mark, `laced_eyelets`: a shoe's laces crossing between two rows of eyelets, in straight strokes.

## Release

This ships with the next retail catalogue re-release, not as its own ingest (the batch rule).
