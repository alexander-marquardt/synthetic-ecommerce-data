# Sports & Outdoors: the tree, its filters and what is not built (gen#290)

The department is built by `prototypes/retail_drawings/sports_rows.py` (gen#265, first increment,
PR #288). This note records, per leaf, what a shopper filters on and whether a reference
retailer's tree was compared; and, per type not yet built, where it is scheduled.
`tests/test_retail_sports_tree_note_290.py` keeps both tables equal to the rows: a new leaf
without a line here, or a line for a leaf that is gone, fails it.

## Leaves

The shape is department > family > (group) > leaf. The guidance on gen#265 asked for the shape of
large sports retailers' trees and for their leaves to be noted. **No leaf was checked against a
retailer's tree**: the author of the first increment had no tree to compare with, so the last
column reads `none` on every line rather than claiming a match. What does trace to a source is
the filter: the guidance on gen#265 named tent capacity and season rating (camping), mat
thickness (yoga) and weight (dumbbells), and those leaves carry them. A leaf whose filters have
no guidance example says `none` there too.

| Leaf | Filters (export keys) | Guidance example | Retailer tree |
| --- | --- | --- | --- |

Leaf depth is mixed on purpose for now: Dome Tents, Tunnel Tents, Yoga Mats, Dumbbells and
Kettlebells sit under a group (four levels), Sleeping Bags, Camping Chairs and Foam Rollers sit
directly under their family (three). The Yoga group has one leaf until yoga blocks and straps
arrive (below), and a group with one leaf is kept rather than flattened so those leaves land
beside it. The tree guard's rules hold on the subtree either way.

## Not built

Every type the issue listed that the first increment did not ship has a disposition. "Not
reached" is not one: it is scope, not a reason. A type is either scheduled in an open issue or
carries a reason.

| Type | Family | Disposition |
| --- | --- | --- |
