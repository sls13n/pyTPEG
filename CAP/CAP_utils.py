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
# This file contains utility functions used in CAP related scripts.
import math, xml
from EawUtils.DouglasPeucker import simplifyDouglasPeucker
from typing import List, Optional
from xml.etree.ElementTree import Element, ElementTree
from CAP.CAP_alert_component import CAP_alert_component

# Type Aliases
Coordinate = List[float]  # A single coordinate [latitude, longitude]
Polygon = List[Coordinate]  # A polygon is a list of coordinates (closed loop of [latitude, longitude])
Polygons = List[Polygon]  # A list of polygons (multi-polygon or holes)

def WGS84_distance(origin: Coordinate, destination: Coordinate) -> float:
    """
    Calculate the WGS84 distance between two coordinates in meters.

    Args:
        origin: A tuple representing the starting coordinate (latitude, longitude).
        destination: A tuple representing the destination coordinate (latitude, longitude).

    Returns:
        The distance between the two coordinates in meters.
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371000  # Earth radius in meters

    # Convert latitude/longitude differences to radians
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def WGS84_offset(origin: Coordinate, distanceNorthMeter: float, distanceEastMeter: float) -> Coordinate:
    """
    Calculate a new coordinate by applying an offset (in meters) from a given origin.

    Args:
        origin: The origin coordinate (latitude, longitude).
        distanceNorthMeter: The offset distance to the north in meters.
        distanceEastMeter: The offset distance to the east in meters.

    Returns:
        A new coordinate (latitude, longitude) after applying the offset.
    """
    lat1, lon1 = origin
    radius = 6371000  # Earth radius in meters

    # Calculate latitude and longitude offsets in radians
    distanceNorthRadian = (distanceNorthMeter) / (radius)
    distanceEastRadian = (distanceEastMeter) / (radius * math.cos(math.radians(lat1)))

    # Convert the offsets back to degrees
    destination = [lat1 + math.degrees(distanceNorthRadian), lon1 + math.degrees(distanceEastRadian)]

    return destination


def string_to_ascii(s: str) -> bytes:
    """
    Convert a string to an ASCII byte string, replacing any non-ASCII characters with '?'.

    Args:
        s: The input string to be converted.

    Returns:
        The ASCII-encoded byte string.
    """
    if type(s) == type('a'):
        return s.encode('ascii', 'replace')
    else:
        trans_table = ''.join([chr(i) for i in range(128)] + ['?'] * 128)
        return s.translate(trans_table)


def generalise_polygon(polygon: Polygon, maxcoords: int, isHole: bool, useDouglasPeucker: bool, interpolation: bool = False) -> Polygon:
    """
    Generalise a polygon by reducing the number of coordinates to a specified maximum.

    Args:
        polygon: The original polygon to be generalised.
        maxcoords: The maximum number of coordinates allowed in the generalised polygon.
        isHole: Whether the polygon is a hole (affects the print output).
        useDouglasPeucker: Whether to use DouglasPeucker algorithm for simplification.
        interpolation: Whether to interpolate the polygon so the points are not too far apart.

    Returns:
        The generalised polygon with at most `maxcoords` coordinates.
    """
    lenpoly = len(polygon)

    # If polygon has more coordinates than allowed, reduce the number of points
    if lenpoly > maxcoords:
        if isHole:
            print("Truncating inner polygon", lenpoly, "To max coords", maxcoords)
        else:
            print("Truncating outer polygon", lenpoly, "To max coords", maxcoords)

        # Use DouglasPeucker algorithm for simplification if it is required to do so
        if useDouglasPeucker:
            polygon = simplifyDouglasPeucker(polygon, maxcoords)
        else:
            print("Selected coords", maxcoords,
                  [int(0.5 + i * (lenpoly - 1) / (maxcoords - 1)) for i in range(0, maxcoords - 1)] + [
                      lenpoly - 1])
            # Select a set of coordinates by equally distributing points
            selected_coords = [int(0.5 + i * (lenpoly - 1) / maxcoords) for i in range(0, maxcoords - 1)]
            polygon = [polygon[idx] for idx in selected_coords] + [polygon[-1]]

    if interpolation:
        poly = polygon[:1]
        [oldlon, oldlat] = poly[0]
        for coord in polygon[1:]:
            [lon, lat] = coord

            # Check whether difference fits in a signed short for OLR!
            lonTL = int(1.0 + math.fabs(lon - oldlon) / 0.32767)
            lanTL = int(1.0 + math.fabs(lat - oldlat) / 0.32767)

            steps = max(lonTL, lanTL)
            if steps > 1:
                for i in range(1, steps):
                    print("Interpolating", i, steps, (lon - oldlon) / steps, (lat - oldlat) / steps, \
                          "org", (lon - oldlon), (lat - oldlat))
                    poly.append([oldlon + (lon - oldlon) / steps, oldlat + (lat - oldlat) / steps])
            #
            # add last coord
            poly.append([lon, lat])
            [oldlon, oldlat] = [lon, lat]

        polygon = poly

    return polygon


def get_optional_element(CAPcomponent: object, name: str, default: str = "") -> str:
    """
    Retrieve an optional element from a CAP component by name.

    Args:
        CAPcomponent: The CAP component from which to retrieve the element.
        name: The name of the element to retrieve.
        default: The default value to return if the element is not found.

    Returns:
        The value of the element if found, otherwise the default value.
    """
    el = [el for el in CAPcomponent.elements if el[0] == name]
    el = default if not el else el[0][1]
    return el


def XML_indent(elem: Element, level: int = 0) -> None:
    """
    Indent an XML tree element to make the XML output more readable.

    Args:
        elem: The root element of the XML tree to indent.
        level: The current indentation level.
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            XML_indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def load_payload_from_XML(file_string: str) -> (Element, str):
    """
    Load the payload from the given XML file string.

    Args:
        file_string: The XML file content as a string.

    Returns:
        The payload object and the CAP version as a string
    """
    # XML namespace definitions for CAP and fallback for older CAP version 1.1
    capns12 = "{urn:oasis:names:tc:emergency:cap:1.2}"
    capns11 = capns12.replace("1.2", "1.1")

    # Parse the XML file string into an ElementTree
    root = xml.etree.ElementTree.fromstring(file_string)

    # Determine which alert element is at the top level
    model = None
    CAPversion = "1.2"  # default CAP version
    if root.tag == capns12 + "alert":
        model = root
    elif root.tag == capns11 + "alert":
        model = root
        CAPversion = "1.1"

    # If no alert element is found, return None
    if model is None:
        print("No alert element found")
        return None, ""
    else:
        # Set the payload to the model and continue processing
        payload = model
        if payload is None:
            print("NoAlert found")
            return None, ""

    return payload, CAPversion


def CAP_parse_AlertMessages(file_string: str, CAPmessagedict: dict) -> Optional[object]:
    """
    Parse CAP alert messages from the given XML file string.

    Args:
        file_string: The XML file content as a string.

    Returns:
        The parsed alert message object, or None if parsing fails.
    """

    payload, CAPversion = load_payload_from_XML(file_string)

    if payload is None:
        return None

    # Initialize message ID counter
    ID = 0

    # Loop through the payload (preparing for future XML with multiple alerts)
    for alert in [payload]:
        ID += 1

        # Parse the alert using CAP_alert_component class
        CAPalert = CAP_alert_component(ID, CAPversion=CAPversion)
        CAPalert.parse(alert)

        AlertID = CAPalert.identifier
        AlertSent = CAPalert.sent

        # Check if the alert ID already exists in the CAP message dictionary
        AlertMSG = CAPmessagedict.get(AlertID, False)
        if AlertMSG:  # If it exists, update if the sent time differs
            if AlertSent != AlertMSG.sent:
                CAPmessagedict[AlertID] = CAPalert
            else:
                continue  # Skip if it's already processed
        else:  # Otherwise, add it as a new CAP message
            CAPmessagedict[AlertID] = CAPalert

    return alert


