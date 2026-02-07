#!/usr/bin/env python3
#
# Copyright 2023-2024 TISA ASBL
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
# This file is a Python script that reads a binary TPEG message and exports it to JSON.

import sys
import zipfile
import optparse
import json

from time import sleep

from Base.TPEG_error import TPEG_error_suppress_reports
from Base.TPEG_string import TPEG_string
from Base.TPEG_frame import TPEG_Transport_Frame
from Base.TPEG_sync_frame import TPEG_sync_frame

from TpegApps import *
from typing import List, Tuple, Dict, Optional, Union
from optparse import Values

def export_TPEG_EAW_to_JSON(bytestring: bytes, fname: str) -> List[Dict[str, Union[str, Dict[str, str]]]]:
    """
    Parse a binary TPEG string and export it to JSON.

    Args:
        bytestring: The binary TPEG string to parse.
        fname: The name of the file from which the bytestring was read.

    Returns:
        A list of dictionaries representing the parsed TPEG data.
    """
    exported_data = []
    # AID to frame continuation mapping for TPEG applications
    TPEGappFrameDict = {}
    TPEGappFrameDict[0] = TPEG_SNI.TPEG_SNI_frame_continuation
    TPEGappFrameDict[5] = TPEG_TEC.TPEG_TEC_frame_continuation
    TPEGappFrameDict[15] = TPEG_EAW.TPEG_EAW_frame_continuation
    TPEGstring = TPEG_string(bytestring)
    frames = []
    # print("\n\n")
    # TPEG registry
    Registry = {}

    while TPEGstring.len() > 0:
        if TPEG_sync_frame(TPEGstring, AppName="TPEG"):
            TPEGframe = TPEG_Transport_Frame(0, ApplicationFramesDict=TPEGappFrameDict)
            TPEGframe.parse(TPEGstring, Registry)
            frames.append(TPEGframe)

    for frame in frames:
        # This prints out the contents of the entire TPEG message
        # frame.out()
        # print("\n")

        # TODO: below is the information needed
        # The dict follows the ordinary EAW message structure
        frame_data = {
            "messageManagementContainer": {},  # messageManagementContainer
            "alertInformation": {},  # alertInformation
            "informationArea": {}   # informationArea
        }

        # There are three types of subcomponents present in the alert:
        message_containers = frame.serviceframe.CompFrames[1].frame_continuation.components[0].subcomponents
        # print(message_containers[0].type)   # 1) Message Management Container (type = MMC_component)
        # print(message_containers[1].type)   # 2) Application Data Container (type = EAW_AlertInformation)
        # print(message_containers[2].type)   # 3) Location Referencing Container (type = InformationArea)
        # print()
        message_management_container = None
        alert_information_container = None
        information_area_container = None
        for container in message_containers:
            if container.type == "MMC_component":
                message_management_container = container
            elif container.type == "EAW_AlertInformation":
                alert_information_container = container
            elif container.type == "LRC":
                information_area_container = container

        # 1) messageManagementContainer
        if message_management_container:
            mmc_data = {}
            for pair in message_management_container.attributes:
                if pair[0] == "messageExpiryTime" or pair[0] == "messageGenerationTime":
                    # Date to ISO date string
                    mmc_data[pair[0]] = pair[1].isoformat()
                    continue
                mmc_data[pair[0]] = pair[1]
            frame_data["messageManagementContainer"] = mmc_data

        # 2) alertInformation
        if alert_information_container:
            eaw_data = {}
            # 2.1) Attributes: top-level EAW message information
            for pair in alert_information_container.attributes:
                if pair[0] == "_complex_":
                    # print(pair[1].type)
                    eaw_data[pair[1].name] = {}
                    for sub_pair in pair[1].attributes:
                        attr_data = sub_pair[1]
                        if pair[1].type == "EAW_CapTimeInfo":
                            attr_data = attr_data.isoformat()
                        elif pair[1].type == "EAW_EventType" or pair[1].type == "EAW_InstructionType":
                            separator = attr_data.index(':')
                            if separator > -1:
                                separator += 1
                                attr_data = filtered_value(attr_data)
                        eaw_data[pair[1].name][sub_pair[0]] = attr_data
                    continue
                eaw_data[pair[0]] = filtered_value(pair[1])

            # 2.2) Ordered components: LocalisedAlertTextInfo and AffectedArea
            for subcomponent in alert_information_container.subcomponents:
                # print()
                # print(subcomponent.name)
                # print(subcomponent.type)
                # print(subcomponent.attributes)
                # print(subcomponent.subcomponents)
                # print()
                eaw_data[subcomponent.name] = {}
                # 2.2.1) LocalisedAlertTextInfo
                for pair in subcomponent.attributes:
                    if type(pair[1]) != type(""):
                        continue
                    # print(pair[1])
                    eaw_data[subcomponent.name][pair[0]] = pair[1].replace('"', '')
                # 2.2.2) AffectedArea
                # TODO: handle cases for EAW_LocalisedAlertTextInfo and other components
                if subcomponent.type == "LRC":
                    for lrc_subcomponent in subcomponent.subcomponents:
                        # TODO: handle cases for ETL, GLR, TMC
                        if lrc_subcomponent.type == "LRC_OLR":
                            for olr_sub in lrc_subcomponent.subcomponents:
                                if olr_sub.type == "OLR_LocationDescription":
                                    for pair in olr_sub.attributes:
                                        eaw_data[subcomponent.name][pair[0]] = pair[1]
                                if olr_sub.type == "OLR_PolygonLR":
                                    if "coordinates" not in eaw_data:
                                        eaw_data["coordinates"] = []
                                    polygon_coordinates = []
                                    last_abs_coord = None
                                    # Coordinates
                                    for pair in olr_sub.attributes:
                                        if pair[0] == "_complex_" and pair[1].type == "OLR_AbsoluteGeoCoordinate":
                                            # Parse abs coord pair
                                            coord = [0, 0]
                                            for coord_string_part in pair[1].attributes:
                                                if coord_string_part[0] == "longitude":
                                                    coord[0] = coord_string_part[1]
                                                elif coord_string_part[0] == "latitude":
                                                    coord[1] = coord_string_part[1]
                                            polygon_coordinates.append(coord)
                                            last_abs_coord = coord
                                            # print(coord)
                                        elif pair[0] == "_complex_" and pair[1].type == "OLR_RelativeGeoCoordinate":
                                            if not last_abs_coord:
                                                continue
                                            # Parse rel coord pair
                                            coord = [0, 0]
                                            divisor = 100000
                                            for coord_string_part in pair[1].attributes:
                                                if coord_string_part[0] == "delta longitude":
                                                    coord[0] = truncate(
                                                        last_abs_coord[0] + coord_string_part[1]/divisor, 5)
                                                elif coord_string_part[0] == "delta latitude":
                                                    coord[1] = truncate(
                                                        last_abs_coord[1] + coord_string_part[1]/divisor, 5)
                                            polygon_coordinates.append(coord)
                                            last_abs_coord = coord
                                    eaw_data["coordinates"].append(polygon_coordinates)
            frame_data["alertInformation"] = eaw_data

        # 3) informationArea
        if information_area_container:
            area_data = {}
            for subcomponent in information_area_container.subcomponents:
                # TODO: handle cases for ETL, GLR, TMC
                if subcomponent.type == "LRC_OLR":
                    for shape in subcomponent.subcomponents:
                        if shape.type == "OLR_RectangleLR":
                            area_data["rectangle"] = {}
                            for pair in shape.attributes:
                                # print(pair[1].type)
                                # print(pair[1].attributes)
                                for pair in pair[1].attributes:
                                    if pair[0] == "_complex_" and pair[1].type == "OLR_AbsoluteGeoCoordinate":
                                        # Parse abs coord pair
                                        coord = [0, 0]
                                        for coord_string_part in pair[1].attributes:
                                            name = pair[1].name if pair[1].name == "lowerLeftCoordinate" or pair[
                                                1].name == "upperRightCoordinate" else "undefinedCoordinates"
                                            if name not in area_data["rectangle"]:
                                                area_data["rectangle"][name] = {}
                                            if coord_string_part[0] == "longitude":
                                                coord[0] = coord_string_part[1]
                                            elif coord_string_part[0] == "latitude":
                                                coord[1] = coord_string_part[1]
                                        area_data["rectangle"][name] = coord
            frame_data["informationArea"] = area_data

        # print("\n")
        exported_data.append(frame_data)
    return exported_data


