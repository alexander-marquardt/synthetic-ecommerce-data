# Electronics gaming, slice 2b (gen#956)

Electronics held 1,166 SKUs at the ceiling build, against the 14,000 the catalogue mix plans
(`docs/catalogue-mix-837.md`). A search for a `game controller` found nothing. A search for a
`gaming headset` found one `Earbuds` row under `Accessories`. Slice 2 of gen#956 names five
types, more than the three a PR may add (`docs/new-type-quick-path.md`, "Sizing rule"), so it
was cut in two. Slice 2a is smart home. Slice 2b, this page, adds the two gaming types under
`Electronics > Gaming`, each a derivable spec of its own.

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Game Controller | `type_specs/game_controller.py` | Electronics > Gaming > Game Controllers | 8 (4 title patterns x 2 brands) | color |
| Gaming Headset | `type_specs/gaming_headset.py` | Electronics > Gaming > Gaming Headsets | 8 (4 title patterns x 2 brands) | color |

`gaming_rows.py` holds the shared pieces: the paths, the six main colors of gen#275, `row()`
and `decoy()`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`).

**Attributes.**
- Controllers carry `controller_form` (Classic, Pro, Mobile), `connection` (Wireless, Wired) and
  `controller_feature` (Hall Effect Sticks, Remappable Buttons).
- Headsets carry `connection` (Wireless, Wired), `headset_sound` (Stereo, 7.1 Surround) and
  `headset_feature` (Noise Cancelling Mic, RGB Lighting, Memory Foam Cushions).
- `connection` has the key and name that the Electronics earbuds and mice use.

**Main colors.** Both types come in all six main colors on every template, so neither one is an
exception.

**Drawings.** `kit_gaming.py` draws two shapes. Both are upright (`orientation.UPRIGHT`).
- `game_controller` takes `controller_form`: a classic pad with a d-pad, two sticks and four
  face buttons, a pro pad that adds two triggers and two back paddles, or a mobile controller
  with two grips either side of a phone.
- `game_controller` also takes `connection`: a cable when wired, a lit bar when wireless.
- `gaming_headset` draws a headband, two ear cups with lit rings and a boom mic. It takes
  `connection`: a cable and plug when wired, a power light when wireless.

Each param is the lower-cased attribute value, so a derived style that swaps the value is drawn
true (gen#512). The form is `Pro`, not a word that `Programmable` would contain, so a value swap
never rewrites part of another word.

**Breadth, and why each type is held to a band.** A template derives one style per signature:
each combination of its title-shown values, times each color family, less the template's own
(`scale._signatures`). Slices 2a, 2b and 3 share the department's last 4,500 SKUs, so each title
shows one value, or two. The controller has two features, not three. With three, it sat at
the top edge of its band. Each type lands between 350 and 600 SKUs.
The test holds that band, so a later title that shows another value fails there.

**Decoys.** Each type carries two text-match decoys (gen#309).
- Class 4 is a color word on a part: red trigger buttons on a black controller, or green ring
  lights on a black headset.
- Class 6 is a color word in a range name: `Blue Harbor` or `Yellow Peak`.

The structured fields tell the truth.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. On
their own, the two types add at least 700 SKUs, the slice's floor. The guards are in
`tests/test_retail_electronics_gaming_956.py`. `tests/test_retail_scale.py` counts Electronics
among the departments with derivable styles.
