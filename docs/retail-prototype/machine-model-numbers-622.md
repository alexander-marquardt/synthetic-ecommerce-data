# Small machines: series and model numbers (gen#622)

The large appliances ([large-appliances-334.md](large-appliances-334.md)) and the bicycles
(gen#625) carry a brand's series and a model number. The kettles, toasters, lawn mowers, robot
mowers, grass trimmers, hedge trimmers and drill drivers do too, in the shape of the bicycles.
`machine_model_numbers.py` holds the scheme and `tests/test_retail_machine_model_numbers_622.py`
holds it.

A title reads brand, series, model number, spec, then the row's own words: "Hearth & Table Brew
Max HTKT30S-26 3000W Rapid Boil Jug Kettle". A drill driver's own words open on its voltage, so
it adds no spec: "Calderby & Lune Torque Pro CL-DD26B18 18 V Cordless Drill Driver with Two
Batteries".

A code is built from four parts, in the order and with the separators of the brand's scheme
(`machine_model_numbers.SCHEMES`), and `decode` reads each part back:

| Kind | Letters | Variant letter | Digits | Spec in the title |
|---|---|---|---|---|
| Kettle | `KT` | `kettle_type` | `wattage` in hundreds | `3000W` |
| Toaster | `TS` | `finish` | `browning_settings` | `6 Setting` |
| Lawn Mower | `LM` | `power_source` | `grass_box_capacity` in liters | `40 Liter Box` |
| Robot Mower | `RM` | `boundary` | `max_slope` in percent | `35% Slope` |
| Grass Trimmer | `GT` | `power_source` | `shaft_length` in centimeters | `120cm Shaft` |
| Hedge Trimmer | `HG` | `power_source` | `tooth_gap` in millimeters | `16mm Tooth Gap` |
| Drill Driver | `DD` | `motor_type` | `voltage_v` | none |

The fourth part is the model year. One code is one product: color and size are what the SKU sells
by, so they stay out of it, as a bike's frame size does. Every SKU states the row's code as its
`model_number` option. The row also states `model_number` and `model_year` as attributes, and
`product_line` is the series, which export reads as the `series` field. A grass trimmer had no
fixed number to build the digits from, so its rows gained `shaft_length`.
A mower's spec spells "Liter" out, because `net_volume.TITLE_VOLUME` would read `40L` in a title as
a net volume.

A series is a lead word of the kind's family in `line_grammar` and a sub-model ("Brew Max"), so
`is_model` accepts it, and the lead word is one brand's across all of its kinds. An authored lead
word leaves the deal, so a derived style of another brand cannot draw it.

The text decoys of these kinds (the `DC*` rows, the color-word brand rows) carry no code. The
exact code finds its machine first on `baseline_rank.rank(index, code, 1, popular=False)`, because
no other row can match it. The titles grew, so shorter titles without a code sit above the
machines on a query for the words alone, which is the failure a policy repairs. A toaster has no
such decoys: `toaster` still finds the toasters first.

Not numbered: the other power tools (combi and hammer drills, impact drivers) and the fans and
heaters, which the maintainer's list of 2026-10-21 does not name.
