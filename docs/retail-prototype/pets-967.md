# Pets, slices 1 to 3 (gen#967)

The store had no pets department, so a search for `dry dog food`, `wet cat food` or `cat litter`
found nothing. `Pets` is now on the closed list of retail departments (`core/departments.RETAIL`)
and on the build record's list (`domains/retail/departments.py`), which keys the brand pools. Its
first three types are specs of their own:

| Type | Spec | Paths | Templates | SKU axis |
|---|---|---|---|---|
| Dog Food | `type_specs/dog_food.py` | Pets > Dog Food > Dry Dog Food, Pets > Dog Food > Wet Dog Food | 6 dry (life stage, breed size, flavor), 3 wet (pouches, trays, tins) | dry: bag weight (`net_weight_g`); wet: pack of 6 to 48 (`units_per_pack`) |
| Cat Food | `type_specs/cat_food.py` | Pets > Cat Food > Dry Cat Food, Pets > Cat Food > Wet Cat Food | 5 dry (life stage, need, flavor), 3 wet (pouches, trays, tins) | dry: bag weight; wet: pack of 4 to 48 |
| Cat Litter | `type_specs/cat_litter.py` | Pets > Litter & Hygiene > Cat Litter | 8 (scent and litter type: clumping clay, non-clumping clay, silica crystal, wood pellet, recycled paper, clumping corn) | bag weight |

