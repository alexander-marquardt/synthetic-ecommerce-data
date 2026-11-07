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

52 products and 210 SKUs. Every film sells in seven or more categories, and each sells a cake or
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
- **The Blue Balloon comes in many colors, not mostly blue** (gen#904): a red mug, a yellow
  tee, a green sweatshirt, a white duvet set, blue party cups and red party bags. Each colored
  product has one color and its title names it ("The Blue Balloon Red Stoneware Mug"), so
  `the blue balloon` has to stay a name and not become the color Blue: one of its twelve
  colored SKUs is blue. A title that names one of the product's own colors is one the output
  standard's text check passes, as it passes any other product.

## The emblems (gen#904)

Each film has one emblem, printed on every product it sells, so the hits of a film search can be
seen to belong together. The emblems are original drawings in SVG paths
(`src/synthetic_ecommerce_data/domains/retail/film_emblems.py`), each a round badge: a white
disc in a dark ring with the film's picture in it.

| Film | Emblem | Studio on the licence line |
|---|---|---|
| Plaything Story | a toy cowboy, his hat and his red neckerchief | Plaything Story Studios |
| Lovely and the Beast | a lit lantern | Lovely and the Beast Studios |
| Duck Run | a yellow duck, running | Duck Run Studios |
| Really Cold | an ice castle of three towers | Really Cold Studios |
| Little Tiny Queen | a small gold crown | Little Tiny Queen Studios |
| Home Without Anybody | a scared face, wide eyes and an open mouth | Home Without Anybody Studios |
| The Blue Balloon | a blue balloon in the badge's circle | Blue Balloon Studios |

The scared face, the balloon, the ice castle and the duck are the maintainer's; the cowboy, the
lantern and the crown are proposals the maintainer may change. The five films of gen#905 get
theirs when they join the catalog.

- **On the product.** `film_emblems.PLACES` gives each shape the films sell the badge's center
  and radius on its widest plain surface: the chest of a tee, the side of a mug, the top tier of
  a cake, one sticker of a sticker sheet. The badge is drawn inside the product, so it scales,
  turns and shrinks with it, and is the same drawing on every product of the film: the product
  keeps its own color, and The Blue Balloon's balloon stays blue on a red mug. Its ink is not the
  kit's, so a brand's house style does not restyle it.
- **The licence line.** Beside the maker's logo (Brackenmere Home, Lanternby, ...) each film
  product's image sets a small line, the emblem and "Licensed from <studio>", in the logo's
  family and ink, on the product's side of the logo's text: under a logo at the top of the sheet,
  over one at its foot. The product is drawn clear of it, as it is of the logo
  (`house_styles.product_transform`'s `extra`). Each studio is invented and named after its film.
- The drawing is chosen by the product's id (`kids_films.film_of_id`), so no field of the
  record changes, and every SKU still has its own image file.

## Where it lives

- `src/synthetic_ecommerce_data/domains/retail/kids_films.py` holds the films (`FILMS`) and the
  rows (`ROWS`). Each type's spec (`type_specs/mug.py`, `tee.py`, ...) reads its own film rows
  with `kids_films.rows_of(<product type>)`, so the rows are ordinary rows of the types they
  join, with the types' brands, categories, sizes and drawings. The specs are not derivable, so
  the scaled build draws no derived style from a film product.
- **Stickers** are a new type, `type_specs/stickers.py`, at `Toys > Arts & Crafts > Stickers`:
  the film sheets, and two plain ranges so that `stickers` finds more than film products. Its
  drawing, `sticker_sheet`, is drawn in code: a paper sheet of die-cut stickers, the largest in
  the row's first color. A sheet's SKU carries no color. The type is a kind of the toys family
  of the line grammar (`line_grammar_families/toys.py`), as every Toys kind is.
- A film's party cups name their use in the title ("Duck Run Paper Party Cups for Birthday
  Parties"), so they are six to ten words long, as every real party cup is.
- **No other product moves.** The film rows stay out of the passes that weigh one style against
  another: the apparel decoys never clone one (`decoy_apparel.build`), and the main-color and
  sale passes of `scale.templates` leave them out. A film product takes a main color only in a
  group that no other style completes (none today), and it has no sale price. The
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
- every film SKU has its own image file, drawn in SVG paths with no embedded image;
- a Blue Balloon product's title names one of its own colors.

`tests/test_film_emblems_904.py` reads every film SKU's image and checks that it carries its
film's emblem and no other, and its studio's licence line; that no other product of the types the
films sell carries either; that The Blue Balloon sells red, yellow, white, green and blue, with at
least half of its colored SKUs not blue; and that each colored Blue Balloon product has one color
its title names.
- the other products of the types the films join are as main built them before the films
  came (`tests/data/kids_films_887_neighbors.json`).

The names follow the invented-brands rule (no real film titles). They were given by the
maintainer and have not been checked on the web.
