# End-mill run lines sell each diameter at several lengths (#850)

A query that names the size, such as `1/2 end mill`, reaches one SKU of a line that runs on
diameters alone, so each of its tiles grouped one SKU (#850). An end-mill run line therefore
sells each diameter at 1, 2 or 3 neighboring length classes (`REACH`: Stub, Regular and Long,
weighted 15/55/30%). Most tiles on a diameter query group 2 or 3 SKUs, and each title names the
length of cut. A diameter's lengths share its shank and corner radius, the neck follows the
length of cut, and each of those is stated on every SKU of the line or on none, so the product
page offers the diameter and the length and no third choice. The budget counts a line's sizes,
not its SKUs, so the type keeps its number of runs and each diameter's coverage. The end mills'
SKUs grow by the mean reach, and the PR for #850 states the build totals. The flat, must-stock
and pack lines are unchanged. Screws stay on the length axis alone, so a thread × length query
(`5/16-18 x 3/4`) still reaches one SKU per product.

Two records of a size would draw alike if the drawing had to refuse one of them, so a ball-nose line of several lengths states no corner radius (a ball nose has no corners) and any such line is single-ended (two lengths of cut do not fit a long class). A line of one length keeps both as it always did.
