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
# Read in CAP message and create EAW bin file or TPEG frame in directory of source CAP file
#
# alert message assumed in root
#
import optparse
import calendar
import datetime
import glob
import math
import os
import sys

sys.path.append(os.path.abspath(sys.path[0] + os.sep + os.pardir + os.sep + "TPEG"))  ## refer to TPEG branch
#
from collections import OrderedDict
from xml.etree.ElementTree import ElementTree, Element
from CAP.CAP_alert_component import CAP_alert_component
from EawUtils.BBKcodes_to_EAWcodes import BBKevents_to_EAWevents, BBKinstructions_to_EAWinstructions
from EawUtils.TPEG_EAW_frame_composer import TpegFrame_composer_EAW
from CAP_utils import generalise_polygon, WGS84_offset, CAP_parse_AlertMessages

#
# add TTNparser directories when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + os.sep + os.pardir + os.sep + "TPEG"))  ## refer to TPEG branch

from Base.TPEG_data_types import encodeIntSiLi, encodeIntUnLo, encodeIntUnLoMB, encodeLocalisedShortString, \
    encodeLocalisedLongString, encodeWGS84coordinate, encodeIntSi24, encodeShortString, encodeLongString, \
    encodeMajorMinorVersion
from Base.TPEG_string import TPEG_string
from TpegApps.TPEG_EAW import TPEG_EAW_component, EAW_AlertInformation_component, \
    EAW_LocalisedAlertTextInfo_component

from TpegMMC.TPEG_MMC import TPEG_MMC_component
from TpegLRC.TPEG_LRC import TPEG_LRC_component
from TpegLRC.TPEG_LRC_GLR import TPEG_LRC_GLR_component
from TpegLRC.TPEG_LRC_OLR import TPEG_LRC_OLR_component, OLR_CircleLocationReference, OLR_LocationDescription, \
    OLR_RectangleLocationReference, OLR_PolygonLocationReference

from typing import Optional


#
# ==============================================================================================
#
# option parser
#

def parse_options() -> tuple:
    """
    Parses the command-line options for the CAP_to_EAW conversion tool.

    Returns:
        tuple: A tuple containing the parsed options and arguments.
    """

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    # define defaults
    parser.set_defaults(suppress_errors=False,
                        DouglasPeucker=False,
                        LocText_InfoArea=False,
                        max_coords=300,
                        reduction_factor=1,  # no reduction
                        offset_dist=40000,
                        EAWmsg_only=False,
                        GLR_locref=False,
                        all_areas=False
                        )

    #
    # binary options
    parser.add_option("-E", "--without_errors",
                      help="Suppress showing of errors (default %default)",
                      action="store_true", dest="suppress_errors")

    parser.add_option("-D", "--DouglasPeucker",
                      help="Generalise polygons with DouglasPeucker algorthim (default %default)",
                      action="store_true", dest="DouglasPeucker")

    parser.add_option("-T", "--LocText_InfoArea",
                      help="Put location text only in Information Area (default %default)",
                      action="store_true", dest="LocText_InfoArea")

    # configuration options;
    parser.add_option("-O", "--offset_dist",
                      help="set offset distance (meters)for information area beyond affected areas (default %default)",
                      action="store", type="int", dest="offset_dist")

    parser.add_option("-N", "--max_coords",
                      help="set maximum number of coordinates per polygon (default %default)",
                      action="store", type="int", dest="max_coords")

    parser.add_option("-R", "--reduction_factor",
                      help="set reduction factor for number of coordinates per polygon, but at minimum max coords(default %default)",
                      action="store", type="int", dest="reduction_factor")

    parser.add_option("-B", "--bin",
                      help="Output binary EAW message only (default %default)",
                      action="store_true", dest="EAWmsg_only")

    parser.add_option("-G", "--GLR",
                      help="Encode to GLR i.s.o. OLR (default %default)",
                      action="store_true", dest="GLR_locref")

    parser.add_option("-A", "--All",
                      help="show all areas (default %default)",
                      action="store_true", dest="all_areas")

    parser.add_option("-U", "--output_dir",
                      help="Output directory for files created during conversion",
                      action="store", dest="output_dir")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        print("\n\n\n\n==> Nothing selected: Nothing done")
        exit(0)

    return options, args


