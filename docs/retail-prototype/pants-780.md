# Pants are everyday underwear, for women and men (gen#780)

In British English underwear is called pants. Before this change the only products whose
titles said `pants` were period pants, so a demo search for `pants` showed period products and
nothing for men. The maintainer asked that no clothing product be a period product, so:

| Was | Is |
|---|---|
| `Womens/Lingerie/Period Pants`, type `period_pants`, product type `Period Pants`, an `Absorbency` attribute (Light, Medium, Heavy, Overnight) | `Womens/Lingerie/Pants`, type `pants` (`type_specs/pants.py`), product type `Pants`, sold by `Cut` and `Fabric` |
| no pants for men (`Mens/Underwear` held Boxers and Vests) | `Mens/Underwear/Pants`, type `mens_pants` (`type_specs/mens_pants.py`), product type `Mens Pants`, sold by `Cut` (Briefs, Low-Rise Briefs, Hipster) and `Fabric` |
| `Womens/Swimwear/Period Swimwear`, type `period_swimwear`, an `Absorbency` attribute | `Womens/Swimwear/Bikini Bottoms`, type `swim_bottoms` (`type_specs/swim_bottoms.py`), product type `Swim Bottoms`, sold by `Cut` |

No clothing title, description, category or product type says `period`, `tampon`, `flow`,
`absorbent` or `leakproof` any more, and no product carries `absorbency`. Products outside
clothing keep those words where they describe the product (absorbent towels, leakproof bottles).
`tests/test_retail_pants_780.py` holds all of this on the templates.

**Drawings.** The women's pants keep the knicker drawings they had (`kit_underwear.knickers`,
one per cut); none of them showed a period mark. The men's pants have their own shape,
`mens_pants`, drawn in their spec file: a brief, a low-rise brief or a hipster, each with a
contoured pouch and no fly, so they read differently from the boxers' Y-front. The swim bottoms
keep their outline and waistband (`kit_swimwear.swim_bottoms`, renamed from `period_swimwear`).
The one or two gusset layers that drew the absorbency are gone: those layers were the period mark.
As for every SKU, each one has its own image file.

**Ids.** The product ids of the women's pants and the swim bottoms are unchanged (`BRD-PP...`,
`BRD-PRD...`). Their text-match decoys are numbered by type key, so they now have new ids
(`PLT-DSPANTS...`, `PLT-DSSWIM_BOTTOMS...`, `PLT-DSMENS_PANTS...`).

**After this merges.** The leaf, product type and attribute names change, so
elastic/prism-retail-and-industrial needs its fixtures and `served_index_fields.json` updated
when the new data loads.
