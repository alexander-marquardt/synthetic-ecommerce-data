# Cooker hoods, and deeper laundry and freezers (#1116, round 3)

Home > Large Appliances had no cooker hood, six chest and six upright freezers, and no laundry
title with the US word `washer`. So `washer` met windshield washer fluid only.

| Type (leaf) | Kinds (`appliance_type`) | Spec | Drawing |
|---|---|---|---|
| Cooker Hood (`Cooker Hoods`) | Chimney Cooker Hood, Integrated Cooker Hood | `type_specs/cooker_hood.py` | `kit_cooking.cooker_hood` (`kind`, `width`) |

A hood is 50 to 100 cm wide. Its width, extraction rate, fan speeds and energy rating are
structured, and its width is in the title, the model number and the drawing. The model numbers
follow gen#622 with kind letters `F` (chimney) and `Q` (integrated) and the `width` digit group, as
a range and a hob do. Hoods come in white, black and silver (`type_colors.py`). The color decoy is a
stainless chimney hood with black glass trim (`CHK001`).

Depth, in the specs the kinds already had:

| Kind | Models added | Titled |
|---|---|---|
| Washing Machine | 6 front load, 6 compact | `Front Load Washer`, `Compact Washer`; two in the second form, `Washer from <brand>, Model <code>` |
| Washer Dryer | 6 | `Washer Dryer Combo` |
| Tumble Dryer (Heat Pump) | 6 | `Heat Pump Dryer` |
| Chest Freezer | 6 | `Garage-Ready Chest Freezer` |
| Upright Freezer | 6 | `Garage-Ready Upright Freezer` |

No new kind is added: a washer is a washing machine, so its `appliance_type`, and the model
number's kind letter, are the washing machine's.

## What the queries find

On the no-policy baseline ranker (without popularity):

* `cooker hood` finds cooker hoods only in its top five.
* `heat pump dryer` finds tumble dryers only in its top ten.
* `washer` over the retail templates finds a washing machine and windshield washer fluid in its
  top ten.
* `washer` over the retail templates and the 225 flat washer SKUs of the default industrial build
  finds both families, but its top ten is flat washers: their titles are three or four words
  ("Flat Washer: Nylon"), so BM25 ranks them above every machine title. A category policy, not the
  data, picks the laundry intent. The titles are not shortened to win.
* `washer 8kg` finds laundry only and `m8 washer` finds flat washers only, each in its top five.

The department held 471 SKUs after this round (364 before). The brand line-ups that take it past
1,700 came next: see [appliance-lineups-1116.md](appliance-lineups-1116.md).
`tests/test_retail_hood_washer_1116.py` holds this page.
