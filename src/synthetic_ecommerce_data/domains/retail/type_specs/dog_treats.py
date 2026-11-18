"""Dog Treats (gen#967, slice 2): dental chews, biscuits and training treats, by the bag's weight.

**Pets > Dog Treats > Dental Chews** holds sticks and twists whose title names the breed size and
the flavor; **Dog Biscuits** baked biscuits and **Training Treats** soft bites whose title names
the life stage and the flavor. Each SKU is a bag's net weight. :mod:`kit_pet_gear` draws the
pouch with its own treats in the window.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    ALLEY_CAT,
    BARKWELL,
    BISCUITS,
    DENTAL,
    DEPARTMENT,
    FOREST,
    HOUND,
    NAVY,
    OWNERS,
    PLUM,
    RUST,
    SAND,
    SKY,
    TAILMOOR,
    TEAL,
    TRAINING,
    decoy,
    grams,
    row,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_SHAPE = "dog_treats"


def _dental(form: str, breed: str, flavor: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Dog"), a("treat_form", "Treat form", form),
            a("breed_size", "Breed size", breed), a("flavor", "Flavor", flavor))  # fmt: skip


def _baked(form: str, life: str, flavor: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Dog"), a("treat_form", "Treat form", form),
            a("life_stage", "Life stage", life), a("flavor", "Flavor", flavor))  # fmt: skip


ROWS = (
    row("DGTDSC", "Dental Sticks for Small Dogs with Chicken", HOUND, DENTAL, "Dog Treats", _SHAPE,
        "Chewy daily dental sticks with a ridged shape that helps clean teeth and freshen breath.",
        _dental("Dental Stick", "Small", "Chicken"), grams((0.11, 2.5), (0.44, 8.0), (0.88, 14.0)), "net_weight_g", (), TEAL),
    row("DGTDMM", "Dental Sticks for Medium Dogs with Mint", BARKWELL, DENTAL, "Dog Treats", _SHAPE,
        "Daily dental sticks with mint and parsley, firm enough to scrub as a dog chews.",
        _dental("Dental Stick", "Medium", "Mint"), grams((0.18, 3.5), (0.54, 9.0), (1.08, 16.0)), "net_weight_g", (), FOREST),
    row("DGTDLB", "Dental Twists for Large Dogs with Beef", TAILMOOR, DENTAL, "Dog Treats", _SHAPE,
        "Twisted dental chews for big dogs, long-lasting and made with real beef.",
        _dental("Dental Twist", "Large", "Beef"), grams((0.27, 4.5), (0.81, 11.0), (1.62, 19.0)), "net_weight_g", (), RUST),
    row("DGTDMD", "Dental Twists for Medium Dogs with Duck", HOUND, DENTAL, "Dog Treats", _SHAPE,
        "Grain-free twisted dental chews for medium dogs, with a spiral that reaches the back teeth.",
        _dental("Dental Twist", "Medium", "Duck"), grams((0.18, 3.8), (0.54, 9.5), (1.08, 17.0)), "net_weight_g", (), NAVY),
    row("DGTBAP", "Adult Dog Biscuits with Peanut Butter", HOUND, BISCUITS, "Dog Treats", _SHAPE,
        "Crunchy oven-baked bone biscuits for adult dogs, a reward between meals.",
        _baked("Biscuit", "Adult", "Peanut Butter"), grams((0.4, 3.0), (1, 6.0), (2.5, 12.0)), "net_weight_g", (), SAND),
    row("DGTBPL", "Puppy Dog Biscuits with Lamb & Rice", BARKWELL, BISCUITS, "Dog Treats", _SHAPE,
        "Small baked biscuits for growing puppies, gentle on young teeth.",
        _baked("Biscuit", "Puppy", "Lamb & Rice"), grams((0.4, 3.5), (1, 7.0)), "net_weight_g", (), SKY),
    row("DGTBSP", "Senior Dog Biscuits with Pumpkin & Oat", TAILMOOR, BISCUITS, "Dog Treats", _SHAPE,
        "Light baked biscuits for older dogs, lower in fat, with pumpkin for digestion.",
        _baked("Biscuit", "Senior", "Pumpkin & Oat"), grams((0.4, 3.5), (1, 7.0), (2.5, 13.0)), "net_weight_g", (), NAVY),
    row("DGTBAB", "Adult Dog Biscuits with Bacon & Cheese", BARKWELL, BISCUITS, "Dog Treats", _SHAPE,
        "Crunchy baked biscuits for adult dogs, a savory reward for a good walk.",
        _baked("Biscuit", "Adult", "Bacon & Cheese"), grams((0.4, 3.2), (1, 6.5), (2.5, 12.5)), "net_weight_g", (), RUST),
    row("DGTTPC", "Puppy Training Treats with Chicken", HOUND, TRAINING, "Dog Treats", _SHAPE,
        "Soft, bite-sized treats for puppy training, small enough to give often.",
        _baked("Training Bite", "Puppy", "Chicken"), grams((0.1, 2.0), (0.25, 4.0), (0.5, 7.0)), "net_weight_g", (), PLUM),
    row("DGTTAS", "Adult Training Treats with Salmon", BARKWELL, TRAINING, "Dog Treats", _SHAPE,
        "Soft training treats for adult dogs, rich in fish oil for a glossy coat.",
        _baked("Training Bite", "Adult", "Salmon"), grams((0.1, 2.2), (0.25, 4.5), (0.5, 8.0)), "net_weight_g", (), TEAL),
    row("DGTTAD", "Adult Training Treats with Duck", TAILMOOR, TRAINING, "Dog Treats", _SHAPE,
        "Grain-free soft treats for adult dogs, for training and recall practice.",
        _baked("Training Bite", "Adult", "Duck"), grams((0.1, 2.4), (0.25, 4.8), (0.5, 8.5)), "net_weight_g", (), SAND),
    row("DGTTST", "Senior Training Treats with Turkey", HOUND, TRAINING, "Dog Treats", _SHAPE,
        "Soft, low-fat treats for older dogs, easy to chew and small enough to give often.",
        _baked("Training Bite", "Senior", "Turkey"), grams((0.1, 2.2), (0.25, 4.4), (0.5, 7.8)), "net_weight_g", (), FOREST),
)  # fmt: skip

SPEC = TypeSpec(
    key="dog_treats",
    department=DEPARTMENT,
    product_type="Dog Treats",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(7, "cat treats", "generic", decoy(ROWS[3], "DGTCAT", "Adult Dog Biscuits, Peanut Butter Recipe",
              "Crunchy baked biscuits for adult dogs from the Alley Cat Provisions kitchen.", ALLEY_CAT)),
        Decoy(6, "dental chews", "generic", decoy(ROWS[4], "DGTDEN", "Dental Hill Puppy Dog Biscuits",
              "From the Dental Hill range: small baked biscuits for growing puppies.")),
    ),
)  # fmt: skip
