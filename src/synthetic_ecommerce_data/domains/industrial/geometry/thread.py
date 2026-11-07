"""The crest spacing a compressed threaded part is drawn at. Nothing here draws.

A threaded rod or double-end stud too long to draw at scale is drawn compressed, and
its crests are spread so that a set number at most fit the drawing. The spread is one
factor for every thread of a diameter, taken from the diameter's coarse pitch, so a
fine thread is drawn finer than the coarse one at their true ratio: ``Thread Type`` is
a form the drawing shows, not only a word the record prints (#9).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core import standards_library as library
from synthetic_ecommerce_data.core.dimensions import MM_PER_INCH, Thread


def coarse_pitch_in(thread: Thread) -> float:
    """The coarse pitch of ``thread``'s diameter (ASME B1.1's UNC, ISO 262's metric coarse),
    or the thread's own pitch for a diameter neither table carries a coarse pitch for."""
    if thread.major.unit == "mm":
        for row in library.table("iso_262_metric_threads").rows:
            if abs(row["diameter_mm"] / MM_PER_INCH - thread.major.inches) < 1e-6:
                return row["coarse_pitch_mm"] / MM_PER_INCH
    else:
        for row in library.table("asme_b1_1_unified_threads").rows:
            if abs(row["major_dia_in"] - thread.major.inches) < 1e-4 and row.get("unc_tpi"):
                return 1.0 / row["unc_tpi"]
    return thread.pitch_in


def capped_pitch(thread: Thread, floor: float, shrink: float = 1.0) -> float:
    """The spacing a compressed part's crests are drawn at: the published pitch times
    ``shrink``, or, where that would put the COARSE thread of the diameter closer than
    ``floor``, times the one factor that brings the coarse thread to ``floor``. Every thread
    of a diameter is stretched alike, so a fine thread stays finer than the coarse one at
    their true ratio (#9): a fixed ``floor`` drew 5/16-18 and 5/16-24 alike."""
    return thread.pitch_in * max(shrink, floor / coarse_pitch_in(thread))
