"""The observed reference records.

**These are OBSERVED records, not this catalog's convention.** Their values
were read off reference pages and are kept verbatim -- the trailing periods in
the attribute names, and the inconsistent unit spellings across the set
(``1/2 in`` in one record beside ``0.411 in`` in the same one beside ``3/8"``
in another). Their hashes are in the committed reference fingerprints and the
non-copying audit compares generated records against them, so editing a value
here would silently weaken that audit. Nothing in this file may be tidied.

What that verbatim-ness is evidence OF, and what it is not:

* it IS evidence that a drawing must read published names and values as they
  come. A drawing that only works against normalised input does not work
  against a real catalog, and these records are what proves it does.
* it is NOT a licence for the GENERATOR to publish one magnitude several ways.
  These five records came from five different pages of different eras; the
  variation is BETWEEN sources. The generator used to reproduce it WITHIN one
  column of one catalog, which is a different thing and is the defect ruled
  out by elastic/prism#9284 -- it fragmented every dimensional facet roughly
  threefold and matched nothing in the reference distributor's own data, whose facet values
  carry one spelling each.

The generator now publishes exactly one spelling per magnitude per unit
system: see :mod:`synthetic_ecommerce_data.core.formats`. If you are
here because you are adding a fixture, keep it verbatim. If you are here
because you are changing what the generator EMITS, this is the wrong file.
"""

from __future__ import annotations

from typing import Any

Record = dict[str, Any]

#: Four end mills and one cap screw, spanning the cases a drawing must survive:
#: mixed-number lengths, a metric record, and a tool whose cutting and shank
#: diameters carry the same value.
#:
#: Note what these four end mills do NOT carry: ``End Mill Style``. The
#: drawing requires it -- a square end and a ball nose are different tools and
#: a drawing has to pick one -- so these four are drawn as their product
#: type rather than to scale. That is the rule working, not a regression: the
#: value was never transcribed off the page and inventing one here would put a
#: cutting end on the drawing that no record asserts. The census
#: (``00_attribute_name_census.json``) has 132 records carrying ``End Mill
#: Style`` against 129 carrying ``Milling Dia.``, so a real end-mill record
#: does publish it; these fixtures were assembled to exercise the dimension
#: parser and stopped at the dimensions.
#:
#: These five are the OBSERVED ones: their attribute names and values were read
#: off reference pages, their hashes are in the committed reference fingerprint
#: file, and the non-copying audit compares generated records against them. A
#: generated record put in here would collide with the catalog it came from and
#: turn the audit into a false alarm.
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
