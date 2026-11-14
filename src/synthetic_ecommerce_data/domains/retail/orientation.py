"""The orientation of every retail drawing: the set of angles a product's figure turns by (#849).

Retail draws a product as a shape (:data:`kit.SHAPES`), and many types share one (jeans, chinos
and joggers are all ``trousers``), so the orientation is the shape's: what is drawn is what
looks right or wrong turned. Every registered shape names one, here, and
``tests/test_one_paper_one_angle_849.py`` refuses a shape missing from this table, so a new
shape cannot forget it. The sets are :data:`...core.drawing.product_look.ORIENTATIONS`:

* ``any`` (the 24 clock positions): a thing with no natural up. Gloves (the maintainer's ruling
  on #860), a screw, a ball, round fruit, a snowflake, coiled cables and laces.
* ``slight`` (+-15 degrees): clothing, footwear and what is worn with them (a belt, a scarf, a
  tie, a hat), where a garment turned further reads as falling over (the maintainer's ruling
  on #860).
* ``upright`` (+-36 degrees): everything with a natural up (a bottle, a sofa, a lamp, a fridge,
  a toy), and every shape nobody was sure of.

* ``level`` (0 degrees only, #884): a set type drawn as several items (cutlery, a dinner set,
  luggage), which overlap on a slant.

A product any SKU of which is a pack of several items (``pack_copies.count``: its pack size,
units per pack or pack attribute, or "Set of 2" in its title) is drawn level on every SKU
whatever its shape (:func:`of_product`, #884), so a cup set in 2, 4 and 8 packs stands level
while a single cup keeps its tilt. To move a shape, move its line to another tuple.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import pack_copies

#: Things with no natural up, drawn at any of the 24 clock positions.
ANY: tuple[str, ...] = (
    "baseball", "cable", "cable_ties", "football", "gloves", "jumper_cables", "lemon", "orange",
    "potato", "round_produce", "screw", "shoe_laces", "snowflake",
)

#: Clothing, footwear and what is worn with them: within +-15 degrees.
SLIGHT: tuple[str, ...] = (
    "all_in_one", "apron", "baby_bodysuit", "belt", "belt_buckled", "bikini_bottoms", "bikini_top",
    "blouse", "bodysuit", "bolero", "bomber_jacket", "boot_sock", "boxers", "boys_suit", "bra",
    "cardigan", "changing_robe", "coat", "cover_up", "cycling_shorts", "dinner_suit", "dress",
    "dressing_gown", "formal_accessory", "gilet", "hat", "hoodie", "jeans_bootcut",
    "jeans_straight", "joggers", "kids_swimsuit", "knickers", "leggings", "mens_pants",
    "outfit_set", "parka", "pe_shorts", "peacoat", "puddlesuit", "puffer", "puffer_jacket",
    "pyjamas", "raincoat", "sandal", "scarf", "school_blazer", "school_pinafore", "school_polo",
    "school_shirt", "school_skirt", "school_socks", "school_trousers", "shacket", "shapewear",
    "shirt_dress", "shoe", "shorts", "skirt", "sleepsuit", "slip", "snowsuit", "socks",
    "suit_jacket", "suit_trousers", "sweatshirt", "swim_bottoms", "swim_cap", "swim_shorts",
    "swimsuit", "tankini", "tights", "top", "tracksuit", "trainer", "trench_coat", "trouser_suit",
    "trousers", "tshirt", "utility_jacket", "vest", "waistcoat", "windbreaker",
)

#: Everything with a natural up, and every shape nobody was sure of: within +-36 degrees.
UPRIGHT: tuple[str, ...] = (
    "aftershave", "analog_watch", "angled_bottle", "anti_vibration_mat", "apple", "armchair",
    "baby_blanket", "backpack", "bag", "banana", "bar", "baseball_bat", "baseball_glove",
    "basic_phone", "bath_mat", "bath_towel", "battery", "batting_helmet", "bbq", "beach_towel",
    "bed_frame", "bicycle", "bike_bottle", "bike_helmet", "bike_pedals", "bike_pump",
    "bike_saddle", "bird", "blind", "board_game", "body_mist", "bookcase", "bottle", "bouquet",
    "bowl", "box", "box_wide", "bracelet", "building_set", "butter_block", "cabin_case", "cake",
    "camp_chair", "car", "card_game", "carrot", "carton", "casserole", "cat", "cat_litter",
    "caulking_gun",
    "ceiling_fan", "ceiling_light", "chain_lube", "chairbed", "chaise_sofa", "changing_mat",
    "charger", "charging_pad", "cherries", "chest_of_drawers", "chocolate_box", "chopping_board",
    "christmas_tree", "clock", "clothes_airer", "coat_stand", "coffee_table", "colander",
    "combi_drill", "compact", "corded_drill", "corner_sofa", "craft_kit", "crisps_bag", "cupcake",
    "curtains", "cushion", "cutlery_piece", "daisy", "desk_fan", "desk_lamp", "desktop", "diary",
    "digital_watch", "dining_chair", "dining_table", "dinosaur", "dishwasher",
    "dishwasher_tablets", "doll", "dolls_house", "door_stop", "doughnut", "draped_throw", "drill",
    "drill_driver", "drinking_glass", "drop_earrings", "dry_pet_food", "dumbbell", "duvet",
    "e_reader", "earbuds",
    "earrings", "espresso_cup", "eye_patches", "eyeliner", "face_mask", "false_nails", "fish_bag",
    "fitness_band", "floor_lamp", "foam_roller", "footstool", "fragrance", "fridge",
    "fridge_magnet", "fridge_thermometer", "frying_pan", "garden_furniture", "garden_hose",
    "garment_bag", "gift_bag", "gift_card", "gift_hamper", "gift_mug", "glue_gun", "grass_trimmer",
    "greeting_card", "grill_press", "hammer", "hammer_drill", "handbag", "handheld_fan", "hanger",
    "hangers", "heater", "hedge_trimmer", "holdall", "hook_rail", "hoop_earrings", "ice_cream",
    "impact_driver", "jar", "jigsaw", "kayak", "kettle", "kettlebell", "keyboard", "keyring",
    "kick_scooter", "kickboard", "kitchen_bin", "kitchen_knife", "kitchen_scales",
    "kitchen_utensil", "kite", "lampshade", "lantern", "laptop", "laptop_sleeve", "laundry_basket",
    "lawn_mower", "lidded_tub", "light_bulb", "lipstick", "loaf", "marble_run", "mascara",
    "mattress", "mattress_protector", "mattress_topper", "measuring_cup", "memory_card",
    "mesh_bag", "mirror", "modular_sofa", "moisturiser_jar", "money_box", "monitor", "mop",
    "mouse", "mug", "mushroom", "nappy_caddy", "neck_pillow", "necklace", "notebook",
    "nursery_storage", "onion", "ornament", "panettone", "paper_cup", "parasol", "party_cup",
    "pedestal_fan", "pen", "pencil", "phone_case", "photo_frame", "picnic_blanket",
    "picture_hook", "pillow", "pizza", "plant_pot", "plate", "play_kitchen", "potted_herb",
    "potted_tree", "pouch", "primer",
    "produce_pile", "pudding", "pump", "pumpkin", "punnet", "purse", "recliner_sofa",
    "resistance_band", "ride_on", "rim_block", "ring", "robot_mower", "role_play", "roll_mat",
    "rug", "saucepan", "screen_protector", "screwdriver", "sds_drill", "serum", "setting_spray",
    "sheet", "shower_curtain", "side_table", "sippy_cup", "skateboard", "sleeping_bag", "sleeve",
    "smartphone", "sofa", "sofa_bed", "sofa_cover", "sofa_seats", "sofa_version",
    "spiral_notebook", "star",
    "steak_tray", "stems", "step_ladder", "sticker_sheet", "storage_box", "strawberry", "suitcase",
    "sun_cream",
    "sunglasses", "swim_armbands", "swim_goggles", "table_lamp", "tablet", "talc", "tea_cup",
    "tea_towel", "tennis_racket", "tent", "throw", "tin", "toaster", "tomato", "tool_kit",
    "tote_bag", "tower_fan", "travel_cup", "travel_organizer", "tray", "trigger_spray",
    "trinket_tray", "trophy", "tub", "tulip", "tumble_dryer", "tumbler", "tv", "umbrella",
    "volt_meter", "wall_light", "wallet", "wallet_fold", "wallpaper", "wardrobe", "washer_dryer",
    "washing_machine", "watch", "water_gun", "weekend_bag", "wet_pet_food", "whale",
    "wooden_toy",
    "wrapping_paper", "wrench", "yoga_block", "yoga_mat", "yoga_strap",
)

#: Set types, drawn as several items: at 0 degrees only (#884).
LEVEL: tuple[str, ...] = (
    "badminton_set", "cutlery_set", "dinner_set", "drill_bit_set", "gift_set", "luggage_set",
)

#: Shape -> orientation.
ORIENTATION: dict[str, str] = {
    **dict.fromkeys(ANY, "any"),
    **dict.fromkeys(SLIGHT, "slight"),
    **dict.fromkeys(UPRIGHT, "upright"),
    **dict.fromkeys(LEVEL, "level"),
}


def of(shape: str) -> str:
    """The orientation ``shape`` is drawn at. ``KeyError`` for a shape the table does not name."""
    return ORIENTATION[shape]


def of_product(rec: dict[str, Any]) -> str:
    """The orientation product ``rec`` is drawn at: its shape's, or ``level`` when any of its
    SKUs is a pack of several items (#884), so every SKU of it shares the one angle."""
    packed = any(pack_copies.count(rec, sku) > 1 for sku in rec.get("skus", ()))
    return product_look.product_orientation(of(rec["drawing"]["shape"]), packed)
