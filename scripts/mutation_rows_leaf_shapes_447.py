"""Mutation rows for the leaf shapes of gen#447, in their own file.

Each row plants one defect in ``leaf_shapes``, its wiring or the swatch and decoy edits, and names
the test that must go red. ``mutation_rows_garden_hose.ALL`` carries them to ``mutation_check.py``
as rows named ``leaf shapes: ...`` (``--only "leaf shapes:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501  (a row quotes the whole line it breaks)
from __future__ import annotations

_R = "prototypes/retail_drawings"
_T = "prototypes/retail_drawings/test_shape_honesty.py"
_LS = "leaf_shapes.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the bomber leaf is drawn as a coat again",
        _LS,
        'Rule("bomber", "bomber_jacket",',
        'Rule("bomber", "coat",',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and PLT-DA02102"',
        "a bomber jacket is drawn as a bomber",
        _R,
    ),
    (
        "the polo keeps the tee's sleeve",
        _LS,
        '{"kind": "polo", "neckline": "polo", "sleeve": "short"}',
        '{"kind": "polo", "neckline": "polo", "sleeve": "long"}',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and BRD-MDPS240"',
        "a polo is drawn with a polo collar and a short sleeve",
        _R,
    ),
    (
        "the long sleeve top is drawn short",
        _LS,
        '(), {"sleeve": "long"}),',
        '(), {"sleeve": "short"}),',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and PLT-DSL029"',
        "a long sleeve top is drawn with long sleeves",
        _R,
    ),
    (
        "the cargo trousers lose their pockets",
        _LS,
        '{"cargo": "yes", "style": "chino"}',
        '{"style": "chino"}',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and BRD-NXMET041"',
        "cargo trousers are drawn with flapped pockets",
        _R,
    ),
    (
        "the pyjama shorts keep their pockets",
        _LS,
        '"style": "sweat", "pocket": "no"}',
        '"style": "sweat"}',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and PLT-DA50603"',
        "pyjama shorts are drawn plain",
        _R,
    ),
    (
        "the knee boots are drawn as ankle boots",
        _LS,
        '(), {"kind": "knee_boot"}),',
        '(), {"kind": "ankle_boot"}),',
        f'{_T} -k "a_reported_product_is_drawn_as_its_title and PLT-DA36301"',
        "knee high boots are drawn to the knee",
        _R,
    ),
    (
        "apply sets no shape",
        _LS,
        '        drawing["shape"] = rule.shape\n',
        "",
        f'{_T} -k "a_listed_leaf_is_drawn_as_its_rule and puffer"',
        "apply sets the rule's shape on the template",
        _R,
    ),
    (
        "the rules are matched by leaf and type both",
        _LS,
        'in self.leaves or tpl["product_type"] in self.types',
        'in self.leaves and tpl["product_type"] in self.types',
        f'{_T} -k "a_listed_leaf_is_drawn_as_its_rule and pyjama"',
        "a rule applies to a leaf or to a product type",
        _R,
    ),
    (
        "the rules are applied after the decoys clone",
        "scale.py",
        "    body = leaf_shapes.apply(body)  # gen#447: a bomber is drawn as a bomber, before decoys clone it\n",
        "",
        f'{_T} -k "a_listed_leaf_is_drawn_as_its_rule and bomber"',
        "scale.templates applies the leaf shapes",
        _R,
    ),
    (
        "a Boxers decoy clones a brief exemplar",
        "decoy_apparel.py",
        "            and _names_its_drawing(d)\n",
        "",
        f'{_T} -k "a_decoy_titled_boxers"',
        "a Boxers decoy is drawn as boxers",
        _R,
    ),
    (
        "a Checked blazer is plain",
        "mens_depth_rows.py",
        'checked = leaf.pattern == "check" or any(m[0] == "pattern" for m in more)',
        'checked = leaf.pattern == "check"',
        f'{_T} -k "checked_or_striped"',
        "a Checked title carries a gingham swatch",
        _R,
    ),
    (
        "a Striped polo is plain",
        "mens_depth_rows.py",
        '            elif detail == "Striped":',
        "            elif False:",
        f'{_T} -k "checked_or_striped"',
        "a Striped polo carries a stripe swatch",
        _R,
    ),
    (
        "the cargo pockets are not drawn",
        "kit_garments.py",
        '        out += _cargo_pockets(oL)\n',
        "",
        f'{_T} -k "a_new_garment_part_is_drawn_by_its_kit_function"',
        "cargo trousers draw flapped pockets",
        _R,
    ),
    (
        "the polo collar is not drawn",
        "kit_garments.py",
        '        out += _polo_collar(paint)\n',
        "",
        f'{_T} -k "a_new_garment_part_is_drawn_by_its_kit_function"',
        "a polo draws a collar and placket",
        _R,
    ),
    (
        "the puffer loses its baffles",
        "kit_outerwear.py",
        '        _line(baffles, 1.8),\n',
        "",
        f'{_T} -k "a_new_garment_part_is_drawn_by_its_kit_function"',
        "a puffer draws quilted baffles",
        _R,
    ),
    (
        "the shirt dress loses its placket line",
        "kit_garments.py",
        '        _line("M200,100 L200,364"),\n',
        "",
        f'{_T} -k "a_new_garment_part_is_drawn_by_its_kit_function"',
        "a shirt dress draws a buttoned placket",
        _R,
    ),
]
