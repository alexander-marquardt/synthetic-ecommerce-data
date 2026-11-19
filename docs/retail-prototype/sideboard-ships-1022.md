# A sideboard ships with products of its own (gen#1022, slice 5)

Slices 1 to 4 of gen#1022 drew the home and furniture types the issue names, and none of them had
a product in the catalogue. This slice meets the issue's Done-when 3: one of those types ships in
the generator build with products of its own, and passes the product-split and non-copying audits.

The type is `sideboard`, drawn by slice 2's `kit_storage_furniture` shape
([render and finishes](render-and-finishes-1022.md)). Its spec is
`src/synthetic_ecommerce_data/domains/retail/type_specs/sideboard.py`. The registry finds it,
so the retail templates, the scaled build and the ceiling build the release publishes all carry
its products.

## The products

Every row is the generator's own. Its brand comes from the brand book, and its title,
description, price, colors and size are written in the spec. Nothing comes from a benchmark.

| Product id | Title | Brand | Doors | Drawers | Base | Material | W x H x D cm | Colors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `BRD-SDBOK3` | Oak Sideboard with 3 Doors and 3 Drawers | Brackenmere Home | 3 | 3 | Tapered legs | Oak | 160 x 80 x 45 | Natural, White, Black |
| `BRD-SDBWN2` | Walnut Sideboard with 2 Doors | Larchwood Living | 2 | 0 | Hairpin legs | Walnut | 120 x 75 x 40 | Dark Brown, Grey |
| `BRD-SDBPN4` | Painted Pine Sideboard with 4 Doors | Emberly Home | 4 | 0 | Plinth | Pine | 180 x 85 x 45 | White, Green, Navy |
| `BRD-SDBMG4` | Mango Wood Sideboard with 4 Drawers | Cobble & Kiln | 0 | 4 | Tapered legs | Mango Wood | 100 x 85 x 40 | Natural, Black |
| `BRD-SDBAS1` | Ash Sideboard with 1 Door and 2 Drawers | Brackenmere Home | 1 | 2 | Plinth | Ash | 110 x 80 x 42 | Natural, Grey |

`main_colors.complete` adds any missing main color as further SKUs of a style, as it does for
every color-bearing type.

- **What the picture draws.** The doors, the drawers and the base are the shape's `doors`,
  `drawers` and `legs` params. Each is also a structured attribute: `door_count`,
  `drawer_count` (counts, unit `C62`) and `base_style`. A SKU's picture is the style's drawing
  in that SKU's color.
- **What the SKUs vary.** Only the color. The size is stated once per style, as `item_width`,
  `item_height` and `item_depth` in centimeters.
- **Derivation.** The rows are templates only (`derivable` False), so the build's seeded
  derivation, and every product id it makes, is unchanged.

## The audits

`tests/test_sideboard_ships_1022.py` reads the ceiling build (`tests/retail_ceiling.py`) and
checks the following:

- **The build carries them.** Every spec row is a product in the templates and in the ceiling
  build, under Home > Furniture > Sideboards, and the products meet the output standard
  (`core.standard.check_catalog`).
- **The picture matches the product.** Each SKU's picture is the `sideboard` shape. It draws
  exactly the stated number of door and drawer fronts, the stated base, and the SKU's color.
  Each style draws a picture of its own.
- **Product split.** A product's SKUs carry nothing but their color, and no color is sold twice.
  No two products of one brand differ only in color. A planted twin, and a SKU that carries a
  size, are each caught.
- **Non-copying.** No SKU's full attribute tuple, with or without its color, is a reference tuple
  hash in `core.noncopy`, and no SKU code is a reference SKU. A planted reference tuple and a
  planted reference SKU are each caught.

## What comes next

More of the new home types can ship the same way: one spec file per type, with its own rows on
its kit shape. The picture-manifest products ([slice 3](picture-products-1022.md)) stay a
separate entry point for the combined demo, and no generator build reads a manifest.
