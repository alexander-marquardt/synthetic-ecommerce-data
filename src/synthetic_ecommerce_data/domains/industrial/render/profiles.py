"""Output profiles.

Both profiles are sized from where the image is actually displayed.

``card``
    The catalog card shows images in a 150 x 220 CSS-pixel box (and a 150 x 180
    grid cell) with ``object-fit: contain``. 150:220 is 0.6818, so the drawing
    is portrait and a long tool is drawn standing up -- which is also how the
    industry draws one. Rendered at 4x for high-density displays: 600 x 880.

``detail``
    The detail view is a 350 x 350 square box, so the profile is square; a
    portrait image there would letterbox and waste half the space. 4x gives
    1400 x 1400.

Both profiles are rendered at 200 dpi, which makes them 3.0 in and 7.0 in wide
respectively and therefore displayed at the same 50 CSS pixels per figure inch.
One set of point sizes is legible on both.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Card box in CSS pixels, from the catalog card's IMAGE_WIDTH / IMAGE_MAX_HEIGHT.
CARD_CSS = (150, 220)
#: Detail box in CSS pixels.
DETAIL_CSS = (350, 350)
#: Rendered at 4x so the drawing stays crisp on a high-density display.
SCALE = 4


@dataclass(frozen=True)
class Profile:
    name: str
    width_px: int
    height_px: int
    dpi: int = 200
    #: The detail profile has room for an end view, a title block and full
    #: dimensioning; the card carries the silhouette and the two diameters only.
    verbose: bool = False

    @property
    def aspect(self) -> float:
        """Width over height."""
        return self.width_px / self.height_px

    @property
    def figsize(self) -> tuple[float, float]:
        return (self.width_px / self.dpi, self.height_px / self.dpi)


CARD = Profile(
    name="card",
    width_px=CARD_CSS[0] * SCALE,
    height_px=CARD_CSS[1] * SCALE,
    verbose=False,
)
DETAIL = Profile(
    name="detail",
    width_px=DETAIL_CSS[0] * SCALE,
    height_px=DETAIL_CSS[1] * SCALE,
    verbose=True,
)

PROFILES: dict[str, Profile] = {p.name: p for p in (CARD, DETAIL)}
