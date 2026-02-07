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
# This script reads in CAP (Common Alerting Protocol) messages and generates a KML (Keyhole Markup Language) file.
# It handles CAP alerts, areas, and geo-coordinates, including bounding boxes and polygons.
# The output KML file is placed in the same directory as the input CAP file.

import os, sys, zipfile, random, math, optparse, glob, datetime
import xml, gzip, io
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from CAP.CAP_alert_component import CAP_alert_component
from typing import List, Tuple, Optional
from CAP_utils import generalise_polygon, WGS84_offset, get_optional_element, XML_indent, CAP_parse_AlertMessages
from CAP_utils import Coordinate, Polygon, Polygons

if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + os.sep + os.pardir))


def parse_options() -> Tuple[optparse.Values, List[str]]:
    """
    Parse command line options for the CAP_to_KML tool.
    Defines various options for handling the creation of KML files from CAP messages.

    Returns:
        A tuple of parsed options and the list of arguments.
    """
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    # define defaults for various options like bounding box, Douglas-Peucker algorithm, etc.
    parser.set_defaults(suppress_errors=False,
                        DouglasPeucker=False,
                        version_check=False,
                        all_areas=False,
                        bbox=False,
                        offset_dist=40000,  # 40 km
                        max_coords=1000000,  # 1 million, effectively no limit
                        reduction_factor=1,  # no reduction
                        KMZ=False,  # compression
                        offset=False)

    # Command line options for customizing the KML generation process
    parser.add_option("-B", "--bounding_box", help="Add bounding box (default %default)", action="store_true",
                      dest="bbox")
    parser.add_option("-D", "--DouglasPeucker",
                      help="Generalise polygons with DouglasPeucker algorithm (default %default)", action="store_true",
                      dest="DouglasPeucker")
    parser.add_option("-E", "--without_errors", help="Suppress showing of errors (default %default)",
                      action="store_true", dest="suppress_errors")
    parser.add_option("-V", "--Version", help="print version increase information (default %default)",
                      action="store_true", dest="version_check")
    parser.add_option("-A", "--All", help="show all areas (default %default)", action="store_true", dest="all_areas")
    parser.add_option("-N", "--max_coords", help="set maximum number of coordinates per polygon (default %default)",
                      action="store", type="int", dest="max_coords")
    parser.add_option("-R", "--reduction_factor",
                      help="set reduction factor for number of coordinates per polygon (default %default)",
                      action="store", type="int", dest="reduction_factor")
    parser.add_option("-O", "--offset_dist",
                      help="set offset distance (meters) for bounding box beyond affected areas (default %default)",
                      action="store", type="int", dest="offset_dist")
    parser.add_option("-K", "--no KMZ file", help="Do not write a KMZ file (default %default)", action="store_false",
                      dest="KMZ")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        ## print "\n\n\n\n==> Nothing selected: SRTI feed chosen as default"
        ## options.ftp = options.SRTI_ftp = True
        print("\n\n\n\n==> Nothing selected: Nothing done")
        exit(0)

    return options, args


def KML_set_document_name_KML(tree: ElementTree, docname: str) -> None:
    """
    Set the name of the KML document within the given XML tree.

    Args:
        tree: The XML tree containing the KML structure.
        docname: The name to set for the KML document.
    """
    root = tree.getroot()
    ns = '{http://www.opengis.net/kml/2.2}'
    document = root.find(ns + 'Document')

    name = document.find(ns + 'name')
    if name is not None:
        name.text = docname


