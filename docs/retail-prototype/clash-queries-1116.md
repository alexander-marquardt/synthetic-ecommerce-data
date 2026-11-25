# The ten clash queries, without and with a policy (#1116, round 5)

The large appliances share their words with other products. These are the ten queries of the
issue's table, for search-quality demos. The build holds every family of each.

Measured on 2026-11-25 at main `c9ed28c8`, which carries the brand line-ups
([appliance-lineups-1116.md](appliance-lineups-1116.md)), by
`uv run python -m synthetic_ecommerce_data.clash_queries --ceiling`: the scaled
retail build (`retail_figures.ceiling`, every template exhausted) and the default industrial build,
as the combined catalog holds them. The counts are products, not SKUs. They are a record: a product
added later moves them, so re-run the command before quoting one.

* **Without a policy** is the no-policy ranker (`baseline_rank`, text score without popularity).
* **With it** is the same ranker and the row's policy: a filter, or a boost that multiplies a record's
  score by 10, on a structured field. It is the generator's measurement of what the data supports.
  Nobody authored these policies in R&I, and the order there comes from its own engine.
* A policy cell names the field and its values. "first at 57" is the place of the family's first
  product in the whole result.

| Query | Expected | Families found without a policy | Top 10 without a policy | Policy | Families found with it | Top 10 with it |
|---|---|---|---|---|---|---|
| `washer` | Both families; a policy can rank by department intent. | washing machines 96 (first at 57), flat washers 225 (first at 1), washer fluid 18 (first at 61) | washer_flat 10 | appliance_type = Washing Machine or Washer Dryer x10 | washing machines 96 (first at 1), flat washers 225 (first at 97), washer fluid 18 (first at 156) | Washing Machine 7, Washer Dryer 3 |
| `washer 8kg` | Laundry only (kg load). | washing machines 103 (first at 1) | Washer Dryer 6, Washing Machine 4 | filter appliance_type = Washing Machine or Washer Dryer, load = 8 | washing machines 27 (first at 1) | Washer Dryer 6, Washing Machine 4 |
| `m8 washer` | Fasteners only (thread size). | flat washers 225 (first at 1) | washer_flat 9, serrated_flange_nuts 1 | filter product_type = washer_flat, size = M8 | flat washers 26 (first at 1) | washer_flat 10 |
| `dryer` | Both families. | tumble dryers 96 (first at 98), hair dryers 97 (first at 1) | Hair Dryer 10 | appliance_type = Tumble Dryer (Heat Pump) or Tumble Dryer (Condenser) or Tumble Dryer (Vented) x10 | tumble dryers 96 (first at 1), hair dryers 97 (first at 97) | Tumble Dryer (Condenser) 7, Tumble Dryer (Heat Pump) 3 |
| `heat pump dryer` | Laundry only. | tumble dryers 96 (first at 1) | Tumble Dryer (Heat Pump) 10 | filter appliance_type = Tumble Dryer (Heat Pump) | tumble dryers 48 (first at 1) | Tumble Dryer (Heat Pump) 10 |
| `range` | Range cookers first for a kitchen intent. | range cookers 49 (first at 8), signal and firing range 30 (first at 1) | Baby Monitor 5, Range Cooker (Induction) 3, Water Gun 2 | product_type = Range Cooker x10 | range cookers 49 (first at 1), signal and firing range 30 (first at 50) | Range Cooker (Induction) 10 |
| `range cooker 90cm` | Cookers only (width). | range cookers 49 (first at 1) | Range Cooker (Induction) 8, Range Cooker (Dual Fuel) 2 | filter product_type = Range Cooker, item_width = 90 | range cookers 25 (first at 1) | Range Cooker (Induction) 8, Range Cooker (Dual Fuel) 2 |
| `iron` | Both; a policy decides. | clothes irons 7 (first at 4), industrial iron 550 (first at 50) | Minerals 4, Steam Iron 3, Frying Pan 1, Saucepan 1, Kitchen Utensil 1 | product_type = Steam Iron x10 | clothes irons 7 (first at 1), industrial iron 550 (first at 52) | Steam Iron 7, Minerals 3 |
| `steam iron` | Irons only. | clothes irons 7 (first at 1) | Steam Iron 7, Frozen Vegetables 3 | filter product_type = Steam Iron | clothes irons 7 (first at 1) | Steam Iron 7 |
| `freezer` | Appliances first; freezer bags as the second family. | freezers 96 (first at 25), freezer bags 38 (first at 1) | Food Storage Bags 10 | appliance_type = Chest Freezer or Upright Freezer x10 | freezers 96 (first at 1), freezer bags 38 (first at 97) | Upright Freezer 7, Chest Freezer 3 |

## What it shows

* **The clash is in the data.** Without a policy the top ten of `washer` is flat washers, of `dryer`
  hair dryers and of `freezer` freezer bags. The boost turns each into appliances, and keeps the
  second family further down the result.
* `washer 8kg`, `heat pump dryer`, `range cooker 90cm` and `m8 washer` find the right products in
  their top ten with no policy. `m8 washer` also finds one serrated flange nut, titled
  "Washer-Faced Flange Nut". It is a fastener, and the filter takes it out.
* `iron` meets minerals, steam irons and cast iron together. The build holds 7 clothes irons, so
  the boost puts them first and the minerals follow. The industrial iron, 550 products, starts at
  place 50.
* `steam iron` finds seven steam irons and then frozen vegetables ("Steam Ready"), which the filter
  takes out.

`tests/test_retail_clash_queries_1116.py` holds this page: every family is present, each policy
does what its row says on the template build, and the Query, Expected and Policy cells are the
code's.
