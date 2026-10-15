# Add a retail product type: the quick path (one file)

The common case is rows plus a drawing shape the kit already has. You edit ONE file.
The long reference for the industrial catalog is [adding-a-type.md](adding-a-type.md); read it
only when this page does not cover what you need.

1. Scaffold the spec (about 10 s):
   `uv run python scripts/new_type.py <key> --kind clothing|beauty --product-type "<Type>"`
   It writes `prototypes/retail_drawings/type_specs/<key>.py`: one `SPEC = TypeSpec(...)` with a
   working example row. `<key>` is lower-case words joined by underscores and is the file name.
   The row code is the key cut to six letters, with a digit at the end when a registered spec
   already builds that id (two keys that start `specimen_` would build one `BRD-SPECIM`);
   `--code ABCXYZ` sets it. A code a row still outside the registry uses is refused by the
   build, which names the id: give the new row another code.
2. Edit that file. Replace the example with the type's real rows:
   * a style is a `Row` (or an `LRow`, which adds a third SKU axis such as `sold_as`): its
     colors times its sizes are its SKUs; `path` is the category leaf, `shape` an existing
     drawing shape (`kit.SHAPES`), `attrs` the shopper attributes (`a(key, name, value)`);
   * `derivable=True` lets the scaled build draw more styles from the rows (a breadth type);
     False keeps them as templates only;
   * a brand no module states yet goes in `owners=(("Brand", "own"),)`;
   * a hand-authored text-match decoy (gen#294) is a `Decoy(class 1-7, query, policy, row)` in
     `decoys=`; it is never derived and never takes a color completion;
   * a clothing, footwear or lingerie type (Womens, Mens or Kids) carries its apparel decoy plan
     (gen#311) in the same file: the scaffold writes `apparel=ApparelPlan()` (three decoys per
     class; `ApparelPlan(family, per_class)` picks the word family `a` garment, `b` bra,
     `u` underwear, `s` shoe, `k` sock, and more per class). A type that should carry none says
     why: `apparel_exempt="<reason>"` in place of the plan. A beauty type carries neither.
   Worked examples: `type_specs/tracksuit.py` (clothing, an `LRow` with a SKU axis) and
   `type_specs/shampoo.py` (beauty, a derivable breadth type).
3. Check it: `uv run pytest tests/test_retail_type_specs_351.py` (every spec is held to the same
   checks: key equals file name, rows match the type and department, brands have an owner, codes
   are unique, also across specs, the documents meet the output standard).
4. Rebuild the figures (the build writes them; never edit by hand):
   `uv run python prototypes/retail_drawings/retail_figures.py`. It writes
   `golden-retail/stats.json` and `docs/retail-apparel-decoys.md` (the table of the apparel
   decoys, which now lists the new type's), and both go in the commit.

No edit to `scale.py`, `export.py`, `retail_figures.py`, `decoy_apparel.py`, the registry or any
test is needed, for a beauty type or a clothing one: the registry (`type_registry.py`) finds the
module and feeds the scaled build, the figures and the apparel decoys, and
`tests/test_retail_type_specs_351.py` fails a type that is registered anywhere but a spec file.
`tests/test_retail_type_specs_351.py::test_a_real_scaffolded_clothing_and_beauty_type_pass_the_apparel_census`
puts a scaffolded Kaftan and a scaffolded beauty type into the registry and runs the census of
gen#311 on them, so this claim is measured.

`type_specs/legacy_types.txt` lists the types still registered the old way. It only shrinks:
`type_registry.LEGACY_CEILING` is its exact length, so a line appended to it, or a type moved out
of it without lowering the number, reds `registration_problems`. A migration deletes the type's
line, lowers `LEGACY_CEILING` by one and removes the old row. A clothing type already planned
in `decoy_apparel` (Tracksuit) keeps its plan there: its decoy ids are numbered by place in that
plan, and moving it would renumber the 60 types after it. A new type is numbered by its key.

A new drawing shape (the rare case) is a function in the spec module, added with
`kit.register({"name": draw})`, as `kit_lowerbody.py` does for its shapes.

## Sizing rule for an issue

At most three types per issue. Split a bigger one: an agent that adds more than three types in
one run has stopped at its context ceiling before (#351: 10 beauty types, no PR).

## Metric

Tokens per type added (about 55K before this page), measured on the next three type issues.
