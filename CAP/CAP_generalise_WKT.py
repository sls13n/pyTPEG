#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022-2024 TISA ASBL
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#   Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   Neither the name of the copyright holder nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; # OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Read in CAP situation publications, and generalise WKT polygon (reduce number of vertices in polygons)
#
# alert message assumed in root,

import os, sys, zipfile, optparse, glob
import xml, gzip, io
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
import CAP.geomet.wkt as wkt
from CAP_utils import generalise_polygon, XML_indent
from typing import List, Tuple, Dict, Optional, Union
from CAP_utils import Coordinate, Polygon, Polygons

if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + os.sep + os.pardir))


def parse_options() -> Tuple[optparse.Values, List[str]]:
    """
    Parse command line options for the CAP SHN to WKT converter.

    Returns:
        tuple: A tuple containing the options and arguments.
    """
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    # define defaults
    parser.set_defaults(suppress_errors=False,
                        DouglasPeucker=False,
                        Interpolate=False,
                        max_coords=300,
                        reduction_factor=1)  # no reduction

    #
    # binary options
    parser.add_option("-E", "--without_errors",
                      help="Suppress showing of errors (default %default)",
                      action="store_true", dest="suppress_errors")

    parser.add_option("-D", "--DouglasPeucker",
                      help="Generalise polygons with DouglasPeucker algorthim (default %default)",
                      action="store_true", dest="DouglasPeucker")

    parser.add_option("-I", "--Interpolate",
                      help="Generalise polygons for TPEG-OLR with max point distance(default %default)",
                      action="store_true", dest="Interpolate")

    # configuration options;
    parser.add_option("-N", "--max_coords",
                      help="set maximum number of coordinates per polygon (default %default)",
                      action="store", type="int", dest="max_coords")

    parser.add_option("-R", "--reduction_factor",
                      help="set reduction factor for number of coordinates per polygon, but at minimum max coords(default %default)",
                      action="store", type="int", dest="reduction_factor")

    parser.add_option("-U", "--output_dir",
                      help="Output directory for files created during conversion",
                      action="store", dest="output_dir")


    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        print("\n\n\n\n==> Nothing selected: Nothing done")
        exit(0)

    return options, args


def call_generalise_polygon(poly: Polygons) -> Tuple[Polygons, Polygon]:
    """
    This function generalises a polygon by reducing the number of coordinates based on the reduction factor and max_coords options.
    It also generalises any holes in the polygon.

    Args:
        poly: A list of lists representing a polygon and its holes. The first list is the polygon, and any subsequent lists are holes.

    Returns:
        A tuple containing two lists: the generalised holes and the generalised polygon.
    """
    max_coords = max(len(poly[0]) / options.reduction_factor,
                     options.max_coords) if options.reduction_factor > 1 else options.max_coords
    polygon = generalise_polygon(polygon=poly[0], maxcoords=max_coords, isHole=False,
                                 useDouglasPeucker=options.DouglasPeucker, interpolation=options.Interpolate)
    holes = [generalise_polygon(polygon=hole, maxcoords=max_coords, isHole=True,
                                useDouglasPeucker=options.DouglasPeucker, interpolation=options.Interpolate) for
             hole in poly[1:]]
    return holes, polygon


def generalise_geojson(geojson):
    """
    This function generalises a GeoJSON object. If the GeoJSON object is a MultiPolygon, it generalises each polygon.
    If the GeoJSON object is a Polygon, it generalises the polygon.

    Args:
        geojson: A dictionary representing a GeoJSON object.

    Returns:
        The generalised GeoJSON object.
    """
    if geojson["type"] in ["MultiPolygon"]:
        polygons = []
        for poly in geojson['coordinates']:
            # generalise polygons
            holes, polygon = call_generalise_polygon(poly)
            polygons.append([polygon] + holes)

        geojson['coordinates'] = polygons

    elif geojson["type"] == "Polygon":

        poly = geojson['coordinates']

        # generalise polygons
        holes, polygon = call_generalise_polygon(poly)

        geojson['coordinates'] = [polygon] + holes

    return geojson


