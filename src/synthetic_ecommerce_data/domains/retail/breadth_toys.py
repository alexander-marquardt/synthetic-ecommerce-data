"""The breadth rows of the Toys department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import (
    Row,
    _fab,
    _mat,
    paint_range,
)
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Toys: the animal or vehicle is drawn; the fabric, material or power varies.
# --------------------------------------------------------------------------

_SOFT = ("Toys", "Soft Toys", "Cuddly Animals")
_BATH = ("Toys", "Baby & Toddler", "Bath Toys")
_CARS = ("Toys", "Vehicles", "Toy Vehicles")
_FIG = ("Toys", "Figures & Playsets", "Animal Figures")
_LIGHT = ("Toys", "Nursery", "Night Lights")
_KIDS = "kids"

TOYS = (
    Row("SFTCAT", "Plush Cat Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy", 14.0, "cat",
        "A floppy plush cat with stitched eyes and a long tail, soft enough for bedtime. "
        "Surface washable.",
        (cw("Ginger", "#d9822b"), cw("Grey", "#9a9a9a"), cw("Black", "#2a2a2e")),
        _fab("Plush"), audience=_KIDS),
    Row("SFTOWL", "Knitted Owl Soft Toy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy", 16.0,
        "bird",
        "A round knitted owl with felt wings and embroidered eyes, small enough for a cot. "
        "Hand wash.",
        (cw("Oat", "#d8c9a8"), cw("Sage", "#9bb08f")), _fab("Knitted"), audience=_KIDS),
    Row("SFTWHL", "Corduroy Whale Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy", 18.0,
        "whale",
        "A long whale with a squashy body and a stitched smile, filled with recycled fiber. "
        "Machine washable at 30 degrees.",
        (cw("Navy", "#26365c"), cw("Sky Blue", "#8fb8de")), _fab("Corduroy"), audience=_KIDS),
    Row("SFTDIN", "Faux Fur Dinosaur Soft Toy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy",
        20.0, "dinosaur",
        "A big-footed dinosaur with soft spines down its back, made for hugging. "
        "Surface washable.",
        (cw("Moss Green", "#6f8f4a"), cw("Lilac", "#b9a3d0")), _fab("Faux Fur"), audience=_KIDS),
    Row("SFTBIR", "Organic Cotton Bird Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy",
        12.0, "bird",
        "A small bird with a crinkly tummy and a ribbon loop, safe from birth. "
        "Machine washable at 30 degrees.",
        (cw("Mustard", "#d1a03c"), cw("Coral", "#ef7b62")), _fab("Organic Cotton"),
        audience=_KIDS),
    Row("BTHWHL", "Silicone Whale Bath Squirter", "Little Fernby", "Toys", _BATH, "Bath Toy",
        7.0, "whale",
        "A whale that fills and squirts from its blowhole. It opens in two for cleaning, "
        "so no water sits inside.",
        (cw("Teal", "#1c7c7d"), cw("Yellow", "#f2d14b")), _mat("Silicone"), audience=_KIDS),
    Row("BTHDCK", "Natural Rubber Bath Duck", "Puddlecombe Toys", "Toys", _BATH, "Bath Toy",
        6.0, "bird",
        "A sealed bath duck that floats upright and never fills with water. "
        "For babies from 3 months.",
        (cw("Yellow", "#f2d14b"), cw("Pink", "#f2a1b8")), _mat("Natural Rubber"), audience=_KIDS),
    Row("BTHBOT", "Recycled Plastic Whale Bath Set", "Little Fernby", "Toys", _BATH, "Bath Toy",
        12.0, "whale",
        "A floating whale with three stacking cups that pour, sieve and sprinkle. "
        "Dishwasher safe.",
        (cw("Blue", "#3f6fb5"),), _mat("Recycled Plastic"), audience=_KIDS),
    Row("CARRCE", "Wooden Racing Car", "Little Fernby", "Toys", _CARS, "Toy Vehicle", 9.0, "car",
        "A chunky racing car with rubber tires and a driver who lifts out. For ages 18 months "
        "and up.",
        paint_range(cw("Red", "#c8312e"), cw("Blue", "#3f6fb5")), _mat("Wooden"),
        audience=_KIDS),
    Row("CARPOL", "Die-Cast Police Car", "Puddlecombe Toys", "Toys", _CARS, "Toy Vehicle", 6.0,
        "car",
        "A pocket-size police car with opening doors and a pull-back motor. For ages 3 and up.",
        (cw("White", "#ffffff", "solid", "#26365c"),), _mat("Die-Cast"), audience=_KIDS,
        fixed_color="the police livery: white with a navy stripe is what makes it a police car"),
    Row("CARVIN", "Recycled Plastic Vintage Car", "Little Fernby", "Toys", _CARS, "Toy Vehicle",
        11.0, "car",
        "A rounded vintage car with a seat for a small figure and wheels that never come off.",
        paint_range(cw("Mint", "#a8d8c2"), cw("Cream", "#efe8d8")), _mat("Recycled Plastic"),
        audience=_KIDS),
    Row("CARTOW", "Wooden Tow Truck", "Puddlecombe Toys", "Toys", _CARS, "Toy Vehicle", 15.0, "car",
        "A tow truck with a working hook and winch that lifts a second car. "
        "For ages 2 and up.",
        paint_range(cw("Yellow", "#f2d14b")), _mat("Wooden"), label="Tow", audience=_KIDS),
    Row("FIGCAT", "Resin Cat Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 5.0,
        "cat",
        "A sitting cat figure sized for small hands, finished in water-based paint.",
        (cw("Tabby", "#b07a43"),), _mat("Resin"), audience=_KIDS),
    Row("FIGWHL", "Wooden Whale Figure", "Little Fernby", "Toys", _FIG, "Toy Figure", 6.0,
        "whale", "A smooth whale figure with a rounded tail, for play in the bath or on the rug.",
        (cw("Navy", "#26365c"),), _mat("Wooden"), audience=_KIDS),
    Row("FIGBRD", "Rubber Bird Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 4.0,
        "bird", "A robin figure with a flat base so it stands up, soft enough to chew.",
        (cw("Red", "#c8312e", "solid", "#7a4a2a"),), _mat("Rubber"), audience=_KIDS),
    Row("LGTSTR", "Rechargeable Star Night Light", "Little Fernby", "Toys", _LIGHT, "Night Light",
        22.0, "star",
        "A soft-glow star that dims over 30 minutes, then stays on low all night.",
        (cw("Warm White", "#fbefc9"), cw("Pink", "#f2a1b8")), (("power", "Power", "Rechargeable"),),
        audience=_KIDS),
    Row("LGTWHL", "Plug-In Whale Night Light", "Puddlecombe Toys", "Toys", _LIGHT, "Night Light",
        18.0, "whale",
        "A silicone whale that glows when tapped and changes color with a second tap.",
        (cw("Blue", "#8fb8de"),), (("power", "Power", "Plug-In"),), audience=_KIDS),
    Row("LGTCAT", "Battery-Powered Cat Night Light", "Little Fernby", "Toys", _LIGHT,
        "Night Light", 15.0, "cat",
        "A sleeping cat lamp with a timer that switches it off after one hour.",
        (cw("White", "#ffffff"),), (("power", "Power", "Battery-Powered"),), audience=_KIDS),
    # Round 2 (gen#125): at 20K, toys held 23 styles against a half share of 30.
    # Each leaf takes one new value at most and the rest reuse its pool: a value its leaf
    # lacks multiplies the siblings that share a picture, and they then share a grid tile
    # (scale.grid_clones). Extra colors add styles that do not.
    Row("SFTFLC", "Plush Owl Sleep Buddy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy", 15.0,
        "bird",
        "A flat owl with long wings to hold at night and a loop for a buggy. Machine washable.",
        (cw("Heather", "#b4a7c4"), cw("Oat", "#d8c9a8"), cw("Duck Egg", "#b7d3cf")),
        _fab("Plush"), audience=_KIDS),
    Row("SFTVLV", "Corduroy Dinosaur Cuddle Toy, Large", "Little Fernby", "Toys", _SOFT,
        "Soft Toy", 26.0, "dinosaur",
        "A long-necked dinosaur nearly 50 cm tall, weighted at the feet so it sits up.",
        (cw("Teal", "#1c7c7d"), cw("Rose", "#d98c9f"), cw("Mustard", "#d1a03c")),
        _fab("Corduroy"), audience=_KIDS),
    Row("BTHFOM", "Foam Cat Bath Floaters, Set of 3", "Puddlecombe Toys", "Toys", _BATH,
        "Bath Toy", 4.0, "cat",
        "Three cats that float and stick to the side of the bath when wet. Air dry after use.",
        (cw("Orange", "#e98a3a"), cw("Lilac", "#b9a3d0"), cw("Mint", "#a8d8c2")), _mat("Foam"),
        audience=_KIDS),
    Row("BTHVNL", "Natural Rubber Dinosaur Bath Squirter", "Little Fernby", "Toys", _BATH,
        "Bath Toy", 4.5, "dinosaur",
        "A squeezy dinosaur that squirts from its mouth, sized for a toddler's hand.",
        (cw("Green", "#6f8f4a"), cw("Purple", "#7d5ba6"), cw("Orange", "#e98a3a")),
        _mat("Natural Rubber"), audience=_KIDS),
    Row("BTHBMB", "Recycled Plastic Bird Pouring Cups", "Puddlecombe Toys", "Toys", _BATH,
        "Bath Toy", 10.0, "bird",
        "Four nesting cups with a bird on each, for pouring and stacking in the bath.",
        (cw("Sky Blue", "#8fb8de"), cw("Coral", "#ef7b62")), _mat("Recycled Plastic"),
        audience=_KIDS),
    Row("CARBMB", "Bamboo Fire Engine with Ladder", "Little Fernby", "Toys", _CARS,
        "Toy Vehicle", 18.0, "car",
        "A fire engine with a ladder that turns and extends. For ages 2 and up.",
        (cw("Red", "#c8312e"),), _mat("Bamboo"), label="Fire", audience=_KIDS,
        fixed_color="a fire engine is red: the color is what makes it a fire engine"),
    Row("CARTIN", "Die-Cast London Taxi", "Little Fernby", "Toys", _CARS, "Toy Vehicle", 4.5,
        "car", "A pocket-size taxi with a light on its roof and a pull-back motor. For ages 3 "
        "and up.",
        (cw("Black", "#2a2a2e"),), _mat("Die-Cast"), label="Taxi", audience=_KIDS,
        fixed_color="a London taxi is black: the color is what makes it a London taxi"),
    Row("FIGFLT", "Felt Stegosaurus Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 7.0,
        "dinosaur", "A dinosaur figure with a long tail and a flat base, sized for small hands.",
        (cw("Moss Green", "#6f8f4a"), cw("Ochre", "#c8902e")), _mat("Felt"), audience=_KIDS),
    Row("FIGRCY", "Rubber Whale Bath Figure", "Little Fernby", "Toys", _FIG, "Toy Figure", 3.5,
        "whale", "A whale figure with no small parts, for play on the rug or in the bath.",
        (cw("Aqua", "#8fd1d0"), cw("Navy", "#26365c")), _mat("Rubber"), audience=_KIDS),
    Row("FIGPOR", "Wooden Cat Ornament Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure",
        4.0, "cat", "A small figure for a shelf or a dolls' house, for ages 3 and up.",
        (cw("Calico", "#c8a27a"), cw("Grey", "#9a9a9a")), _mat("Wooden"), audience=_KIDS),
    Row("LGTUSB", "USB-Powered Dinosaur Night Light", "Puddlecombe Toys", "Toys", _LIGHT,
        "Night Light", 16.0, "dinosaur",
        "A dinosaur lamp with a touch base that cycles through three brightness levels.",
        (cw("Green", "#6f8f4a"), cw("Sky Blue", "#8fb8de")), (("power", "Power", "USB-Powered"),),
        audience=_KIDS),
    Row("LGTSOL", "Rechargeable Star Lantern", "Little Fernby", "Toys", _LIGHT,
        "Night Light", 12.0, "star",
        "A star lantern for a bedroom shelf, with a soft glow that lasts all night.",
        (cw("Warm White", "#fbefc9"), cw("Lilac", "#b9a3d0")),
        (("power", "Power", "Rechargeable"),), audience=_KIDS),
    Row("LGTWND", "Battery-Powered Bird Night Light", "Puddlecombe Toys", "Toys", _LIGHT,
        "Night Light", 14.0, "bird",
        "A bird lamp with a soft glow and a sleep timer that switches off after 20 minutes.",
        (cw("Mint", "#a8d8c2"), cw("Peach", "#f4b893")),
        (("power", "Power", "Battery-Powered"),), audience=_KIDS),
)  # fmt: skip
