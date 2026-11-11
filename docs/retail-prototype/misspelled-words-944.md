# Misspelled products for the spelling suggestion (gen#944)

The retail-and-industrial demo serves the literal hits of a misspelled search and offers "You may
also consider searching for <common spelling>" only when the search has **3 or fewer** Best
results (the Engine's `did_you_mean_head_hit_threshold`, kept at 3) and the common spelling is at
least 5 times more common. The maintainer asked for a few misspelled products, half of the words
on three products or fewer and half on more, so the demo shows both behaviours.

The rows are in `src/synthetic_ecommerce_data/domains/retail/feature_decoys/misspelled_words_944.py`
and the four invented brands, with their owners and house styles, in `misspelled_brands.py`.

| Misspelling | Products | Common spelling | Category | The demo shows |
|---|---|---|---|---|
| choocolate | 3 | chocolate | Food & Drink > ... > Chocolate Bars > Milk Chocolate Bars | the hits and the suggestion |
| bannana | 3 | banana | Food & Drink > Fruit & Vegetables > Fresh Fruit > Bananas | the hits and the suggestion |
| leggins | 8 | leggings | Womens > Leggings | hits only |
| cardigen | 8 | cardigan | Womens > Knitwear > Cardigans | hits only |

## What a product is

- **An ordinary product of the word's own type and category**: a milk chocolate bar, a pack of
  five bananas, leggings in UK sizes 6 to 16, a cardigan in the same sizes. Every structured
  field tells the truth; these are no decoys.
- **The misspelling is product text only.** It sits in an invented brand (`Choocolate Factory`,
  `Bannana Bros`, `Leggins Lab`, `Cardigen & Co`), in a product name in the title
  (`High-Rise Gym Leggins`, `Big Bannana Bunch`), or, on two products, in the description alone
  (`Hazelnut Milk Chocolate Bar`: "in creamy milk choocolate"). No category node, product type or
  attribute holds one, so no vocabulary or category name learns the misspelling.
- **No real brand.** The four brands are invented and third party; each draws its own name on
  its images in a dedicated house style.

## What else moves

Nothing. The rows are left out of the derived styles (`Home("decoy_product_words", False)` on the
Cardigan, Chocolate Bar and Fresh Fruit specs; Leggings had it already) and out of the clothing
text-match decoys' exemplars (`decoy_apparel.build`), so no other product changes. Measured on the
ceiling build a release ships: 16,686 products and 262,668 SKUs on main, 16,708 and 262,770 with
these rows, the 22 products and their 102 SKUs, and no other record differs.

## Not built here

`pliars` (pliers), the issue's fifth word, is an industrial product: retail has no Pliers type,
and the catalogue's pliers are in `Tools > Hand tools > Pliers`. It is a separate industrial
change.

`tests/test_retail_misspelled_words_944.py` counts each word's products on the ceiling build,
checks each product's category and type, that the common spelling of a three-product word is at
least 5 times more common, and that no category, type or attribute holds a misspelling.
