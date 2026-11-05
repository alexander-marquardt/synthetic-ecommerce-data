# Bronze sleeve bushings: a deep type from a maker's stock tables and ISO 2795 (gen#833)

`Motion Control & Fluid Power > Bushings > Bronze Sleeve Bushings` was a breadth row of two SKUs. It is now a modelled type, `product_types/motion/bronze_sleeve_bushings.py`, and its row is gone from `breadth_categories/`. `tests/test_type_bronze_sleeve_bushings.py` runs the per-type gates over it, plus its own: every published bushing is one size of the table its line reads, every inch catalogue row is the size its catalogue number says, and the ISO 2795 rows are the library's.

**Source.** The inch sizes of a bushing follow no dimensional standard. ASTM B438 and ASTM B584 specify the materials, and the sizes are the stock tables a maker prints. The inch spec space is therefore one public stock catalogue, and the metric spec space is the standard's own table:

| Table | Source | Sizes |
|---|---|---|
| Oil-impregnated sintered bronze, plain | Boston Gear P-1930-BG, Bost-Bronz, printed pages 138 to 140 | 461 |
| Oil-impregnated sintered bronze, flanged | Boston Gear P-1930-BG, Bost-Bronz, pages 141 and 142 | 122 |
| Cast bronze, plain | Boston Gear P-1930-BG, Bear-N-Bronz, pages 146 to 150 | 709 |
| Sintered, plain, normal series (mm) | ISO 2795:2014 Table 1 | 102 |
| Sintered, plain, thin-wall series (mm) | ISO 2795:2014 Table 1 and its footnote a | 80 |

The Boston Gear catalogue is the copy MRO Supply hosts (<https://documents.mrosupply.com/product_documents/MS/MS22/p-1930-bg_bearings.pdf>, read 2026-11-04). It states that Bost-Bronz conforms to ASTM B438 Grade 1 Type 2 and SAE 841 (page 136), and that Bear-N-Bronz is ASTM B584 alloy C93200 (page 145). The ISO table is transcribed into the standards library as `iso_2795_sintered_bushes_mm`, from the standard's public preview (<https://cdn.standards.iteh.ai/samples/63628/1366daadbd954e5cbb597474dc182af7/ISO-2795-2014.pdf>). The second-choice thin-wall outside diameters (34) and (36) are left out.

**Axes.** A line is one form (plain or flanged), one material and one unit system. It is one row of that table, which is one catalogue number prefix such as B46 (1/4" x 3/8") or one ISO inside diameter. Its SKUs are a window of the lengths that row is stocked in. The rows are drafted in a rotation that strides through each table, so even the default build spreads over the bores; every row is reached before any repeats. Metric flanged bushes are not built because the ISO preview stops before the flanged table, and spherical bushes are not built either. The decimal actual sizes the catalogue prints beside each nominal size are not published.

**Names.** `Bore Dia.` is the breadth row's size attribute and a census name, and it is the type's key attribute. `Outside Dia.` and `Length` are census names. `Flange Dia.` and `Flange Thickness` are the catalogue's D and E columns, which the census lacks; `names.NAME_EXCEPTIONS` cites the catalogue for both. `Type` is Plain or Flanged. `Material` is Oil-Impregnated Sintered Bronze or Cast Bronze.

**Standards.** A metric line claims ISO 2795, its table. An inch line claims its bronze's material specification: ASTM B438 for sintered bronze, ASTM B584 for cast bronze. Its provenance names the maker's stock table and says that no dimensional standard covers it.

**Price.** The census has no bushings, so the type's `PriceModel` has `measured=False` and is listed in `tests/test_price.py`'s `NOT_MEASURED`. Its level is hand-set near the breadth row's $2 to $15. Cast bronze is priced at twice sintered (`MATERIAL_FACTORS`); that factor is generated, not measured, and the module says so.

**Brands.** The type keeps the `motion` pool its breadth row had.

**Distinct specs.** A bushing has only its bore, outside diameter, length and two line facts, so two brands' lines can share a size. At the `--lines 39000` build, 0.835 of the type's SKUs are distinct specs, below the catalog's 0.90. `tests/test_catalog_brands_voice.py` gives it a `DISTINCT_SPEC_FLOOR` of 0.80.
