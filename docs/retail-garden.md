# Retail garden machines and barbecues (gen#203, first increment)

The Garden department held plants and growing kits only. `garden_rows.py` adds four types, drawn by
`kit_garden.py`, under two new families of the Garden root.

| Type | Path | Style axis | SKU axis | Key attributes |
|---|---|---|---|---|
| Lawn Mower | Garden > Lawn Care > Lawn Mowers > Cordless / Petrol / Electric Lawn Mowers | power source, drive | cutting width (cm) | power source, drive, grass box capacity (l), cutting heights, battery voltage (V) and battery included on a cordless style |
| Robot Mower | Garden > Lawn Care > Lawn Mowers > Robot Mowers | boundary (wire, GPS) | lawn area (sq m) | boundary, app control, maximum slope (%) |
| Grass Trimmer | Garden > Lawn Care > Grass Trimmers > Cordless / Petrol / Electric Grass Trimmers | power source, cutting head | cutting width (cm) | power source, cutting head, telescopic, battery voltage (V) |
| BBQ | Garden > Barbecues & Grills > Charcoal / Gas Barbecues | fuel, kind (kettle, barrel, kamado, portable, gas) | diameter or length (cm); a gas style states its burners | fuel, kind, lid, side shelves, burners |

Each type has three or more styles from three or more invented brands and offers the six main
colors. A mower's power source is drawn (battery pack, fuel cap, cable), a gas barbecue draws one
knob per burner, and the SKU axes are never printed on an image.

## Text-match decoys

Each type carries three decoys (gen#294), listed in `garden_rows.DECOY_TABLE` with their class and
the query they target. Their structured fields tell the truth.

| Class | Example | Why it matches |
|---|---|---|
| type | "Vintage Lawn Mower Cushion", "BBQ Master Apron" | a sibling product holds the type word |
| absent | "Petrol Free Electric Lawn Mower", "Charcoal BBQ, Not Gas" | a real product of the type names a power source or fuel it lacks |
| incidental | "Freshly Mown Lawn Candle", "Fresh Cut Grass Candle" | a scent holds a word of the query |

## Not done yet

Hedge trimmers, garden furniture sets and parasols (gen#203 continues); garden hoses are in gen#292.
The barbecue cooking area and pizza ovens are also open.
