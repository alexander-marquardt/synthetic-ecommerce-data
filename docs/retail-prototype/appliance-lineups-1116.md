# Brand line-ups of the large appliances (#1116, round 4)

A kind of large appliance was a table of six models, one a brand, so a brand's own machines could
not be compared. Every own brand now sells every kind in at least four models, and Home > Large
Appliances holds 1,737 SKUs on 789 products (471 on 213 before). The issue's target is about 1,500
more than the 283 it measured.

| Product type | Products before | Products after |
|---|---:|---:|
| Fridge & Freezer | 70 | 250 |
| Laundry Appliance | 61 | 223 |
| Dishwasher | 24 | 96 |
| Hob | 19 | 73 |
| Built-in Oven | 13 | 49 |
| Cooker Hood | 13 | 49 |
| Range Cooker | 13 | 49 |

`appliance_lineups.line_up` appends 18 models to each of the 32 tables in the specs, three a brand:

* **Size.** A brand's added models sit at other points of the same table than its authored one, so
  its four are four points. A fridge's or freezer's litres are also moved by the brand's
  `LITRES_OFF`, as no two makers build to one volume. A width, a load and a spin stay the standard
  ones.
* **Price.** The table's price times the brand's `PRICE_LEVEL`, one level a brand across every kind.
  Brimwell is the value brand and Lunden & Voss the premium one.
* **Feature.** Each added model states one feature (`feature`) of its type and its description ends
  with it. A brand's three have three.

The titles and model numbers follow gen#622 unchanged. The authored models come first in each table,
so their ids, titles, brands, prices and numbers are what they were. Two tables of one kind that
share loads and spins (`Compact Washer`, `Washer Dryer Combo`, `Heat Pump Dryer`) name their own
order in `laundry_appliance._STEPS`, so no model number repeats between them.

The models are not derivable, as before: the scaled build copies them as authored. The issue's last
slice, the ten-query table without and with a policy, is
[clash-queries-1116.md](clash-queries-1116.md).
`tests/test_retail_appliance_lineups_1116.py` holds this page.
