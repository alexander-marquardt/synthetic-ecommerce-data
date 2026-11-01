# School uniform: polos, socks, blazers and PE shorts (gen#205)

The first increment (`school_rows.py`) sold trousers, skirts, pinafores and shirts. These four
types sell the rest of the issue's table, each a spec of its own under `Kids > School Uniform`,
drawn in `kit_school.py` and held by `tests/test_retail_school_205_rest.py`.

| Type (spec) | Leaf | Structured attributes | SKUs | Drawing params |
|---|---|---|---|---|
| School Polo Shirt (`school_polo`) | School Polo Shirts | sleeve length, fabric, pack size | color x school age | `sleeve` (short, long) |
| School Socks (`school_socks`) | School Socks | sock style, fabric, pack size | color x UK shoe size band | `height` (ankle, knee, tights) |
| School Blazer (`school_blazer`) | School Blazers | fit, lining, badge ready, fabric | color x school age | `fit` (regular, slim, plus), `badge` (outline, none) |
| PE Shorts (`pe_shorts`) | PE Shorts | leg length, fabric, pack size | color x school age | `leg` (short, mid) |

A pack is what a style is sold as, as it is for the school shirt: each pack is its own product,
and `pack_copies.py` lays out that many items. School socks fan as socks do; a pack of tights fans
each pair folded down its middle, because a fan of two-legged pairs reads as a tangle.

The UK size bands (`size_ladder.SOCK_BANDS`) rank by the band's place in the list: a child's sizes
run to 13 and start again at 1, so `UK 4-7` is the largest although it opens on the smallest number.

The leaf `School Socks` also holds `PLT-SK5KID`, of type Socks, which the real-classes proof names,
so that style stays where it is. School socks are not color restricted in `type_colors.py`: the
completion gives `PLT-SK5KID` the main colors, and a restriction on the leaf leaves it no color to
take. Blazers are restricted to the school dress code colors.

Not here yet: school jumpers and cardigans.
