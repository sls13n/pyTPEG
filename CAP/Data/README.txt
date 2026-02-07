Some of the German CAP messages have areas as in SHN area codes.

These need to be transformed into geographic shapes for TPEG2-EAW.

This page provides links to some resources to perform this transformation, (and also for processing WKT geometry descriptions).

SHN Code database for Germany
=============================
SHN code databases for Germany can be retrieved free-of-charge via Das Bundesamt für Kartographie und Geodäsie (BKG): 

https://gdz.bkg.bund.de/index.php/default/digitale-geodaten.html
https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete.html?___store=default


Use the "ebenen", "kompakt" is not complete!!
Use  level VG250, for municipalities at least
VG2500 do not have municipalities, but can be used for e.g. kreise, and bundeslander, and are more compact, requiring less generalisation



The latest shapefile version (version 1.1.2020 as of 26 Okt 2020 ) can be downloaded here as shape files:

1:250.000         https://gdz.bkg.bund.de/index.php/default/catalog/product/view/id/788/s/verwaltungsgebiete-1-250-000-ebenen-stand-01-01-vg250-ebenen-01-01.html
1:1.000.000:     https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete/verwaltungsgebiete-1-1-000-000-ebenen-stand-01-01-vg1000-ebenen-01-01.html
1:2.500.000:     https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete/verwaltungsgebiete-1-2-500-000-stand-01-01-vg2500.html


Python resources for processing Shape files
===========================================
Python code for shape files

https://github.com/GeospatialPython/pyshp#reading-shapefiles

Python code to convert UTM to WGS84
===================================
https://pypi.org/project/utm/ 
https://docs.obspy.org/tutorial/code_snippets/coordinate_conversions.html


Python resources for processing WKT geocodes
============================================
Python code to transform WKT codes into geojson

https://pypi.org/project/geomet/
