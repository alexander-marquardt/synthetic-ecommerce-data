"""Every test runs under a per-test time limit (elastic/prism#10032).

Without one, a test that hangs or grows its memory without end holds the
machine until something outside pytest kills it. ``pytest-timeout`` turns that
into one failed test. This guard fails if the plugin stops being installed or
the configured limit is removed.
"""

import pytest


def test_the_timeout_plugin_is_loaded(pytestconfig: pytest.Config) -> None:
    assert pytestconfig.pluginmanager.hasplugin("timeout") is True


def test_every_test_has_a_300_second_limit(pytestconfig: pytest.Config) -> None:
    assert pytestconfig.getini("timeout") == "300"
