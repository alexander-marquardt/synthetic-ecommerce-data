"""A finished build keeps no Generator alive (#839).

``FinishMixin._always_published`` was a ``functools.cache`` on a method, so its cache held each
``(Generator, type_key)`` it was asked for, and with the Generator every spec set it drew
(``_drawn_specs``, ``_published_specs``). Nothing freed them: each small build left about 120 MB
resident, and ``tests/test_type_seam.py``, which builds eight times, took a worker from 50 MB to
2.1 GB that it kept for the rest of its shard. Two such workers filled the 6 GB CI container.
"""

from __future__ import annotations

import gc
import weakref

from synthetic_ecommerce_data.core.config import small
from synthetic_ecommerce_data.domains.industrial.generate import Generator, generate
from synthetic_ecommerce_data.domains.industrial.vocab import VOCAB


def test_a_generator_is_freed_once_its_build_returns() -> None:
    generator = Generator(small(), "abrasive_flap_disc")
    assert generator.build(), "the type built nothing, so the test proves nothing"
    held = weakref.ref(generator)
    del generator
    gc.collect()
    assert held() is None, "something still holds the Generator after its build returned"


def test_a_whole_build_leaves_no_generator_behind() -> None:
    def alive() -> int:
        gc.collect()
        return sum(isinstance(o, Generator) for o in gc.get_objects())

    before = alive()
    assert generate(small(), types=["abrasive_flap_disc", "bolt_hex"]).lines
    assert alive() == before


def test_each_generator_answers_always_published_from_its_own_config() -> None:
    """The answer kept on the Generator is its config's: a config that scales every presence to
    1.0 publishes every attribute always, whatever another Generator of that type was told."""
    key = "abrasive_flap_disc"
    usual = Generator(small(), key)._always_published(key)
    scaled = Generator(small().with_(sparsity_scale=1000.0), key)._always_published(key)
    assert usual < scaled == {spec.name for spec in VOCAB[key]}
