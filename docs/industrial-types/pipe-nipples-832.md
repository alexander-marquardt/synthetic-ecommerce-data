# Pipe nipples: a deep type from their size standards (gen#832)

`Hose, Tube, Fittings & Valves > Pipe Fittings > Hex Pipe Nipples` was a breadth row of two SKUs. It is now a modelled type, `product_types/motion/hex_pipe_nipples.py`, and its row is gone from `breadth_categories/`. `tests/test_type_hex_pipe_nipples.py` runs the per-type gates over it, plus three of its own: every hex nipple is a row of the maker's hex chart, every close and barrel nipple is an ASTM A733 size and length in its schedule, and every kind is built. The key and the leaf are unchanged (docs/adding-a-type.md), so the leaf named for hex nipples also holds the close and barrel nipples.

**Sources.** A pipe nipple is a short length of pipe threaded male NPT (ASME B1.20.1) at both ends. It comes in two families:

| Family | Kinds | Read from |
|---|---|---|
| Close and barrel (ASTM A733) | Close, Barrel | The library table `astm_a733_pipe_nipples`, transcribed from two Boshart Industries sheets that state conformance to ASTM A733, ASME B36.10M and ASME B1.20.1: the Schedule 40 stainless booklet (<https://images.boshart.com/boshartimages/2025/09/Booklet-Stainless-Steel-pipe-nipples-ready-cut-pipeV3-REV-2.pdf>) and the Schedule 80 black steel sheet (<https://images.boshart.com/boshartimages/2024/01/BLHNSch80_BlackSteelPipeNipples_technicalsheet.pdf>), read 2026-11-04 |
| Hex (no standard) | Hex, Hex Reducing, Hex Long | The Swagelok "Pipe Fittings" catalogue MS-01-147 R10, pages 4 and 5 (<https://acomee.com.mx/catalogos/catalogoss1/SWAGELOK%20PIPE%20FITTINGS.pdf>, read 2026-11-04) |

The A733 table holds 12 sizes, 1/8 in to 4 in. Each size has its close length, outside diameter, Schedule 40 and 80 walls, and the lengths from 1-1/2 in to 12 in that each sheet's part-number grid offers it in. A length is offered only where the grid prints a part number. Nothing was interpolated. A733's own tables were not read (the standard is sold), so no line claims it.

**Axes.**
- Close and barrel lines come in Schedule 40 (black steel, galvanized steel, 304 and 316 stainless) and Schedule 80 (black steel only, the one material the Schedule 80 sheet covers). A steel Schedule 40 line is stocked on the stainless sheet's lengths, because A733's dimensions do not depend on the material.
- A close line's SKUs are the sizes at their close lengths.
- A barrel line is one size, and its SKUs are the lengths that size is offered in.
- Hex lines come in 316 stainless, brass and zinc-plated steel. Their SKUs are the chart's rows. Each row's pressure rating is the one the chart gives that material: the chart prints one rating for stainless and carbon steel and another for brass.
- Not built: the 1/16 in hex rows, the heavy-wall and ISO-thread hex variants, ready-cut pipe over 12 in, and the sheets' theoretical burst pressures.

**Names.**
- `Pipe Size` is the census's key dimension for the type. The breadth row's `Size` is not used.
- `Length`, `Outside Dia.`, `Hex Size`, `Thread Type`, `Material`, `Finish` and `Type` are census names.
- `Pressure Rating (psi)` is a reference spec-table name.
- `Schedule` is in neither: `names.NAME_EXCEPTIONS` cites A733 and the sheets for it.

**Price.** The type moves from `price.BREADTH_CENSUS` to `price.DEEPENED_CENSUS` with its census row of 81 priced nipples, so its p50 and p90/p10 are scored at both sizes. The model's level is hand-set against the census. Its pipe-size slope is cut from the census's 0.826 to 0.45: the census nipples span three size cells, and at 0.826 sizes from 1/8 in to 4 in would spread the price wider than the census p90/p10. The material factors and the length slope are generated, not measured, and the module says so.

**Brands.** The type keeps the `motion` pool its breadth row had.
