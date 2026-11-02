# Juice children, and labels read without their breadcrumb (gen#299)

Every juice sat in one leaf, `Food & Drink > Drinks > Juice`, with the flavour only in the title.
A search for "orange juice" matched the text, but no category was called "orange juice", so a
category policy had nothing to route it to.

**The children.** Juice is now a parent with one child per flavour, and each child's label names
the product on its own:

| Child | What sits in it |
| --- | --- |
| Orange Juice | JUI Smooth Orange and Orange with Bits; the decoys "Juice from Oranges, 1L" and "Blood Orange Juice, 1L" |
| Apple Juice | JUI Apple; the decoys "Cloudy Juice from Apples" and "Pressed Apple Juice, 1 L" |
| Pineapple Juice | JUI Pineapple |
| Coconut Water | JUI Coconut Water |
| Grape Juice | GJU Red Grape Juice and White Grape Juice |
| Smoothies | the decoy "Strawberries and Bananas Smoothie" |

Nothing sits on Juice itself. JUI and GJU stay one family each: `Family.children` maps a flavour
to its child, and `Family.path_of` adds that child to the family's path for each style. No draw
moves, so every title, id and image stays the same. The juice decoys of `decoy_rows.KINDS` are
now `orange_juice`, `apple_juice` and `smoothie`. Orange-flavoured soft drinks, chocolates and
sweets stay where they were, as decoys for "orange juice", and fresh oranges stay under
`Fresh Fruit > Citrus Fruit > Oranges`.

**Why not `Juice > Orange`.** Some grocers file juice this way. Here it would be wrong, because
the category vocabulary reads a label on its own: a leaf called `Orange` would capture the
shopper's "oranges" (the fruit) and "orange" (the color), and each of those searches would need
a policy to undo the routing.

**The guard.** Rule (d) of `tree_guard.py` (`bare_label_findings`) runs over the whole shipped
tree. It looks for a label that, after the plural rule, matches another node's label or a color
value. Such a label is refused when its products' titles read it in front of its parent's noun:
`Orange` under `Juice` holds "Smooth Orange Juice", so on its own that label means the fruit or
the color, not the product. `Orange Juice`, `Oranges` and `Accessories` all name what they hold,
so they pass. `LABEL_EXCEPTIONS` declares a label that still names its product, with the reason.
Its one entry is `Garden > Plants > Lavender`: a lavender plant is a lavender, and gen#509 made
that node so a shopper's "lavender" has a plant to route to. A declared label that stops firing is
itself a finding.

`tree_guard.named_nodes(paths, query)` returns the nodes a query names when each label is read on
its own (the same words, plural folded). On the shipped tree, "orange juice" names only
`Drinks > Juice > Orange juice`, and "oranges" names only the fresh-fruit `Oranges`.

`tests/test_grocery_juice_children_299.py` holds all of this. It also plants a bare `Orange` leaf
under Juice, and the guard must refuse it.
