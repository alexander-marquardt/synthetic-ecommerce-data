"""The nested ``attributes.value`` carries a normalized keyword sub-field (#123).

Prism (elastic/prism#10648) reads the attribute-set key
``value_normalized_field: value.normalized`` and selects the verbatim spellings
on that sub-field with a folded term. It cannot add a normalizer to an existing
index, so the generator's mapping has to carry the sub-field and the normalizer.
The declared name is ``emit.VALUE_NORMALIZED_FIELD``: the mapping is built from
it, so the declaration and the mapped sub-field cannot drift apart.
"""

from __future__ import annotations

from synthetic_industrial_products.catalog import emit

PROPS = emit.NESTED_MAPPING["mappings"]["properties"]


def _value_columns() -> list[dict]:
    return [
        PROPS["attributes"]["properties"]["value"],
        PROPS["variants"]["properties"]["attributes"]["properties"]["value"],
    ]


def test_the_declared_name_is_the_one_prism_reads():
    assert emit.VALUE_NORMALIZED_FIELD == "value.normalized"


def test_the_declared_name_is_a_keyword_sub_field_of_the_value_column():
    sub = emit.VALUE_NORMALIZED_FIELD.split(".", 1)[1]
    for column in _value_columns():
        assert column["type"] == "keyword"
        assert column.get("fields", {}).get(sub) == {
            "type": "keyword",
            "normalizer": emit.VALUE_NORMALIZER,
        }


def test_the_normalizer_lowercases_and_folds_ascii():
    settings = emit.NESTED_MAPPING.get("settings", {}).get("analysis", {}).get("normalizer", {})
    assert settings.get(emit.VALUE_NORMALIZER) == {
        "type": "custom",
        "filter": ["lowercase", "asciifolding"],
    }
