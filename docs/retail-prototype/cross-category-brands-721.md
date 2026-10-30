# Brands that cross departments, TVs and volt meters (#721)

Five invented brands sell across departments, so a shopper can follow one brand from a laptop to a
fridge. A few styles of each brand and type are ordinary rows of the types they join.

| Brand | Short form | Sells | House style |
|---|---|---|---|
| Grape Computer | | laptops, desktops, the GrapePhone 16 smartphone | `electronics_brand_styles.py`, mark `vine` (gen#720) |
| GoodLook | GL | TVs, washing machines, fridges | `appliance_brand_styles.py`, mark `lens_eye` |
| SingingSam | | TVs, washing machines, fridges, smartphones, a laptop | `appliance_brand_styles.py`, mark `note_pair` |
| PackingHarder | PH | monitors, desktops, laptops, volt meters | `electronics_brand_styles.py`, mark `crate` |
| Xell | | desktops, laptops | `electronics_brand_styles.py`, mark `x_cell` |

- Each mark is the brand's own and imitates no real one. `Xell` was chosen over `Dwell`, a real UK
  furniture retailer and brand.
- Grape Computer's phones and tablets came from #720. The GrapePhone 16 here is a new row beside
  them. The other four names were given by the maintainer; they have had no web check.
- GoodLook and SingingSam take schemes and series in `appliance_model_numbers.py`. They are left out
  of `large_appliance_rows.BRANDS`, which deals the six older brands round the authored range: adding
  them there would rebrand every existing model. `kind_rows(..., brands=)` makes their own rows
  (`cross_brand_rows` in `type_specs/fridge_freezer.py` and `type_specs/laundry_appliance.py`).

## New types

- **TV**, `Electronics > TVs` (`type_specs/tv.py`, rows `electronics_rows.TVS`, shape `tv`, param
  `form`): 14 styles and one color decoy (`red tv`), a screen size per SKU. Colors are limited in
  `type_colors.RESTRICTED`.
- **Volt Meter**, `Home > DIY & Tools > Volt Meters` (`type_specs/volt_meter.py`, shape `volt_meter`,
  param `form`): 6 styles and one absent-feature decoy (`volt meter carry case`). The title says
  `Volt Meter` and the description `voltmeter`, so both spellings find the type, and one style
  names `multimeter`. It sits beside the drills on the retail side, not in the industrial tree: an
  industrial type needs a part-number block, more than a few styles per brand.

## Real names in the line words

`real_brands.check()` over the whole build found two real names among the derived line words:
`Kindle` (lighting) and `Nestle` (casual shoes), 70 titles. They are now `Ember` and `Snuggle`, and
`tests/test_cross_category_brands_721.py` runs the check over the ceiling build, where derived
styles exist, not over the templates alone.
