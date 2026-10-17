"""Mutation rows for the one-key-per-concept guard and its fixes (gen#227), kept out of
``mutation_check.py``.

The first block plants a defect in ``key_guard.py``, the second puts one fixed product back on its
old key. ``mutation_check.py`` turns them into ``Mutation`` rows named ``attribute keys: ...``
(``--only "attribute keys:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_T = "tests/test_retail_attribute_keys_227.py"
_R = "prototypes/retail_drawings"
_LAMP = (
    '{"key": "item_height", "name": "Item height", "value": "46", '
    '"unit_code": "CMT", "value_canonical": 460.0}'
)
#: The coffee table's entry in furniture_rows.py, up to its closing parenthesis.
_FEATURE = (
    '    feature = (("storage_feature", "Storage feature", storage.replace("_", "-").title()),'
)

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a key holds a concept's word only when it is the word",
        "key_guard.py",
        'return word in key.split("_")',
        "return key == word",
        f'{_T} -k "second_height_key_on_a_variant"',
        "height_cm holds the word height",
        _R,
    ),
    (
        "a second key for a concept is no finding",
        "key_guard.py",
        "        extra = [k for k in held if k != c.winner]\n",
        "        extra = []\n",
        f'{_T} -k "second_height_key_is_a_finding"',
        "a concept carried by two keys is reported",
        _R,
    ),
    (
        "a concept's exceptions are not honoured by the finding",
        "key_guard.py",
        "        held = sorted(k for k in keys if _holds(k, c.word) and k not in c.exceptions)\n",
        "        held = sorted(k for k in keys if _holds(k, c.word))\n",
        f'{_T} -k "declared_exception"',
        "heel_height is not a second item height",
        _R,
    ),
    (
        "a concept no document carries under its winner is no finding",
        "key_guard.py",
        "        if c.winner not in held:\n",
        "        if False:\n",
        f'{_T} -k "no_document_carries_under_its_winner"',
        "a winner that vanished is reported",
        _R,
    ),
    (
        "the metric counts a declared exception",
        "key_guard.py",
        "sum(1 for k in keys if _holds(k, c.word) and k not in c.exceptions)",
        "sum(1 for k in keys if _holds(k, c.word))",
        f'{_T} -k "metric_counts"',
        "keys per concept leaves another concept out",
        _R,
    ),
    (
        "an item_ prefix is part of a stem",
        "key_guard.py",
        'return _UNIT_SUFFIX.sub("", key.removeprefix("item_"))',
        'return _UNIT_SUFFIX.sub("", key)',
        f'{_T} -k "one_stem_are_a_finding"',
        "height and item_height are one stem",
        _R,
    ),
    (
        "a unit suffix is part of a stem",
        "key_guard.py",
        'return _UNIT_SUFFIX.sub("", key.removeprefix("item_"))',
        'return key.removeprefix("item_")',
        f'{_T} -k "one_stem_are_a_finding"',
        "weight and weight_kg are one stem",
        _R,
    ),
    (
        "a text key joins a measured one in a stem",
        "key_guard.py",
        '                if not measured or entry.get("unit_code") is not None\n',
        "                if True\n",
        f'{_T} -k "text_key_that_shares_a_stem"',
        "a garment's width is not a dimension",
        _R,
    ),
    (
        "a floor lamp's height goes back to height",
        "lighting_rows.py",
        '_cm("item_height", "Item height", 190)',
        '_cm("height", "Height", 190)',
        f'{_T} -k "test_a_measured_height_is_an_item_height and Floor"',
        "a floor lamp's height is item_height",
        _R,
    ),
    (
        "the committed table lamp sample's height goes back to height",
        "samples.ndjson",
        _LAMP,
        _LAMP.replace('"item_height", "name": "Item height"', '"height", "name": "Height"'),
        f'{_T} -k "no_committed_sample and samples.ndjson"',
        "a sample table lamp's height is item_height",
        _R,
    ),
    (
        "the committed table lamp sample's 46 cm is 46 mm",
        "samples.ndjson",
        _LAMP,
        _LAMP.replace("460.0", "46.0"),
        f'{_T} -k "canonical_in_millimetres and samples.ndjson"',
        "a centimetre height is ten millimetres per centimetre",
        _R,
    ),
    (
        "the olive tree's height goes back to height",
        "distractors.py",
        '(("item_height", "Item height", "60", "CMT"),)',
        '(("height", "Height", "60", "CMT"),)',
        f'{_T} -k "test_a_measured_height_is_an_item_height and Gift"',
        "an olive tree's height is item_height",
        _R,
    ),
    (
        "a doll's height goes back to height_cm",
        "toys_rows.py",
        '("item_height", "Item height", str(cm), "CMT", cm * 10.0)',
        '("height_cm", "Height", str(cm), "CMT", cm * 10.0)',
        f'{_T} -k "test_a_measured_height_is_an_item_height and Dolls"',
        "a doll's height is item_height",
        _R,
    ),
    (
        "a tree's height goes back to height",
        "export.py",
        '"height": ("item_height", "Item height", None),',
        '"height": ("height", "Height", None),',
        f'{_T} -k "test_a_measured_height_is_an_item_height and Christmas"',
        "a tree's feet are item_height",
        _R,
    ),
    (
        "a footstool's storage goes back to storage_compartment",
        "sofa_rows.py",
        '("storage_feature", "Storage feature", "Lift-Top" if storage else "None")',
        '("storage_compartment", "Storage compartment", _yes(storage))',
        f'{_T} -k "storage_is_one_kind and Footstools"',
        "a footstool's storage is storage_feature",
        _R,
    ),
    (
        "a coffee table with no storage carries no storage_feature",
        "furniture_rows.py",
        _FEATURE + ")\n",
        _FEATURE + ') \\\n        if storage != "none" else ()\n',
        f'{_T} -k "storage_is_one_kind and Coffee"',
        "None means no storage",
        _R,
    ),
]
