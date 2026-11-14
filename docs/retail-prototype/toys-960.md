# Toys in depth, slice 1 (gen#960): board games, jigsaws and card games

The Toys department held 1,464 SKUs at the ceiling build, 10 of them board games and 7 jigsaws,
because every game and puzzle row was a template only (`toys_rows`, left out of the
derivation). Slice 1 of gen#960 makes three types breadth types: their spec files hold
`derivable` rows whose titles show the values a derived style swaps.

| Type | Spec | Path | Templates | Title shows | SKU axis |
|---|---|---|---|---|---|
| Board Game | `type_specs/board_game.py` | Toys > Games > Board Games | 20 themes | theme, kind | edition: Standard, Travel, Deluxe |
| Jigsaw Puzzle | `type_specs/jigsaw_puzzle.py` | Toys > Puzzles > Jigsaw Puzzles | 12 piece counts, 150 to 2000 | theme, piece count | one SKU |
| Card Game | `type_specs/card_game.py` | Toys > Games > Card Games | 6 named, 16 themed | kind (and a themed row's theme) | edition: Standard, Travel, Deluxe |

The older board games and jigsaws stay in `toys_rows` as templates only (the spec's `homes`
entry), so their seeded styles do not move. Their toy type and theme now use the breadth
rows' words, so a title and its attribute agree and a facet holds one value per kind: "Family
Board Game" (was "Family Game"), "Strategy Board Game", "Party Board Game", and the jigsaw
themes "World Map" (was "Maps"), "Dinosaur" and "Landscape". Their drawing params are
unchanged, so their pictures are too.

**What a derived style swaps.** A board game's title is `<theme> <kind> Board Game` ("Pirate
Island Strategy Board Game"): the theme pool is the twenty themes, the kind pool is Family,
Strategy and Party Board Game. A card game's kind is Family, Party or Strategy Card Game, and a
themed row's title is `<theme> <kind> Card Game`. A jigsaw's theme is one of the five pictures
the kit draws (Seaside, Dinosaur, World Map, Space, Landscape); its piece count has a unit, so
a derived jigsaw keeps it. Each text names the theme and the kind and nothing that holds for
one of them only, so a swapped style reads true.

**What a derived style keeps.** `age_range`, `play_time` and `finished_size` are in
`scale_text.FROZEN_KEYS`: a game's age and play time follow the template's game, a jigsaw's
age and finished size follow its piece count. No derivable template carried them before, so no
other department's styles move. The player counts and the item length and width have units, so
they are kept too.

**Drawings.** Each param is the lower-cased attribute value, so it follows a swap (gen#512).
`kit_toys.board_game` reads a kind that ends in " board game" and `kit_toys_play.card_game`
one that ends in " card game", so a derived Party Board Game draws the sand timer and a
derived Strategy Card Game the square pip. `kit_toys.jigsaw` maps the breadth themes to its
pictures (`JIG_THEMES`: "world map" draws the map, "dinosaur" the dinosaurs, "landscape" the
landscape) and draws a grid of exactly the piece count. A themed board game or card game also
carries a `theme` param, and the kit prints the theme on a name panel on the box, as the title
shows it. Without it, two derived games of one template and kind drew the same results tile at
the same price: the ceiling build's grid-clone share was 19.1%, over its 15.2% cap
(`tests/test_retail_scale.py`); with it, 12.1%.

**Brands.** The rows sell under brands that already have a house style and an owner: Little
Fernby, Puddlecombe Toys, Calderby & Lune, Lanternby and Thistle & Wren. Pipwick Toys is the
department's invented brand (`scale.EXTRA_BRANDS`), which only a derived style carries, so no
template sells under it. A derived style draws its brand from the department's pool, so a type yields at most (title-shown value combinations x
6 brands) styles; a jigsaw template yields at most 4 more, one per other theme.

**Decoys.** Board games and jigsaws each carry a class 6 decoy (another toy's words as a range
name: `Jigsaw Junction`, `Card Game Club`) and a class 4 decoy (a material the product lacks:
`Wooden-Look`, on a board game and on a jigsaw). Card games keep their four. Some 270 derived card games
now answer `card game` ahead of every decoy, so `tests/test_retail_toys_depth_424.py` measures a
decoy's ranking window against the authored styles it was placed beside.

**Measured** (ceiling build, seed 0): about 3,400 Toys SKUs, against the slice's floor of 3,000;
the exact figures are read from the build (`retail_figures`). Figures, dolls and building sets
(slice 2) and crafts, remote-control toys and learning toys (slice 3) are later slices. The
guards are in `tests/test_retail_toys_960.py`.
