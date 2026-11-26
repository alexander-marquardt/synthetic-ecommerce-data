"""Team, racket, ball, water, fishing and golf sports: the options each spec declares (gen#413,
gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

MOVED: dict[str, list[Option]] = {
    "baseball_glove": [Option("glove_size_in", "glove_size", "Glove size", "INH")],
    "batting_helmet": [Option("head_cm", "head_circumference", "Head circumference", "CMT")],
    "swim_armbands": [Option("max_load_kg", "max_load_kg", "Maximum load", "KGM")],
    "football": [Option("ball_size", "ball_size", "Ball size", "C62")],
    "badminton_set": [Option("players", "players", "Players", "C62")],
    "tennis_racket": [Option("grip", "grip_size", "Grip size")],
    # a fishing reel's size and a golf club's hand (gen#959), declared by their specs from the start
    "fishing_reel": [Option("reel_size", "reel_size", "Reel size")],
    "golf_club": [Option("handedness", "handedness", "Handedness")],
    # a table tennis bat's handle shape (gen#959 slice 2), declared by its spec from the start
    "table_tennis_bat": [Option("handle_shape", "handle_shape", "Handle shape")],
}
