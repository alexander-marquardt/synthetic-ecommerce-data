"""Pixel helpers shared by the drawing tests."""

from __future__ import annotations

import numpy as np
from matplotlib.colors import to_rgb


def figure_pixels(fig) -> np.ndarray:
    """RGB array of a built figure, rows counted from the top."""
    fig.canvas.draw()
    return np.asarray(fig.canvas.buffer_rgba())[..., :3] / 255.0


def color_mask(image: np.ndarray, color: str, tol: float = 0.06) -> np.ndarray:
    """Pixels within ``tol`` of ``color`` on every channel.

    The tolerance is tight on purpose. At 0.12 a mid-grey antialiased edge
    falls inside the flute color's box and the mask stops meaning anything.
    """
    return np.all(np.abs(image - np.array(to_rgb(color))) < tol, axis=-1)


def rows_from_top(fig, ax, y_data: float) -> float:
    """Pixel row (from the top) of a data-space y coordinate."""
    return fig.canvas.get_width_height()[1] - ax.transData.transform((0.0, y_data))[1]


def within_axes(fig, ax, shape: tuple[int, int]) -> np.ndarray:
    """Mask of the pixels belonging to one axes, for a figure with several."""
    height = shape[0]
    box = ax.bbox
    mask = np.zeros(shape, dtype=bool)
    mask[
        max(int(height - box.y1), 0) : int(np.ceil(height - box.y0)),
        max(int(box.x0), 0) : int(np.ceil(box.x1)),
    ] = True
    return mask


def longest_row_runs(mask: np.ndarray) -> np.ndarray:
    """Length of the longest contiguous True run in each row.

    Letting a dimension arrow be told apart from the text beside it: both are
    drawn in the dimension color and share rows, but only the arrow is one
    long unbroken run.
    """
    padded = np.pad(mask, ((0, 0), (1, 1)))
    edges = np.diff(padded.astype(np.int8), axis=1)
    out = np.zeros(mask.shape[0])
    for row in range(mask.shape[0]):
        starts = np.flatnonzero(edges[row] == 1)
        if starts.size:
            out[row] = (np.flatnonzero(edges[row] == -1) - starts).max()
    return out


def pixels_per_inch(ax) -> float:
    origin = ax.transData.transform((0.0, 0.0))[0]
    return ax.transData.transform((1.0, 0.0))[0] - origin
