# Retail SKU and product ids name the product (gen#626)

A partial reload writes a SKU as the Elasticsearch `_id`. Until gen#626 a SKU was numbered by
its place in the style (`<product_id>-001` on), and a derived style's id by its place in the
build, so adding a row to one range moved every id after it: across two exports 51K SKUs moved
and 14.7K then named a different product, and a partial reload overwrote one product with
another.

## The rule

- A SKU id is `<product_id>-<8 hex>`: the hash of the SKU's own axes (size, color and the other
  values that tell it from its siblings). Price, stock and the ingredient lists are not axes
  (`stable_ids.NOT_AXES`), so a repricing keeps the SKU.
- A style derived from a template is `<prefix>-<12 hex>`: the hash of the template's id and
  the signature (the values its title shows, and the hero color family). Whether a style exists
  does not depend on how many styles were drawn before it: each template has its own clock
  (`scale._Lane`), and the clocks are merged by time.
- A collision raises `stable_ids.IdCollision` at generation time. The id is never bumped to fit.
  A derived draw whose SKUs would merge is refused, as a text contradiction is, and drawn again.
- The visible prefix (`JEA-`, `BRD-`) is kept.

Guards: `tests/test_retail_stable_ids_626.py`.

## What still moves, and what is out of scope

- The table generators that count (their product ids run `WD-0001`, `DPT-0001`, ...) keep their
  product ids by position within their own table; their SKUs are hashed like the rest.
- A bigger pool, a new brand or the near-duplicate check (`used`, `titles`) can change a
  neighbour's pick. The build holds the draws to a hash of the style, so only the styles that
  share a leaf and a type with the change can differ.
- The industrial side (`core/ids.py`, `IdMinter`) is a different scheme and is not changed here.
- The ceiling figures (`golden-retail/stats.json`) changed with the derived styles.
- Near the ceiling the derived department mix is skewed against the targets: the fast clocks of
  small departments run out first. `DEPARTMENT_RATE` in `scale.py` holds the rates, calibrated to
  `DEPARTMENT_SHARE` at today's templates; when a template changes a department's share
  (`test_the_department_rates_give_the_department_shares` fails) recompute them.

## One-off migration: the last positional ids

The last commit that numbered SKUs by position is `759f24c4`. A load that holds ids from it needs
the mapping once; the next load after that is stable.

For a template product (every authored style) the old id is its place in the style's `skus`
list, and the list order did not change, so the pair is:

```
.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, "src/synthetic_ecommerce_data/domains/retail")
import scale
print("old_sku,new_sku")
for r in scale.templates():
    for n, s in enumerate(r["skus"], 1):
        print(f"{r['product_id']}-{n:03d},{s['sku']}")
PY
```

Run it, save the output, and rename or delete the old `_id`s with it. A derived style has no
mapping: the old derived ids were positional (`<prefix>-<serial, 6 digits>`), and the derived set is drawn
again from the templates, so the first load after this change is one full reload of the derived
styles (delete what the mapping does not name, then load).
