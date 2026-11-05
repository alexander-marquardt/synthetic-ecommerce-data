# ER collets: a deep type from the ER collet tables (gen#831)

`Tool Holding > Collets > ER Collets` was a breadth row of two SKUs. It is now a modelled type, `product_types/cutting_tools/er_collets.py`, and its row is gone from `breadth_categories/`. `tests/test_type_er_collets.py` runs the per-type gates over it, plus checks of its own: every published size, clamping range, outside diameter, length and runout is its table row's, every series and class is built, and the breadth row's inch sizes are still built. The drill bushing, the other half of gen#831, is a separate pull request.

**Source.** ISO 15488 (DIN 6499 form B) is sold, and no public copy was found, so the tables are a maker's: the REGO-FIX Tool Corporation *ER System* product catalog, the catalogue of the maker of the original ER collet (<https://br.rego-fix.com/system/files/docs/2017-08/RFTC_ER_Catalog121616_Linked.pdf>, read 2026-11-04). Its tables carry the headings DIN 6499-B and ISO 15488. The rows are in the standards library as `iso_15488_er_collets`. Each was copied from the catalogue's text layer by a script, not retyped:

| Table | Printed page | What it gives |
|---|---|---|
| ER standard and ER-UP collets | 87 to 95 | each series' metric and inch nominal bores, each with its clamping range in mm and in inches: 269 rows, ER 8 to ER 50 |
| ER collets dimensions | 161 | each series' outside diameter D1 and length L; the ER 16 collets of 9.5 to 10 mm are 26 mm long |
| Runout TIR of ER standard and ER-UP collets | 83 | the DIN 6499 runout by clamping diameter (0.015 to 0.025 mm), and the maker's 0.010 mm (ER standard) and 0.005 mm (ER-UP) |

A collet grips one collapse below its nominal bore: 0.5 mm for ER 8 and ER 11 and for the 1 and 1.5 mm collets of ER 16 to ER 25, 1 mm for the rest of ER 16 to ER 40, and 2 mm for ER 50. ER 50 has no inch row. A line claims ISO 15488 and DIN 6499, the standards the catalogue's tables are printed under, and its provenance names that table for every dimension.

**Axes.** A line is one brand's collets of one series (ER 8, 11, 16, 20, 25, 32, 40 or 50), in one unit system, in one accuracy class. Its SKUs are a run of that series' nominal bores. The three classes are the runout columns of the page 83 table: `Standard` holds the DIN 6499 runout of the collet's clamping diameter, `Precision` holds 0.010 mm, and `Ultra Precision` holds 0.005 mm. The 15 series and unit-system ladders and the 3 classes are rotated so that every ladder is built within 15 lines, every class within 3, and every pair within 45. The sealed (ER-DM), tapping (ER-GB, PCM ET1) and microbore (ER-MB) collets are other tables of the same catalogue and are not built.

**Names.** The series is published as `Type` (`ER32`), the name the breadth row gave it. The census's `Collet Series` is refused, because it repeats the leaf's own noun, as the lock nut's `Nut Style` was. The other names are census names: `Size` (the nominal bore, the breadth row's `size_attr` and the price key), `Grip Range` (the clamping range), `Concentricity Tolerance` (the runout), `Outside Diameter` (D1), `Overall Length` (L), `Class` and `Material`.

**Material.** The catalogue names no material. Collets are hardened spring steel (65Mn or 50CrV4), an alloy steel, so a collet is published as `Alloy Steel`, a material that already has a drawing fill, a hatch and a price factor.

**Price.** The census has no ER collets, so the model is `measured=False`: generated, not measured. A standard-tier, standard-class 1/2" collet is anchored at about 22 USD. A 0.25 log-log slope on the nominal bore prices a 36 mm ER 50 collet at about 2.4 times a 1 mm ER 11 collet. The class multiplies the price (`CLASS_FACTORS`): 1.0, 1.4 and 2.0.

**Brands.** The type keeps the `cutting_tool` pool its breadth row had. Collets are sold beside end mills and drills by the same tooling makers.

**Sizes.** A line's SKUs are a run of neighbouring bores. Its run starts at the breadth row's sizes (1/8", 3/16", 1/4", 3/8" and 1/2") before any other bore. Each inch ladder begins at a different one of the five, so the default build of about two lines per ladder reaches them all.

**Share.** 0.015: 62 SKUs over 39 products at the default build, and 1,015 over 559 at `--lines 39000` (fill 559 of 585 lines, 96%).
