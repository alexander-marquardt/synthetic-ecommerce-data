# Merchandise of invented kids' films, named only in the text (gen#887, gen#905)

The catalog sells merchandise for twelve invented kids' films. A film's name is a phrase a shopper
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
| The Toy Movie | `TM` | mug, kids' tee, kids' sweatshirt, pyjamas, lunch box, party cups, birthday cake, sweets |
| Frozen Story | `FS` | mug, kids' tee, pyjamas, lunch box, seagull soft toy, stickers, sweets |
| The Home Run | `HR` | kids' tee, kids' sweatshirt, pyjamas, mascot soft toy, stickers, party bags, birthday cake |
| The Lady in High Heels | `LH` | mug, kids' tee, pyjamas, lunch box, stickers, party bags, birthday cake, sweets |
| The Haunted Dollhouse | `HD` | mug, kids' tee, kids' sweatshirt, kids' duvet set, ghost cat soft toy, stickers, cake |

Each film sells a few dozen SKUs. Every film sells in seven or more categories, and each sells a cake or
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
- **Five names hold a category word (gen#905), and none of those films sells in that
  category.** The name is the only link to it, so a search for the name that became a category
  filter would lose every one of the film's products (`kids_films.NAMED_CATEGORIES`):

  | Film | Category words in the name | It sells nothing under |
  |---|---|---|
  | The Toy Movie | toy | Toys (no stickers, no soft toy) |
  | Frozen Story | frozen | Food & Drink > Frozen, Frozen Food |
  | The Home Run | home, run | the Home department, Running Shoes, Marble Runs |
  | The Lady in High Heels | heel (and so every shoe) | Shoes |
  | The Haunted Dollhouse | doll | Dolls & Accessories (Dolls, Dolls' Houses) |

  "Movie" is part of one name, The Toy Movie, so its descriptions say "from The Toy Movie"
  rather than "The Toy Movie movie", and its titles say "Movie" only inside the name
  (`kids_films.called_a_movie`).
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
| The Toy Movie | a red wind-up robot with a key | Toy Movie Studios |
| Frozen Story | a six-armed snowflake | Frozen Story Studios |
| The Home Run | a baseball over a crossed bat | Home Run Studios |
| The Lady in High Heels | a red high-heeled shoe | Lady in High Heels Studios |
| The Haunted Dollhouse | a small house with a ghost in its window | Haunted Dollhouse Studios |

The scared face, the balloon, the ice castle and the duck are the maintainer's; the cowboy, the
lantern and the crown are proposals the maintainer may change, as are the five of the films
of gen#905.

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
- The drawing is chosen by the product's id (`film_emblems.emblem_of_id`, which reads
  `kids_films.film_of_id`), so no field of the record changes, and every SKU still has its own
  image file. The Barry Plotter range carries its own emblem and licence line the same way
  ([barry-plotter-925.md](barry-plotter-925.md#the-emblem-and-the-licence-line-gen928), gen#928).

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
  group that no other style completes (none today). Its sale comes from a pass of its own over
  the film products, as the Kids depth rows' does (gen#905): the film SKUs count toward each
  people department's total, so they carry their part of its share (`sale_share.SHARE`), and
  no other style's sale moves. Without that pass the five films of gen#905 thinned the Kids
  share to 9.97%, under its 10%. Four film products are reduced today (the Really Cold jumper
  and three pyjamas); a film product outside the people departments is never reduced. When
  gen#887 landed, the template builds of main and of its branch differed by the 54 new
  products alone, and the 150K scaled build differed only by its last two derived styles,
  which the new templates pushed past the SKU target.
- Every SKU has its own image file, drawn by the kit (one per SKU, [images](../images.md)).

## The test

`tests/test_kids_films_887.py` pins the film list and checks these points over the whole
template build (`tests/test_kids_films_905.py` adds the named categories, below):

- no film name is in a brand, a series or a category field anywhere;
- only the film rows name a film;
- every film sells in five categories or more, with a Food & Drink item among them;
- every description says `<film> movie`, and no title says "movie" outside the film's name;
- every film has both a description-only product and a titled one;
- every film SKU has its own image file, drawn in SVG paths with no embedded image;
- the film SKUs on sale reach each people department's share;
- a Blue Balloon product's title names one of its own colors;
- the other products of the types the films join are as main built them before the films
  came (`tests/data/kids_films_887_neighbors.json`).

`tests/test_film_emblems_904.py` reads every film SKU's image and checks that it carries its
film's emblem and no other, and its studio's licence line; that no other product of the types the
films sell carries either; that The Blue Balloon sells red, yellow, white, green and blue, with at
least half of its colored SKUs not blue; and that each colored Blue Balloon product has one color
its title names.

`tests/test_kids_films_905.py` checks that no product of the five gen#905 films has a category
path that holds a word its name names, that each of those words is a category of the catalogue
(so the check is not empty), and the range of SKUs each film sells.

Each film's emblem, printed on its products, is gen#904's.

The names follow the invented-brands rule (no real film titles). They were given by the
maintainer and have not been checked on the web.
