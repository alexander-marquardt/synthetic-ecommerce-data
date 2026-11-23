# Retail luggage and travel: seven types (gen#209)

The catalog held a wash bag and a few "Travel Cases" decoys, so a search for a suitcase, a cabin
bag, a holdall, a weekend bag, a luggage set, a packing cube or a neck pillow found a make-up bag
or nothing, and size, shell and wheel filters could not be shown for a high-volume family. Each
type below is its own spec under `src/synthetic_ecommerce_data/domains/retail/type_specs/` (the quick path in
[new-type-quick-path.md](new-type-quick-path.md)), built from the shared pieces in
`luggage_common.py` and drawn by `kit_luggage.py`. Since gen#1114 every type is a breadth type
(`derivable=True`): the scaled build derives styles from the authored rows (the decoys never), so
the ceiling build (seed 0) holds 1,963 luggage SKUs, up from 138. A derived style keeps the keys
its text and drawing follow (`scale_text.TYPE_FROZEN_KEYS`: a suitcase's shell, wheels, lock,
expansion and material, a cabin case's allowance and dimensions, and so on), so it differs from its
template by brand, model word (the `luggage` family of `line_grammar_families/`, after the brand: "Skerry Travel Stopover Memory Foam Neck Pillow"), price and colors; the authored rows carry six colorways each so
the range still reaches its size. `tests/test_retail_luggage_209.py` holds the table below, the
frozen keys and a floor of 1,963 on that count.

| Type (spec key) | Leaf (under Home > Luggage & Travel) | Key attributes | SKUs | Shape and param |
|---|---|---|---|---|
| Suitcase (`suitcase`) | Suitcases | shell, wheels, lock, expandable, material, capacity, weight, dimensions | color x size (litres) | `suitcase` shell |
| Cabin Case (`cabin_case`) | Cabin Cases | airline allowance, dimensions, shell, wheels, capacity, weight | color | `cabin_case` kind |
| Holdall (`holdall`) | Holdalls | material, wheels, shoulder strap, use, capacity | color | `holdall` wheels |
| Weekend Bag (`weekend_bag`) | Weekend Bags | material, compartments, trolley sleeve, capacity | color | `weekend_bag` compartments |
| Luggage Set (`luggage_set`) | Luggage Sets | shell, wheels, piece count, sizes included | color | `luggage_set` pieces |
| Travel Organizer (`travel_organizer`) | Travel Organizers | organizer type, piece count, material | color | `travel_organizer` kind |
| Neck Pillow (`neck_pillow`) | Neck Pillows | fill, cover, hood | color | `neck_pillow` hood |

Every type has three to eight styles from three or more invented brands (Tarnwick, Fenmoor & Co and
Skerry Travel are new, with a mark and a lockup of their own in `luggage_brand_styles.py`), the six
main colors with no exception, and three text-match decoys (a red lining, a word that names
another type, a finish that is not leather). The audience is Unisex.

A suitcase's size is the SKU axis (the `luggage_size` option): its capacity in litres is the
value, and each litre carries its size name (Cabin, Medium, Large), its weight in kilograms and
its outer dimensions in centimetres, so `lightweight suitcase under 3 kg` and `red suitcase 65 litre`
are a range and an equality filter on structured entries. Every Cabin size is `55 x 40 x 20 cm` or
within it, the cabin allowance of most airlines: the demo query `cabin suitcase 55x40x20` (gen#1114)
has Cabin suitcase SKUs and the `55 x 40 x 20 cm` cabin cases to match on the `dimensions` entry. A luggage set's pieces and a cabin case's shell are style-level, because the
drawing shows them: one image per style and colorway. A capacity in litres is exported with its
canonical value in millilitres, like every `LTR` entry. A decoy states the capacity of the
authored row it copies, so its litres never disagree with its dimensions or material.

The department path is `Home > Luggage & Travel` (gen#1114), the generator department Home. Until
gen#1114 it was `Womens > Accessories > Travel`, where a shopper looking for luggage would not look;
the large retailers file luggage as a range of its own (Luggage & Travel), not under womenswear. The
store adds no new root for it (the retail roots are `core/departments.RETAIL`, guarded by
`tests/test_retail_departments_281.py`), and the audience stays an attribute (Unisex). The "Travel
Cases" decoys of gen#326 are not luggage and stay under `Womens > Accessories > Travel`.
