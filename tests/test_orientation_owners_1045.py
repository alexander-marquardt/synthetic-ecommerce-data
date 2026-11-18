"""A retail shape's orientation sits in its owner's module, the one that registers it (#1045).

:mod:`...retail.orientation` names no shape: it walks :mod:`...retail.orientations`, one module
per module that registers shapes, so two departments' PRs edit two files. That holds only while
each shape is filed with its owner: a shape filed in another module, such as ``kit.py``'s, brings
back the one shared file the split removed. These tests record which module registers each
shape and refuse an ``orientations/<m>.py`` that names a shape its owner does not register. The
other half of the guard, a shape line added back to ``orientation.py``, is
``scripts/check_no_registry_append.py``'s (``tests/test_registry_append_guard_513.py``).

The owner is read in a fresh interpreter: a shape is registered when its module is imported, and
in a test session every module is already imported, so the call that registered it is gone.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from synthetic_ecommerce_data.domains.retail import orientation

#: Wraps :func:`kit.register` before any ``kit_*`` module is imported, fills the registry
#: (:func:`kit.register_all`) and prints ``{shape: the module that first registered it}``. A
#: module that registers a shape again (``kit_packs.py`` wraps a drawing another module owns)
#: is not its owner: it reads the shape from the registry, so the owner registered it first.
_PROBE = """
import json, sys
from synthetic_ecommerce_data.domains.retail import kit
early = sorted(m for m in sys.modules if m.rsplit(".", 1)[-1].startswith("kit_"))
assert not early, f"imported before kit.register is wrapped: {early}"
owner = dict.fromkeys(kit.SHAPES, kit.__name__)
_register = kit.register
def register(shapes, offsets=None):
    caller = sys._getframe(1).f_globals["__name__"]
    for shape in shapes:
        owner.setdefault(shape, caller)
    _register(shapes, offsets)
kit.register = register
kit.register_all()
print(json.dumps(owner))
"""


def module_for(registrant: str) -> str:
    """The :mod:`orientations` module that files the shapes module ``registrant`` registers:
    ``kit_<x>`` -> ``<x>``, ``kit`` -> ``kit``, ``type_specs.<x>`` -> ``spec_<x>``."""
    package, _, name = registrant.rpartition(".")
    if package.endswith(".type_specs"):
        return f"spec_{name}"
    if name == "kit":
        return name
    return name.removeprefix("kit_") if name.startswith("kit_") else registrant


@pytest.fixture(scope="module")
def owners() -> dict[str, str]:
    done = subprocess.run(
        [sys.executable, "-c", _PROBE], capture_output=True, text=True, timeout=300, check=False
    )
    assert done.returncode == 0, done.stderr[-2000:]
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_each_orientations_module_names_only_the_shapes_its_owner_registers(owners):
    misfiled = [
        f"orientations/{module}.py names {shape!r} ({name}), which "
        + (
            f"{owners[shape]} registers: move it to orientations/{module_for(owners[shape])}.py"
            if shape in owners
            else "no module registers"
        )
        for module, sets in orientation._OWNED.items()
        for name, shapes in sets.items()
        for shape in shapes
        if shape not in owners or module_for(owners[shape]) != module
    ]
    assert misfiled == [], "\n".join(misfiled)


@pytest.mark.parametrize(
    ("registrant", "module"),
    [
        ("synthetic_ecommerce_data.domains.retail.kit_health", "health"),
        ("synthetic_ecommerce_data.domains.retail.kit", "kit"),
        ("synthetic_ecommerce_data.domains.retail.type_specs.belt", "spec_belt"),
        (
            "synthetic_ecommerce_data.domains.retail.details",
            "synthetic_ecommerce_data.domains.retail.details",
        ),
    ],
)
def test_a_registering_module_maps_to_the_orientations_module_named_after_it(registrant, module):
    assert module_for(registrant) == module
