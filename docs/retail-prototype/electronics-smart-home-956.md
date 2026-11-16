# Electronics smart home, slice 2a (gen#956)

Electronics held 1,166 SKUs at the ceiling build, against the 14,000 the catalogue mix plans
(`docs/catalogue-mix-837.md`), and a search for a `smart plug`, a `smart bulb` or a
`video doorbell` found nothing. Slice 2 of gen#956 names five types (smart plugs, smart bulbs,
doorbell cameras, game controllers, gaming headsets), over the three a PR may add
(`docs/new-type-quick-path.md`, "Sizing rule"), so it is cut in two. Slice 2a adds the three
smart home types under `Electronics > Smart Home`, each a derivable spec of its own. Slice 2b
(gaming) comes next.

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Smart Plug | `type_specs/smart_plug.py` | Electronics > Smart Home > Smart Plugs | 8 (4 title patterns x 2 brands) | color |
| Smart Bulb | `type_specs/smart_bulb.py` | Electronics > Smart Home > Smart Bulbs | 12 (one title pattern x 12 brands) | light, connection and brightness, each in a Single, 2 pack or 4 pack |
| Doorbell Camera | `type_specs/doorbell_camera.py` | Electronics > Smart Home > Doorbell Cameras | 8 (4 title patterns x 2 brands) | color |

The shared pieces (the paths, the six main colors of gen#275, `row()` and `decoy()`) are in
`smart_home_rows.py`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`).

**Attributes.** Plugs carry `plug_form` (Mini, Dual Outlet, Outdoor), `connectivity` (Wi-Fi,
Zigbee) and `plug_feature` (Energy Monitoring, Voice Control, Scheduling). Doorbells carry
`doorbell_power` (Battery, Wired), `video_quality` (1080p, 2K) and `doorbell_feature` (Night
Vision, Two-Way Talk, Package Detection).

**Smart bulbs: one product, one picture.** A bulb product is its brand, range, shape and fitting
(the 2026-11-15 ruling on gen#1005: every different product has a different picture). It
carries `bulb_shape` (A60 Standard, Candle, Golf Ball, Large Globe, Reflector, Spot, Edison
Filament) and `bulb_fitting` (E27, E14, B22, GU10: the key and name the lighting rows use), on
the 13 pairs `smart_home_rows.BULB_FITTINGS` holds, the fittings each shape is really sold on: a
candle or a golf ball on E14 or E27, a spot on GU10 alone. What a picture does not show is a SKU
option, not another product: the light (`bulb_light`: Color Changing, Tunable White, Warm White),
the connection (`connectivity`: Wi-Fi, Bluetooth, Zigbee) and the brightness (`brightness_lm`:
470, 806, 1055 or 1521 lm, the steps the shape is sold at), each variant in a Single, a 2 pack
and a 4 pack, each priced on its own (`smart_home_rows.bulb_skus`), so the product's price
range follows them. Matter (`matter`), the voice assistants it works with (`works_with`: Alexa,
Google Home, Apple Home) and whether it needs a hub (`hub_required`) are filter-only, and a
derived bulb keeps them (`scale_text.FROZEN_KEYS`). No bulb names a timer or a schedule.
**Main colors.** Plugs and doorbells come in all six main colors. A smart bulb is sold in white
frosted glass, with its light color set in the app, so it is a declared exception in
`main_colors.EXCEPTIONS`, and its SKUs are its variants and packs instead of colors. A pack is
drawn as copies of the bulb (`pack_copies`).

**Drawings.** `kit_smart_home.py` draws three shapes, each upright (`orientation.UPRIGHT`).
`smart_plug` takes `plug_form`: one socket on a small body, two sockets on a wide one, or a tall
body with a hinged cover and a cable. `smart_bulb` takes `bulb_shape`, each shape its own glass
outline (a pear-shaped A60, a tall candle with a pointed tip, a small golf ball, a wide globe, a
reflector dome on a cone, a clear Edison bulb with its filament), and `bulb_fitting`: a threaded
screw base (narrow for E14) or a smooth bayonet base with two side pins. A spot, the one shape on
GU10, is a cone on two pins. `doorbell_camera` takes `doorbell_power`: a battery gauge, or two wires out of the
foot. Each param is the lower-cased attribute value, so a derived style that swaps the value is
drawn true (gen#512).

**Breadth, and why each type is held to a band.** A template derives one style per signature:
each combination of its title-shown values, times each color family, less its own
(`scale._signatures`). Slice 1 (audio) shows three values in most titles and draws 2,000 to
3,300 SKUs a type. Slices 2a, 2b and 3 share the department's last 4,500 SKUs, so these titles
show fewer values. A plug or doorbell title shows one value, or two. Every bulb template has
one title pattern, `{Shape} Smart Bulb, {Fitting} Fitting`, and its own brand, so a derived
bulb is a new shape and fitting for its brand: a draw whose brand already sells that pair retries
with another brand (`scale.twin_key`), and a pair the shape is not sold on is never drawn
(`smart_home_rows.real_pair`). A bulb derived to another shape takes that shape's brightness
steps and prices (`smart_home_rows.fit_bulb`). Each type lands between 350 and 900 SKUs at the
ceiling build. The test holds that band, so a later title that shows another value and doubles
the type fails there.

**Decoys.** Each type carries two text-match decoys (gen#309). One is class 4: a color word on a
part, such as a red status light on a white plug, a green energy label on a white bulb, or a
blue ring light on a black doorbell. The other is class 6: a color word in a range name, such as
`Yellow Brick`, `Blue Meadow` or `Green Lane`. The structured fields tell the truth. A bulb decoy
draws its base row's picture, so it carries a brand the bulb templates do not use.

**Department rates.** A department's derived share comes from its rate (`scale.DEPARTMENT_RATE`).
Electronics gets its own, so its share meets its target, and Clothing's is recomputed, since
the new department took Clothing more than 3 points under its 44% target
(`tests/test_retail_stable_ids_626.py`).

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. On
their own, the three types add at least 1,200 SKUs, the slice's floor. The guards are in
`tests/test_retail_electronics_smart_home_956.py`, which also holds that no two bulb products of
one brand share a picture, on the ceiling build and on a bulb-only build of seeds 0 to 5.
`tests/test_retail_scale.py` reads the departments with derivable styles from the figures.
