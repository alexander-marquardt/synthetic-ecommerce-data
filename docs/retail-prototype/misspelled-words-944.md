# Misspelled products for the spelling suggestion (gen#944, gen#1130)

The retail-and-industrial demo serves the literal hits of a misspelled search and offers "You may
also consider searching for <common spelling>" only when the search has **3 or fewer** Best
results (the Engine's `did_you_mean_head_hit_threshold`, kept at 3) and the common spelling is at
least 5 times more common, counted in the catalogue's titles (the `title` term suggester's
document frequency: a description that says the word adds nothing). The maintainer asked for a few misspelled products, half of the words
on three products or fewer and half on more, so the demo shows both behaviours.

The rows are in `src/synthetic_ecommerce_data/domains/retail/feature_decoys/misspelled_words_944.py`
and the four invented brands, with their owners and house styles, in `misspelled_brands.py`.

| Misspelling | Products | Common spelling | Where it sits | The demo shows |
|---|---|---|---|---|
| choocolate | 3 | chocolate | the `Choo-Choocolate Express` brand: two chocolate train gift boxes (Chocolate Boxes) and a wooden train set (Wooden Toys) | the hits and the suggestion |
| bannana | 3 | banana | the `Bannana Bros` brand: two bags of gummy sweets (Sweets); the Bannana Brothers Crazy Apes board game (Board Games) | the hits and the suggestion |
| pliars | 3 | pliers | Pliars, a bluffing party card game (pliers and liars): the base game, an expansion and a travel edition (Card Games) | the hits and the suggestion |
| leggins | 8 | leggings | the `Leggins & Co` fashion label: eight leggings (Womens > Leggings) | hits only |
| cardigen | 8 | cardigan | `Cardigen`, a deck-building trading card game (cards and generations): a starter deck, a booster pack, a booster box, the Dragons and Deep Space expansions, a two-player battle set, card sleeves and a deck box (Card Games) | hits only |

## What a product is (gen#1130)

- **The misspelling is a deliberate brand or product name**, a pun a real company might choose,
  so a shopper who types it is looking for that brand. It is never a misspelled generic word in
  an ordinary product's title or description: #944's `Big Bannana Bunch` of fresh bananas and
  `Hazelnut Milk Chocolate Bar` ("in creamy milk choocolate") read as data errors, and are gone.
  So are #944's `High-Rise Gym Leggins` and `Chunky Knit Cardigen`.
  `tests/test_retail_misspelled_words_944.py` checks that every occurrence of each of the five
  words sits inside one of the named brands or products.
- **Cardigen is far from knitwear.** It is a trading card game in Toys > Games > Card Games,
  with its own brand, title pattern and drawing, apart from the Pliars bluffing party game.
- **Each product is drawn by its own kit**: a gift box, a wooden train, a sweets bag, a
  board-game box, a card-game tuck box, leggings in three lengths (one pair with pockets), and
  the `trading_cards` shape of `kit_toys_play.py` for Cardigen: a foil pack (an expansion's
  shows its theme), a display box of packs, a stacked deck, two decks on a play mat, sleeves
  and a deck box. No product reuses the banana drawing.
- **No category node, product type or attribute holds a misspelling**, so no vocabulary or
  category name learns one. The types and categories are the real ones of the catalogue.
- **No real brand.** The four brands (`Choo-Choocolate Express`, `Bannana Bros`, `Leggins & Co`,
  `Cardigen`) are invented and third party; each draws its own name on its images in a
  dedicated house style, with a mark no other brand draws (`bar_grid`, `peel_arc`,
  `stride_bars`, `card_fan`). The board game and the three Pliars card games carry the own toy
  brand `Little Fernby`, with the misspelling in the product name.

## Pliars moved from industrial to retail

#944 put `pliars` on three industrial pliers (`Conduit Pliars`, `Snap Ring Pliars`, `Convertible
Snap Ring Pliars`): misspelled generic titles. gen#1130 removed them (the industrial module
`misspelled_pliers_944.py` and its hook in `domains/industrial/generate.py` are gone) and put the
word on the retail Pliars card game instead. `tests/test_industrial_misspelled_pliers_944.py`
now checks that no industrial pliers line and no golden-catalogue row holds `pliars`, and that
the golden catalogue still has its pliers.

## The pliers the suggestion counts

The industrial catalogue titles only 4 SKUs with `pliers`, against 3 with `pliars`, so the served
`pliars` search showed no suggestion (gen#1130). `type_specs/pliers.py` sells eight plain pairs of
pliers (combination, long nose, side cutter, water pump, slip joint and locking) in Home > DIY &
Tools > Pliers, two handle colors a pair, each drawn as its own jaw by `kit_pliers.py`. The ceiling
build holds `pliers` in 17 retail SKU titles (these 16 and one decoy) and 4 industrial ones: 21, over
the 15 the 5x ratio needs.
`test_the_common_spelling_is_five_times_more_common` counts titles SKU by SKU, as the Engine does.

## What else moves

- The rows are left out of the derived styles: `Home("decoy_product_words", False)` on the Board
  Game, Card Game and Wooden Toy specs (Chocolate Box and Sweets had it already). Fresh Fruit and
  Chocolate Bar no longer hold a row here, so their home is dropped, and so is Cardigan's once
  the Cardigen rows became card games.
- The golden catalogue loses the three industrial pliers products and their 3 SKUs
  (`nested.jsonl`, `flat.jsonl` and `images.jsonl` each drop 3 rows), and `stats.json`,
  `measured_builds.json` and the industrial field weights are rebuilt from it. No pin moved.

`tests/test_retail_misspelled_words_944.py` counts each word's products on the ceiling build,
checks each product's category, type and drawing, that a suggestion word sits only in its named
brand or product, that the common spelling is at least 5 times more common over the retail build
and the golden catalogue, and that no category, type or attribute holds a misspelling.
