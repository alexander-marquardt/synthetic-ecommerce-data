"""Collision-word depth (gen#273): each sense of a demo collision word holds dozens of styles.

``collision_words.count`` measures, per word, the Food & Drink styles and the scented non-food
styles. A thin side (mint as a cleaner scent in ten styles, lime in seven) leaves a policy that
routes the word on the pair nothing to route, so each side holds :data:`collision_words.TARGET`.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import (
    collision_words,
    scale,
)


@pytest.fixture(scope="module")
def counts() -> dict[str, dict[str, int]]:
    return collision_words.count(scale.templates())


@pytest.mark.parametrize("word", collision_words.WORDS)
@pytest.mark.parametrize("sense", ["food", "scent"])
def test_each_sense_of_a_collision_word_holds_the_target_styles(counts, word, sense):
    assert counts[word][sense] >= collision_words.TARGET, (word, sense, counts[word])
