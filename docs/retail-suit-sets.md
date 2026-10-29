# Retail suits sold as a set: Trouser Suit and Boys Suit (gen#215)

The five Mens tailoring types (jacket, trousers, waistcoat, dinner suit, formal accessories) are
in [retail-mens-depth.md](retail-mens-depth.md). Two more suit types sit under the Womens and
Kids roots, each a registered spec (`src/synthetic_ecommerce_data/domains/retail/type_specs/`) and each drawn as
the set by `src/synthetic_ecommerce_data/domains/retail/kit_suit_sets.py`:

| Product type | Category path | Key attributes (structured entries) | Drawing params | Styles |
|---|---|---|---|---|
| Trouser Suit | Womens / Suits & Tailoring / Trouser Suits | `jacket_style` (Single Breasted, Double Breasted, Collarless), `leg_fit` (Slim, Straight, Wide), `fabric`, `piece_count` (2), `occasion` | `jacket`, `fit` | 8, six brands, UK 8 to 18 |
| Boys Suit | Kids / Boys / Suits | `piece_count` (2 or 3), `fit` (Slim, Regular), `fabric`, `occasion` | `pieces`, `fit` | 6, five brands, 3-4 to 13-14 Yrs |

`fabric` is a plain fibre or weave from the closed shopper list (Wool, Linen, Cotton, Polyester,
Suiting, Velvet), never a blend, and each style's `occasion` is set on the style so a
description that names an occasion (a wedding suit, an evening jacket) agrees with it.

A drawing states what the record states: the jacket style is the `jacket` param, the leg fit the
`fit` param, and a three piece Boys Suit draws its waistcoat. `tests/test_retail_suit_sets_215.py`
reads each choice back from the drawing (`class="jacket-double"`, `class="legfit-wide"`,
`class="pieces-3"`) and holds the geometry apart from the stamp.

Each type carries the gen#311 apparel decoys (three of each of six classes), generated from its
first row by `decoy_apparel`; the class 2 compounds are real retail names (Tuxedo, Waistcoat and
Culotte Trouser Suit; Sailor, Tuxedo and Page Boy Suit), also named in the reviewed list of
`tests/test_retail_apparel_decoys_311.py`. A decoy's colored part is its trouser cuffs
(`details.PARTS`).

The one old Suit Jacket row (`SUITCK`, Womens / Coats & Jackets / Blazers) is drawn with the
`suit_jacket` shape of `kit_suits.py`, no longer the generic `coat`.

Trouser leg and jacket length are SKU axes, as a shop sells a suit (34/32, 40R). Mens Suit
Trousers are color x waist x `inside_leg` (Short/Petite, Regular, Long), with `in_stock` per SKU
and a `size_range` derived from the legs in stock, which is the legwear rule of
[retail-prototype.md](retail-prototype.md) (gen#206) that jeans and joggers follow. Every fourth
floor style has its short leg sold out and every fourth its long one, so a `petite` filter finds
only the styles with a short leg in stock. A Mens Suit Jacket is color x chest x `length` (Short,
Regular, Long). A leg or jacket length is a size, not a cut, so the drawing does not change with
it: the `suit_trousers` shape takes no `leg` param, draws the hem where a regular leg ends, and no
record states a `leg_length`. There is still one image per style and colorway, as for jeans
(ruled on gen#215, 2026-10-28). The Womens Blazers, Waistcoat, Dinner Suit, Trouser Suit and Boys
Suit are sold by one size and keep it.