def KML_add_point_to_KML(tree: ElementTree, ID: int, coord: Coordinate, name: str = "CAPmessage",
                         description: Optional[str] = None, icon: Optional[str] = None) -> None:
    """
    Add a point (placemark) to the KML document at the given coordinate.

    Args:
        tree: The KML document's XML tree.
        ID: The ID for the placemark.
        coord: The coordinate (latitude, longitude) where the point should be placed.
        name: The name of the point.
        description: A description for the point, if any.
        icon: The icon to use for the point, if any.
    """
    root = tree.getroot()
    ns = '{http://www.opengis.net/kml/2.2}'
    document = root.find(ns + 'Document')

    # Add placemark element to document
    submarket = SubElement(document, ns + "Placemark")

    # Set placemark name and description
    sub_el = SubElement(submarket, ns + "name")
    sub_el.text = name + " " + str(ID)

    if description:
        sub_el = SubElement(submarket, ns + "description")
        sub_el.text = description

    # Set placemark visibility
    sub_el = SubElement(submarket, ns + "visibility")
    sub_el.text = "1"

    # Set placemark icon based on type
    sub_el = SubElement(submarket, ns + "styleUrl")
    sub_el.text = "#downArrowIcon"  # default icon
    if icon == "T":
        sub_el.text = "#trafficIcon"
    elif icon == "TA":
        sub_el.text = "#trafficWithAccidentIcon"

    # Set placemark coordinates (latitude, longitude)
    Point = SubElement(submarket, ns + "Point")
    sub_el = SubElement(Point, ns + "altitudeMode")
    sub_el.text = "clampToGround"
    coords = SubElement(Point, ns + "coordinates")
    lat = str(coord[0])
    lon = str(coord[1])
    coords.text = lon + "," + lat


def KML_add_line_to_KML(tree: ElementTree, ID: int, color: int, line: Polygon, name: str = "CAPmessage",
                        description: str = None) -> None:
    """
    Add a line (placemark) to the KML document using the given coordinates.

    Args:
        tree: The KML document's XML tree.
        ID: The ID for the placemark.
        color: The color of the line (as an integer key).
        line: The list of coordinates defining the line.
        name: The name of the line.
        description: A description for the line, if any.
    """
    # Dictionary mapping color codes to KML line styles
    colordict = {255: "#TecLine",
                 6: "#BlackLine",
                 5: "#RedLine",
                 4: "#OrangeLine",
                 3: "#YellowLine",
                 2: "#DarkGreenLine",
                 1: "#GreenLine"
                 }

    root = tree.getroot()
    ns = '{http://www.opengis.net/kml/2.2}'
    document = root.find(ns + 'Document')

    # Add placemark element to document
    submarket = SubElement(document, ns + "Placemark")

    # Set placemark name and description
    sub_el = SubElement(submarket, ns + "name")
    sub_el.text = name + " " + str(ID)

    if description:
        sub_el = SubElement(submarket, ns + "description")
        sub_el.text = description

    # Set placemark visibility
    sub_el = SubElement(submarket, ns + "visibility")
    sub_el.text = "1"

    # Set placemark style based on color key
    sub_el = SubElement(submarket, ns + "styleUrl")
    sub_el.text = colordict.get(color, "#GreenLine")  # Default to green line if color not found

    # Define the line geometry (altitude mode and tessellation for smoother rendering)
    LineString = SubElement(submarket, ns + "LineString")
    sub_el = SubElement(LineString, ns + "altitudeMode")
    sub_el.text = "clampToGround"
    sub_el = SubElement(LineString, ns + "tesselate")
    sub_el.text = "1"

    # Set the coordinates for the line
    coords = SubElement(LineString, ns + "coordinates")
    lat = str(line[0][0])
    lon = str(line[0][1])
    coords.text = lon + "," + lat  # Start with the first coordinate

    # Add the remaining coordinates to the KML line
    for coord in line[1:]:
        lat = str(coord[0])
        lon = str(coord[1])
        coords.text += ",\n" + lon + "," + lat


