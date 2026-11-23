# Cohort shoppers and their purchases (gen#1131)

The combined demo shows cohort personalization for grocery shoppers as the grocery demo does:
a shopper in the `halal` cohort sees Halal products first. The cohorts need shoppers, and the
shoppers need purchase histories that fit them. `shoppers.py` writes both:

```bash
uv run python -m synthetic_ecommerce_data.domains.retail.shoppers --out out/retail [--date YYYY-MM-DD]
```

It writes `users/profiles_<date>.yaml` and `users/purchases_<date>.yaml` under `--out`, in
grocery's schema. `prism-studio load-users --file <profiles>` loads the profiles, and
`prism-engine load-purchases --persona Combined --file <purchases>` loads the purchases. The
date (default `shoppers.DATE`) names the files and ends the purchase window. Two runs with the
same date write the same bytes.

## The roster

The 14 shoppers mirror grocery's set, with ids `gen_user_1` to `gen_user_14`, apart from the
combined demo's `ri_*` users:

| Shoppers | Cohort | Purchases | What they buy |
|---|---|---|---|
| `gen_user_1`, `gen_user_2` | `halal` | 8, 4 | SKUs that carry Halal; half are meat or fish |
| `gen_user_3`, `gen_user_4` | `kosher` | 8, 4 | SKUs that carry Kosher; half are meat or fish |
| `gen_user_5`, `gen_user_6` | `organic` | 8, 4 | three in four carry Organic, the rest any food |
| `gen_user_7`, `gen_user_8` | `vegan` | 8, 4 | SKUs that carry Vegan |
| `gen_user_9`, `gen_user_10` | `vegetarian` | 8, 4 | SKUs that carry Vegetarian |
| `gen_user_11`, `gen_user_12` | `sweet_tooth` | 8, 4 | three in four from Chocolate & Sweets, the rest any food |
| `gen_user_13` | none (a meat eater) | 8 | meat or fish, pork included |
| `gen_user_14` | none | 0 | nothing: a shopper with no preferences |

The cohort names are grocery's, lowercase. The Dietary values they map to keep the product
data's Title Case (`halal` boosts `Halal`), and `sweet_tooth` boosts the Chocolate & Sweets
aisle. Slice 1's rules already keep pork and alcohol off Halal, and pork and shellfish off
Kosher, so a shopper who buys only certified SKUs buys none of those.

## A purchase

Each purchase is one food SKU of the grocery build, a different product from the shopper's
other purchases. Its `product_id` is the SKU id (`GRC-CHB-0001-86CACE62`), because the loader
looks each one up in the catalogue by document id, and the flat field map's `id` is `sku`. Its
`title`, `brand` and `image_url` are that flat document's, so a purchase reads the same with or
without the catalogue lookup. `persona` is `Combined`, `purchase_count` is 1 to 6, and
`last_purchase` is a day 1 to 60 days before the date. Each draw comes from an RNG seeded by the
shopper's id.

The grocery styles are templates of the retail scale build, kept as they are, so every SKU a
purchase names is in the release catalogue.

`tests/test_shoppers_1131.py` checks every purchase against its shopper's cohort, using the
grocery build's own facts (the flavor's flags, the SKU's labels and the alcohol rule) rather
than the fits `shoppers.py` draws with. It also parses both files for the keys the loaders read.
