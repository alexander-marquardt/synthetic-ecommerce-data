# A retail drawing stays inside its sheet (gen#242)

Every retail shape is drawn on a 400 x 400 sheet. A pedestal fan's lower pole once ended at
y=434 in all four pedestal styles and every drawing test passed, because none measured where
a drawing ends. The house style later shrinks the product into its frame (about 0.78), which
hides an overrun of that size in the shipped image, so the guard measures the plain sheet the
shape is drawn on (`kit.render` without a style).

The guard is `tests/test_retail_sheet_242.py`. It renders every SKU image of every authored row
(`scale.templates()`, one image per style and colorway as the release draws them) on the plain
sheet (`image_release.render(rec, sku, styled=False)`) and fails when a drawing's geometry
reaches past it. The failure names the count of rows that overrun and each row with its shape
and how far it reaches. A derived style keeps its template's drawing, so the templates are the
rows.

`prototypes/retail_drawings/sheet_extent.py` measures:

| It reads | How |
| --- | --- |
| `<path>` (`M L H V C S Q T A Z`, absolute and relative) | Curves at their true extremes, not their control points; an arc along its ellipse |
| `<rect>`, `<circle>`, `<ellipse>` | By their corners or radii, through the matrix |
| `translate`, `rotate`, `scale`, `matrix` on any group or element | Composed down the tree |
| A `clip-path` | The element's box is cut to the clip path's box |
| `<defs>`, `<pattern>`, `<mask>`, `<clipPath>`, gradients | Not drawn: their children are definitions |

Stroke width is not counted: the guard is about the geometry a drawing places. A painting
element, path command or transform it does not read raises `ValueError` instead of being
skipped, so a drawing that starts to use one is not measured as a smaller box.

When a shape fails: move or shorten the part the failure names. A pool of glow from a light is
a polygon whose corners `kit_lighting._glow` holds to the sheet. Do not widen the check or add
an allow-list: the test has none, so the count only goes down.

`prototypes/retail_drawings/motifs.drawn_box` is the older, coarser measure (the control-point
hull of a shape's default drawing, for placing a print); it and this guard agree on the sheet.
