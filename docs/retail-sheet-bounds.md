# A retail drawing stays inside its sheet (gen#242)

Every retail shape is drawn on a 400 x 400 sheet. A pedestal fan's lower pole once ended at
y=434 in all four pedestal styles and every drawing test passed, because none measured where
a drawing ends. The house style later shrinks the product into its frame (about 0.78), which
hides an overrun of that size in the shipped image, so the guard measures the plain sheet the
shape is drawn on (`kit.render` without a style).

The guard is `tests/test_retail_sheet_242.py`. It renders every SKU image of every authored row
(`scale.templates()`, one image per style, colorway and size rung as the release draws them) on the plain
sheet (`image_release.render(rec, sku, styled=False)`) and fails when a drawing's geometry
reaches past it. The failure names the count of rows that overrun and each row with its shape
and how far it reaches. A derived style keeps its template's drawing, so the templates are the
rows.

`src/synthetic_ecommerce_data/domains/retail/sheet_extent.py` measures:

| It reads | How |
| --- | --- |
| `<path>` (`M L H V C S Q T A Z`, absolute and relative) | Curves at their true extremes, not their control points; an arc along its ellipse |
| `<rect>`, `<circle>`, `<ellipse>` | By their corners or radii, through the matrix |
| `translate`, `rotate`, `scale`, `matrix` on any group or element | Composed down the tree |
| A `clip-path` | The element's box is cut to the clip path's box |
| `<defs>`, `<pattern>`, `<mask>`, `<clipPath>`, gradients | Not drawn: their children are definitions |
| `<text>` | Not measured: a label is skipped, not read (no row overruns by an estimate of its width today) |

Stroke width is not counted: the guard is about the geometry a drawing places. Counting half
the stroke would add 2 rows (BRD-MRSUN by 2.8, BRD-DTMB8 by 0.8), a possible follow-up. A painting
element, path command or transform it does not read raises `ValueError` instead of being
skipped, so a drawing that starts to use one is not measured as a smaller box. That covers a
nested `<svg>`, a `style` holding `transform`, and a `<clipPath>` with `transform` or
`clipPathUnits`; `<text>` is the one family that is skipped, as the table says.

When a shape fails: move or shorten the part the failure names. A pool of glow from a light is
a polygon whose corners `kit_lighting._glow` holds to the sheet. Do not widen the check or add
an allow-list: the test has none, so the count only goes down.

`src/synthetic_ecommerce_data/domains/retail/motifs.drawn_box` is the older, coarser measure (the control-point
hull of a shape's default drawing, for placing a print); it and this guard agree on the sheet.

## In its house style: clear of the logo and the licence line (gen#932)

`house_styles.product_transform` scales the product into the rows that the logo's text leaves
free (`house_styles.reach`), plus a licensed product's licence line (`film_emblems.licence_band`),
keeping `AIR` beside them and `FREE_EDGE` from a bare edge. It used to fit a fixed span, y 28..362
of the kit's sheet, so a drawing that reached past that span still crossed the logo: an XL
hoodie's hood rose over "Licensed from Barry Plotter Studios", and a turned all-in-one's ground
shadow dipped into a logo at the foot. On the default build 3,249 of the 121,456 SKU images
crossed.

`kit._render_styled` now measures the rows the drawing covers (`house_styles.drawn_rows`): the
largest size after its turn, and the SKU's own when that differs. The transform fits that span,
joined with 28..362, so every size of one product is placed alike, and a drawing inside
28..362 keeps the transform it had. `tests/test_product_clear_of_logo_932.py` measures every
hoodie and all-in-one SKU image's `<g class="product">` against those rows.
`tests/test_every_image_clear_of_logo_932.py` makes the same check on every styled SKU image of
the default catalogue, every shape: about 121,600 SKUs and 83,300 drawings, 110 s on one local
core. It deals the templates into 12 tests that xdist spreads over its workers.
