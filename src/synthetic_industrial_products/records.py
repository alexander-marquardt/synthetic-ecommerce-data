"""Reference records used as fixtures.

**These are OBSERVED records, not this catalog's convention.** Their values
were read off reference pages and are kept verbatim -- the trailing periods in
the attribute names, and the inconsistent unit spellings across the set
(``1/2 in`` in one record beside ``0.411 in`` in the same one beside ``3/8"``
in another). Their hashes are in the committed reference fingerprints and the
non-copying audit compares generated records against them, so editing a value
here would silently weaken that audit. Nothing in this file may be tidied.

What that verbatim-ness is evidence OF, and what it is not:

* it IS evidence that a renderer must read published names and values as they
  come. A renderer that only works against normalised input does not work
  against a real catalog, and these fixtures are what proves it does.
* it is NOT a licence for the GENERATOR to publish one magnitude several ways.
  These five records came from five different pages of different eras; the
  variation is BETWEEN sources. The generator used to reproduce it WITHIN one
  column of one catalog, which is a different thing and is the defect ruled
  out by elastic/prism#9284 -- it fragmented every dimensional facet roughly
  threefold and matched nothing in the reference distributor's own data, whose facet values
  carry one spelling each.

The generator now publishes exactly one spelling per magnitude per unit
system: see :mod:`synthetic_industrial_products.catalog.formats`. If you are
here because you are adding a fixture, keep it verbatim. If you are here
because you are changing what the generator EMITS, this is the wrong file.
"""

from __future__ import annotations

from typing import Any

Record = dict[str, Any]

#: Four end mills and one cap screw, spanning the cases a renderer must survive:
#: mixed-number lengths, a metric record, and a tool whose cutting and shank
#: diameters carry the same value.
#:
#: Note what these four end mills do NOT carry: ``End Mill Style``. The
#: renderer requires it -- a square end and a ball nose are different tools and
#: a drawing has to pick one -- so these four are now drawn as their product
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
#: file, and the non-copying audit compares generated records against them.
#: :data:`GENERATED` below is a different thing and is kept out of this name for
#: exactly that reason -- a generated record put in here would collide with the
#: catalog it came from and turn the audit into a false alarm.
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


