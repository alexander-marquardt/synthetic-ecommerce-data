# Retail DIY & Tools: the drill family (gen#191)

Searching "drill" on the Retail catalog found four power drills from one brand, all typed
"Cordless Drill", and none corded. Nine type specs in `prototypes/retail_drawings/type_specs/` now
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
| Drill Bit Set | Tool Sets > Drill Bit Sets | material drilled; shank; piece count; case | `drill_bit_set` | `shank`, `bits` |
| Tool Kit | Tool Sets > Tool Kits | piece count; contents; case | `tool_kit` | `case` |
| Step Ladder | Ladders > Step Ladders | steps; material; max load (kg); platform height (m); kind | `step_ladder` | `steps`, `kind` |

Every type has at least four styles from four or five invented brands (Calderby & Lune, Torvane
Tools, Marlowick, Harkwell Power, Stonemarsh; text only, with a house style in
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

## Checks

`tests/test_retail_drills_191.py` holds the types, brands, shapes, attributes, colors, decoys and
that every `image_id` resolves through `image_release.py`. The query shapes (`18 V drill driver`,
`corded SDS drill 1100 W`, `masonry drill bit set`, `61 piece tool kit`, `4 step ladder`, `step
stool`) are checked against the titles. Whether the live search answers them is not measured here.
