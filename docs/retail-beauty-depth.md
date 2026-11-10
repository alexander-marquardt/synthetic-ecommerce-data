# Retail beauty depth: ten types (gen#214)

The beauty range held lipstick, foundation, eyeliner, highlighter, a skin tint, a face powder, a
perfume and a few creams, so a search for a mascara, a setting spray, a serum or an aftershave
found an unrelated make-up item and finish, skin concern and size had nothing to filter. Each type
below is its own spec under `src/synthetic_ecommerce_data/domains/retail/type_specs/` (the quick path in
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
| Body Mist (`body_mist`) | Fragrance > Body Mists | fragrance family | scent x size (ml) | `body_mist` cap |
| Aftershave (`aftershave`) | Fragrance > Aftershave | fragrance family, concentration | size (ml) | `aftershave` cap |
| Talc (`talc`) | Bath & Body > Talc | scent | size (g) | `talc` lid |
| Sun Cream (`sun_cream`) | Suncare > Face Sun Cream, Suncare > Body Sun Cream | area (face, body) | SPF x size (ml) | `sun_cream` form |

Every type has at least three styles from three or more invented brands. A body mist's scent
is a third SKU axis (`LRow`), exported as the `scent` option beside the size. A mascara's
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

## Lipsticks: a line draws its own case (gen#738)

Every lipstick drew one case and only its shade changed, so a page of separate products read as a
grouping failure. `lipstick_looks.py` now reads a look from the product, and `export.drawing_spec`
carries it, so each image the release draws has it:

- The product's line chooses the case shape, the case color, the bullet's cut, the emblem and the
  collar. A row with no model reads its title instead. The five choices multiply to more looks
  than the beauty grammar has models, and a model is numbered from its words, so no two models
  share a look. `lipstick_looks.SALT` is chosen so that no two lines of one brand share both a case
  and its color; a new line that lands on a taken pair needs a new salt, and a test names it.
- The finish chooses the bullet's surface: satin has a white gloss and a shadow down its far side,
  matte has neither, and sheer shows through with two glosses. It is the `finish` attribute, else
  the finish word in the title, else satin. Two products of one line in two finishes share the
  case, so they read as one range.
- The shade stays the SKU's own, so the SKUs of a product share the case and a group reads as one
  product.

A lip balm is drawn the same way. `tests/test_retail_lipstick_looks_738.py` holds all of this over
the grammar and the ceiling build. The choices are positional, so a new case, bullet or color
redraws every line.

## Foundation, creams, bath salts and perfume: a line draws its own pack (gen#748)

A foundation, a face cream, a moisturiser, a bath salt and a perfume each drew one pack, so a page
of separate products read as a grouping failure, as lipstick did. `pack_looks.py` now reads a look
from the product, `export.drawing_spec` carries it, and `kit_packs.py` draws it:

- The product's line chooses the pack's form, the top, the top's color, the emblem and the trim.
  A row with no model reads its title instead. A bottle has 8 forms, a jar 7 and a flacon 7. The
  tops of a bottle and a flacon are a block, a tall cap, a ball, a pump, a dropper, a wide cap and a
  stepped cap, and a jar's are a ribbed, smooth, dome, low, tiered or knobbed lid.
- A model is numbered from its words, as a lipstick's is, and each kind raises its base to that
  number modulo a prime, so no two models of a kind share a look. `pack_looks.BASES` are chosen so
  that no two lines of a kind draw one picture with the colors taken out, and no two lines of a
  brand share a form and a top; a new line that lands on a taken one needs a new entry, and a test
  names it. Two products of one line share their pack: it is the line that chooses it.
- The top's color used to follow the shade or the color's accent. A look's color is the line's, so
  the SKUs of a product share a pack and differ by the shade on its body or by its size.
- Only the kinds of `pack_looks.KINDS` draw a look. Hand wash, shower gel and the other creams print
  their model's name on the pack, so a tile tells them apart, and they draw as they did.

`tests/test_retail_pack_looks_748.py` holds this over the grammar, and
`tests/test_retail_pack_lines_748.py` over the ceiling build. The choices are positional, so a new
form, top or color redraws every line of the family.

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

## Face cream decoys that hold the phrase (gen#874)

With interpretation off, the served search multiplies a product's text score by 3 for each typed
word in its title and by 2.5 more for the typed phrase itself (prism#14050). Every real face cream
says "Face Cream". The older decoys ("Cream Face Towel", "Cream Baby Face Fabric Sofa") hold both
words but never the phrase, so the 23 real creams took the top 23 of `face cream`, and the demo
had nothing for interpretation to fix. Two changes fix that:

- Four decoys in `feature_decoys/face_cream_874.py` hold the phrase in a short title. A
  sofa range names its fabric and colour together, so the "Baby Face" upholstery of gen#541 in
  cream gives the Baby Face Cream Sofa and its matching cushion. Face Cream Travel Jars and Face
  Cream Sample Pots are empty containers in Beauty > Travel & Minis.
- The 20 face creams of the five brands now say who they are for or what they hold ("Repair
  Night Face Cream for Dry Skin", "Renewal Night Face Cream with Retinol"), so a short title no
  longer wins on length alone. The three Velling Apothecary class rows keep their titles, because
  the proof pins them. A cream's pack is numbered from its title (gen#748), and the new titles
  put two lines on one outline, so `pack_looks.BASES` starts Face Cream at 3787, not 3785.

Every decoy is a Sofa, a Cushion or a Travel Set outside the Face Creams node. With interpretation
on, the Face Creams route of class 12 boosts the real creams ×6 against the decoys' ×2, so the top
12 stays all face creams. `tests/test_face_cream_decoys_874.py` ranks the build with the served
factors and the `_explain` figures of the loaded index, and holds that at least three decoys are
in the top 12.

## False nails (gen#751)

`false_nails` (`type_specs/false_nails.py`, leaf `Nails > False Nails`, shape `false_nails` with the param `tip`) gives `nails` its second real meaning: the hardware is under `Fasteners > Nails` ([adding-a-type.md](adding-a-type.md#nails-three-kinds-three-leaves-gen751)). Five styles from three brands, tip shape and nail length as attributes, each style in two colors and packs of 24 and 30, so 20 SKUs, and three decoys. The six main colors are spread across the styles. The titles hold both `Nails` and `Nail` (`Oval False Nail Set`), and the descriptions say `fake nails`. `tests/test_nails_751.py` holds them.

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