The shared pieces (the paths, the invented brands and who owns each, the pack colors, `grams()`,
`units()`, `row()` and `decoy()`) are in `pets_rows.py`. Food and litter carry no color
(`colorless`): a style's one color is its pack's print, which the drawing takes as its fill and
the store does not sell as a variant. So a style's SKUs are its sizes alone: a dry food or a
litter by its bag's net weight in grams, a wet food by the pouches, trays or tins in its pack.
Every brand is invented (ruling 2026-10-30, gen#720), and `pet_brand_styles.py` gives each its
house style.

**Drawings.** `kit_pets.py` draws three shapes. `dry_pet_food` is a stand-up bag with a window
of kibble, which takes `animal` (dog, cat): bones for a dog, fish for a cat. `wet_pet_food` takes
`pack_format` (pouches, trays, tins), which draws a pouch, a peel-lid tray or a ring-pull tin, and
`animal`. `cat_litter` takes `litter_type`, which draws the granules in the bag's window: clay
grains, crystals, wood or paper pellets, or corn grains. Each param is the lower-cased attribute
value, so a derived style that swaps the value is drawn true (gen#512). All three are upright.

What the pack says is drawn on it too, so two styles of one leaf and one price read apart on a
results grid. `pets_rows.row()` adds each style's `life_stage`, `flavor`, `breed_size`,
`special_need` and `scent` to its drawing's params (`pets_rows.DRAWN`):

- the life stage is a row of pips: one for a puppy or a kitten, two for an adult, three for a senior;
- the flavor is a band in two inks, its meat's or fish's and its side's (rice, gravy, jelly, ...);
- a dog's breed size is the size of the kibble in the bowl;
- a cat's special need is an emblem beside the paw: a house for indoor, a heart for sterilized, a
  coil for hairball control, a leaf for sensitive;
- a litter's scent is a sprig in the scent's ink, and an unscented litter has none.

Without them the three shapes drew a style as its animal, its pack color and its format alone,
and 389 of the 619 Pets styles at the ceiling shared a grid tile. That took the catalog's
grid-clone share to 18.7%, over the 15.2% cap in `tests/test_retail_scale.py`. With them, 2 Pets
styles share a tile and the catalog's share is 13.4% (963 of 7,194 styles).

**Breadth.** The three types are derivable. A colorless style has only its three or four sizes
as SKUs, so a type needs more templates than a colored one to reach the same SKU count: the two
last litter templates (Multi-Cat Fresh Linen Clumping Clay, Citrus Clumping Wood Pellet) widen
the scent and brand pools that the derived litters draw from.

**Decoys.** Each type carries two text-match decoys: a word that names another type in a brand
or a range name (`Alley Cat Provisions` dog food, `Dog Rose` cat food, `Kitten Mill` adult cat food,
`Puppy Hill` senior dog food, `Lavender Hill` pine litter) and, for litter, a refill bag
whose title names a litter tray it does not include.

**Measured** (ceiling build, `retail_figures.ceiling()`, seed 0): the department's and the three
types' SKUs and styles, and the authored and derived split, are build output, read with
`retail_figures.figures()` and not restated here. Slice 1's floor is 2,000 SKUs, against the
department's 7,000 target in `docs/catalogue-mix-837.md`. The guards are in
`tests/test_retail_pets_967.py`.

## Slice 2: treats, toys and beds

Slice 2 adds three more derivable types, each a spec of its own drawn by `kit_pet_gear.py`:

| Type | Spec | Paths | SKU axis |
|---|---|---|---|
| Dog Treats | `type_specs/dog_treats.py` | Pets > Dog Treats > Dental Chews, Dog Biscuits, Training Treats | bag weight (`net_weight_g`); colorless, like the food |
| Pet Toy | `type_specs/pet_toy.py` | Pets > Pet Toys > Dog Toys, Cat Toys | the six main colors, times Small and Large for a dog toy |
| Pet Bed | `type_specs/pet_bed.py` | Pets > Pet Beds > Dog Beds, Cat Beds | the six main colors, times Small, Medium and Large for a dog bed |

A dental chew's title names its breed size and flavor, and a biscuit's or training treat's names
its life stage and flavor. A dog toy is a ball, rope, ring, bone or flying disc, and a cat toy a
wand, mouse, ball or kicker. Each title names its play feature (squeaky, floating, chew-resistant,
glow-in-the-dark, feather, catnip, jingle bell, crinkle, tug). A dog bed is a donut, bolster,
orthopedic or cushion bed, and a cat bed a cave, donut or radiator bed. Each title names its cover (faux fur,
corduroy, quilted, waterproof, velvet, sherpa). Toys and beds are sold in each of the six main
colors (red, blue, green, yellow, black, white; ruling 2026-10-13, gen#275). Treats are not:
the pouch's color is its print, as on a food bag. `pets_rows.gear()` builds a toy or bed row
from its sizes and colors, and the new paths and brands live in `pets_rows.py` with slice 1's.

**Drawings.** `dog_treats` is a resealable pouch with its treats in a window (sticks, twists,
bone biscuits or small bites, by `treat_form`), and it carries the food bags' flavor band,
life-stage pips and breed-sized treats. `pet_toy` draws the toy (`toy_kind`) in its color, with
its feature's mark beside it (`play_feature`): sound arcs for a squeaker, waves for a floater, a
shield for a chew-resistant toy, and so on. `pet_bed` draws the bed (`bed_style`) in its color, with a
swatch tag of its cover (`cover`). The five new attributes join `pets_rows.DRAWN`, so a derived
style that swaps one draws what it states (gen#512). All three shapes are upright, filed in
`orientations/pet_gear.py`, the module named after `kit_pet_gear.py` (gen#1045).

**Decoys.** Each new type has two text-match decoys. Each one is a word that names another type,
used in a brand or range name: `Alley Cat Provisions` dog biscuits and a dog toy, a `Dental Hill`
biscuit that is not a dental chew, a `Tennis Club` rope that is not a tennis ball, a `Kitten Mill`
dog bed, and a `Sofa Style` bolster bed that is a pet bed, not a sofa.

**Measured** (ceiling build, seed 0): the department's and each type's SKUs are build output,
read with `retail_figures.figures()`. Slice 2's floor is 4,300 Pets SKUs.

## Slice 3: leashes and collars, grooming brushes, fish and small-animal supplies

Slice 3 adds the last three types, each a spec of its own drawn by `kit_pet_care.py`:

| Type | Spec | Paths | SKU axis |
|---|---|---|---|
| Leash & Collar | `type_specs/leash_collar.py` | Pets > Leashes & Collars > Dog Leashes, Retractable Leashes, Dog Collars, Dog Harnesses, Cat Collars | the six main colors, times Small, Medium and Large for dog gear |
| Grooming Brush | `type_specs/grooming_brush.py` | Pets > Grooming > Dog Brushes, Cat Brushes | the six main colors, times Small and Large for a dog brush |
| Small Pet Supply | `type_specs/small_pet_supply.py` | Pets > Fish & Aquarium > Fish Food, Aquarium Gravel; Pets > Small Animal > Small Animal Food, Hay, Small Animal Bedding | pack weight (`net_weight_g`); colorless, like the food |

A leash, collar or harness title names its material (nylon, leather, rope, padded, reflective),
and a brush title names the coat it is for (short, long, double, curly) and its kind (slicker,
pin, bristle, deshedding, rubber curry, grooming glove). Leashes, collars and brushes are sold in
each of the six main colors (gen#275). A small-pet supply title names its formula (tropical,
goldfish, betta, timothy, meadow, vitamin C, and so on) and its animal (fish, rabbit, guinea pig,
hamster). As on a food bag, the pack's color is its print, not a variant. Two new invented brands
sell the fish and small-animal supplies: `Finbrook` and `Burrowell` (gen#720). Their marks and
house styles are in `pet_brand_styles.py`. Both are appended to the scale roster's added brands
(`range_ownership.SCALE.added`), so the names they own move no other brand's (#1052).

**Drawings.** `pet_leash` draws a leash with its handle loop and clip, a retractable leash's
case, a buckled collar or a harness (`gear_kind`) in its color, with a swatch of its `material`:
a nylon weave, leather stitching, reflective rays, padded quilting or rope twists.
`grooming_brush` draws a slicker, pin, bristle or deshedding brush, a rubber curry or a grooming
glove (`brush_kind`) in its color, with a tag of its `coat_type`: short strokes, long waves, two
layers or curls. `small_pet_supply` draws a tub for fish and a bag for the rest. Its window shows
what the pack holds (`supply_kind`: flakes, pellets, gravel, hay, nuggets, bedding), and it also
carries the animal's emblem and the formula's band. The six new attributes join `pets_rows.DRAWN`
(gen#512). The three shapes are upright, filed in `orientations/pet_care.py`.

**Decoys.** Each new type has two text-match decoys: a `Seat Belt Buckle` leash that is not a
seat belt, a `Chain Link` harness with no chain, a `Hairbrush Style` dog brush that is not for
people, a `Toothbrush Grip` slicker, a `Litter Corner` rabbit bedding that is not cat litter, and
a `Tea Time` hay that is not a tea.

**Measured** (ceiling build, seed 0): slice 3's floor is the issue's own, 6,650 Pets SKUs (95% of
the 7,000 target in `docs/catalogue-mix-837.md`). The figures themselves are build output, read
with `retail_figures.figures()`. The guards are in `tests/test_retail_pets_967.py`.