def parse_options() -> Tuple[Values, List[str]]:
    """
    Parse command line options for the TPEG parser.

    Returns:
        A tuple containing the parsed options and arguments.
    """
    usage = "usage: %prog [options] <binary TPEG frame files>"
    parser = optparse.OptionParser(usage)

    # define defaults
    parser.set_defaults(max_file_size=500000,
                        suppress_errors=False)
    #
    #
    # configuration options; keep -e -s -v for compatibility
    parser.add_option("-s", "--max_size",
                      help="set max file size (bytes) to truncate individual input files (default %default)",
                      action="store", type="int", dest="max_file_size")
    #
    # binary options
    parser.add_option("-E", "--WithoutErrors",
                      help="Suppress showing of errors (default %default)",
                      action="store_true", dest="suppress_errors")
    #

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        exit(0)

    return options, args


def filtered_value(string: str) -> str:
    """
    Filter a string to remove any leading characters up to and including the first colon.

    Args:
        string: The string to filter.

    Returns:
        The filtered string.
    """
    i = string.index(':')
    if i < 0 or i == len(string)-1:
        return string
    i = i+2 if string[i+1] == ' ' else i+1
    return string[i:]


def truncate(n: float, decimals: int = 0) -> float:
    """
    Truncate a float to a specified number of decimal places.

    Args:
        n: The float to truncate.
        decimals: The number of decimal places to keep (default is 0).

    Returns:
        The truncated float.
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


# run when file is run on command line
if __name__ == '__main__':

    options, args = parse_options()
    #
    # do not show error reports if suppressed
    if options.suppress_errors:
        TPEG_error_suppress_reports(options.suppress_errors)

    files = args  # contains the list of *.s files

    # print("TPEG parser: "+"number of files ",len(files))

    tpeg_exports = []
    for fname in files:
        tpeg_data = None
        # print(" === start parsing " + fname +"=========================================\n")
        if zipfile.is_zipfile(fname):
            fzip = zipfile.ZipFile(fname, "r")
            # print("\n\n")
            fnamelist = fzip.namelist()
            for zipfname in fnamelist:
                # print("\n--- Zipfile entry: "+zipfname+"------------- \n")
                bytestring = fzip.read(zipfname)
                # truncate if needed
                if len(bytestring) > options.max_file_size:
                    bytestring = bytestring[:options.max_file_size]
                    # print("\nTruncated",zipfname,"to", (options.max_file_size/1000),"KB\n")
                    sleep(1)

                tpeg_data = export_TPEG_EAW_to_JSON(bytestring, zipfname)
                # print(tpeg_json)
            #
            fzip.close()
        else:
            f = open(fname, "rb")
            if f:
                bytestring = f.read()
                # truncate if needed
                if len(bytestring) > options.max_file_size:
                    bytestring = bytestring[:options.max_file_size]
                    # print("\nTruncated",fname,"to", (options.max_file_size/1000),"KB\n")
                    sleep(1)

                tpeg_data = export_TPEG_EAW_to_JSON(bytestring, fname)
                # print(tpeg_json)
                f.close()
            else:
                # print('==> '+fname+' could not be opened..')
                sys.exit(1)
        tpeg_exports.append(tpeg_data)
        # print("\n === end parsing " + fname +"=========================================\n")
    sys.stdout.write(json.dumps(tpeg_exports))
    sys.exit(0)
