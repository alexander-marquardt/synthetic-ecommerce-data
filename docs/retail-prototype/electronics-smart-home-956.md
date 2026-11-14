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
| Smart Bulb | `type_specs/smart_bulb.py` | Electronics > Smart Home > Smart Bulbs | 8 (4 title patterns x 2 brands) | Single, 2, 4 or 6 pack |
| Doorbell Camera | `type_specs/doorbell_camera.py` | Electronics > Smart Home > Doorbell Cameras | 8 (4 title patterns x 2 brands) | color |

The shared pieces (the paths, the six main colors of gen#275, `row()` and `decoy()`) are in
`smart_home_rows.py`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`).

**Attributes.** Plugs carry `plug_form` (Mini, Dual Outlet, Outdoor), `connectivity` (Wi-Fi,
Zigbee) and `plug_feature` (Energy Monitoring, Voice Control, Scheduling). Bulbs carry
`bulb_fitting` (E27, E14, B22, GU10: the key and name the lighting rows use), `bulb_light`
(Color Changing, Tunable White, Warm White) and `connectivity` (Wi-Fi, Bluetooth, Zigbee).
Doorbells carry `doorbell_power` (Battery, Wired), `video_quality` (1080p, 2K) and
`doorbell_feature` (Night Vision, Two-Way Talk, Package Detection).

**Main colors.** Plugs and doorbells come in all six main colors. A smart bulb is sold in white
frosted glass, with its light color set in the app, so it is a declared exception in
`main_colors.EXCEPTIONS`, and its SKUs are packs instead of colors. A pack is drawn as copies
of the bulb (`pack_copies`).

**Drawings.** `kit_smart_home.py` draws three shapes, each upright (`orientation.UPRIGHT`).
`smart_plug` takes `plug_form`: one socket on a small body, two sockets on a wide one, or a tall
body with a hinged cover and a cable. `smart_bulb` takes `bulb_fitting`: a globe on a threaded
screw base (narrow for E14), a globe on a smooth bayonet base with two side pins, or a spot cone
on two pins. `doorbell_camera` takes `doorbell_power`: a battery gauge, or two wires out of the
foot. Each param is the lower-cased attribute value, so a derived style that swaps the value is
drawn true (gen#512).

**Breadth, and why each type is held to a band.** A template derives one style per signature:
each combination of its title-shown values, times each color family, less its own
(`scale._signatures`). Slice 1 (audio) shows three values in most titles and draws 2,000 to
3,300 SKUs a type. Slices 2a, 2b and 3 share the department's last 4,500 SKUs, so these titles
show fewer values. A plug or doorbell title shows one value, or two, and a bulb title shows two
or three, because a bulb has one color family. Each type lands between 350 and 900 SKUs at the
ceiling build. The test holds that band, so a later title that shows another value and doubles
the type fails there.

**Decoys.** Each type carries two text-match decoys (gen#309). One is class 4: a color word on a
part, such as a red status light on a white plug, a green energy label on a white bulb, or a
blue ring light on a black doorbell. The other is class 6: a color word in a range name, such as
`Yellow Brick`, `Blue Meadow` or `Green Lane`. The structured fields tell the truth.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. On
their own, the three types add at least 1,200 SKUs, the slice's floor. The guards are in
`tests/test_retail_electronics_smart_home_956.py`. `tests/test_retail_scale.py` counts
Electronics among the departments with derivable styles.
