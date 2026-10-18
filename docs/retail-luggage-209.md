# Retail luggage and travel: seven types (gen#209)

The catalog held a wash bag and a few "Travel Cases" decoys, so a search for a suitcase, a cabin
bag, a holdall, a weekend bag, a luggage set, a packing cube or a neck pillow found a make-up bag
or nothing, and size, shell and wheel filters could not be shown for a high-volume family. Each
type below is its own spec under `prototypes/retail_drawings/type_specs/` (the quick path in
[new-type-quick-path.md](new-type-quick-path.md)), built from the shared pieces in
`luggage_common.py` and drawn by `kit_luggage.py`. The styles are templates only (`derivable`
False): the range grows by authored rows. `tests/test_retail_luggage_209.py` holds the table below.

| Type (spec key) | Leaf (under Womens > Accessories > Travel) | Key attributes | SKUs | Shape and param |
|---|---|---|---|---|
| Suitcase (`suitcase`) | Suitcases | shell, wheels, lock, expandable, material, capacity, weight | color x size (litres) | `suitcase` shell |
| Cabin Case (`cabin_case`) | Cabin Cases | airline allowance, dimensions, shell, wheels, capacity, weight | color | `cabin_case` kind |
| Holdall (`holdall`) | Holdalls | material, wheels, shoulder strap, use, capacity | color | `holdall` wheels |
| Weekend Bag (`weekend_bag`) | Weekend Bags | material, compartments, trolley sleeve, capacity | color | `weekend_bag` compartments |
| Luggage Set (`luggage_set`) | Luggage Sets | shell, wheels, piece count, sizes included | color | `luggage_set` pieces |
| Travel Organizer (`travel_organizer`) | Travel Organizers | organizer type, piece count, material | color | `travel_organizer` kind |
| Neck Pillow (`neck_pillow`) | Neck Pillows | fill, cover, hood | color | `neck_pillow` hood |

Every type has three or four styles from three or more invented brands (Tarnwick, Fenmoor & Co and
Skerry Travel are new, with a mark and a lockup of their own in `luggage_brand_styles.py`), the six
main colors with no exception, and three text-match decoys (a red lining, a word that names
another type, a finish that is not leather). The audience is Unisex.

A suitcase's size is the SKU axis (the `luggage_size` option): its capacity in litres is the
value, and each litre carries its size name (Cabin, Medium, Large) and its weight in kilograms, so
`lightweight suitcase under 3 kg` and `red suitcase 65 litre` are a range and an equality filter on
structured entries. A luggage set's pieces and a cabin case's shell are style-level, because the
drawing shows them: one image per style and colorway. A capacity in litres is exported with its
canonical value in millilitres, like every `LTR` entry. A decoy states the capacity of the
authored row it copies, so its litres never disagree with its dimensions or material.

The department path is `Womens > Accessories > Travel`, the path the existing "Travel Cases"
decoys already use. A suitcase or a holdall is not women's-only, and the store has no unisex
travel or luggage root (the eleven roots are in `tests/test_retail_departments_281.py`), so the
audience is an attribute (Unisex) and the path stays under `Womens`.
