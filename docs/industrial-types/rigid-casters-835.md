# Rigid casters: a deep type from a maker's stock charts (gen#835)

`Material Handling & Storage > Casters & Wheels > Rigid Casters` was a breadth row of two SKUs. It is now a modelled type, `product_types/material_handling/rigid_casters.py`, and its row is gone from `breadth_categories/`. `tests/test_type_rigid_casters.py` runs the per-type gates over it, plus one of its own: every published tread, height and load is its chart row, never scaled from a neighbour.

**Source.** No dimensional standard covers a caster (ANSI/ICWM writes a caster's performance tests, not its sizes), so a caster claims none. The spec space is one public stock catalogue: the Durable Superior Casters "Industrial, Food Service, Institutional" catalogue 2017-2018, as Caster Depot republishes it (<https://www.casterdepot.com/media/pdf/2016-durable-catalog_cd.pdf>, read 2026-11-04). Each rigid plate series it prints is one `Series` in the module:

| Series | Printed pages | Wheels | Tread |
|---|---|---|---|
| 11/12 General Duty | 21 | 2", 2-1/2" | 15/16", 1-1/16" |
| 13/14 Light-Medium Duty (plate) | 25 to 27 | 3" to 5" | 1-1/4" |
| 43/44 Medium Heavy Duty | 70 to 73 | 4" to 8" | 2" |
| 43/44 Medium Heavy Duty | 70 to 73 | 6" to 10" | 2-1/2" |

**Axes.** Each series table gives a wheel diameter its tread width and the caster's overall height. Each table row gives a wheel type its load per caster and the bearings it is offered with. A line is one wheel material and one bearing in one series; its SKUs are the wheel diameters the table offers that pair on, so no line offers a wheel the maker does not. Stem mounts, swivel casters and brakes are not built; the plate's size and bolt pattern are not published, as the census has no name for either.

**Names.** The census keys the type on `Wheel Dia.`, but the key `wheel_dia` is retired for `diameter` (`retail.rules.MERGED_AWAY`), so the wheel diameter is published as `Wheel Diameter`. `Tread Width` and `Bearing Type` are the catalogue's column headings. The wheel material is `Material`, the one name every type gives what it is made of; the catalogue calls it "Wheel Type". `Overall Height` and `Load Capacity` are census names; a load is in lbf, as every load in the catalog is. `names.NAME_EXCEPTIONS` cites the catalogue for the three names the census lacks, and `names.TYPE_SPECIFIC` admits `Wheel Diameter`, which carries the path's own noun.

**Values.** A wheel type is published under a generic name: "Mold-On Rubber" (page 133, a vulcanized rubber tread on a cast iron core) reads Rubber on Cast Iron, and "Polyon" (page 143, a polyurethane tread bonded to a cast iron core) reads Polyurethane on Cast Iron. Trademarked wheels are not built. The bearings are the tables' own names: Plain Bore, Sleeve, Ball, Precision Ball and Roller.

**Price.** The type moves from `price.BREADTH_CENSUS` to `price.DEEPENED_CENSUS` with its census row of 157 priced rows, so its p50 and p90/p10 are scored at both sizes. Its model's level is hand-fitted to the census. The per-wheel-material factors that spread it (`WHEEL_FACTORS`) are generated, not measured, and the module says so.

**Brands.** The type keeps the `hand_tool` pool its breadth row had. The five pools are fixed (`core.brands.FAMILIES`) and none is for material handling; a sixth is a core change outside this issue. The `hand_tool` product words read correctly in a caster title. The `motion` pool's "Replacement" would claim a fit that no field backs.
