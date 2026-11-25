# Retail DIY & Tools: the drill family (gen#191)

Searching "drill" in the retail domain found four power drills from one brand, all typed
"Cordless Drill", and none corded. Nine type specs in `src/synthetic_ecommerce_data/domains/retail/type_specs/` now
hold the range. Each product type names its tool, and none is a plain "Drill", so a retail type
never collides with the industrial drill bits and bushings on a merged index.

| Product type | Leaf under Home > DIY & Tools | Key attributes | Shape (`kit_drills.py`) | Param that changes the drawing |
|---|---|---|---|---|
| Drill Driver | Drills > Cordless Drills | voltage 12, 18, 20 V; motor; battery | `drill_driver` | `pack` |
| Combi Drill | Drills > Combi Drills | voltage; modes | `combi_drill` | `pack` |
| Hammer Drill | Drills > Hammer Drills | power source (Cordless or Corded); 18, 40 V or 550-1,100 W | `hammer_drill` | `power` |
| Corded Drill | Drills > Corded Drills | wattage 450-710 W; chuck | `corded_drill` | `handle` |
| Impact Driver | Drills > Impact Drivers | voltage; torque (Nm); bit holder; battery kit | `impact_driver` | `batteries` |
| SDS Hammer Drill | Drills > SDS Drills | power source; impact energy (J); modes | `sds_drill` | `power` |
| Drill Bit Set | Drill Accessories > Drill Bit Sets | material drilled; shank; piece count; case | `drill_bit_set` | `shank`, `bits` |
| Tool Kit | Tool Sets > Tool Kits | piece count; contents; case | `tool_kit` | `case` |
| Step Ladder | Ladders > Step Ladders | steps; material; max load (kg); platform height (m); kind | `step_ladder` | `steps`, `kind` |

Every type has at least four styles from four or five invented brands (Calderby & Lune, Torvane
Tools, Marlowick, Harkwell Works, Stonemarsh; text only, with a house style in
`diy_brand_styles.py`), and offers the six main colors across its styles in three color pairs.
Impact driver voltage and kit are carried as styles, so each image matches its SKUs.

## Decoys (gen#294)

Each type carries three text-match decoys, each a product that holds the type's words and is not one:

- Class 4, in the type's spec: a real product of the type under a title that names a feature it
  lacks ("Corded Drill, Cordless Free").
- Class 2, in `diy_decoy_rows.py`: a cushion or an apron whose title holds the type's phrase.
- Class 6, in `diy_decoy_rows.py`: a scented candle with one word of the type in its title and the
  other in its description.

Their structured fields tell the truth, so a department or category policy drops them. The decoys
are templates: the scaled build neither derives from them nor completes their colors.

## Fill (gen#1215)

Each shape but the bit set's is drawn as the real product, with a highlight and a shadow, over at least half of
the product area (`TURN_AREA`) at every param and in every main color. Share of the product area on
the retail templates' SKUs, measured by `scripts/picture_fill_1129.py` (least to most):

| Product type | Before | After |
|---|---|---|
| Drill Driver | 22-24% | 54-58% |
| Combi Drill | 22-24% | 55-59% |
| Hammer Drill | 23-26% | 61-62% |
| Corded Drill | 20-21% | 60-63% |
| Impact Driver | 19-24% | 56-68% |
| SDS Hammer Drill | 20-23% | 59-63% |
| Tool Kit | 40-53% | 69-90% |
| Step Ladder | 14-21% | 51-56% |
| Volt Meter | 25-27% | 52-69% |

A cable is wound in a coil and strapped, as it is sold, and a tool kit is open, so each shows what
it holds. No type needs a named exception. `tests/test_fill_drills_1215.py` holds the floor, the light and the
bounds. Before and after: [the sheet](images/drills-fill-1215.png).

## Checks

`tests/test_retail_drills_191.py` holds the types, brands, shapes, attributes, colors, decoys and
that every `image_id` resolves through `image_release.py`. The query shapes (`18 V drill driver`,
`corded SDS drill 1100 W`, `masonry drill bit set`, `61 piece tool kit`, `4 step ladder`, `step
stool`) are checked against the titles. Whether the live search answers them is not measured here.
