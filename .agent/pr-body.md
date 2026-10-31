<!-- pr-body-for: branch=issue-455 -->

Closes #455

Builds on #577 and #684, which moved seven sports types and six soft-furnishing types into specs, and on #691, which deleted `legacy_types.txt`. That left one open Done-when: no retail source file over 1,000 lines. "Retail source" here means the `.py` files under `src/synthetic_ecommerce_data/domains/retail/`; tests and `scripts/` are out of scope.

Nine files were over the limit. Code moves verbatim into new sibling modules, and every importer keeps reading the original module, so no import elsewhere changes.

| File | Lines before | Lines after | Moved to |
| --- | --- | --- | --- |
| `breadth_rows.py` | 1615 | 62 | `breadth_row.py` (the `Row`) and one module per department: `breadth_toys`, `breadth_garden`, `breadth_gifts`, `breadth_cleaning`, `breadth_food`, `breadth_beauty`, `breadth_home`, `breadth_34` |
| `decoy_product_words.py` | 1441 | 601 | `decoy_word_kinds.py`, `decoy_word_table.py` |
| `house_styles.py` | 1423 | 684 | `house_marks.py` |
| `scale.py` | 1287 | 951 | `scale_text.py`, `scale_measures.py` |
| `kit_toys.py` | 1132 | 819 | `kit_toy_parts.py`, `kit_toys_craft.py` |
| `kit_footwear.py` | 1080 | 916 | `kit_footwear_last.py` |
| `grocery_rows.py` | 1048 | 285 | `grocery_model.py`, `grocery_families.py` |
| `decoy_apparel.py` | 1032 | 860 | `decoy_apparel_words.py` |
| `class_rows.py` | 1006 | 608 | `class_rows_apparel.py` |

- `tests/test_retail_source_lines_455.py` holds the limit. The file-size gate's 1,750 cap does not, so no `File-Size-Exception` line can lift it.
- `decoy_word_kinds.py` and `decoy_word_table.py` now hold registry lines, so they join `scripts/check_no_registry_append.py` with the same line shapes. Their rows are new to those paths, so the move commit carries a `Registry-Append:` trailer; no row was added.
- Mutation rows follow their anchors: 30 rows now name the module that holds their text.
- #743 is open and edits `scale.py`, only inside `_draw`, which stays there. It should rebase without a conflict on that file.

Guard: `tests/test_retail_source_lines_455.py::test_no_retail_source_file_is_over_the_cap`
Docs-Impact: `docs/file-size-budget.md` states the 1,000-line limit and the split; the retail pages that named a moved table now name its module.
Efficiency-Metric: largest retail source file 1,615 to 951 lines. Tokens per type added were not re-measured.

Claims
- No retail source file is over 1,000 lines: `test_no_retail_source_file_is_over_the_cap`.
- The cap counts the first line past it, in nested packages too: `test_the_cap_names_the_first_line_past_it`.
- An appended row or kind in either new decoy module is refused: `test_an_appended_registry_line_is_refused_and_names_the_new_file_form`.

Evidence
- Red commit 811290f0: `test_no_retail_source_file_is_over_the_cap` failed naming the nine files.
- The catalogue is unchanged. A SHA-256 over `scale.templates()` and over `scale.build()` at 0, 50,000 and 600,000 SKUs is identical on a clean `eddbeda9` worktree and on this branch: 12,199 templates, and 17,415 records at 600,000 SKUs. The mark list, every mark's SVG and the kit's shape list hash the same too.
- Every module-level value of the retail modules was compared the same way, sets order-insensitive. Of 153 names that left an original module, each is in a sibling with the same value. The other differences are absolute paths (`HERE` and its like) and `facet_leaves._FIBRES`, `_FIBRE_NAMES` and `_FIBRE`: the same words in another tie order among equal lengths, which cannot change a match. They come from a `sorted(..., key=len)` over a set.
