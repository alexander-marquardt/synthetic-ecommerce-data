# Electronics audio, slice 1 (gen#956)

Electronics held 1,166 SKUs at the ceiling build, against the 14,000 the catalogue mix plans
(`docs/catalogue-mix-837.md`). It had no derivable type, so the scaled build never drew more
electronics than the authored rows, and a search for `headphones`, `bluetooth speaker` or a
`soundbar` found little beyond 23 earbuds. Slice 1 adds three derivable types under
`Electronics > Audio`, each a spec of its own:

| Type | Spec | Path | Templates | SKU axis |
|---|---|---|---|---|
| Headphones | `type_specs/headphones.py` | Electronics > Audio > Headphones | 8 (4 title patterns x 2 brands) | color |
| Portable Speaker | `type_specs/portable_speaker.py` | Electronics > Audio > Portable Speakers | 8 (4 title patterns x 2 brands) | color x Single or 2 pack |
| Soundbar | `type_specs/soundbar.py` | Electronics > Audio > Soundbars | 8 (4 title patterns x 2 brands) | color |

The shared pieces (the paths, the six main colors of gen#275, `row()` and `decoy()`) are in
`audio_rows.py`. Every brand is an invented Electronics brand of `electronics_rows.py`
(`ELECTRONICS_OWNERS`). A speaker sold as a 2 pack for stereo is drawn as two (`pack_copies`).

**Attributes.** Headphones carry `connection` (Wireless, Wired, USB-C), `fit` (Over-Ear, On-Ear)
and `sound_feature`. Speakers carry `speaker_size` (Mini, Compact, Large), `weatherproofing`
(Waterproof, Splash-Proof) and an `Extra`. Soundbars carry `channels` (2.0, 2.1, 3.1, 5.1),
`connectivity` and `profile`. The speaker's key is `weatherproofing`, not `water_resistance`:
the jewellery rows use that key in metres, and a key carries a unit on all its entries or
none.

**Drawings.** `kit_audio.py` draws three shapes, each upright (`orientation.UPRIGHT`).
`headphones` takes `fit`, which draws large over-ear cups or small on-ear pads, and `connection`,
which draws a cable with a 3.5 mm jack, a cable with a USB-C plug, or a power light.
`portable_speaker` takes `speaker_size`, which draws a mini, compact or large cylinder.
`soundbar` takes `channels`: a driver per front channel, and a subwoofer box for a `.1`. Each
param is the lower-cased attribute value, so a derived style that swaps the value is drawn true
(gen#512).

**Breadth.** A derived style's twin key is its leaf, brand and title, so a type yields at most
(title-shown value combinations x brands) styles per title pattern. Each type has four title
patterns, each authored by two brands.

**Decoys.** Each type carries two text-match decoys: class 4 (a color word for a part, such as
red cushions on black headphones or a yellow strap on a black speaker) and class 6 (a color word
in a range name, such as `Blue Harbor` or `Red Rock`). The structured fields tell the truth.

**Measured** (ceiling build, seed 0): the department's size, its styles per type and the
authored and derived split are read from the build (`retail_figures`), never typed here. The
slice's floor is 4,500 Electronics SKUs. Slice 2 (smart home and gaming) and slice 3 (printers
and ink, wearables, power banks and webcams) are later slices of gen#956. The guards are in
`tests/test_retail_electronics_audio_956.py`; `tests/test_retail_scale.py` counts Electronics
among the departments with derivable styles.
