# Nike, the second real-brand exception (gen#341)

On the Combined persona `nike air max` found nothing, and with spelling correction on the phrase
suggester showed "nose air max". Shoppers type well-known sportswear brands, so the maintainer
ruled (2026-10-15) that Nike is a real brand beside Apple, iPhone and iPad. Every other brand stays
invented.

## What a real brand is

Text only. The name is in the `title`, the `brand` field and the `description`. No drawing carries a
logo, a swoosh, a wordmark or a trade dress: `house_styles.HOUSE_STYLES["Nike"]` has the mark
`none`, and `house_styles.logo()` draws nothing for it. `tests/test_retail_nike_341.py` renders
Nike drawings and refuses a mark, a text element or the name in the SVG.

## The guard

`prototypes/retail_drawings/real_brands.py` holds `ALLOWED` (the exceptions) and `KNOWN_REAL` (the
real names the catalogue refuses: sportswear, electronics, retail). `check()` scans the brand,
title and description of every product and returns a line per refused name; a name inside an
invented word ("Pumaleigh") is not a match. To rule another brand in, move its name from
`KNOWN_REAL` to `ALLOWED` in the same change as the README and the issue that records the ruling.

## What the catalogue holds

`prototypes/retail_drawings/nike_rows.py` (templates only: `scale.derivable` leaves them out as
`scale.NIKE_IDS`, and `main_colors.complete` gives none a color):

- 14 trainers and running shoes in the existing leaves of Mens, Womens and Kids, eight of them Air
  Max, each in three or more of the six main colors.
- Sportswear: joggers (Mens, Womens), crew sweatshirts and tees (Mens, Kids), a sports bra. The kit
  has no hooded sweatshirt, so there is no hoodie.
- 9 text-match decoys (gen#294): products of other, invented brands in 7 product types whose
  description names Nike ("safe on Nike and other trainers") while the title does not.

`decoy_apparel.build()` never clones a Nike product, so no invented-brand decoy copies the brand.

## Release

This ships with the next retail catalogue re-release, not as its own ingest (the batch rule).
