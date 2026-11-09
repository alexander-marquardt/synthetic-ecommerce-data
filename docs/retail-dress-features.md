# A dress draws the construction and pattern its title names (gen#922)

The "Petite Pinstripe Wrap Midi Dress" was drawn as the plain strap dress, with no wrap front and
no pinstripe, so its image contradicted the title on its result card. A dress title's construction
or pattern word is now drawn on the dress.

## The vocabulary

`src/synthetic_ecommerce_data/domains/retail/dress_features.py` declares each word (`WORDS`) and
what the release image must show for it:

| Kind | Words | Drawn as |
|---|---|---|
| construction | wrap | the front panel crossing to the right waist, the overlap down the skirt, a tie at the left waist; no separate neckline cut |
| construction | tiered | two gathered seams across the skirt |
| construction | smocked, smock | rows of zigzag smocking across the bodice |
| construction | ruched | gathers along both side seams |
| construction | belted | a belt band and buckle at the waist |
| construction | button front, button through | a placket with buttons down the center |
| construction | pinafore | broad straps, a square bib with two buttons, a patch pocket |
| construction | pleated | pleat lines from waist to hem |
| construction | seamed | top-stitched princess seams |
| construction | slashed hem | a slit up from the hem, the lining dark inside it |
| pattern | pinstripe | fine lines following the body from neckline to hem |
| pattern | broderie | rows of eyelet flowers |
| pattern | roses, boat print | roses or small sailing boats scattered over the body |
| pattern | stripe, spot, check, tartan, leopard, print | the color's own fill (`kit.pattern_defs`, a motif print) |

A shirt dress (`kit_garments.shirt_dress`) always draws a belt and a buttoned placket, so "belted"
and "button front" are its own marks. It also draws pinstripe, broderie, the named prints, pleats,
seams and tiers.

Materials (satin, lace trim, sequin, cable knit, crinkle, jacquard) are attributes, not marks.
Silhouettes (skater, shift, slip, tent, bodycon) belong to the style table
([retail-garment-styles.md](retail-garment-styles.md)). Neither kind is in the vocabulary.

## How it is drawn

`dress_features.apply` runs in `scale.templates()` after the decoys and the neckline pass, so a
cloned decoy is read too. It sets the drawing's `features` param to a space-separated list, such as
`"pinstripe wrap"`. A SKU's fill comes from its color swatch (`image_release.colorway_drawing`),
so a feature rides as a param and never in the color data: the `pattern` facet and the colors do
not change.

The shapes call `dress_features.draw`, which returns two lists. Pattern marks go over the fill and
construction marks go over the dress's own seams. Each feature is a `<g data-feature="<name>">`
group. On a dark fill (luma under 70), its ink lines draw in a light tint of the fill so they stay
visible. Every mark is original art drawn by code, as [drawings.md](drawings.md) requires.

## The check

`tests/test_dress_features_922.py` renders each generated dress row's release image
(`image_release.render`, first SKU). `dress_features.unshown` lists every vocabulary word whose
image shows neither its mark nor its fill pattern, with the rows that name it: the whole set, not
only the first word missing. The test also pins:

- the reported row, styled and plain;
- a row for every word a dress title carries today;
- that each feature draws a mark the plain shape lacks.

A new construction or pattern word in a dress title is added to `WORDS` with its drawing before a
row uses it. The next image release built from main carries the redrawn files.
