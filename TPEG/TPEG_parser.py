#!/usr/bin/env python3
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
# This file is the main TPEG parser. It reads binary TPEG frames from a file or a zip file and parses them.
# The parsed frames are then printed to the console.

import os, sys, getopt, re, zipfile,optparse,copy
#
from time import sleep
#
#
import Base

from Base.TPEG_error      import TPEG_log_error, TPEG_error_set_context, TPEG_error_unset_context,TPEG_error_suppress_reports
from Base.TPEG_string     import TPEG_string
from Base.TPEG_frame      import TPEG_Transport_Frame
from Base.TPEG_CRC        import TPEG_CRC
from Base.TPEG_component  import TPEG_component
#
from Base.TPEG_sync_frame import TPEG_sync_frame
#
import TpegApps
from TpegApps import *
from typing import List, Tuple, Dict, Optional, Union
from optparse import Values


def parse_options() -> Tuple[Values, List[str]]:
    """
    Parse command line options for the TPEG parser.

    Returns:
        A tuple containing the parsed options and arguments.
    """
    usage = "usage: %prog [options] <binary TPEG frame files>"
    parser = optparse.OptionParser(usage)

    # define defaults
    parser.set_defaults(max_file_size=500000, suppress_errors=False)
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


def parse_TPEG_binary(bytestring: bytes, fname: str) -> None:
    """
    Parse a binary TPEG string.

    Args:
        bytestring: The binary TPEG string to parse.
        fname: The name of the file from which the bytestring was read.
    """
    # AID to frame continuation mapping for TPEG applications
    TPEGappFrameDict    = {}
    TPEGappFrameDict[ 0] = TPEG_SNI.TPEG_SNI_frame_continuation
    TPEGappFrameDict[ 5] = TPEG_TEC.TPEG_TEC_frame_continuation
    TPEGappFrameDict[15] = TPEG_EAW.TPEG_EAW_frame_continuation
    # Register TFP parser (AID=7)
    try:
        from TpegApps import TPEG_TFP
        TPEGappFrameDict[7] = TPEG_TFP.TPEG_TFP_frame_continuation
    except Exception as e:
        TPEG_log_error(f"TFP parser registration failed: {e}")

    TPEGstring = TPEG_string(bytestring)

    frames = []

    print("\n\n")
    # TPEG registry
    Registry = {}

    while TPEGstring.len() > 0:
         if TPEG_sync_frame(TPEGstring,AppName="TPEG"):
              TPEGframe = TPEG_Transport_Frame(0,ApplicationFramesDict=TPEGappFrameDict)
              TPEGframe.parse(TPEGstring, Registry)
              frames.append(TPEGframe)

    for frame in frames:
        frame.out()
        print("\n")


# run when file is run on command line
if __name__ == '__main__':

    options, args = parse_options()
    #
    # do not show error reports if suppressed
    if options.suppress_errors:
        TPEG_error_suppress_reports(options.suppress_errors)

    files = args #contains the list of *.s files

    print(f"TPEG parser: number of files {len(files)}")

    for fname in files:
        print(f" === start parsing {fname} =========================================\n")
        if zipfile.is_zipfile(fname):
            fzip = zipfile.ZipFile(fname,"r")
            print("\n\n")

            fnamelist = fzip.namelist()
            for zipfname in fnamelist:
                print(f"\n--- Zipfile entry: {zipfname} ------------- \n")
                bytestring = fzip.read(zipfname)
                # truncate if needed
                if len(bytestring) >options.max_file_size:
                    bytestring = bytestring[:options.max_file_size]
                    print(f"\nTruncated {zipfname} to {options.max_file_size / 1000} KB\n")
                    sleep(1)

                parse_TPEG_binary(bytestring, zipfname)
            #
            fzip.close()
        else:
            f = open(fname,"rb")
            if f:
                bytestring = f.read()
                # truncate if needed
                if len(bytestring) >options.max_file_size:
                    bytestring = bytestring[:options.max_file_size]
                    print(f"\nTruncated {fname} to {options.max_file_size / 1000} KB\n")
                    sleep(1)

                parse_TPEG_binary(bytestring, fname)
                f.close()
            else:
                print(f"==> {fname} could not be opened..")

        print(f"\n === end parsing {fname} =========================================\n")
