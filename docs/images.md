# Images

This is the README's images reference: what the drawings promise, where a record points, the
bundle, the image release, and the one renderer (moved out of the README, #701).

The picture and the drawing speed are at the [top of the README](../README.md#synthetic-ecommerce-data).

**One drawing per SKU, drawn from that SKU's own values, with no text in it but
its brand's name.** The rulings are on elastic/prism-industrial-products#103
(2026-09-26 to -28); the brand plate is #132 (2026-10-08).
How the code does it -- record to figure to SVG bytes, the registry, the
provenance ladder, the publish gate, and a checklist for adding a type -- is in
[docs/drawings.md](drawings.md).

**Exception: the [breadth categories](../README.md#catalog-breadth) draw one of seven
FIXED shapes** (sphere, cylinder, block, disc, tube, bracket, and a found C-clamp --
`domains/industrial/drawing/breadth_shapes.py`), never scaled or dimensioned from the SKU's own
published values. The "drawn from its own dimensions" rule above does not
apply to them: they are filler to give a facet something to show, not a
figure meant to survive a close look (maintainer, 2026-09-30). They still go
through the same text allow-list, brand plate, house style and material/finish fill as
every other drawing -- only the GEOMETRY is fixed.

* **One image per SKU**, so two lengths of one screw look different, and a
  grouped view can switch the picture when a variant is selected.
* **A brand plate under the figure** (#132): the brand's mark beside its
  name, in a strip at the foot of the sheet (`core/drawing/sheet.py`,
  `PLATE_BOX`). The figure is drawn in the sheet above it, so the plate never
  covers a dimension, a head or a thread of any type; an engineering
  drawing's maker sits in its title block the same way. Legible at the
  Studio grid tile (180 px for the 300-unit sheet, 0.6 px a unit): no
  name's capitals render under 10 px tall there. The full name is set beside
  the mark, on two lines beside it, split around it, or under it, whichever
  comes first at that size; a name none of them fits is refused, never
  shortened. The plate is 56 units tall, so the figure has the 236 units
  above it. Every SKU of a brand carries the same plate.
* **No other text** -- no dimension, callout, label or SKU.
  The words are on the record (title, description, attributes); the drawing
  reflects the specifications **visually**: a longer length of cut is drawn
  longer, a finer thread with more crests, a flat head is a cone and a button
  head a dome, a sealed bearing is closed and an open one shows its balls.
  The gate is an **allow-list**, not a list of text forms
  (`drawing.svg_problems`):
  - every element must be one the figures emit (`svg, rect, defs, pattern, g,
    path, circle`, and the plate's `text`), and there is no nested `<svg>`;
  - the `<text>` elements' words, joined, must be a brand's wordmark, and
    the font attributes appear on `<text>` only;
  - every attribute must be one they use, and every attribute VALUE must fit
    its grammar: a paint is a color, `none` or a same-file hatch reference,
    never an external or `data:` URL;
  - every id is a hatch's or texture's (`tgrid`, `tdot`); dasharray: book's only;
  - no element but `<text>` may carry character data;
  - no comment, processing instruction, doctype or entity reference may
    appear, but the `&amp;` of a name like `Lark & Lathe`.

  One thing no structural check can catch: a glyph's outline drawn as a plain
  path is indistinguishable from any other outline. The review's plants
  -- `<title>`, `<desc>`, `aria-label`, a comment, `<metadata>`,
  `<foreignObject>`, an embedded raster, `@font-face`, a glyph path from any
  font -- each red `tests/test_sku_drawings.py`.
* **Brands visibly different**, by house style and by mark: each brand owns
  one (ink, frame) pair and an independent paper tint -- twelve inks, six
  papers, four frames in use -- and one mark, consistent within a brand, never
  random per product ([Brands](../README.md#brands)). Any two brands' marks, rasterised
  at the tile's 19 px, differ in at least 24 pixels
  (`tests/test_brand_marks.py`; the closest pair measures 25).
* **A part longer than its type's extent is drawn BROKEN**, not shrunk: the
  shank is shortened between two drafting break lines, head and thread end
  kept, to a height that still grows with the true length. The screw and bolt
  extents are the pre-100K ones, so one 14-5/8" outlier no longer draws every
  socket screw 2.5x smaller.
* **Finish and material** are the part's fill (the finish's color, else the
  bare material's) and its section hatch.
* **Small SVG**, written directly rather than through a figure library:
  about 2 KB a drawing. `figures.drawings` in `golden-catalog/stats.json` has
  the committed catalog's count, total and largest bytes and the largest's
  type; `uv run ecom-generate images --catalog golden-catalog --out /tmp/img
  --archive /tmp/img.tar.gz` prints them with the archive's size. Every root
  declares `width="200" height="300"` beside its viewBox: an `<img>` sized only
  by max-width/max-height in a flex item that does not grow renders a
  viewBox-only SVG at 0 x 0.

The drawing is a pure function of `(product type, brand, published attributes)`
(`src/synthetic_ecommerce_data/core/drawing/`). For the six kinds
with a module in `domains/industrial/geometry/` (end mills, drills, taps, screws
and bolts, washers, flap discs) it reads the SKU's geometry through that module's
`geometry_from_record`, which parses and checks a record and draws nothing; the other depth types read their few values inline, and the breadth
shapes read none.

**Sizes are visible.** The scale is one constant per product type: sheet units
per inch are the usable sheet over the type's largest drawn extent, declared
per type in `domains/industrial/drawing/figures.py`. There is no exception to it: a part too
small to read is not drawn larger, it is shown through a **magnifier**
(maintainer ruling on elastic/prism-industrial-products#103, 2026-09-28):

* a part is **too small to see** when it is drawn at most 1/5 of the sheet's
  width (40 units) AND at most 1/6 of its height (50), and such a part ALWAYS
  gets a lens (the refined ruling of 2026-09-28, with the edge cases settled at
  1/5 wide so socket screws drawn just over 1/6 are lensed); every other part
  is drawn plain, centred;
* the lensed part is drawn at its type's scale near the bottom of the sheet,
  horizontally centred, with no circle around it, and the lens above it shows
  the same figure enlarged so its bounding box's diagonal spans 92% of the lens;
* the lens is a magnifying glass in the icon's shape (a ring, a thin shaft and a
  grip twice the shaft's width, round caps, the handle at 45 degrees to the
  bottom-right), stroked at 35% of the icon's weight in the brand's ink, when
  that glass enlarges the part at least 2.5 times; otherwise it is a larger
  HANDLE-LESS lens -- the same thin ring and white interior -- sized to the
  sheet's width at an 8-unit side margin (the smallest that clears every brand
  frame by at least a unit), or to the 236-unit figure area above the brand
  plate where that is tighter. It cannot grow further: at the rule's extreme
  (a part drawn 40 x 50) it is height-bound and enlarges only ~x2.05, below
  the x2.5 the handled glass guarantees;
* the whole glyph is horizontally centred and as large as fits; the space above
  it equals the space below the part, with a 14-unit gap between them;
* no outline is thinner than 2.3 sheet units (~2 px on a 180 px-wide
  thumbnail), so a hairline part -- a 1/16" drill is under one unit wide at its
  type's scale -- is visible with or without a lens. Interior detail lines
  (flutes, threads, hatch) are texture and keep their finer weight.

How many committed SKUs are too small to see, how many of them get the handled
glass and how many the handle-less lens, with each lens's enlargement range, is
what the command in [docs/drawings.md](drawings.md#scale-the-magnifier-and-the-only-text) prints. The
lowest enlargement any committed lens gives is x2.46, a width-bound
handle-less lens (below); no committed part reaches
the rule's 40 x 50 extreme. No drawing
carries text; the magnifier adds only paths and circles, and
`stroke-linecap="round"` to the allow-list.

What `tests/test_sku_drawings.py` proves over the committed catalog:

* **One scale per type.** Every product is drawn at its type's scale, so any
  two parts of a type are in true proportion, and a head, a thread or a bore
  siblings share is drawn identically on each (measured on the true-scale
  part of every drawing: screws' heads and bearings' outer rings).
* **The magnifier:**
  * a lens appears on exactly the SKUs drawn at most 1/5 of the sheet's width
    and 1/6 of its height, over every committed SKU;
  * the handle-less lens is used exactly where the handled glass cannot reach
    x2.5; the committed catalog's lowest enlargement is the `lens.min_enlargement` of `tests/data/golden_pins.json` (its
    measured minimum, rounded down), and the rule's extreme (40 x 50) at
    x2.05 to x2.5 -- below x2.5 because the lens is height-bound in the
    236-unit figure area above the brand plate (#132);
  * the handle-less lens clears the brand frame (8 units in, frames at 6 with
    strokes at most 2 wide);
  * each dimension binds on its own (planted: 41 x 5 and 5 x 50.5 plain,
    39 x 5 and 5 x 49 lensed); long thin parts never get a lens;
  * the lens shows the same part: the same shapes, scaled about the two
    centres by the layout's enlargement, and inside the lens;
  * the space above the glyph equals the space below the part, the gap is
    14 units, and the glyph and the part are centred, for both kinds of lens;
  * the ring, shaft and grip are in the brand's ink; the handle-less lens has no
    shaft or grip;
  * no outline, glyph stroke included, is thinner than 2.3 units (the hairline
    drill 93TD57, under two units wide, is pinned).
* **Other properties:**
  * no product exceeds its type's extent;
  * no drawing leaves its sheet;
  * no two siblings draw alike unless they differ only in values no figure
    draws.

An M3 washer's true-scale drawing is exactly 7/30 of an M16's diameter.

A record whose geometry cannot be read as published -- an attribute absent, a
value that does not parse, a pair that contradicts itself -- is drawn with its
kind's **nominal** proportions for the missing or conflicting values, and
`images.jsonl` says so per SKU (`geometry`: `record`, `partial` or `nominal`).
A drawing with no text states no number, so a nominal proportion cannot
contradict a published value; a consistent published value always wins.
`tests/test_sku_drawings.py` asserts the parts that are drawn from the record
are drawn to exactly its published length.

### Where a record points, and the bundle

Every SKU's `image_id` is `<product type>/<product id>/<sku>`; its `image_url`
is `/images/industrial/<image_id>.svg`, and `image_detail_url` names the same
file (one SVG serves both views). A product shows its first variant's drawing.
The URL is relative on purpose: the demo serves the bundle's folder itself
(elastic/prism#9770), and nothing points at a third-party host. That includes
the personal site of the write-up: it hosts only a small sample of the
drawings (a few hundred), so a demo takes the full set from the generator or
the release bundle and serves it itself.

```sh
uv run ecom-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz
```

rebuilds every drawing from the **committed** catalog (`nested.jsonl`, with each
SKU's published spelling read from `flat.jsonl`), refuses unless each one's
sha256 equals the one `images.jsonl` records, and writes the files and a
deterministic archive (sorted members, zeroed times and owners, a gzip header
without a timestamp).

**Layout.** Every member is `industrial/<type>/<product>/<sku>.svg`: the
archive carries its own top-level `industrial/` folder, so a customization
unpacks it into its images folder, the demo serves that folder at `/images`
(elastic/prism#9770), and `image_url` -- `/images/industrial/...` -- resolves
with no per-deployment mount. A test pins that every member is exactly its
`image_url` under `/images`.

**The pin is of the content, not the compressed bytes.** gzip output depends on
the zlib build, so the archive's own sha256 is only stable on one toolchain.
What a customization pins is the **content digest**: the sha256 of the sorted
`<member path>\t<file sha256>` lines, printed by `ecom-generate images` and
written beside the archive as `.content-sha256`. It is derivable from the
committed `images.jsonl` alone (`bundle.manifest_digest`), and the installer
recomputes it after unpacking. `out/` is ignored by git, and a test asserts it,
so a drawing can never be committed here.

```sh
uv run python scripts/contact_sheet.py --catalog golden-catalog --out out/contact-sheets
```

writes an HTML contact sheet of real catalog SKUs -- one screw across its
lengths for two brands, flat washers across sizes, materials and brands, and
twenty SKUs of every type -- for judging the drawings by eye.

### The image release: one set, one file per SKU

```sh
uv run python -m synthetic_ecommerce_data.domains.retail.image_release --out out/images --archive out/images.tar.gz \
    [--skus ceiling] [--industrial-catalog out/catalog-100k]
```

packages the combined catalog's drawings as ONE image set under ONE pin (gen#706): every retail
SKU's image, and with `--industrial-catalog` every SKU of that industrial catalog directory
(rebuilt and checked against its `images.jsonl`, as `ecom-generate images` does), in the
industrial bundle's shape, so the same installer takes it. Members are `retail/<image_id>.svg`
and `industrial/<image_id>.svg` in one archive, unpacked into one images folder; every
`image_url` is its member under `/images/`. The deterministic archive, the content digest and
the file count are printed and written beside it as `.content-sha256`.

**Every SKU has its own file.** A retail `image_id` is `<type>/<product>/<sku>`, as an
industrial one is. What the file draws is keyed separately (`export.drawing_id`): the style and
colorway, the pack scale (a smaller size of a line draws smaller, gen#543; see
[the pack scale page](retail-prototype/pack-scale-543.md)), the pack count (a pack of N draws N
items, gen#728; see [the pack copies page](retail-prototype/pack-copies-728.md)), and for a type that declares a
size axis (`size_axes.AXES`) the size-ladder rung (`size_ladder.py`, gen#339, gen#719). SKUs that draw the same picture each get their own
copy of it, so one SKU's color, size or shape can change later without moving another's image.
The authored-styles build is `templates.authored` SKUs and files over `templates.authored_drawings`
distinct drawings (`retail_figures.figures()`); `--skus N` releases the scaled build instead
(`scale.py`'s).

**The release refuses a broken set** and writes nothing: a file two SKUs name, a SKU with no
file, or a file no SKU names (`bundle.sku_file_problems`), and a `drawing_id` that names two
different drawings. There is no committed manifest for the retail half (the retail build is
code, not a committed catalog), so the render is its source.
`tests/test_retail_image_release.py` and `tests/test_one_file_per_sku_706.py` pin the keying,
the one-file-per-SKU rule, that every document's image URL resolves to a packaged file, and the
package shape.

A `v*` tag builds the ceiling export, the industrial large build and this bundle, uploads them to a release with their
`.content-sha256`, and opens the pin-bump pull request in the catalogue repository
([docs/releasing.md](releasing.md), gen#536); a manual run of the workflow is the dry run.

### One renderer

`domains/industrial/drawing/` is the only way a product is drawn, and its drawings carry no
text. The matplotlib renderers that put tables, stamps and callouts into a picture
(`domains/industrial/render/`, and the `sip-render` and `ecom-render` commands) were
retired in #27. What they shared with `drawing/` -- reading a record into measurements --
lives in `domains/industrial/geometry/`.
