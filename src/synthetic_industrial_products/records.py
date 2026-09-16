"""Reference records used as fixtures.

Attribute names are kept verbatim, including the trailing periods and the
inconsistent unit spellings (``1/2 in`` beside ``0.411 in`` beside ``3/8"``)
that catalogs in this vertical actually publish. Renderers read these names as
published rather than a normalised internal schema, because a renderer that
only works against tidied input does not work against the catalog.
"""

from __future__ import annotations

from typing import Any

Record = dict[str, Any]

#: Four end mills and one cap screw, spanning the cases a renderer must survive:
#: mixed-number lengths, a metric record, and a tool whose cutting and shank
#: diameters carry the same value.
FIXTURES: dict[str, Record] = {
    "4LU10": {
        "sku": "4LU10",
        "Item": "Cobalt End Mill",
        "Milling Dia.": '1/4"',
        "Shank Dia.": '3/8"',
        "Length of Cut": '5/8"',
        "Overall Length": '3-3/8"',
        "Number of Flutes": "4",
        "Helix Angle": "30 Degrees",
        "Finish": "Bright",
        "System of Measurement": "Inch",
    },
    "438D34": {
        "sku": "438D34",
        "Item": "Cobalt End Mill",
        "Milling Dia.": '3/16"',
        "Shank Dia.": '3/8"',
        "Length of Cut": '1/2"',
        "Overall Length": '2-5/16"',
        "Number of Flutes": "4",
        "Helix Angle": "30 Degrees",
        "Finish": "Uncoated",
        "System of Measurement": "Inch",
    },
    "33TN24": {
        "sku": "33TN24",
        "Item": "Carbide End Mill",
        "Milling Dia.": '1/2"',
        "Shank Dia.": '1/2"',
        "Length of Cut": '1"',
        "Overall Length": '3"',
        "Number of Flutes": "4",
        "Helix Angle": "30 Degrees",
        "Finish": "AlTiN",
        "System of Measurement": "Inch",
    },
    # 35AM34's two diameters are the observed ones. Its length of cut and
    # overall length were NOT observed -- the reference page carried only the
    # diameters -- and are supplied here so the metric path has something to
    # draw. They follow the standard metric series for a 3.5 mm cutter on a
    # 6 mm shank. Anything measured off this record's lengths is measuring the
    # fill-in, not the reference.
    "35AM34": {
        "sku": "35AM34",
        "Item": "Carbide End Mill",
        "Milling Dia.": "3.5 mm",
        "Shank Dia.": "6 mm",
        "Length of Cut": "10 mm",
        "Overall Length": "57 mm",
        "Number of Flutes": "4",
        "Helix Angle": "30 Degrees",
        "Finish": "AlTiN",
        "System of Measurement": "Metric",
    },
    "26LD37": {
        "sku": "26LD37",
        "Item": "Socket Flat Head Cap Screw",
        "Screw Style": "Socket Flat Head Cap Screw",
        "Screw Head Type": "Flat",
        "Dia./Thread Size": "#10-32",
        "Length": "1/2 in",
        "Drive Type": "Hex Socket",
        "Drive Size": "1/8 in",
        "Head Dia.": "0.411 in",
        "Head Height": "0.127 in",
        "Thread Length": "1/2 in",
        "System of Measurement": "Inch",
    },
}
