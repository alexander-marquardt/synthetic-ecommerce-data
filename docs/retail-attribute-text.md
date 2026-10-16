# Retail text and attributes agree (gen#250)

A description that says "magnetic fastening" over a style whose `closure` is Zip, or a polka dot
umbrella that sells a gingham color, contradicts its own facet. `attribute_text.disagreements(records)`
(`prototypes/retail_drawings/attribute_text.py`) returns one line per row that disagrees, and its
length is the metric. `tests/test_retail_attribute_text_250.py` holds it at zero on the templates
and on the ceiling build, and holds the check itself against hand-made rows.

| Attribute | The row agrees when |
| --- | --- |
| `closure` is Zip, Magnetic, Snap, Drawstring, Clasp or Buckle | the title or description, if it names any closure word (zip, magnetic, snap, drawstring, clasp, buckle), names that one |
| `closure` is anything else (Lace-Up, Pull-On, Ankle Strap, ...) | the text names no closure word, or only those `ALSO` lists for that value, each with its reason |
| `pattern` | every color option and the drawing carry the pattern `PATTERN_KIND` maps it to, and the text names no other pattern (a gingham check may say "check") |

A zipped pocket, compartment or lining is not a closure (`NOT_A_CLOSURE`). A text that names no
closure word agrees with any closure.

A new closure value that its text names, or a new `pattern` value, needs its row in `ALSO` or
`PATTERN_KIND`; an unmapped pattern is reported, not skipped. `test_every_allowance_is_used_by_a_real_row`
fails when an `ALSO` entry no row uses any more.

**Material words are not read.** A draft rule that compared the material words of the text with the
`material`, `fabric` and `upper_material` attributes flagged 71 template rows, and none was a defect:
a leather-look or suede-look decoy says the word to deny it, a steak knife has a wooden handle on a
steel blade, a griddle has a ceramic coating on an aluminum pan. A rule on them would need an
allowance per row.
