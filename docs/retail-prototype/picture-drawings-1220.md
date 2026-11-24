# One drawing for every row of a picture manifest (gen#1220)

`synthetic_ecommerce_data.picture_drawings` draws a whole [picture manifest](picture-products-1022.md#the-picture-manifest)
in the `unbranded` finish: step 1 of #1022. It reads the manifest and nothing else, and imports no
product writer.

```sh
uv run python -m synthetic_ecommerce_data.picture_drawings MANIFEST OUT_DIR
```

It writes `OUT_DIR/images/<image id>.svg`, one file per row:

- a row with a `type` is drawn as that type, one of the 28 types of `drawings.PROPORTIONS`, with
  its color, parts and proportions;
- a fallback row (`image_id` and `department`) is drawn as the shape that stands for its department
  (`picture_manifest.DEPARTMENTS`), in grey. A fallback row names a department instead of a type, so
  no row is left without a file.

| Department | Shape |
| --- | --- |
| `furniture` | `armchair` |
| `storage` | `storage_box` |
| `bedding` | `bed_pillow` |
| `bath` | `bath_towel` |
| `kitchen` | `saucepan` |
| `decor` | `ornament` |
| `lighting` | `table_lamp` |
| `rugs` | `floor_mat` |
| `hardware` | `hook_rail` |
| `garden` | `watering_can` |
| `kids` | `wooden_toy` |
| `pets` | `pet_bed` |
| `other` | `box` |

The words are the generator's own. Whoever writes the manifest maps its products to them, and that
map stays on its side.

## The report

It prints rows, files (counted in the directory), own-type drawings, fallbacks, the rows this run
drew, and a count per type and department. The exit status is 1 when files are not equal to rows
(a stray picture in the directory).

## Repeating and resuming

A picture's bytes come from its own row alone, so the same manifest gives the same files. A file is
moved into place whole, so a stopped run leaves no half-written picture. The next run draws only the
rows with no picture.

`OUT_DIR/run.json` holds the digest of the manifest file and of the renderer (each type and
department drawn at its defaults). A run on another manifest or renderer, or into a directory
holding pictures of no run, is refused: draw into a new directory.

## Cost

42,994 rows of random specs in the manifest's vocabulary (no benchmark data) took 18 s in one
process and 212 MB on disk. A second run over the finished directory took 2 s.

## What the tests pin

`tests/test_picture_drawings_1220.py` runs on one row per type and one per department:

- every row has a file, fallbacks are counted, and a second run gives the same bytes;
- a stopped run, and a half-written picture, are gone on from by drawing only what is missing;
- a directory of another manifest, renderer or no run is refused;
- every value of every part of every type draws, in every combination;
- a fallback row takes no field but its two, and no picture holds text;
- the run imports no product writer.
