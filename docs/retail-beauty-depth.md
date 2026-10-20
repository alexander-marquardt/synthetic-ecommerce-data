# Retail beauty depth: ten types (gen#214)

The beauty range held lipstick, foundation, eyeliner, highlighter, a skin tint, a face powder, a
perfume and a few creams, so a search for a mascara, a setting spray, a serum or an aftershave
found an unrelated make-up item and finish, skin concern and size had nothing to filter. Each type
below is its own spec under `prototypes/retail_drawings/type_specs/` (the quick path in
[new-type-quick-path.md](new-type-quick-path.md)), built from the shared pieces in
`beauty_depth.py` and drawn by `kit_beauty.py`. The styles are templates only (`derivable` False):
the range grows by authored rows. `tests/test_retail_beauty_214.py` holds the table below.

| Type (spec key) | Leaf | Key attributes | SKUs | Shape and param |
|---|---|---|---|---|
| Mascara (`mascara`) | Make-Up > Eyes > Mascara | effect, waterproof | shade | `mascara` effect |
| Face Primer (`face_primer`) | Make-Up > Face > Primers | finish, skin type | size (ml) | `primer` form |
| Setting Spray (`setting_spray`) | Make-Up > Face > Setting Sprays | finish, skin type | size (ml) | `setting_spray` nozzle |
| Serum (`serum`) | Skincare > Serums | active, skin concern | size (ml) | `serum` form |
| Face Mask (`face_mask`) | Skincare > Face Masks | mask type, skin concern | pack count | `face_mask` mask |
| Eye Patches (`eye_patches`) | Skincare > Eye Patches | patch type, skin concern | pack count | `eye_patches` patch |
| Body Mist (`body_mist`) | Fragrance > Body Mists | fragrance family | fragrance x size (ml) | `body_mist` cap |
| Aftershave (`aftershave`) | Fragrance > Aftershave | fragrance family, concentration | size (ml) | `aftershave` cap |
| Talc (`talc`) | Bath & Body > Talc | fragrance | size (g) | `talc` lid |
| Sun Cream (`sun_cream`) | Suncare > Face Sun Cream, Suncare > Body Sun Cream | area (face, body) | SPF x size (ml) | `sun_cream` form |

Every type has at least three styles from three or more invented brands. A body mist's fragrance
is a third SKU axis (`LRow`), exported as the `fragrance` option beside the size. A mascara's
shades are a declared exception to the six main colors (`main_colors.EXCEPTIONS`); every other
type is sold in one pack and carries no color. A drawing never prints a size or a count.

A sun cream's SPF (15, 30 and 50) is a second SKU axis (`LRow`), exported as the `spf` option
beside the size, and its area (face or body) is an attribute and its leaf, so `SPF 30 body sun
cream` is a filter on two entries and a node. The one-style `SPF 50 Face Sun Cream` of
`class_rows.py` (`PLT-SPFFCE`) stays beside the range: it is the near-type distractor of the "face
cream" demo (class 12), and the committed Elasticsearch proof (`real_classes_proof.json`, rebuilt
only by an `es_proof.py` run) names its id. `PROOF_PINNED_CLASS_ROWS` in
`tests/test_retail_type_specs_351.py` exempts that one id from the rule that a spec's type has no
row outside the spec.

## Face creams: five brands (gen#542)

`type_specs/face_cream.py` adds five brands the generator already sells for other beauty products to the Face Creams leaf (Skincare > Creams >
Face Creams), beside Velling Apothecary, whose three class rows and the "Daylight" decoy stay
where they are (the proof pins them, as for `PLT-SPFFCE`; `PROOF_PINNED_CLASS_ROWS` and
`DECOY_ROWS_BESIDE_A_SPEC` in `tests/test_retail_type_specs_351.py` exempt those ids). Each new
brand sells a day, a night and an SPF line and a fourth line (barrier, sensitive, anti-ageing or
rich), 20 products in all, in 30, 50 and 100 ml: pharmacy (Sorrel & Salt, Aldermist), mid (Thornlea
Skin, Pearlbrook) and premium (Fenmere). The attributes are skin type and skin
concern, the volume is a SKU option (`net_volume`, ml) and an SPF line is also sold by SPF, the
option `sun_cream` declares. The price rises with the volume and falls per ml in every series of
the type; `tests/test_retail_face_creams_542.py` holds that, five brands, 20 products and the
three sizes. The five names keep the marks and house styles they already have; no brand, mark or style is new. The
decoys of the type stay in `decoy_rows.py`.

## Text-match decoys (gen#294)

Each type carries three decoys, a clone of its first style whose words mislead a plain text
search while its fields tell the truth: class 1 (a color part: a "Pink Cap Volume Mascara" is
black), class 4 (a feature named and absent: a "Dewy Gold Cap Face Primer" is matte), class 6 (an
incidental word in a short range name) and class 7 (an invented brand that holds the word). A
decoy names a value of its own filter on purpose, so `scale.TEXT_EXEMPT` includes the registry's
decoys, by id, as it does the other decoy tables.

## House styles

The 15 invented brands each have a `house_styles.HOUSE_STYLES` entry and a mark of their own: 14
beauty marks (`m_lash_fan` to `m_rose_bud`) joined the table so none reuses a mark another brand
holds (the fifteenth, Coconut Plover, a sun cream decoy brand, has `m_coconut_palm`), and no two brands share a logo arrangement with the same wordmark.
`test_each_invented_beauty_brand_has_a_house_style_of_its_own` holds both for these brands. The
eight mark pairs already on main are #362's.
