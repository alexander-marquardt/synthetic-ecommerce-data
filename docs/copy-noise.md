# Copy noise

A distributor's copy mentions sizes a product does NOT fit, the siblings it
is also sold in, the unit a shopper might have typed, what it pairs with and
what it cuts. Every one of those words is searchable, so a query matches more
than the products it names, and the policies and facets are what narrow the
page back down (`core/noise.py`). Every sentence is TRUE of its record --
read from its own published values, its siblings, or a table -- and the
attributes are never touched, so the facets can always separate the noise out.
Since #937 the sentences are in the searchable `text` only: the description ends
with the part number.

| type | example | from |
|---|---|---|
| negative fit | `Not for M10 or M16 threads.` / `Will not fit 5/32" sockets.` | the neighbouring diameters; the next smaller key |
| siblings | `Also available in 3/16" / 7/32" sizes.` / `Also available in M12x1.25 sizes (M12 thread, 1.25 mm pitch).` | the product's other SKUs, on its variant axis |
| unit equivalent | `12mm (approx. 15/32").` | the published value, to the nearest 64th or 0.1mm |
| fit / pairing | `Bore 11.992-12.000mm (ISO 492 Normal class).` / `Pair with M12x1.75 hex nuts and a 10mm hex key.` | ISO 492 bore tolerances; the record's thread and drive |
| material contrast | `Zinc-plated steel (not stainless).` / `18-8 Stainless Steel (not plated).` | the record's material and finish |
| work material | `Suitable for aluminum, brass and mild steel.` | what the tool's material cuts, by common practice |
| standards | `Equivalent to DIN 912 / ISO 4762.` / `Higher strength than Class 8.8.` | same-dimension standards; ISO 898 / SAE J429 grades |
| application | `For use with socket cap screws.` | hex keys |

**One knob:** `GeneratorConfig.noise` (`--noise`) scales every rate; 1.0 is
the realistic default and 0 a clean catalog. Each record draws from its own
stream (catalog seed + SKU), so the clean and the noisy build have IDENTICAL
attributes and titles, record for record -- `tests/test_noise_text.py`
builds both and compares. **Unit equivalents are held to a minority**:
15-20% of the records that could carry one (measured 18.0% on the golden,
1,043 of 5,792),
because the facets expand units themselves and a result should show the facet
working, not text luck. Every sentence type has a checker in that test
against tables written out there, a planted false sentence reds, and five
mutation rows prove the checks bite.
