# Pets, slice 1 (gen#967)

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

**Breadth.** The three types are derivable. A colorless style has only its three or four sizes
as SKUs, so a type needs more templates than a colored one to reach the same SKU count: the two
last litter templates (Multi-Cat Fresh Linen Clumping Clay, Citrus Clumping Wood Pellet) widen
the scent and brand pools that the derived litters draw from.

**Decoys.** Each type carries two text-match decoys: a word that names another type in a brand
or a range name (`Alley Cat Larder` dog food, `Dog Rose` cat food, `Kitten Mill` adult cat food,
`Puppy Hill` senior dog food, `Lavender Hill` pine litter) and, for litter, a refill bag
whose title names a litter tray it does not include.

**Measured** (ceiling build, seed 0): 2,173 SKUs in 626 styles under Pets (Dog Food 239 styles,
Cat Food 235, Cat Litter 152; 31 authored with the decoys, 595 derived), about 31% of the
department's 7,000 target in `docs/catalogue-mix-837.md`. Treats, toys and beds (slice 2), and
leads and collars, grooming and aquarium and small-animal supplies (slice 3), are later slices
of gen#967. The guards are in `tests/test_retail_pets_967.py`.
