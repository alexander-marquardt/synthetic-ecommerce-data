# Merchandise of invented kids' films, named only in the text (gen#887)

The catalog sells merchandise for seven invented kids' films. A film's name is a phrase a shopper
types (`plaything story mug`), and no structured field holds it: the products keep the brands of
the houses that make them, carry no series and sit in the categories of their types. Each
description says the film is a movie ("a mug from the Plaything Story movie"). "Movie" is not part
of the name, so the phrase is the name alone.

| Film | Code | Sells |
|---|---|---|
| Plaything Story | `PS` | mug, kids' tee, pyjamas, lunch box, dinosaur soft toy, stickers, birthday cake, party bags |
| Lovely and the Beast | `LB` | mug, kids' tee, pyjamas, kids' duvet set, soft toy, party cups, sweets |
| Duck Run | `DR` | mug, kids' tee, kids' sweatshirt, pyjamas, lunch box, duckling soft toy, party cups, sweets |
| Really Cold | `RC` | mug, kids' sweatshirt, knitted jumper, pyjamas, kids' duvet set, stickers, cake |
| Little Tiny Queen | `LQ` | kids' tee, pyjamas, lunch box, kids' duvet set, stickers, party bags, sweets |
| Home Without Anybody | `HW` | mug, knitted jumper, kids' sweatshirt, pyjamas, lunch box, stickers, cake |
| The Blue Balloon | `BB` | mug, kids' tee, kids' sweatshirt, kids' duvet set, party cups, party bags, stickers, sweets |

52 products and 222 SKUs. Every film sells in seven or more categories, and each sells a cake or
sweets. A product's id is `BRD-KF<film code><kind>`, for example `BRD-KFPSMG`, the Plaything Story
mug.

## What a search meets

- **The name collides with catalog words on purpose.** `duck` is a product word, `cold` a drink
  and weather word, `Home` a department and `Blue` a color value, and `story` is no catalog word
  at all, so the spelling corrector rewrites it. Phrase matching has to keep each name together.
- **One product of each film names the film in its description only**, not in its title: the
  Plaything Story party bags, the Lovely and the Beast "Enchanted Castle" mug, the Duck Run
  "Farmyard" pyjamas, the Really Cold "Snow Day" sweatshirt, the Little Tiny Queen "Royal Picnic"
  lunch box, the Home Without Anybody "Holiday Family" cake and The Blue Balloon "Sky Adventure"
  stickers (`kids_films.DESCRIPTION_ONLY`). A search can rank a description-only match against
  a title match of the same film.
- **The Blue Balloon products that have a color sell Blue**, so a title that names Blue names a
  color the product has, and the output standard's text check passes them as it passes any other
  product.

## Where it lives

- `src/synthetic_ecommerce_data/domains/retail/kids_films.py` holds the films (`FILMS`) and the
  rows (`ROWS`). Each type's spec (`type_specs/mug.py`, `tee.py`, ...) reads its own film rows
  with `kids_films.rows_of(<product type>)`, so the rows are ordinary rows of the types they
  join, with the types' brands, categories, sizes and drawings. The specs are not derivable, so
  the scaled build draws no derived style from a film product.
- **Stickers** are a new type, `type_specs/stickers.py`, at `Toys > Arts & Crafts > Stickers`:
  the film sheets, and two plain ranges so that `stickers` finds more than film products. Its
  drawing, `sticker_sheet`, is drawn in code: a paper sheet of die-cut stickers, the largest in
  the row's first color. A sheet's SKU carries no color.
- **No other product moves.** The film rows stay out of the passes that weigh one style against
  another: the apparel decoys never clone one (`decoy_apparel.build`), and the main-color and
  sale passes of `scale.templates` leave them out. A film product takes a main color only in a
  group that no other style completes (the kids' lunch boxes), and it has no sale price. The
  template build of main and of this branch differ by the 54 new products alone, and the 150K
  scaled build differs only by its last two derived styles, which the new templates push past
  the SKU target.
- Every SKU has its own image file, drawn by the kit (one per SKU, [images](../images.md)).

## The test

`tests/test_kids_films_887.py` pins the film list and checks these points over the whole
template build:

- no film name is in a brand, a series or a category field anywhere;
- only the film rows name a film;
- every film sells in five categories or more, with a Food & Drink item among them;
- every description says `<film> movie`, and no title says "movie";
- every film has both a description-only product and a titled one;
- every film SKU has its own image file, drawn in SVG paths with no embedded image.

The names follow the invented-brands rule (no real film titles). They were given by the
maintainer and have not been checked on the web.
