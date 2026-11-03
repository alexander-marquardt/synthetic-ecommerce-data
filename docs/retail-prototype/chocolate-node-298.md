# The Chocolate node (gen#298)

The grocery tree had no chocolate node. Bars and boxes sat directly under
`Food & Drink > Chocolate & Sweets`, beside Sweets. A shopper's bare "chocolate" named no
category, so a category policy such as "chocolate without peanuts" had nothing to route to.
Real grocery trees have the node: Open Food Facts has `en:chocolates`, and a UK grocer has a
Chocolate aisle with bars, multipacks, sharing bags and boxes. This tree follows the UK grocer,
because the catalogue is UK-styled, and the shape is the one the maintainer set on 2026-10-14:

```
Chocolate & Sweets > Chocolate > Chocolate Bars > Dark Chocolate Bars
                                                > Milk Chocolate Bars
                                                > White Chocolate Bars
                               > Chocolate Multipacks
                               > Sharing Bags
                               > Chocolate Boxes
                   > Sweets
```

Every chocolate product sits one level deeper than before. Nothing sits on Chocolate or on
Chocolate Bars itself. The node is named `Chocolate`, singular, so the shopper's "chocolate"
names it exactly and no plural rule is needed. Hot chocolate stays under `Drinks`, as the
natural decoy for "chocolate", and the sweets and wine gums stay in Sweets.

| Leaf | What sits in it |
| --- | --- |
| Dark Chocolate Bars | CHB dark bars, CHO Dark Chocolate Orange, and the dark #294 peanut decoys (PNT, PNH, PNF); the decoy "Chocolate & Candied Oranges" |
| Milk Chocolate Bars | CHB milk bars, CHO Milk Chocolate Orange, and the milk #294 peanut decoys |
| White Chocolate Bars | CHB White and Lemon White; the decoy "White Chocolate Raspberries Bar" |
| Chocolate Multipacks | CMP, a bar line in 4 x 35g and 6 x 25g |
| Sharing Bags | CSB, a bar line's buttons or bites in a 150g or 250g bag |
| Chocolate Boxes | CHX, the seasonal advent calendar, and the `chocolate_box` decoys |

**One chocolate per style.** A CHB style carries several flavors. It used to mix types: the
anchor (Milk, Salted Caramel Milk, White) was one listing. `_bars` in `grocery_families.py`
maps each bar flavor to its child: White or Dark when the name says so, otherwise Milk, and a
milk flavor must contain milk. A flavor that is none of the three stops the build. `Family.kin`
then gives a style the flavors that share its first flavor's child. So a CHB style draws from
one chocolate, and the two mixed anchors are re-picked within one: (Dark 70%, Raspberry Dark)
may contain peanuts, and (Milk, Salted Caramel Milk) is nut free. A family with no children
draws exactly as before. CHB is the first core family, though, so its new draw moves the core
families built after it. The catalogue load for this batch reloads them anyway.

**The new leaves.** CMP and CSB are depth families appended last. They are built from the depth
stream, so no earlier draw moves. Their product type is `Chocolate Bar`, the bar lines in another
pack, so no new type is registered. The decoy kind `chocolate` is now `dark_chocolate` and
`white_chocolate`, one for each of its two rows.

**Engine side.** Elastic/prism auto-generates ampersand spellings, and today they exclude
`chocolate` because it is the head noun of `Hot Chocolate`. A node that is literally named
`Chocolate` is its own label, so that exclusion must not hide it. This is checked at the batch
load, not in this repo.

The test is `tests/test_grocery_chocolate_node_298.py`.
