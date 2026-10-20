"""Text-match decoys for the first Sports & Outdoors increment (gen#375, the rule of #294).

The seven types of gen#265 (tents, sleeping bags, camping chairs, yoga mats, dumbbells,
kettlebells and foam rollers) carried no decoys when the second increment (gen#368) added its own.
Each has two here: a product of another department whose title holds the shopper's word. The
structured fields tell the truth (department, category path, product type, drawing), so a
department policy drops it. A title and a description name no color: the drawing cannot disagree
with them. The rows are class 8 (``noun`` is a word of the sports type's own name, ``target`` the
type), made with the table's row maker, and ``tests/test_retail_sports_decoys_368.py`` holds the
two-decoy floor for every type of the department.
"""

from __future__ import annotations


def word_rows(d):
    def s(n, kind, title, desc, color, noun, target, query=None, cross=True):
        """A decoy of ``target``: another department's product holding ``noun`` in its title."""
        return d(
            n,
            kind,
            title,
            desc,
            color,
            query or noun,
            noun,
            "department",
            cross=cross,
            target=target,
        )

    return (
        s(
            540,
            "s_dress",
            "Tent Dress, Swing Fit",
            "A loose swing dress cut like a tent, with short sleeves and a round neck.",
            "Pink",
            "tent",
            "Tent",
            cross=False,
        ),
        s(
            541,
            "cushion",
            "Tent Stitch Cushion",
            "A cushion worked in tent stitch needlepoint, with a zip cover.",
            "Cream",
            "tent",
            "Tent",
        ),
        s(
            542,
            "cushion",
            "Sleeping Cat Cushion",
            "A soft cushion with a curled sleeping cat on the front and a zip cover.",
            "Grey",
            "sleeping",
            "Sleeping Bag",
        ),
        s(
            543,
            "doll",
            "Sleeping Beauty Doll",
            "A soft-bodied doll with eyes that close, made for bedtime.",
            "Cream",
            "sleeping",
            "Sleeping Bag",
        ),
        s(
            544,
            "kids_tee",
            "Camping Club Kids T-Shirt",
            "A cotton tee printed with a campfire and the words camping club.",
            "Green",
            "camping",
            "Camping Chair",
            cross=False,
        ),
        s(
            545,
            "candle_vanilla",
            "Camping Trip Scented Candle",
            "A warm vanilla candle in a glass jar.",
            "Cream",
            "camping",
            "Camping Chair",
        ),
        s(
            546,
            "seed_jeggings",
            "Yoga Waist Leggings",
            "Soft stretch leggings with a high waist and a flat seam.",
            "Black",
            "yoga",
            "Yoga Mat",
            cross=False,
        ),
        s(
            547,
            "lav_candle",
            "Yoga Calm Scented Candle",
            "A lavender candle in a glass jar, for a quiet evening.",
            "Cream",
            "yoga",
            "Yoga Mat",
        ),
        s(
            548,
            "s_tee",
            "Dumbbell Print Tee",
            "A soft cotton tee printed with a pair of dumbbells.",
            "Grey",
            "dumbbell",
            "Dumbbell",
            cross=False,
        ),
        s(
            549,
            "s_tennisbr",
            "Dumbbell Charm Bracelet",
            "A fine chain bracelet with a small dumbbell charm.",
            "Gold",
            "dumbbell",
            "Dumbbell",
            cross=False,
        ),
        s(
            550,
            "s_tee",
            "Kettlebell Class Tee",
            "A cotton tee with a kettlebell print and a relaxed fit.",
            "Orange",
            "kettlebell",
            "Kettlebell",
            cross=False,
        ),
        s(
            551,
            "s_tote",
            "Kettlebell Class Tote Bag",
            "A canvas tote with a wide gusset and a zip pocket, for the studio.",
            "Navy",
            "kettlebell",
            "Kettlebell",
            cross=False,
        ),
        s(
            552,
            "s_handwash",
            "Foam Hand Wash",
            "A gentle hand wash that pumps out as a light foam.",
            "Pink",
            "foam",
            "Foam Roller",
        ),
        s(
            553,
            "s_sandal",
            "Foam Sole Sandals",
            "Light sandals with a molded foam sole and a buckle strap.",
            "Brown",
            "foam",
            "Foam Roller",
            cross=False,
        ),
    )