#: One record per remaining product type, so that every renderer and every type
#: drawing has a fixture to exercise it.
#:
#: **These were not observed.** They are verbatim snapshots of records this
#: repository's own generator produced at its default seed -- which is why
#: their attribute sets are ragged and one of them publishes a thread longer
#: than its tap. Nothing here was read off a reference page, and nothing here
#: should be quoted as evidence about what a real catalog publishes; for that,
#: the statistics under ``reference-statistics`` are the source.
#:
#: The mix is deliberate. Four can be drawn to scale; four cannot, one for each
#: way a record refuses -- an absent attribute, a value with no unit, a pair
#: that contradicts itself, and a product type whose geometry no attribute
#: determines.
GENERATED: dict[str, Record] = {
    # Drawn to scale.
    # Five end mills, because one end mill does not exercise an end mill. The
    # cutting end, the hand of the helix, the number of cutting ends and the
    # corner radius are four separate things the record decides, and the
    # renderer drew a square, right-hand, single-ended, sharp-cornered tool for
    # every record until each of them was read.
    "26VW40": {
        "sku": "26VW40",
        "Item": "Solid Carbide Square End Mill",
        "End Mill Style": "Square",
        "End Mill Material": "Solid Carbide",
        "Number of Flutes": "4",
        "Helix Angle": "45 Degrees",
        "Cutting Direction": "Right Hand",
        "Single End/Double End": "Single End",
        "Coolant Fed": "Non-Coolant Through",
        "List Number": "K115",
        "Standards": "REACH",
        "Milling Dia.": '9/32"',
        "Shank Dia.": '5/16"',
        "Length of Cut": '7/8"',
        "Overall Length": '1-5/8"',
    },
    "52BN29": {
        "sku": "52BN29",
        "Item": "End Mill",
        "End Mill Style": "Ball Nose",
        "End Mill Material": "Cobalt",
        "Finish - Machining": "AlTiN",
        "Number of Flutes": "4",
        "Helix Angle": "35 Degrees",
        "Cutting Direction": "Right Hand",
        "Single End/Double End": "Single End",
        "End Mill Cutting Type": "Center Cutting",
        "End Mill Application": "Roughing/Finishing",
        "Milling Dia.": '1/4"',
        "Shank Dia.": '1/4"',
        "Length of Cut": '3/8"',
        "Overall Length": '1-1/2"',
    },
    "77VV89": {
        "sku": "77VV89",
        "Item": "Cobalt Square End Mill",
        "End Mill Style": "Square",
        "Finish - Machining": "nACo",
        "Number of Flutes": "3",
        "Helix Angle": "35 Degrees",
        "Cutting Direction": "Right Hand",
        "Single End/Double End": "Double End",
        "End Mill Application": "Roughing/Finishing",
        "Standards": "DIN 6527",
        "Milling Dia.": "8.00mm",
        "Shank Dia.": "8.00mm",
        "Length of Cut": "12.00mm",
        "Overall Length": "38.00mm",
        "Neck Length": "15.20mm",
        "Dimension Type": "Metric",
    },
    "60AR50": {
        "sku": "60AR50",
        "Item": "High Speed Steel Square End Mill",
        "End Mill Style": "Square",
        "End Mill Material": "High Speed Steel",
        "Finish - Machining": "AlTiN",
        "Number of Flutes": "4",
        "Helix Angle": "35 Degrees",
        "Cutting Direction": "Right Hand",
        "List Number": "K663",
        "Standards": "REACH",
        "Milling Dia.": "12.00mm",
        "Shank Dia.": "12.00mm",
        "Length of Cut": "48.00mm",
        "Overall Length": "78.00mm",
        "Corner Radius": "0.75mm",
    },
    "83LZ75": {
        "sku": "83LZ75",
        "Item": "Cobalt Square End Mill",
        "End Mill Style": "Square",
        "End Mill Material": "Cobalt",
        "Finish - Machining": "Uncoated",
        "Number of Flutes": "2",
        "Helix Angle": "30 Degrees",
        "Cutting Direction": "Left Hand",
        "Single End/Double End": "Single End",
        "End Mill Application": "Roughing",
        "Material Grade - Machining": "General Purpose",
        "Coolant Fed": "Non-Coolant Through",
        "List Number": "P630",
        "Milling Dia.": "1/2in",
        "Shank Dia.": "1/2in",
        "Length of Cut": "2in",
        "Overall Length": "3-1/4in",
    },
    "42SR26": {
        "sku": "42SR26",
        "Item": "Jobber Length Drill Bit",
        "Drill Bit Material": "Solid Carbide",
        "Drill Point Type": "Split Point",
        "Point Angle": "118 Degrees",
        "Drill Bit Finish": "TiN",
        "Shank Type": "Reduced",
        "Drill Size": '15/32"',
        "Flute Length": '4"',
        "Overall Length": '5-7/8"',
        "Shank Dia.": '15/32"',
        "Dimension Type": "Fractional Inch",
    },
    "65NL78": {
        "sku": "65NL78",
        "Item": "Spiral Point Tap",
        "Tap Style": "Spiral Point",
        "Tap Material": "High Speed Steel",
        "Tap Finish": "TiN",
        "Thread Type": "UNC",
        "Number of Flutes": "3",
        "Standards": "DIN 6527",
        "Thread Size": "#10-32",
        "Pitch": "32",
        "Overall Length": '1.8000"',
        "Thread Length": '0.8100"',
        "Shank Dia.": '0.1710"',
        "Dimension Type": "Fractional Inch",
    },
    "57KY59": {
        "sku": "57KY59",
        "Item": "Flat Washer",
        "Washer Type": "Plain",
        "Fastener Material": "18-8 Stainless Steel",
        "Standards": "RoHS 2011/65/EU",
        "Washer Size": "M8",
        "Inside Dia.": "8.40 mm",
        "Outside Dia.": "16.00 mm",
        "Thickness": "1.60 mm",
        "Dimension Type": "Metric",
    },
    "96HD84": {
        "sku": "96HD84",
        "Item": "Flap Disc",
        "Abrasive Material": "Zirconia Alumina",
        "Backing Material": "Fiberglass",
        "Flap Disc Shape": "Type 29 Conical",
        "Grit": "36",
        "Disc Dia.": '4-1/2"',
        "Arbor Hole Size": '7/8"',
        "Max. RPM": "10,700",
        "Dimension Type": "Fractional Inch",
    },
    # Refused, and so drawn as their type. One per way of refusing.
    # No Shank Dia.: a jobber drill's shank is usually its nominal size, but
    # "usually" is not this record.
    "56FL37": {
        "sku": "56FL37",
        "Item": "Jobber Length Drill Bit",
        "Drill Bit Material": "Solid Carbide",
        "Drill Point Type": "Split Point",
        "Point Angle": "118 Degrees",
        "Drill Bit Finish": "TiN",
        "Shank Type": "Reduced",
        "Drill Size": '7/16"',
        "Flute Length": '3-15/16"',
        "Overall Length": '5-11/16"',
        "Decimal Equivalent": "0.4375",
    },
    # A thread longer than the tap it is cut on.
    "77HW11": {
        "sku": "77HW11",
        "Item": "Spiral Point Tap",
        "Tap Style": "Spiral Point",
        "Tap Material": "High Speed Steel",
        "Tap Finish": "TiN",
        "Thread Type": "UNC",
        "Number of Flutes": "3",
        "Standards": "DIN 6527",
        "Thread Size": "#6-32",
        "Pitch": "32",
        "Overall Length": '1.8000"',
        "Thread Length": "2.90 in",
        "Shank Dia.": '0.1242"',
    },
    # Bare numbers: 4-1/2 of what?
    "44LU90": {
        "sku": "44LU90",
        "Item": "Flap Disc",
        "Abrasive Material": "Zirconia Alumina",
        "Backing Material": "Fiberglass",
        "Flap Disc Shape": "Type 29 Conical",
        "Grit": "40",
        "Disc Dia.": "4-1/2",
        "Arbor Hole Size": "7/8",
        "Max. RPM": "10,700",
        "Dimension Type": "Fractional Inch",
    },
    # Complete, well-formed, and still undrawable to scale: see render/hammer.py.
    "2DY27": {
        "sku": "2DY27",
        "Item": "Ball Pein Hammer",
        "Hammer Head Material": "Forged Steel",
        "Handle Material": "Steel",
        "Hammer Face Type": "Ball Pein",
        "Standards": "ASME B107.400",
        "Head Weight": "4 oz",
        "Overall Length": '10-5/8"',
        "Face Dia.": '0.6800"',
        "Handle Length": '9-1/8"',
        "Measurement System": "Fractional Inch",
    },
}

#: Every record that ships with the package: the observed reference records and
#: the generated samples together. ``sip-render fixtures`` draws all of them.
#: Anything that needs the REFERENCE records specifically -- the non-copying
#: audit above all -- wants :data:`FIXTURES`, not this.
BUNDLED: dict[str, Record] = {**FIXTURES, **GENERATED}

#: The bundled records that no drawing is true of.
#:
#: Both drawings an end mill can get -- the dimensioned one and the generic one
#: -- have to know whether the cutting end is square or a ball nose, and these
#: four publish no ``End Mill Style``. There is no third drawing that is true
#: of "an end mill, end unknown", so these four get no image, which is the
#: right answer and not a gap. See the note on :data:`FIXTURES`.
NO_IMAGE: frozenset[str] = frozenset({"4LU10", "438D34", "33TN24", "35AM34"})

#: Every bundled record that does produce an image.
DRAWABLE: dict[str, Record] = {k: v for k, v in BUNDLED.items() if k not in NO_IMAGE}
