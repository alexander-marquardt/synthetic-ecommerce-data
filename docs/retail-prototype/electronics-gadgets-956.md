# Electronics gadgets, slice 3a (gen#956)

Electronics held 1,166 SKUs at the ceiling build, against the 14,000 the catalogue mix plans
(`docs/catalogue-mix-837.md`). A search for a `webcam` or a `smartwatch` found nothing. A search
for a `power bank` found four `Charger` rows under `Accessories > Chargers`. Slice 3 of gen#956
names five types: printers, ink, wearables, power banks and webcams. That is more than the three a
PR may add (`docs/new-type-quick-path.md`, "Sizing rule"), so it was cut in two. Slice 3a, this
page, adds three types, each a derivable spec of its own. Slice 3b, printers and ink, stays
together for the next cut.

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Power Bank | `type_specs/power_bank.py` | Electronics > Accessories > Power Banks | 8 (4 title patterns x 2 brands) | color |
| Webcam | `type_specs/webcam.py` | Electronics > Computers > Webcams | 8 (4 title patterns x 2 brands) | color |
| Smartwatch | `type_specs/smartwatch.py` | Electronics > Wearables > Smartwatches | 8 (4 title patterns x 2 brands) | color |

`gadgets_rows.py` holds the shared pieces: the paths, the six main colors of gen#275, `row()`
and `decoy()`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`). The four power-bank `Charger` rows stay chargers for a named device.
`Fitness Band`, the Womens and Mens `Watches` type of gen#423, is not touched.

**Attributes.**
- Power banks carry `power_bank_form` (Slim, Rugged, Magnetic), `power_bank_charging` (USB-C,
  Wireless) and `power_bank_feature` (Built-in Cable, Kickstand).
- Webcams carry `webcam_resolution` (Full HD, 4K), `webcam_use` (Streaming, Conference) and
  `webcam_feature` (Ring Light, Privacy Shutter). The resolution is `Full HD`, never `1080p`. A
  derived style's title swap reads an all-lowercase word as lower case, so a `1080p` template
  would become `4k`. The test holds the `4K` case.
- Smartwatches carry `smartwatch_face` (Round, Square), `smartwatch_network` (GPS, Cellular) and
  `smartwatch_feature` (Heart Rate Monitor, Sleep Tracking).

Every key is new to the catalogue and carries no unit, so no key's values clash with another
type's.

**Drawings** (`kit_gadgets.py`, all three upright in `orientation.py`).
- `power_bank` draws its form: a slim brick, a rugged one with corner bumpers, or a magnetic one
  with a metal ring. It draws its charging: a USB-C port and cable, or charge waves.
- `webcam` draws its use: a round streaming camera, or a wide conference bar with speaker
  grilles. It draws its feature: a lit ring around the lens, or a privacy shutter above it.
- `smartwatch` draws its face, round or square. It draws its network: a map pin on screen for
  GPS, or a red crown for cellular.

A derived style that changes one of these params draws what it states (gen#512).

**Colors.** Every template is offered in the six main colors (gen#275). No type declares an
exception.

**Decoys** (gen#309), two per type. Each is cut from a template, holds one color, and names
another color in its title:
- `Slim Power Bank with Red Charge Lights` is black. `Green Hollow USB-C Power Bank` is white.
- `4K Webcam with Blue Status Light` is black. `Yellow Brook Conference Webcam` is white.
- `Cellular Smartwatch with Red Crown` is black. `White Peak GPS Smartwatch` is black.

**Breadth.** Measured on the ceiling build, seed 0: Power Bank 563, Webcam 449 and Smartwatch 447
SKUs. That is 1,459 on its own, and Electronics goes from 1,166 to 2,625 on main. With slice 1
(9,479), slice 2a (+1,782) and slice 2b (+1,052), the department holds about 13,769. That passes
the issue's 13,300 floor (95% of 14,000). The first power-bank cut, with three features, drew 612
SKUs, over the 350-to-600 band each type keeps so slice 3b has its share. The feature list was
cut to two.

**Test.** `tests/test_retail_electronics_gadgets_956.py` checks the following:
- the slice's floor of 1,000 SKUs, and each type's band;
- each type's node, and that each type is derived;
- unique ids, titles, SKUs and twin keys;
- deterministic rows and drawings, and that each param changes its drawing;
- the `4K` case, and a golden slice per type.