# polygon and holes most be closed rings (last coordinate == first coordinate!
def KML_add_polygon_to_KML(tree: ElementTree, ID: str, color: str, polygon: Polygon, holes: Polygons,
                           name: str = "CAPmessage", description: Optional[str] = None) -> None:
    """
    Add a polygon (with optional holes) to the KML document.

    Args:
        tree: The KML document's XML tree.
        ID: The ID for the placemark.
        color: The color of the polygon.
        polygon: The list of coordinates defining the outer boundary of the polygon.
        holes: The list of polygons defining the holes within the polygon.
        name: The name of the polygon.
        description: A description for the polygon, if any.
    """
    root = tree.getroot()
    ns = '{http://www.opengis.net/kml/2.2}'
    document = root.find(ns + 'Document')

    # Add placemark element to document
    submarket = SubElement(document, ns + "Placemark")

    # Set placemark name and description
    sub_el = SubElement(submarket, ns + "name")
    sub_el.text = ID
    sub_el = SubElement(submarket, ns + "description")
    sub_el.text = description if description else ""

    # Set placemark visibility
    sub_el = SubElement(submarket, ns + "visibility")
    sub_el.text = "1"

    # Set random style for the polygon
    sub_el = SubElement(submarket, ns + "styleUrl")
    sub_el.text = random.choice(["#transBluePoly", "#transRedPoly", "#transGreenPoly", "#transYellowPoly"])

    # Define polygon geometry (altitude mode)
    PolygonEl = SubElement(submarket, ns + "Polygon")
    sub_el = SubElement(PolygonEl, ns + "altitudeMode")
    sub_el.text = "clampToGround"

    # Define the outer boundary of the polygon
    sub_el = SubElement(PolygonEl, ns + "outerBoundaryIs")
    sub_el = SubElement(sub_el, ns + "LinearRing")
    coords = SubElement(sub_el, ns + "coordinates")
    coords.text = ''

    # Set the coordinates for the outer boundary
    for coord in polygon:
        coords.text += '\n\t\t ' + str(coord[0]) + "," + str(coord[1]) + " "
    coords.text += '\n\t\t'

    # Define any holes (inner boundaries) in the polygon
    for hole in holes:
        sub_el = SubElement(PolygonEl, ns + "innerBoundaryIs")
        sub_el = SubElement(sub_el, ns + "LinearRing")
        coords = SubElement(sub_el, ns + "coordinates")
        coords.text = ''

        # Set the coordinates for each hole
        for coord in hole:
            coords.text += '\n\t\t ' + str(coord[0]) + "," + str(coord[1]) + " "
        coords.text += '\n\t\t'


