# Beauty, hair care in depth (gen#957, slice 1)

The 500K mix ([catalogue-mix-837.md](../catalogue-mix-837.md)) plans 14,000 `Beauty` SKUs. Main's
ceiling build held 2,589. Shampoo and Conditioner had 24 SKUs each, and the department had no hair
tool, so a search for `hair dryer`, `straightener` or `paddle brush` found nothing. Slice 1 of
gen#957 deepens `Beauty > Hair Care`.

## The three new types

Each type is a spec of its own and is derivable. Every style is sold in the six main colors
(gen#275). A SKU is a color crossed with the type's own option. The shared pieces (the paths,
the colors, `row()` and `decoy()`) are in `hair_rows.py`.

| Type | Spec | Title-shown values (the derived pools) | SKU option |
|---|---|---|---|
| Hair Dryer | `type_specs/hair_dryer.py` | technology (Ionic, Ceramic, Tourmaline, Infrared) and form (Salon, Compact, Travel, Folding) | `attachments`: dryer only, with diffuser, with diffuser and concentrator |
| Hair Straightener | `type_specs/hair_straightener.py` | plate material (Ceramic, Titanium, Tourmaline) and kind (Salon, Mini, Cordless, Travel) | `plate_width`: 25 mm, 38 mm |
| Hairbrush | `type_specs/hairbrush.py` | head (Paddle, Round, Vent, Detangling) and bristle (Boar, Nylon, Mixed) | `size`: Small, Medium, Large |

`attachments` and `plate_width` are declared by their specs (`options=`, gen#413). Each type has
two text-match decoys (gen#309). The class 4 decoy names a colored part its fields do not hold
(`Ionic Hair Dryer with Red Diffuser`, sold in black). The class 6 decoy has a color word in its
range name (`Green Lane Ceramic Hair Dryer`, sold in white). The brands are the department's
invented brands (gen#720).

## Drawings

`kit_hair.py` draws three shapes: `hair_dryer`, `hair_straightener` and `hairbrush`. The SKU's
color fills the body, the arms or the handle. Each title-shown value changes the figure, so a
derived style that swaps a value is drawn the way its title reads (gen#512):

- A dryer's technology picks the color of its badge, and its form picks the handle. A folding
  handle is drawn with a hinge. A salon dryer gets a long handle and a cord. A compact or travel
  dryer is drawn smaller.
- A straightener's plate material picks the tone of its plates. A mini is drawn short. A salon
  model has a cord, and a cordless one has a battery.
- A brush's head picks its outline. A vent head has slots, a round head is a barrel with pins on
  either side, and a detangling head has widely spaced pins. The bristle picks the color of the
  tips, and a mixed brush alternates two tones.

`orientation.py` files all three shapes as upright.

## Shampoo and Conditioner

Each type gains four templates and now spans six hair types and six ingredients, so the scaled
build draws more styles from the wider pools. Shampoo's new rows sit in its spec. Conditioner's
two original rows stay in `breadth_beauty.py`, and its four new rows are the spec's own.

## Tests

`tests/test_retail_beauty_hair_957.py` checks:

- the slice's floor of 5,000 `Beauty` SKUs at the ceiling build;
- that each new type is derived under `Hair Care`;
- that Shampoo and Conditioner each reach six hair types, six ingredients and 400 SKUs;
- unique ids, titles, twin keys and SKU ids for each new type;
- that rows and drawings come out the same on every call;
- that each param value draws its own figure;
- a golden slice for each type.
