# Books (gen#1119)

The store had no books, so a search for `the book of chocolate` found only chocolate bars, and a
demo had no way to show a title's words pulling in the thing the book is about. `Books` is now on
the closed list of retail departments (`core/departments.RETAIL`) and on the build record's list
(`domains/retail/departments.py`), which keys the brand pools. Its one type is a spec of its own:

| Type | Spec | Paths | Templates | SKU axis |
|---|---|---|---|---|
| Book | `type_specs/book.py` | Books > Cookery & Baking, Crafts & Sewing, Gardening, DIY, Pet Books, Children's Books, Fiction, Travel Books | 480 (60 a leaf), and the Barry Plotter series | format (`format`): Ebook, Paperback, Hardback, cheapest first |

Books are templates only (`derivable=False`): the scaled build invents no title. The rows, the
eight publishers and the collision list are in `books_rows.py`. A book carries no color (`colorless`): its cover color is drawn, not sold.

**Attributes.** Every title carries `author`, `publisher`, `genre`, `pages` and
`publication_year`. A children's title also carries `age_band` (0-2, 3-5, 6-8 or 9-12 years),
and its page count is drawn from that band's range. The other leaves draw their pages from the
leaf's own range, so a novel runs longer than a picture book.

**Invented, not copied.** Every title, author and publisher is invented (ruling 2026-11-21). The
id is our own (`BRD-BOOK001`), never an ISBN. The eight publishers (Wrenhallow Press, Marlowby
Books, Thimblecote Press, Ferncastle Editions, Ashcombe & Rook, Lindenquay Publishing, Moddlewick
Books, Gullfeather Press) are each a book's brand and its `publisher` attribute, and
`book_brand_styles.py` gives each its mark and house style. No author is a brand.

**Collisions.** A title is written by hand when it collides with a type of another department,
and otherwise built from one of its leaf's subjects in one of the leaf's frames. `COLLISIONS`
holds 63 `(title, type, word)` entries over 61 titles and 57 types: `The Book of Chocolate`
beside the chocolate bars and boxes, `Knife Skills` beside the kitchen knives, `Your First
Puppy` beside the dog food. Each word is in the title and in some title of its type in the build,
so a search for it finds the book beside the product.

**Range names.** A character or place in a generated title (`Goodnight, Olwen Owl`, `Summer at
Quoyness`) is invented to read as no range or brand the build already holds. The range guards of
gen#623 (`tests/test_retail_scale.py`) read a title's leading name as a range, so a book named
for another brand's range would put that range under two brands.

**Drawings.** `kit_books.py` draws one shape, `book_cover`: a book seen from the front, a little
turned, with the page block behind, the spine in a darker shade and two bars where the title and
author are printed. It takes `layout` (0 to 5: a top band, a foot band, an inset frame, a sash,
rules, a medallion) and `genre` (the leaf's emblem). A title's index in its leaf picks one of ten
cover colors and one of six layouts, so no two titles of a leaf share a picture.

**The Barry Plotter series (slice 2).** The invented franchise of gen#925
([barry-plotter-925.md](barry-plotter-925.md)) sold its merchandise but none of the books it is
named for. `barry_plotter_books.py` holds nine products, two dozen SKUs, in Books > Children's Books,
for ages 9-12:

| Product | Formats | SKUs |
|---|---|---|
| Book 1: The Enchanted Allotment | Ebook, Paperback, Hardback | 3 |
| Book 2: The Talking Scarecrow | Ebook, Paperback, Hardback | 3 |
| Book 3: The Moonlit Glasshouse | Ebook, Paperback, Hardback | 3 |
| Book 4: The Compost Dragon | Ebook, Paperback, Hardback | 3 |
| Book 5: The Clockwork Mole | Ebook, Paperback, Hardback | 3 |
| Book 6: The Whispering Bramble | Ebook, Paperback, Hardback | 3 |
| Book 7: The Frost Fairy | Ebook, Paperback, Hardback | 3 |
| Box Set, Books 1 to 7 | Paperback, Hardback | 2 |
| Book 1: The Enchanted Allotment, Illustrated Edition | Hardback | 1 |

Every title starts with the series ("Barry Plotter, Book 3: The Moonlit Glasshouse") and takes its
words from the range's own motifs, never from a real series' titles or their pattern. The name is
in the title and the description only, never "Barry's", and each description says "the Barry
Plotter books" where the merchandise says "from the Barry Plotter films". The author (Winifred
Tansley) and the publisher (Trowelgate Books) are invented and sell nothing else. A cover prints
its motif's badge and no licence line, and the box set is a slipcase of seven spines
(`kit_books.book_box_set`). The guards are in `tests/test_barry_plotter_books_1119.py`.

**The brownie set (slice 3).** `How to Make Brownies` had nothing to collide with, so a small
baking set is sold beside it:

| Type | Spec | Path | SKU axis |
|---|---|---|---|
| Brownie Mix | `type_specs/brownie_mix.py` | Food & Drink > Food Cupboard > Baking > Baking Mixes | net weight (`net_weight_g`): 350 g, 500 g, 1 kg |
| Brownie Tin | `type_specs/brownie_tin.py` | Home > Kitchen & Dining > Bakeware > Brownie Tins | length (`length_cm`) |

Both are templates only, from brands the two departments already sell, and neither is sold by
color. `kit_baking.py` draws them: a mix's carton shows what tops the brownies, and a tin shows
its outline, loose base, twelve cells, depth, enamel or lid. Two products hold the plural the book
title holds (the kit with a foil tray, and the divided tin for 12 brownies). The others say
`brownie`, so a search has to stem the word to find them. The guards are in
`tests/test_retail_brownies_1119.py`.

## Demo queries

What each query is expected to return. These are expectations to demo against, not measured
results. "With a policy" names what a merchandiser's policy is meant to do; the policies belong to
the demo that loads this catalogue.

| Query | Collides with | Without a policy (expected) | With a policy (expected) |
|---|---|---|---|
| `the book of chocolate` | Chocolate Bar, Chocolate Box | The book in its three formats, possibly below chocolate boxes | The book first (book intent) |
| `chocolate` | The book `The Book of Chocolate` | Bars and boxes, with the book mixed in | Bars and boxes; the book demoted, or behind a Books facet |
| `how to make brownies` | Brownie Mix, Brownie Tin | The book, plus mixes and tins | The book first |
| `brownie tin` | The book `How to Make Brownies` | Tins, and maybe the mixes and the book | Tins only |
| `learn to sew` | Sewing Thread and the Sewing & Knitting range; sewing machines once gen#1118 adds them | The book, plus sewing thread (and sewing machines, once sold) | The book first |
| `barry plotter book 3` | The Barry Plotter merchandise | Book 3's three formats, with merchandise that carries a "3" (3-packs, age 3+) near them | Book 3 in all three formats first |
| `barry plotter box set` | The Barry Plotter gift sets | The box set among the merchandise's "set" products | The box set first, in paperback and hardback |
| `barry plotter` + Books facet | The Barry Plotter merchandise | Without the facet: the books among all the merchandise | With the facet: only the series' two dozen SKUs |

**Measured** (ceiling build, seed 0): slice 1's floor is 1,400 Books SKUs, against the 1,500
target in `docs/catalogue-mix-837.md`. The figures themselves are build output, read with
`retail_figures.figures()`. The guards are in `tests/test_retail_books_1119.py`.