#
# ==============================================================================================
#
# --- geo helper functions ---------
#

#
#

#
# ==============================================================================================
#
#
def encodeTimeStamp(time_string: str) -> int:
    """
    Encodes a timestamp from a string in the format "%Y-%m-%dT%H:%M:%S" to a UNIX timestamp.

    Args:
        time_string (str): The string representation of the timestamp.

    Returns:
        int: The UNIX timestamp corresponding to the input time string.
    """
    count = time_string.count('-')
    if count == 3:  # negative time zone
        time_string = time_string.rsplit("-", 1)[0]
    else:
        time_string = time_string.rsplit("+", 1)[0]

    timestamp = int(calendar.timegm(datetime.datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S").timetuple()))

    return timestamp


#
#
# processing below
#
# ==============================================================================================
#
#
# Alert component
CapMsgTypes = ["Unknown", "Alert", "Update", "Cancel"]  # out of scope: "Ack","Error"

# Info compoent
CapCategories = ["Unknown", "Geo", "Met", "Safety", "Security",
                 "Rescue", "Fire", "Health", "Env",
                 "Transport", "Infra", "CBRNE", "Other"]

CapUrgencies = ["Unknown", "Immediate", "Expected", "Future", "Past"]
CapSeverities = ["Unknown", "Extreme", "Severe", "Moderate", "Minor"]
CapCertainties = ["Unknown", "Observed", "Likely", "Possible", "Unlikely"]

CapResponseTypes = ["Unknown", "Shelter", "Evacuate", "Prepare",
                    "Execute", "Avoid", "Monitor", "Assess", "AllClear", "None"]

# mapping severity to German Alert Levels
GermanAlertLevel = {"Unknown": 1, "Extreme": 40, "Severe": 41, "Moderate": 1, "Minor": 42}


def CAP_fill_Info_component(CAP_alert: CAP_alert_component, Info_component: EAW_AlertInformation_component) -> tuple[EAW_AlertInformation_component, object]:
    """
    Fills the information component for a CAP alert with relevant details like categories, urgency, severity, and time.

    Args:
        CAP_alert (CAP_alert_component): The CAP alert component containing the alert information.
        Info_component (EAW_AlertInformation_component): The information component to fill.

    Returns:
        tuple: A tuple containing the filled information component and the bounding box component.
    """
    sent = [x[1] for x in CAP_alert.elements if x[0] == "sent"]
    msgType = [x[1] for x in CAP_alert.elements if x[0] == "msgType"]

    CAPinfos = [info for info in CAP_alert.subcomponents if info.type == "CAP_info"]
    CAP_info = CAPinfos[0]

    # EAW Alert level
    ## Info_component.attr_string += b'\x01' # Alert level CAP derived

    ## AW Alert levelfor Germany, use 40,41,42
    Info_component.attr_string += bytes([GermanAlertLevel[CAP_info.severity]])  # Alert level Based on German levels

    # CAP categories
    categories = [x[1] for x in CAP_info.elements if x[0] == "category"]

    Info_component.attr_string += bytes([len(categories)])
    for cat in categories:
        Info_component.attr_string += bytes([CapCategories.index(cat)])

    # Urgency, Severity, Certainty
    Info_component.attr_string += bytes([CapUrgencies.index(CAP_info.urgency)])
    Info_component.attr_string += bytes([CapSeverities.index(CAP_info.severity)])
    Info_component.attr_string += bytes([CapCertainties.index(CAP_info.certainty)])

    # CapTimeInfo
    substring = b""
    CTIselector = 0

    effective = [x[1] for x in CAP_info.elements if x[0] == "effective"]
    if effective:
        CTIselector = (CTIselector | 0x40)
        substring += encodeIntUnLo(encodeTimeStamp(effective[0]))
    elif sent:
        CTIselector = (CTIselector | 0x40)
        substring += encodeIntUnLo(encodeTimeStamp(sent[0]))

    onset = [x[1] for x in CAP_info.elements if x[0] == "onset"]
    if onset:
        CTIselector = (CTIselector | 0x20)
        substring += encodeIntUnLo(encodeTimeStamp(onset[0]))

    expiry = [x[1] for x in CAP_info.elements if x[0] == "expiry"]
    if expiry:
        CTIselector = (CTIselector | 0x10)
        substring += encodeIntUnLo(encodeTimeStamp(expiry[0]))

    Info_component.attr_string += bytes([CTIselector]) + substring

    # remaining optional items
    InfoSelector = 0
    substring = b""

    # msgType for user
    if msgType:
        InfoSelector = (InfoSelector | 0x40)
        substring += bytes([CapMsgTypes.index(msgType[0])])

    # CAP responses
    responseTypes = [x[1] for x in CAP_info.elements if x[0] == "responseType"]

    if responseTypes:
        InfoSelector = (InfoSelector | 0x20)
        substring += bytes([len(responseTypes)])
        for response in responseTypes:
            substring += bytes([CapResponseTypes.index(response)])

    # EawEventTypes
    eventCodes = [x[2] for x in CAP_info.parameters if x[0] == "eventCode"]
    if eventCodes:
        InfoSelector = (InfoSelector | 0x10)

        # filter duplicates
        eventCodes = list(OrderedDict.fromkeys(eventCodes))

        substring += BBKevents_to_EAWevents(eventCodes)

    # EawInstructionTypes
    instructionCodes = [x[2] for x in CAP_info.parameters if x[0] == "parameter" and x[1] == "instructionCode"]
    if instructionCodes:
        InfoSelector = (InfoSelector | 0x08)

        # remove shortCode label on last instruction
        instructionCodes = instructionCodes[0].replace("shortCode:", "").split()

        # filter duplicates
        instructionCodes = list(OrderedDict.fromkeys(instructionCodes))

        substring += BBKinstructions_to_EAWinstructions(instructionCodes)

    # pack optional attributes in
    Info_component.attr_string += bytes([InfoSelector]) + substring

    # ---- now add sub components ---------------------------

    # textual elements
    LocInfo_component = CAP_create_localised_info_component(CAP_info)
    if LocInfo_component:
        Info_component.subcomponents.append(LocInfo_component)

    # areas
    CAP_areas = [area for area in CAP_info.subcomponents if area.type == "CAP_area"]

    area_components, BoundingBox = CAP_create_alert_area_LRC_components_GLR(CAP_areas)

    Info_component.subcomponents.extend(area_components)

    # resources
    # cross references
    # profile parameters

    return Info_component, BoundingBox


#
#
#
# ==============================================================================================
#
#
def CAP_create_localised_info_component(CAP_info: CAP_alert_component) -> EAW_LocalisedAlertTextInfo_component:
    """
    Creates a localized information component for a CAP alert.

    Args:
        CAP_info (CAP_alert_component): The CAP alert info component containing localization details.

    Returns:
        EAW_LocalisedAlertTextInfo_component: The localized alert text info component.
    """
    EAWstring = b""
    selector1 = 0
    selector2 = 0

    LocInfo_component = EAW_LocalisedAlertTextInfo_component(4, 3)  # id = 4, level = 3

    language = [x[1] for x in CAP_info.elements if x[0] == "language"]
    event = [x[1] for x in CAP_info.elements if x[0] == "event"]
    audience = [x[1] for x in CAP_info.elements if x[0] == "audience"]
    senderName = [x[1] for x in CAP_info.elements if x[0] == "senderName"]
    headline = [x[1] for x in CAP_info.elements if x[0] == "headline"]
    description = [x[1] for x in CAP_info.elements if x[0] == "description"]
    instruction = [x[1] for x in CAP_info.elements if x[0] == "instruction"]
    web = [x[1] for x in CAP_info.elements if x[0] == "web"]
    contact = [x[1] for x in CAP_info.elements if x[0] == "contact"]

    # CAP MoWaS 1.7 alternative for senderName
    sender_langname = [x[2] for x in CAP_info.parameters if x[0] == "parameter" and x[1] == "sender_langname"]

    if language:
        # check for CAP MOWAS language code issue
        rfc3066_code = "de_DE" if language[0] in ["DE"] else language[0]

        LocInfo_component.attr_string += encodeShortString(rfc3066_code)
    else:
        LocInfo_component.attr_string += encodeShortString("en_US")  # default

    # optional information
    if event:
        selector1 = (0x40 | selector1)
        EAWstring += encodeLongString(event[0])

    if audience:
        selector1 = (0x20 | selector1)
        EAWstring += encodeLongString(audience[0])

    # prefer sender_langname (if available) over senderName (CAP MoWas 1.7 convention)
    if sender_langname:
        selector1 = (0x10 | selector1)
        EAWstring += encodeLongString(sender_langname[0])
    elif senderName:
        selector1 = (0x10 | selector1)
        EAWstring += encodeLongString(senderName[0])

    if headline:
        selector1 = (0x08 | selector1)
        EAWstring += encodeLongString(headline[0])

    if description:
        selector1 = (0x04 | selector1)
        EAWstring += encodeLongString(description[0])

    if instruction:
        selector1 = (0x02 | selector1)
        EAWstring += encodeLongString(instruction[0])

    if web:
        selector1 = (0x01 | selector1)
        EAWstring += encodeLongString(web[0])

    if contact:
        selector1 = (0x80 | selector1)  ## set continuation flag
        selector2 = (0x40 | selector2)
        EAWstring += encodeLongString(contact[0])

    if (selector1 & 0x80):
        LocInfo_component.attr_string += bytes([selector1, selector2]) + EAWstring
    else:
        LocInfo_component.attr_string += bytes([selector1]) + EAWstring

    if selector1 == 0:
        locInfo_component = False

    return LocInfo_component


#
#
# ==============================================================================================
#
#
def CAP_fill_MMC_component(CAP_alert: CAP_alert_component, MMC_component: TPEG_MMC_component, version: int = None) -> TPEG_MMC_component:
    """
    Fills the Message Management Container (MMC) component for a CAP alert.

    Args:
        CAP_alert (CAP_alert_component): The CAP alert component.
        MMC_component (TPEG_MMC_component): The MMC component to fill.
        version (int, optional): The version of the alert (optional).

    Returns:
        TPEG_MMC_component: The filled MMC component.
    """
    # MMC (fake)
    # create timestamp
    timestampnow = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())

    if version is None:
        # set version based on message type "Alert,"Update","Cancel
        msgType = [x[1] for x in CAP_alert.elements if x[0] == "msgType"]
        version = CapMsgTypes.index(msgType[0])

    # fixed                         ID        version
    MMC_component.attr_string = b'\x14' + bytes([version]) + encodeIntUnLo(timestampnow) + b'\x00'

    return MMC_component


#
# ==============================================================================================
#
#
def CAP_fill_LRC_component(CAP_alert: CAP_alert_component, LRC_component: TPEG_LRC_component, BB: Element) -> TPEG_LRC_component:
    """
    Fills the Location Reference Container (LRC) component for a CAP alert with bounding box details.

    Args:
        CAP_alert (CAP_alert_component): The CAP alert component.
        LRC_component (TPEG_LRC_component): The LRC component to fill.
        BB (Element): The bounding box component.

    Returns:
        TPEG_LRC_component: The filled LRC component.
    """
    # LRC
    # add GLR/OLR bounding box spanning all alert areas

    if BB is not None:
        LRC_component.subcomponents.append(BB)

    return LRC_component


#
# ==============================================================================================
#


def CAP_create_alert_area_LRC_components_GLR(CAP_areas: list[object]) -> tuple[list[object], object]:
    """
    Creates the Location Reference Container (LRC) components for the alert areas in a CAP alert.

    Args:
        CAP_areas (list): A list of CAP alert area components.

    Returns:
        tuple: A tuple containing the list of LRC components and the bounding box component.
    """
    bbset = False

    if options.GLR_locref:
        GLR = True
        OLR = False
    else:
        GLR = False
        OLR = True

    area_components = []
    for area in CAP_areas:
        name = area.areaDesc

        ## TEST code: truncate name
        ## name = name[:10]+"..."

        # break down multi polygons in single polygons for futher processing
        single_geo_areas = []
        for geo in area.geojson_areas:

            if geo["type"] == "MultiPolygon":

                for polygon in geo['coordinates']:
                    single_geo_areas.append({"type": "Polygon", "coordinates": polygon})
            else:
                single_geo_areas.append(geo)

        #
        # here no multi polygon should exist anymore
        for geo in single_geo_areas:
            if geo["type"] == "MultiPolygon":
                print("MultiPolygon is not decoded yet")

            elif geo["type"] == "Circle":
                LRC_component = TPEG_LRC_component(5, 3, Cname="AffectedArea")  # ID = 5, level = 3
                area_components.append(LRC_component)

                [lon, lat] = geo['coordinates']
                radius = int(geo['radius'] * 1000 + 0.5)
                # construct local bounding box borders for circle
                [c_minlat, c_minlon] = WGS84_offset([lat, lon], -radius, -radius)
                [c_maxlat, c_maxlon] = WGS84_offset([lat, lon], radius, radius)

                # check with global bounding box
                if bbset:
                    if c_minlon < minlon: minlon = c_minlon
                    if c_maxlon > maxlon: maxlon = c_maxlon
                    if c_minlat < minlat: minlat = c_minlat
                    if c_maxlat > maxlat: maxlat = c_maxlat
                else:
                    minlon = c_minlon
                    maxlon = c_maxlon
                    minlat = c_minlat
                    maxlat = c_maxlat
                    bbset = True

                # encode locref
                if GLR:
                    GLR_component = TPEG_LRC_GLR_component(6, 4)  # ID = 6, level = 4

                    LRC_component.subcomponents.append(GLR_component)

                    GLR_component.attr_string = b'\x20'  # geographicBoundingCircleSector

                    GLR_component.attr_string += encodeWGS84coordinate(lon, lat)
                    GLR_component.attr_string += encodeIntUnLoMB(radius)

                    GLR_component.attr_string += b'\x10' + b'\x01' + encodeLocalisedShortString(name, LC=33)

                elif OLR:
                    OLR_component = TPEG_LRC_OLR_component(8, 4)  # ID = 6, level = 4
                    LRC_component.subcomponents.append(OLR_component)

                    OLR_component.attr_string += encodeMajorMinorVersion(1, 1)

                    # create circle subcomponent
                    OLR_circle_component = OLR_CircleLocationReference(4, 5)  # ID = 4, level = 5
                    OLR_component.subcomponents.append(OLR_circle_component)

                    OLR_circle_component.attr_string += encodeWGS84coordinate(lon, lat) + b'\x00'  # no altitude
                    OLR_circle_component.attr_string += encodeIntUnLoMB(radius)
                    OLR_circle_component.attr_string += b'\x00'  # no optional data

                    # create location description subcomponent
                    OLR_location_description_component = OLR_LocationDescription(11, 5)
                    OLR_component.subcomponents.append(OLR_location_description_component)
                    OLR_location_description_component.attr_string += b'\x01' + encodeLocalisedLongString(name, LC=33)


            elif geo["type"] == "Polygon":
                LRC_component = TPEG_LRC_component(5, 3, Cname="AffectedArea")  # ID = 5, level = 3
                area_components.append(LRC_component)

                # now build up Loc Ref
                poly = geo['coordinates']

                # generalise polygones
                if options.reduction_factor > 1:
                    polygon = generalise_polygon(polygon=poly[0],
                                                 maxcoords=max(len(poly[0]) / options.reduction_factor, options.max_coords),
                                                 isHole=False, useDouglasPeucker=options.DouglasPeucker)
                    holes = [
                        generalise_polygon(polygon=hole, maxcoords=max(len(hole) / options.reduction_factor, options.max_coords), isHole=True, useDouglasPeucker=options.DouglasPeucker)
                        for hole in poly[1:]]
                else:
                    polygon = generalise_polygon(polygon=poly[0], maxcoords=options.max_coords, isHole=False, useDouglasPeucker=options.DouglasPeucker)
                    holes = [generalise_polygon(polygon=hole, maxcoords=options.max_coords, isHole=True, useDouglasPeucker=options.DouglasPeucker) for hole in poly[1:]]

                # determine bounding box on generalised polygon
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

                # create loc ref
                if GLR:
                    GLR_component = TPEG_LRC_GLR_component(6, 4)  # ID = 6, level = 4
                    LRC_component.subcomponents.append(GLR_component)

                    # polygon with/without holes
                    if holes:
                        GLR_component.attr_string = b'\x02'  # geographicAreaWithHolesReference
                    else:
                        GLR_component.attr_string = b'\x04'  # geographicAreaReference

                    # encode polygon points
                    GLR_component.attr_string += encodeIntUnLoMB(len(polygon))
                    for coord in polygon:
                        [lon, lat] = coord
                        GLR_component.attr_string += encodeWGS84coordinate(lon, lat)  # lon,lat

                    if holes:
                        # polygon with holes: encode those
                        GLR_component.attr_string += encodeIntUnLoMB(len(holes))
                        for hole in holes:
                            # encode hole
                            GLR_component.attr_string += encodeIntUnLoMB(len(hole))  # num coords)
                            for coord in hole:
                                [lon, lat] = coord
                                GLR_component.attr_string += encodeWGS84coordinate(lon, lat)  # lon,lat

                    if not options.LocText_InfoArea:
                        ## add 1 name
                        GLR_component.attr_string += b'\x10' + b'\x01' + encodeLocalisedShortString(name, LC=33)
                    else:
                        GLR_component.attr_string += b'\x00'


                elif OLR:
                    OLR_component = TPEG_LRC_OLR_component(8, 4)  # ID = 6, level = 4
                    OLR_component.attr_string += encodeMajorMinorVersion(1, 1)

                    LRC_component.subcomponents.append(OLR_component)

                    # create polygon subcomponent
                    OLR_polygon_component = OLR_PolygonLocationReference(5, 5)  # ID = 5, level = 5
                    OLR_component.subcomponents.append(OLR_polygon_component)

                    # encode start coordinate
                    [oldlon, oldlat] = polygon[0]
                    OLR_polygon_component.attr_string += encodeWGS84coordinate(oldlon, oldlat) + b'\x00'  # lon,lat

                    # encode coordinate path als delta, add interpolation points for OLR as needed
                    numcoords = len(polygon) - 1
                    coordstring = b""
                    for coord in polygon[1:]:
                        [lon, lat] = coord

                        # Check whether difference fits in a signed short for OLR!
                        lonTL = int(1.0 + math.fabs(lon - oldlon) / 0.32767)
                        lanTL = int(1.0 + math.fabs(lat - oldlat) / 0.32767)

                        steps = max(lonTL, lanTL)
                        if steps > 1:
                            # interpolation needed; OLR supports only a limited range between successive points.
                            numcoords += (steps - 1)
                            for i in range(1, steps + 1):
                                print("Interpolating", i, steps, int((lon - oldlon) * 100000 / steps),
                                      int((lat - oldlat) * 100000 / steps),
                                      "org", int((lon - oldlon) * 100000), int((lat - oldlat) * 100000))
                                coordstring += encodeIntSiLi(int((lon - oldlon) * 100000 / steps)) + encodeIntSiLi(
                                    int((lat - oldlat) * 100000 / steps)) + b'\x00'
                        else:
                            coordstring += encodeIntSiLi(int((lon - oldlon) * 100000)) + encodeIntSiLi(
                                int((lat - oldlat) * 100000)) + b'\x00'  # delta lon,lat

                        [oldlon, oldlat] = coord

                    OLR_polygon_component.attr_string += encodeIntUnLoMB(numcoords)
                    OLR_polygon_component.attr_string += coordstring

                    OLR_polygon_component.attr_string += b'\x00'  # no optional date

                    for hole in holes:
                        # create polygon subcomponent
                        OLR_polygon_component = OLR_PolygonLocationReference(5, 6)  # ID = 5, level = 6
                        OLR_component.subcomponents.append(OLR_polygon_component)

                        # encode start coordinate
                        [oldlon, oldlat] = hole[0]
                        OLR_polygon_component.attr_string += encodeWGS84coordinate(oldlon, oldlat) + b'\x00'  # lon,lat

                        # encode coordinate path als delta, add interpolation points for OLR as needed
                        numcoords = len(hole) - 1
                        coordstring = ""
                        for coord in hole[1:]:
                            [lon, lat] = coord
                            # Check whether difference fits in a signed short for OLR!
                            lonTL = int(1.0 + math.fabs(lon - oldlon) / 0.32767)
                            lanTL = int(1.0 + math.fabs(lat - oldlat) / 0.32767)

                            steps = max(int(1.0 + math.fabs(lon - oldlon) / 0.32767),
                                        int(1.0 + math.fabs(lat - oldlat) / 0.32767))
                            if steps > 1:
                                # interpolation needed
                                numcoords += (steps - 1)
                                for i in range(1, steps + 1):
                                    print("Interpolating", i, steps, int(0.5 + (lon - oldlon) * 100000 / steps),
                                          int(0.5 + (lat - oldlat) * 100000 / steps),
                                          "org", int(0.5 + (lon - oldlon) * 100000), int(0.5 + (lat - oldlat) * 100000))
                                    # OLR specifies rounding
                                    coordstring += encodeIntSiLi(
                                        int(0.5 + (lon - oldlon) * 100000 / steps)) + encodeIntSiLi(
                                        int(0.5 + (lat - oldlat) * 100000 / steps)) + b'\x00'
                            else:
                                # OLR specifies rounding
                                coordstring += encodeIntSiLi(int(0.5 + (lon - oldlon) * 100000)) + encodeIntSiLi(
                                    int(0.5 + (lat - oldlat) * 100000)) + b'\x00'  # delta lon,lat

                            [oldlon, oldlat] = coord

                        OLR_polygon_component.attr_string += encodeIntUnLoMB(numcoords)
                        OLR_polygon_component.attr_string += coordstring
                        OLR_polygon_component.attr_string += b'\x00'  # no optional date

                    if not options.LocText_InfoArea:
                        # create location description subcomponent
                        OLR_location_description_component = OLR_LocationDescription(11, 5)
                        OLR_component.subcomponents.append(OLR_location_description_component)
                        OLR_location_description_component.attr_string += b'\x01' + encodeLocalisedLongString(name,
                                                                                                              LC=33)

                        # construct Bounding box for information ares
    if bbset:
        OFFSETDIST = options.offset_dist
        if GLR:
            [NWlat, NWlon] = WGS84_offset([maxlat, minlon], OFFSETDIST, -OFFSETDIST)
            [SElat, SElon] = WGS84_offset([minlat, maxlon], -OFFSETDIST, OFFSETDIST)

            BB_component = TPEG_LRC_GLR_component(6, 2)  # ID = 6, level = 2

            BB_component.attr_string = b'\x40'  # Bounding Box
            # NW corner
            BB_component.attr_string += encodeWGS84coordinate(NWlon, NWlat)
            # SW corner
            BB_component.attr_string += encodeWGS84coordinate(SElon, SElat)

            if options.LocText_InfoArea:
                ## add 1 name
                BB_component.attr_string += b'\x20' + b'\x01' + encodeLocalisedShortString(name, LC=33)
            else:
                BB_component.attr_string += b'\x00'


        elif OLR:
            [SWlat, SWlon] = WGS84_offset([minlat, minlon], -OFFSETDIST, -OFFSETDIST)
            [NElat, NElon] = WGS84_offset([maxlat, maxlon], OFFSETDIST, OFFSETDIST)

            BB_component = TPEG_LRC_OLR_component(8, 2)  # ID = 8, level = 2
            BB_component.attr_string += encodeMajorMinorVersion(1, 1)

            Rectangle_component = OLR_RectangleLocationReference(6, 3)  # ID = 6, level = 4
            BB_component.subcomponents.append(Rectangle_component)

            Rectangle_component.attr_string += encodeWGS84coordinate(SWlon, SWlat) + b'\x00'
            Rectangle_component.attr_string += encodeWGS84coordinate(NElon, NElat) + b'\x00'
            Rectangle_component.attr_string += b'\x00'

            if options.LocText_InfoArea:
                # create location description subcomponent
                OLR_location_description_component = OLR_LocationDescription(11, 3)
                BB_component.subcomponents.append(OLR_location_description_component)
                OLR_location_description_component.attr_string += b'\x01' + encodeLocalisedLongString(name, LC=33)


    else:
        BB_component = None

    return area_components, BB_component


#
#
#
## ==============================================================================================
#

def CAP_to_EAW(CAP_alert: CAP_alert_component) -> TPEG_EAW_component:
    """
    Converts a CAP alert component into an EAW component suitable for TPEG encoding.

    Args:
        CAP_alert (CAP_alert_component): The CAP alert component.

    Returns:
        TPEG_EAW_component: The resulting EAW component.
    """
    # set-up main structure
    EAW_component = TPEG_EAW_component(0, 0)  # ID = 0, level = 0

    MMC_component = TPEG_MMC_component(1, 1, Cname="MessageManagementContainer")  # ID = 1, level = 1
    LRC_component = TPEG_LRC_component(2, 1, Cname="InformationArea")  # ID = 2, level = 1
    Info_component = EAW_AlertInformation_component(3, 1)  # ID = 3, level = 1

    EAW_component.subcomponents.append(MMC_component)
    EAW_component.subcomponents.append(Info_component)
    EAW_component.subcomponents.append(LRC_component)

    # now fill in attributes and details

    # Alert
    Info_component, BB = CAP_fill_Info_component(CAP_alert, Info_component)

    # MMC (fake)
    # version based on Alert,update,cancel
    MMC_component = CAP_fill_MMC_component(CAP_alert, MMC_component)

    # last create information area
    LRC_component = CAP_fill_LRC_component(CAP_alert, LRC_component, BB)

    # now parse
    EAW_string = EAW_component.to_binary()  # create binary format
    TPEGstring = TPEG_string(EAW_string)

    EAW_component = TPEG_EAW_component(0, 0)  # ID = 0, level = 0

    CompID = TPEGstring.IntUnTi()
    if CompID == 0:
        EAW_component.parse(TPEGstring)
    else:
        print(f"==> Wrong EAW component ID: {CompID}")

    return EAW_component


#
#
# ==============================================================================================
#

if __name__ == '__main__':
    # print "CAP parser
    options, args = parse_options()

    if options.suppress_errors:
        pass
        # TPEG_error_suppress_reports(options.suppress_errors)

        # process wild cards in arguments to obtain the list of frame files
    files = []
    for arg in args:
        files.extend(glob.glob(arg))

    for fname in files:
        print(f"\n\nProcessing file {fname}\n\n")
        # reset message dicts
        CAPmessagedict: dict = {}

        f = open(fname, "rb")
        if f:
            file_string = f.read()
            if len(file_string) > 0:
                CAP_parse_AlertMessages(file_string, CAPmessagedict)
            f.close()
        else:
            print(f"==> {fname} could not be opened..")

        for alert in CAPmessagedict:
            EAW = CAP_to_EAW(CAPmessagedict[alert])
            ## print "\n\n"
            ## EAW.out()
            ## print "\n\n"

        # set up time stamp
        t = datetime.datetime.utcnow()
        stime = t.strftime("_%Y%m%dT%H%M%S")

        # remove file type and any directory info
        if os.sep in fname:
            [dirname, fname] = fname.rsplit(os.sep, 1)
            fname_stem = fname.rsplit('.', 1)[0]
            if options.output_dir:
              dirname = options.output_dir
            tpgbin_fname_stem = dirname + os.sep + "TPEG_EAW_for_" + fname_stem + stime
            print(f"writing to {tpgbin_fname_stem}")
        else:
            fname_stem = fname.rsplit('.', 1)[0]
            if options.output_dir:
              dirname = options.output_dir + os.sep
            else:
              dirname = ""
            tpgbin_fname_stem = dirname + "TPEG_EAW_for_" + fname_stem + stime
            print(f"writing to {tpgbin_fname_stem}")

        #

        if options.EAWmsg_only:
            fname_ext = ".bin"
            s = EAW.to_binary()
        else:
            fname_ext = ".tpeg"
            s = TpegFrame_composer_EAW(EAW.to_binary())

        # write file
        tpgbin_fname = tpgbin_fname_stem + fname_ext
        f = open(tpgbin_fname, "wb")
        if f:
            f.write(s)
            f.close()

        print(f"\n\n {tpgbin_fname}")

        # Print a summary of the file processing
        numVersions: int = 1
        # For message in CAPmessagedict.values():
        # numVersions += len(message["v"])

        print(f"\n\n======== Summary for file: {fname} ====\n")
        print(f"Number distinct CAP messages: {len(CAPmessagedict)}, avg. #versions {numVersions // max(1, len(CAPmessagedict))}")