def CAP_generalise_WKT_codes(file_string: str) -> str:
    """
    Replace WKT codes in the given CAP file string with generalised WKT polygons.

    Args:
        file_string (str): The CAP file content as a string.

    Returns:
        str: Updated XML string with WKT codes replaced by generalised WKT polygons.
    """
    capns = "{urn:oasis:names:tc:emergency:cap:1.2}"
    backup_capns = capns.replace("1.2", "1.1")  ## NWS still has 1.1

    root = xml.etree.ElementTree.fromstring(file_string)

    #
    # Determine alert top-level element
    model = None
    if root.tag == capns + "alert":
        model = root
    elif root.tag == backup_capns + "alert":
        model = root
        capns = backup_capns

    if model is None:
        print("No alert element found")
        return ""
    else:
        payload = model
        if payload is None:
            print("No Alert found")
            return ""

    #
    # here we have a valid list of CAP Alerts
    ID = 0
    for alert in [payload]:  # prepare also for future XML file with multiple Alerts

        for info in alert.findall(capns + "info"):
            for area in info.findall(capns + "area"):
                for geocode in area.findall(capns + "geocode"):
                    valueName = geocode.find(capns + "valueName").text
                    value = geocode.find(capns + "value").text

                    if geocode.find(capns + "valueName").text == "WKT":
                        # convert to geojson
                        geojson = wkt.loads(geocode.find(capns + "value").text)
                        # generalise
                        geojson = generalise_geojson(geojson)
                        # convert to WKT
                        geocode.find(capns + "value").text = wkt.dumps(geojson, decimals=10)

                        # now convert back to string again to be written als _WKT.cap file
    XML_indent(root)

    return tostring(root, encoding="unicode")
#    return tostring(root, encoding="UTF-8")


if __name__ == '__main__':
    # print "CAP parser
    options, args = parse_options()

    if options.suppress_errors:
        pass
        # TPEG_error_suppress_reports(options.suppress_errors)

    WKT_file_string = ""
    # process wild cards in arguments to obtain the list of frame files
    files = []
    for arg in args:
        files.extend(glob.glob(arg))

    for fname in files:
        print("\n\n===== Processing file", fname)

        if zipfile.is_zipfile(fname):
            fzip = zipfile.ZipFile(fname, "r")

            fnamelist = fzip.namelist()
            for zipfname in fnamelist:
                #
                if zipfname.endswith(os.sep):
                    continue  # skip directory names

                #
                frame_name = zipfname
                file_string = fzip.read(zipfname)
                #
                if zipfname.endswith(".gz"):  # gzipped
                    sIO = io.BytesIO(file_string)
                    gzip_file = gzip.GzipFile(fileobj=sIO, mode='rb')
                    file_string = gzip_file.read()
                    sIO.close()
                #
                WKT_file_string += CAP_generalise_WKT_codes(file_string)
                # print"\n\n"
            #
            fzip.close()
        elif fname.endswith(".gz"):  # gzipped
            with gzip.open(fname, 'rb') as f:
                file_string = f.read()
                WKT_file_string += CAP_generalise_WKT_codes(file_string)
                f.close()
        else:
            f = open(fname, "rb")
            if f:
                file_string = f.read()
                WKT_file_string += CAP_generalise_WKT_codes(file_string)
                f.close()
            else:
                print('==> ' + fname + ' could not be opened..')

        # remove file type and any directory info
        if os.sep in fname:
            [dirname, fname] = fname.rsplit(os.sep, 1)
            fname_stem = fname.rsplit('.', 1)[0]
            if options.output_dir:
              dirname = options.output_dir
            xml_fname_stem = dirname + os.sep + fname_stem + "_generalised"
        else:
            fname_stem = fname.rsplit('.', 1)[0]
            if options.output_dir:
              dirname = options.output_dir + os.sep
            else:
              dirname = ""
            xml_fname_stem = dirname + fname_stem + "_generalised"

        xml_fnames = []
        xml_fname = xml_fname_stem + ".cap"
        xml_fnames.append(xml_fname)

        f = open(xml_fname, "w")
        if f:
            f.write(WKT_file_string)
            f.close()
            print("\nfile", xml_fname, "created")

        print("\n===== File processing finished: " + fname + " ====\n")
