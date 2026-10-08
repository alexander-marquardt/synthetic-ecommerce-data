"""What the PNG on disk actually is: size, shape, and whether anything was drawn."""

from __future__ import annotations

import numpy as np
import pytest

from helpers import colour_mask
from synthetic_ecommerce_data.domains.industrial.records import DRAWABLE
from synthetic_ecommerce_data.domains.industrial.render import CARD, DETAIL, render_record
from synthetic_ecommerce_data.domains.industrial.render.canvas import INK
from synthetic_ecommerce_data.domains.industrial.render.profiles import CARD_CSS, DETAIL_CSS, SCALE

ALL_SKUS = sorted(DRAWABLE)


@pytest.mark.parametrize("sku", ALL_SKUS)
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_the_file_is_exactly_the_size_the_profile_promises(sku, profile, tmp_path, png_size):
    path = render_record(DRAWABLE[sku], tmp_path / f"{sku}.png", profile)
    assert png_size(path) == (profile.width_px, profile.height_px)


@pytest.mark.parametrize("sku", ALL_SKUS)
def test_the_card_has_the_catalog_card_aspect_ratio(sku, tmp_path, png_size):
    # 150 x 220 is the box the card renders into; an image of any other ratio
    # gets letterboxed by object-fit: contain and stops filling the card.
    width, height = png_size(render_record(DRAWABLE[sku], tmp_path / f"{sku}.png", CARD))
    assert width / height == pytest.approx(CARD_CSS[0] / CARD_CSS[1], abs=1e-12)
    assert (width, height) == (CARD_CSS[0] * SCALE, CARD_CSS[1] * SCALE)


@pytest.mark.parametrize("sku", ALL_SKUS)
def test_the_detail_image_is_square_like_its_box(sku, tmp_path, png_size):
    width, height = png_size(render_record(DRAWABLE[sku], tmp_path / f"{sku}.png", DETAIL))
    assert width == height
    assert (width, height) == (DETAIL_CSS[0] * SCALE, DETAIL_CSS[1] * SCALE)


@pytest.mark.parametrize("sku", ALL_SKUS)
@pytest.mark.parametrize("profile", [CARD, DETAIL], ids=lambda p: p.name)
def test_the_image_is_not_blank(sku, profile, tmp_path):
    import matplotlib.image as mpimg

    path = render_record(DRAWABLE[sku], tmp_path / f"{sku}.png", profile)
    image = mpimg.imread(path)[..., :3]
    inked = float(np.mean(np.any(image < 0.85, axis=-1)))
    # A drawing of nothing, and a drawing that has run away and filled the
    # frame, are both failures; the real ones sit between these.
    assert 0.005 < inked < 0.5, f"{sku} {profile.name}: {inked:.3%} of the frame is inked"


@pytest.mark.parametrize("sku", ALL_SKUS)
def test_the_subject_is_centred_in_the_card(sku, tmp_path):
    """The silhouette sits in the middle of the frame, not pushed off by a label.

    The prototype centred the axes' *data*, so the tool drifted sideways by
    however much room the dimension text claimed on one side. Only the black
    ink is measured here: dimension arrows and their labels are deliberately
    lopsided and are drawn in other colours.
    """
    import matplotlib.image as mpimg

    path = render_record(DRAWABLE[sku], tmp_path / f"{sku}.png", CARD)
    image = mpimg.imread(path)[..., :3]
    black = colour_mask(image, INK, tol=0.15)
    columns = np.nonzero(black.any(axis=0))[0]
    assert columns.size, "no silhouette found"
    centre = (columns.min() + columns.max()) / 2
    assert centre == pytest.approx(image.shape[1] / 2, abs=image.shape[1] * 0.02)
