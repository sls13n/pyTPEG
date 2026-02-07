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
# Read in CAP situation publications and replace any SHN code with WKT polygon
#
# alert message assumed in root,
#
import os, sys, zipfile, optparse, glob
import xml, gzip, io
from xml.etree.ElementTree import ElementTree, tostring
import CAP.geomet.wkt as wkt
import EawUtils.CAP_SHN_database
from CAP_utils import XML_indent

if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + os.sep + os   .pardir))


def parse_options() -> tuple[optparse.Values, list[str]]:
    """
    Parse command line options for the CAP SHN to WKT converter.
    Returns a tuple with options and arguments.
    """
    '''CAP_SHN_to_WKT: parse command line options'''

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    # define defaults
    parser.set_defaults(suppress_errors=False)

    #
    # binary options
    parser.add_option("-E", "--without_errors",
                      help="Suppress showing of errors (default %default)",
                      action="store_true", dest="suppress_errors")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        print("\n\n\n\n==> Nothing selected: Nothing done")
        exit(0)

    return options, args


def parse_SHN_code(code: str) -> list:
    """
    Parse the provided SHN code and return a GeoJSON object.
    Args:
        code (str): SHN code to be parsed.
    Returns:
        list: A GeoJSON object corresponding to the SHN code.
    """
    #
    geojson = EawUtils.CAP_SHN_database.CAP_SHN_to_geojson(code)
    if geojson is None:
        geojson = []

    return geojson


def CAP_replace_SHN_codes(file_string: str, SHNcodes: dict) -> str:
    """
    Replace SHN codes in the given CAP file string with corresponding WKT polygons.
    Args:
        file_string (str): The CAP file content as a string.
        SHNcodes (dict): A dictionary to store SHN code mappings.
    Returns:
        str: Updated XML string with SHN codes replaced by WKT.
    """
    capns = "{urn:oasis:names:tc:emergency:cap:1.2}"
    capns11 = capns.replace("1.2", "1.1")  ## NWS still has 1.1

    tree = ElementTree()
    root = xml.etree.ElementTree.fromstring(file_string)

    #
    # determine alert top-levelelement
    model = None
    if root.tag == capns + "alert":
        model = root
    elif root.tag == capns11 + "alert":
        model = root
        capns = capns11

    if model is None:
        print("No alert element found")
        return
    else:
        payload = model
        if payload is None:
            print("No Alert found")
            return

    #
    # here we have a valid list of CAP Alerts
    ID = 0
    for alert in [payload]:  # prepare also for future XML file with multiple Alerts

        for info in alert.findall(capns + "info"):
            for area in info.findall(capns + "area"):
                for geocode in area.findall(capns + "geocode"):
                    valueName = geocode.find(capns + "valueName").text
                    value = geocode.find(capns + "value").text

                    # now convert SHN codes to WKT
                    if valueName == "SHN":
                        area = parse_SHN_code(value)
                        #
                        ## check area and update geocode
                        if area:
                            SHNcodes[value] = wkt.dumps(area, decimals=10)  # convert to WKT
                            #
                            # update geocode
                            geocode.find(capns + "valueName").text = "WKT"
                            geocode.find(capns + "value").text = SHNcodes[value]

    # now convert back to string again to be written als _WKT.cap file
    XML_indent(root)

    return tostring(root, encoding="UTF-8")


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
        print(f"\n\n===== Processing file {fname}")

        # reset SHNcodes dict
        SHNcodes = {}

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
                if len(file_string) > 0:
                    WKT_file_string = CAP_replace_SHN_codes(file_string, SHNcodes)
                # print"\n\n"
            #
            fzip.close()
        elif fname.endswith(".gz"):  # gzipped
            with gzip.open(fname, 'rb') as f:
                file_string = f.read()
                if len(file_string) > 0:
                    WKT_file_string = CAP_replace_SHN_codes(file_string, SHNcodes)
                f.close()
        else:
            f = open(fname, "rb")
            if f:
                file_string = f.read()
                if len(file_string) > 0:
                    WKT_file_string = CAP_replace_SHN_codes(file_string, SHNcodes)
                f.close()
            else:
                print(f"==> {fname} could not be opened..")

        # remove file type and any directory info
        if os.sep in fname:
            [dirname, fname] = fname.rsplit(os.sep, 1)
            fname_stem = fname.rsplit('.', 1)[0]
            xml_fname_stem = dirname + os.sep + fname_stem + "_WKT"
        else:
            fname_stem = fname.rsplit('.', 1)[0]
            xml_fname_stem = fname_stem + "_WKT"

        xml_fnames = []
        xml_fname = xml_fname_stem + ".cap"
        xml_fnames.append(xml_fname)

        if len(SHNcodes) > 0:
            f = open(xml_fname, "w")
            if f:
                f.write(WKT_file_string)
                f.close()
                print(f"\nfile {xml_fname} created")
        else:
            print("\nNo SHN codes found, no new CAP file created\n", end=' ')

        print(f"\nNumber SHN codes converted: {len(SHNcodes)}")
        print(f"\n===== File processing finished: {fname} ====\n")
