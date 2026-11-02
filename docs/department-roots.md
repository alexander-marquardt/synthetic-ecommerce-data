# Every path starts at its department

The top level of every `category_path`, industrial and retail alike, is the store's department,
from the closed list in `core/departments.py`; there is no `department` field (the 2026-10-28
ruling on #125, after gen#281). Industrial types author their paths from their root down
(`Milling > End mills > Square end mills`), and `domains/industrial/taxonomy.DEPARTMENT_OF` files
each root under Hardware, Tools or Workshop & safety, so the document reads `Tools > Milling > End
mills > Square end mills`. A root with no row is refused, and `core/standard.check_catalog`
refuses a top level off the list for any domain. The table was the catalogue repository's
(`INDUSTRIAL_DEPARTMENTS`, which re-rooted every industrial path at load) until it moved here.