def CAP_create_KML_for_CAP(tree: ElementTree, CAPmessages: dict) -> None:
    """
    Create a KML document based on the provided CAP messages.

    Args:
        tree: The XML tree of the KML document.
        CAPmessages: A dictionary of CAP messages to include in the KML.
    """

    # Iterate over each CAP message in the dictionary
    for messageID in CAPmessages:
        AlertMsg = CAPmessages[messageID]

        # Create an alert name based on the message ID
        CAPalert = "Alert " + str(messageID)

        # Extract the CAP_info elements from the alert message
        CAPinfos = [info for info in AlertMsg.subcomponents if info.type == "CAP_info"]

        # Debug print the number of CAP_info elements found
        print("num CAPinfo's", len(CAPinfos))

        # Ensure there is at least one CAP_info element; stop processing if none found
        if CAPinfos:
            CAPinfo = CAPinfos[0]
        else:
            print("NO CAP info element, stopping...")
            return

        # Extract CAP_area elements from the CAP_info
        CAPareas = [x for x in CAPinfo.subcomponents if x.type == "CAP_area"]

        print("num CAPareas", len(CAPareas))

        # If no CAP_area elements found, stop processing
        if not CAPareas:
            print("NO CAP area element, stopping...")
            return

        # If the `all_areas` option is not selected, only process the first CAP_area
        if not options.all_areas:
            CAPareas = [CAPareas[0]]

        # Iterate over each CAP_area
        for CAParea in CAPareas:

            ## CAPinfos  = [info for info in AlertMsg.subcomponents if info.type == "CAP_info"]
            ## CAPinfo   = CAPinfos[0]

            ## CAPareas  = [area for area in CAPinfo.subcomponents  if area.type == "CAP_area"]
            ## CAParea   = CAPareas[0]

            description = ""
            # Build a description string for the CAP_area using various attributes from CAP_info and CAP_area
            description = "..headline = " + get_optional_element(CAPinfo, "headline") + '\n'
            description += ".....event = " + CAPinfo.event + '\n'
            description += ".......area = " + CAParea.areaDesc + '\n\n'
            description += AlertMsg.out(["web", "uri", "WKT", "SAME", "SHN", "warnVerwaltungsbereiche"])

            # Remove http[s] tags, so that Google Earth does not screw up formatting
            description = description.replace("http://", "").replace("https://", "")

            # icon = "T"
            # KML_add_point_to_KML(tree, messageID, coord, name="", description = string_to_ascii(description),icon=icon)
            # KML_add_point_to_KML(tree, messageID, coord, name="", description = string_to_ascii(description),icon=icon)

            # Set to false initially; add bounding box, if set to true
            bbset = False

            # Initialize list of polygons (and holes) from geojson areas if available
            polygons: Polygons = []
            if CAParea.geojson_areas:
                for geojson_area in CAParea.geojson_areas:

                    # If area type is "MultiPolygon", process each polygon
                    if geojson_area["type"] == "MultiPolygon":
                        for poly in geojson_area['coordinates']:

                            if options.reduction_factor > 1:
                                polygon = generalise_polygon(polygon=poly[0], maxcoords=max(len(poly[0]) // options.reduction_factor,
                                                                          options.max_coords), isHole=False, useDouglasPeucker=options.DouglasPeucker)
                                holes = [generalise_polygon(polygon=hole, maxcoords=max(len(hole) // options.reduction_factor,
                                                                      options.max_coords), isHole=True, useDouglasPeucker=options.DouglasPeucker) for hole in poly[1:]]
                            else:
                                polygon = generalise_polygon(polygon=poly[0], maxcoords=options.max_coords, isHole=False, useDouglasPeucker=options.DouglasPeucker)
                                holes = [generalise_polygon(polygon=hole, maxcoords=options.max_coords, isHole=True, useDouglasPeucker=options.DouglasPeucker) for hole in poly[1:]]

                            polygons.append([polygon, holes])

                            # Determine bounding box on the generalized polygon
                            for coord in polygon:
                                [lon, lat] = coord
                                if bbset:
                                    if lon < minlon: minlon = lon
                                    if lon > maxlon: maxlon = lon
                                    if lat < minlat: minlat = lat
                                    if lat > maxlat: maxlat = lat
                                else:
                                    minlon = maxlon = lon
                                    minlat = maxlat = lat
                                    bbset = True

                    # If area type is "Polygon", process the polygon
                    elif geojson_area["type"] == "Polygon":
                        poly = geojson_area['coordinates']
                        if options.reduction_factor > 1:
                            polygon = generalise_polygon(polygon=poly[0], maxcoords=max(len(poly[0]) // options.reduction_factor,
                                                                      options.max_coords), isHole=False, useDouglasPeucker=options.DouglasPeucker)
                            holes = [
                                generalise_polygon(polygon=hole, maxcoords=max(len(hole) // options.reduction_factor, options.max_coords),
                                                   isHole=True, useDouglasPeucker=options.DouglasPeucker) for hole in poly[1:]]
                        else:
                            # Process without reduction
                            polygon = generalise_polygon(polygon=poly[0], maxcoords=options.max_coords, isHole=False, useDouglasPeucker=options.DouglasPeucker)
                            holes = [generalise_polygon(polygon=hole, maxcoords=options.max_coords, isHole=True, useDouglasPeucker=options.DouglasPeucker) for hole in poly[1:]]

                        polygons.append([polygon, holes])

                        # Determine bounding box on the generalized polygon
                        for coord in polygon:
                            [lon, lat] = coord
                            if bbset:
                                if lon < minlon: minlon = lon
                                if lon > maxlon: maxlon = lon
                                if lat < minlat: minlat = lat
                                if lat > maxlat: maxlat = lat
                            else:
                                # Set initial bounding box values
                                minlon = maxlon = lon
                                minlat = maxlat = lat
                                bbset = True

                    # If area type is "Circle", process the circle
                    elif geojson_area["type"] == "Circle":
                        centercoord = geojson_area['coordinates']
                        radius = geojson_area['radius'] * 1000.0  # Convert radius to meters

                        # Calculate local bounding box for the circle
                        [lon, lat] = centercoord
                        [c_minlat, c_minlon] = WGS84_offset([lat, lon], -radius, -radius)
                        [c_maxlat, c_maxlon] = WGS84_offset([lat, lon], radius, radius)

                        # Adjust the global bounding box based on the circle
                        if bbset:
                            if c_minlon < minlon: minlon = c_minlon
                            if c_maxlon > maxlon: maxlon = c_maxlon
                            if c_minlat < minlat: minlat = c_minlat
                            if c_maxlat > maxlat: maxlat = c_maxlat
                        else:
                            # Set initial bounding box values
                            minlon = c_minlon
                            maxlon = c_maxlon
                            minlat = c_minlat
                            maxlat = c_maxlat
                            bbset = True

                        # Now circle is transformed into tesselated polygon
                        lon = centercoord[0]
                        lat = centercoord[1]

                        # Local approximation of radius in delta_lon and delta_lat
                        delta_lat = 180.0 * radius / (math.pi * 6371000)  # radius translated in delta degrees latitude
                        delta_lon = delta_lat / math.cos(lat * math.pi / 180.0)

                        # Create the polygon approximation for the circle
                        polygon = []
                        step = 4
                        for i in range(0, 360 + step, step):  # include 360 degree == 0 degree
                            polygon.append([lon + delta_lon * math.cos(i * math.pi / 180.0),
                                            lat + delta_lat * math.sin(i * math.pi / 180.0)])

                        polygons.append([polygon, []])  # Add the circle polygon (no holes)

            else:  # If no geojson areas, use a default polygon (if needed)
                polygon = [
                    [4.676503, 52.970517],
                    [4.678503, 52.970517],
                    [4.678503, 52.980517],
                    [4.676503, 52.980517],
                    [4.676503, 52.970517]
                ]
                ## Comment below to get a "default" polygon
                polygon = []
                holes = []
                polygons = [[polygon, holes]]

            # Skip if no valid polygons are found or if `all_areas` is disabled and no valid polygons exist
            if not options.all_areas or (len(polygons) > 0 and len(polygons[0][0]) > 0):
                pass

            print("Num polygons", len(polygons))

            # Process each polygon and add to KML
            for [polygon, holes] in polygons:
                if options.all_areas and len(polygon) == 0:
                    continue  # Skip empty polygons
                if holes:
                    print("Polygon with %d coordinates, %d hole(s) with in total %d coordinates" % (
                        len(polygon), len(holes), sum(map(len, holes))))
                else:
                    print("Polygon with %d coordinates" % (len(polygon)))

                # Add the polygon to the KML document
                KML_add_polygon_to_KML(tree, messageID, "Blue", polygon, holes, name=CAPalert,
                                       description=description)  # = string_to_ascii(description))

            # Add a bounding box to the KML document if it was set and the option is enabled
            if bbset and options.bbox:
                OFFSETDIST = options.offset_dist
                [minlat, minlon] = WGS84_offset([minlat, minlon], -OFFSETDIST, -OFFSETDIST)
                [maxlat, maxlon] = WGS84_offset([maxlat, maxlon], OFFSETDIST, OFFSETDIST)
                line = [[minlat, minlon], [minlat, maxlon], [maxlat, maxlon], [maxlat, minlon], [minlat, minlon]]

                # Add the bounding box as a line to the KML
                KML_add_line_to_KML(tree, messageID, 255, line, name="EAW boundingbox",
                                    description="offset distance %d meter" % OFFSETDIST)


def CAP_create_KML_file(fname: str, CAPmessages: dict, KMZ: bool = False) -> None:
    """
    Create a KML file from the provided CAP messages.

    Args:
        fname: The filename for the KML file.
        CAPmessages: A dictionary of CAP messages to include in the KML.
        KMZ: Whether to compress the file as a KMZ (default: False).
    """

    tree = ElementTree()
    # Parse the KML template file from the current directory
    tree.parse(os.path.abspath(sys.path[0] + os.sep + 'KML_template.kml'))

    KML_name = "CAP messages"

    ## if options.ftp: # add time stamp
    ##     t     = datetime.datetime.utcnow()
    ##     stime = t.strftime("%Y%m%dT%H%M")
    ##     KML_name += " at "+stime
    # Set the document name in the KML file
    KML_set_document_name_KML(tree, KML_name)

    # Create the KML content from the CAP messages
    CAP_create_KML_for_CAP(tree, CAPmessages)

    # Indent the XML tree for readability
    XML_indent(tree.getroot())

    # If the KMZ option is selected, compress the KML file into a KMZ archive
    if KMZ:
        fzipname = fname[:-1] + 'z'
        fzip = zipfile.ZipFile(fzipname, 'w', zipfile.ZIP_DEFLATED)

        # Write the KML content into the KMZ file
        fzip.writestr("CAP.kml", tostring(tree.getroot(), encoding="UTF-8", xml_declaration=True))
        fzip.close()
    else:
        # Otherwise, write the KML file normally
        tree.write(fname, encoding="UTF-8", xml_declaration=True)


def CAP_create_indented_XML(file_string: str) -> bytes:
    """
    Create an indented XML file from the given string content.

    Args:
        file_string: The original unindented XML content as a string.

    Returns:
        The indented XML content as a byte string.
    """

    tree = ElementTree()

    # Parse the input XML string into an ElementTree
    root = xml.etree.ElementTree.fromstring(file_string)

    # Indent the XML tree for better readability
    XML_indent(root)

    # Return the XML as a string with UTF-8 encoding
    return tostring(root, encoding="UTF-8")


if __name__ == '__main__':
    # Parse command line options
    options, args = parse_options()

    # If the suppress errors option is enabled, handle the errors quietly
    if options.suppress_errors:
        pass
        # TPEG_error_suppress_reports(options.suppress_errors)

    # Collect all files matching arguments (wildcard processing)
    files: List[str] = []
    for arg in args:
        files.extend(glob.glob(arg))

    # Loop through each file to process CAP messages
    for fname in files:
        print("\n\nProcessing file", fname)

        # Reset the CAP message dictionary for each file
        CAPmessagedict: dict = {}

        # Check if the file is a ZIP file
        if zipfile.is_zipfile(fname):
            with zipfile.ZipFile(fname, "r") as fzip:
                fnamelist: List[str] = fzip.namelist()
                # Loop through each file in the ZIP
                for zipfname in fnamelist:
                    if zipfname.endswith(os.sep):
                        continue  # Skip directories in ZIP file

                    file_string: bytes = fzip.read(zipfname)

                    # Handle gzipped files within the ZIP
                    if zipfname.endswith(".gz"):
                        with io.BytesIO(file_string) as sIO:
                            with gzip.GzipFile(fileobj=sIO, mode='rb') as gzip_file:
                                file_string = gzip_file.read()

                    # Parse the alert messages if the file string is not empty
                    if len(file_string) > 0:
                        CAP_parse_AlertMessages(file_string, CAPmessagedict)

        # Handle standalone gzipped files
        elif fname.endswith(".gz"):
            with gzip.open(fname, 'rb') as f:
                file_string: bytes = f.read()
                if len(file_string) > 0:
                    CAP_parse_AlertMessages(file_string, CAPmessagedict)

        # Handle regular files
        else:
            with open(fname, "rb") as f:
                file_string: bytes = f.read()
                if len(file_string) > 0:
                    CAP_parse_AlertMessages(file_string, CAPmessagedict)
                else:
                    print(f'==> {fname} could not be opened..')

        # Set up the timestamp for the KML filename
        t: datetime.datetime = datetime.datetime.utcnow()
        stime: str = t.strftime("_%Y%m%dT%H%M%S")

        # Remove file type and directory info to create the output filename
        if os.sep in fname:
            dirname, fname = fname.rsplit(os.sep, 1)
            fname_stem = fname.rsplit('.', 1)[0]
            kml_fname_stem = dirname + os.sep + "CAP_KML_for_" + fname_stem + stime
        else:
            fname_stem = fname.rsplit('.', 1)[0]
            kml_fname_stem = "CAP_KML_for_" + fname_stem + stime

        # Determine if output should be KMZ or KML based on the options
        KML_ftype: str = '.kmz' if options.KMZ else '.kml'

        kml_fnames: List[str] = []
        kml_fname: str = kml_fname_stem + KML_ftype
        kml_fnames.append(kml_fname)

        print(kml_fname)

        # Create the KML file from the CAP messages
        CAP_create_KML_file(kml_fname, CAPmessagedict, KMZ=options.KMZ)

        # Print a summary of the file processing
        numVersions: int = 1
        # For message in CAPmessagedict.values():
        # numVersions += len(message["v"])

        print(f"\n\n======== Summary for file: {fname} ====\n")
        print(f"Number distinct CAP messages: {len(CAPmessagedict)}, avg. #versions {numVersions // max(1, len(CAPmessagedict))}")
