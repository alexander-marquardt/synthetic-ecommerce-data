<!-- pr-body-for: branch=issue-721 -->

Fixes #721

<!-- issue: The catalogue should hold TVs and volt meters and five cross-category brands (Grape Computer, GoodLook, SingingSam, PackingHarder, Xell); currently it has no TVs and no brand spans computers and appliances -->

## What this changes

Adds two product types and five invented brands. Each brand has its own mark and house style, and sells the types in the issue's table as a few ordinary rows.

| Brand | Sells here | Style file |
|---|---|---|
| Grape Computer | 2 laptops, 2 desktops, GrapePhone 16 | `electronics_brand_styles.py` |
| GoodLook (GL) | 5 TVs, 3 washing machines, 4 fridges | `appliance_brand_styles.py` |
| SingingSam | 5 TVs, 3 washing machines, 4 fridges, 2 smartphones, 1 laptop | `appliance_brand_styles.py` |
| PackingHarder (PH) | 2 monitors, 2 desktops, 2 laptops, 3 volt meters | `electronics_brand_styles.py` |
| Xell | 2 desktops, 2 laptops | `electronics_brand_styles.py` |

- **TV**: `Electronics > TVs`, `type_specs/tv.py`, shape `tv`. 14 styles and one color decoy (`red tv`), with a screen size per SKU. Colors are limited to Black, Grey, Silver and White in `type_colors.RESTRICTED`.
- **Volt Meter**: `Home > DIY & Tools > Volt Meters`, `type_specs/volt_meter.py`, shape `volt_meter`. 6 styles and one absent-feature decoy (`volt meter carry case`). The title says `Volt Meter` and the description says `voltmeter`, so both spellings find it. One style names `multimeter`.
- Builds on the tree guard of #284: both nodes pass `tree_guard`.

Docs: `docs/retail-prototype/cross-category-brands-721.md` (new), `docs/retail-electronics.md`, `docs/retail-type-colors-448.md`.

## What the review should look at

1. **`tv` "routes to the TV node" is measured on the no-policy baseline, not on a live route.** The evidence is `baseline_rank.rank` over the ceiling build, the check the gate comment named. No build was ingested and no Prism was run, and this PR adds no policy, so a live route is still to be shown once the catalogue is re-released.
2. **`real_brands.check()` was already red on main.** Over the ceiling build it found 70 titles: the derived line words `Kindle` (64, lighting) and `Nestle` (6, kids' sandals). The existing guards ran over the templates only, where these words do not appear. They are now `Ember` and `Snuggle`, and the new test runs the check over the whole build. Those 70 derived titles change.
3. **The metric's "0 today" holds only for the five brands.** Halvern and its peers already span phones and computers, so counting every brand passes before this change. The test counts the five. GoodLook and SingingSam span two or more, and Grape Computer reaches two only through a phone.
4. **That is why this PR has a GrapePhone 16, which the table does not list.** Grape Computer's phones were left to #720, which would leave the metric at 2 until #720 lands. The row is new and clashes with no name #720 renames to, and the maintainer's words were "create products called GrapePhone". #720 will also touch `_OS` (`Grape OS` is added here) and the Grape Computer style, which it should reuse rather than add again.
5. **Volt meters are on the retail side, not the industrial tree the issue hypothesized.** An industrial type needs a part-number block and more than "a few styles". PackingHarder therefore crosses computers and DIY tools, not the two sides of Combined.
6. **GoodLook and SingingSam are not in `large_appliance_rows.BRANDS`.** That tuple deals the six older brands round the authored range, so adding them would rebrand every existing model. `kind_rows` takes `brands=` instead, and each spec has a `cross_brand_rows()`.
7. **The five names have had no web check.** The maintainer gave them. Nothing else in this PR was checked for being a real name either, including the new series and line words beyond `real_brands`.

Decoys planted: 2, one per new type. The quick path counts none for these departments, and each new type's own text gives `tv` and `voltmeter` nothing to collide with on this build.

## Evidence

`baseline_rank.rank` over the ceiling build (17,321 products, 176,320 SKUs), `real_brands.check` empty:

```
== tv
BRD-ETV008 | SingingSam | Electronics/TVs | SingingSam Duet 4K LED Smart TV
BRD-ETV011 | Halvern    | Electronics/TVs | Halvern Vision 4K LED Smart TV
BRD-ETV003 | GoodLook   | Electronics/TVs | GoodLook Clear 4K LED Smart TV
BRD-ETV006 | SingingSam | Electronics/TVs | SingingSam Encore 4K OLED Smart TV
BRD-ETV001 | GoodLook   | Electronics/TVs | GoodLook Vivid 4K OLED Smart TV
BRD-ETV012 | Halvern    | Electronics/TVs | Halvern Vision 4K OLED Smart TV
BRD-ETV009 | SingingSam | Electronics/TVs | SingingSam Duet Full HD LED Smart TV
BRD-ETV013 | Marrick    | Electronics/TVs | Marrick View 4K LED Smart TV
BRD-ETV005 | GoodLook   | Electronics/TVs | GoodLook Curve 4K OLED Smart TV
BRD-DCETV1 | Marrick    | Electronics/TVs | Marrick Red Line 4K LED Smart TV
BRD-ETV007 | SingingSam | Electronics/TVs | SingingSam Encore 4K Mini LED Smart TV
BRD-ETV014 | Torvane    | Electronics/TVs | Torvane Pixel 4K Mini LED Smart TV
```

On main the same query returned nothing for `tv`, `television` and `voltmeter`, and two screwdriver sets for `volt meter`.

Red commit: `619b6ed2`.

Guard: tests/test_cross_category_brands_721.py
