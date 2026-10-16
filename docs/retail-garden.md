# Retail garden machines, barbecues, hoses, furniture and parasols (gen#203; hoses gen#292)

The Garden department held plants and growing kits only. `garden_rows.py` adds four types, drawn by
`kit_garden.py`, under two new families of the Garden root. Three more are specs of their own
(`type_specs/hedge_trimmer.py`, `garden_furniture_set.py`, `parasol.py`), drawn by `kit_outdoor.py`.

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Lawn Mower | Garden > Lawn Care > Lawn Mowers > Cordless / Petrol / Electric Lawn Mowers | power source, drive | cutting width (cm) | power source, drive, grass box capacity (l), cutting heights, battery voltage (V) and battery included on a cordless style |
| Robot Mower | Garden > Lawn Care > Lawn Mowers > Robot Mowers | boundary (wire, GPS) | lawn area (sq m) | boundary, app control, maximum slope (%) |
| Grass Trimmer | Garden > Lawn Care > Grass Trimmers > Cordless / Petrol / Electric Grass Trimmers | power source, cutting head | cutting width (cm) | power source, cutting head, telescopic, battery voltage (V) |
| BBQ | Garden > Barbecues & Grills > Charcoal / Gas Barbecues | fuel, kind (kettle, barrel, kamado, portable, gas) | diameter or length (cm); a gas style states its burners | fuel, kind, lid, side shelves, burners |
| Hedge Trimmer | Garden > Lawn Care > Hedge Trimmers | power source (cordless, corded electric, petrol) | blade length (cm) | power source, tooth gap (mm), battery voltage (V) and battery included on a cordless style |
| Garden Furniture Set | Garden > Garden Furniture > Garden Furniture Sets | layout and material (bistro, corner lounge, dining, sun lounger) | seats | material, layout, cushions |
| Parasol | Garden > Garden Furniture > Center Pole / Cantilever Parasols | kind (center pole, cantilever), tilt, base | canopy diameter (m) | parasol kind, tilt, base included |

Each type has three or more styles from three or more invented brands and offers the six main
colors. A mower's power source is drawn (battery pack, fuel cap, cable), a gas barbecue draws one
knob per burner, and the SKU axes are never printed on an image.

## Text-match decoys

Each of the eight types (the seven above and the garden hose) carries fifteen decoys, three of each
of five classes (gen#294), listed in `garden_rows.DECOY_TABLE` with their class and the query they
target. The hose's are copies of its two styles from `type_specs/garden_hose.py`. The guard
`test_each_type_carries_at_least_three_decoys_of_each_class` reads the Garden types from the
registry (the spec files and the legacy list), so a Garden type added later owes its decoys or is
listed in the test's `EXEMPT` with the reason; the plants and growing kits are listed that way. Their structured fields tell
the truth: the color field holds the product's one main color, and only a title or description
carries the misleading word. Each is exempt from the text check and left out of the derivation.

| Class | Example | Why it matches |
|---|---|---|
| type | "Vintage Lawn Mower Cushion", "BBQ Master Apron", "Robot Mower Chef Apron" | a sibling product holds the type word |
| absent | "Petrol Free Electric Lawn Mower", "Charcoal BBQ, Not Gas", "Latex Free Garden Hose" | a real product of the type names a power source or fuel it lacks |
| incidental | "Freshly Mown Lawn Candle" (a scent), "Red Kite Lawn Mower" (a black mower with red handle), "Red Kite Garden Hose" (red connectors only) | a word of the query sits in a short title or a scent, not in the product's color |
| secondary | "Green Lawn Mower with Red Wheels", "Red Portable BBQ with Black Legs", "Black Garden Hose with Green Connectors" | the title names a part's color beside the product's own, so "red lawn mower" matches a green one |
| shade | "Light Corded Lawn Mower" (a blue mower with "a bright red start switch"), "Family Kettle BBQ" | the description alone names another main color |

A decoy title names a color only when its drawing shows it (the #311 ruling). The twenty-four
secondary decoys and the sixteen short-title incidental decoys on a real product name one: the row
passes `part` and `part_color` to its shape (`kit_garden.PARTS` lists the parts), and the shape draws
that part, and only that part, in the color, each element marked `data-part`. A secondary title
names its part ("with Red Wheels", "with White Engine", "with Green Connectors"); a short title
("Red Kite Lawn Mower") colors the shape's first part (a handle, a bumper, a handle, the legs, the
hose's connectors, which are brass unless a decoy names their color; a hedge trimmer's handle, a
furniture set's legs, a parasol's pole). A test reads each rendered drawing:
the named color on the marked part and on nothing else of it.

## Units

Most key attributes carry a UN/CEFACT unit code in the export (width, volts, litres, burners).
Two do not: `lawn_area_m2` is exported as a plain number with no unit code (it is named in square
metres), and a robot mower's maximum slope is a string with `%` in its name.

## The drawing states what the record states

A barbecue draws a `shelf` group per side when `side_shelves` is Yes (the gas styles; the barrel
states No), a `side-burner` group when `side_burner` is Yes, and a self-drive mower a `drive-lever`
and a `drive-arrow` group. A test reads each against the row.

## Not done yet

Hedge trimmers, garden furniture sets and parasols are done (gen#203) and sit in the table above.
Garden hoses (`Garden/Watering/Garden Hoses`, gen#292) are a spec, `type_specs/garden_hose.py`, drawn by `kit_garden.py`: two styles, a length axis in metres, and the fifteen decoys above.
The barbecue cooking area and pizza ovens are also open.
