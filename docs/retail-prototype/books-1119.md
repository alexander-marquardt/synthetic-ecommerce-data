# Books (gen#1119, slices 1 and 2)

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
holds 61 `(title, type, word)` entries over 60 titles and 55 types: `The Book of Chocolate`
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

**Pending.** Slice 3 adds a brownie mix and tin set, so `How to
Make Brownies` has something to collide with, and the demo query list: the issue's eight queries,
each with its family and its expected results.

**Measured** (ceiling build, seed 0): slice 1's floor is 1,400 Books SKUs, against the 1,500
target in `docs/catalogue-mix-837.md`. The figures themselves are build output, read with
`retail_figures.figures()`. The guards are in `tests/test_retail_books_1119.py`.
