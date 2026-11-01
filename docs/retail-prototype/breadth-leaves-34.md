# Plain breadth leaves (gen#34)

Three leaves of one or two plain products, so a plain word gains a category and that category's
facets. Breadth is not depth: nothing here grows into a range.

| Leaf | Spec | The word it joins |
|---|---|---|
| Home / DIY & Tools / Picture Hooks | `type_specs/picture_hook.py` | `hook` |
| Home / Home Accessories / Plant Pots | `type_specs/plant_pot.py` | `pot` |
| Electronics / Accessories / Batteries | `type_specs/battery.py` | `batteries` |

They were picked from the products no retail title named, by how many other leaves their word
already reaches in a title or description: a query for a word that crosses many types shows the
union of their facets.

- The three shapes are in `kit_plain_goods.py`. A battery reads the cell its row states
  (`battery_size`), so an AAA is the thinner cell; the proportions are the real cells' (IEC 60086).
- Each product is colorless: its color is its material or its casing, not a choice a shopper makes.
- A pack's count comes from its `pack_size` attribute, so `pack_copies` draws that many.

`tests/test_retail_breadth_leaves_34.py` holds each leaf to one or two products, each title to its
plain word, and each shape to a text-free drawing that its parameter changes.
