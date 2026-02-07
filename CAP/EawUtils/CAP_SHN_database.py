#!/usr/bin/env python3
#
# -*- coding: utf-8 -*-
#
# Copyright 2022 TISA ASBL
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
# utility to access SHN shape file
#

import os, sys, optparse
import utm

## importing SHN shapefile utility
from . import SHNshapefile as shapefile

#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + os.pardir))
    DBpath_extension = os.sep + os.pardir + os.sep + "Data" + os.sep
else:
    DBpath_extension = os.sep + "Data" + os.sep

#
# path to directory with files
_DBpath_250 = os.path.abspath(sys.path[
                                  0]) + DBpath_extension + "vg250_01-01.utm32s.shape.ebenen" + os.sep + "vg250_ebenen_0101" + os.sep + "VG250"
_DBpath2500 = os.path.abspath(
    sys.path[0]) + DBpath_extension + "vg2500_01-01.utm32s.shape" + os.sep + "vg2500" + os.sep + "vg2500"

## ==============================================================================================
#
# ascii conversion

trans_table = ''.join([chr(i) for i in range(128)] + ['?'] * 128)


def ascii(s):
    if isinstance(s, str):
        return s.encode('ascii', 'replace')
    else:
        return s.translate(trans_table)


#
#
# ==============================================================================================
#
def _to_WGS84(x):
    convert = utm.to_latlon(x[0], x[1], 32, 'U')
    return [convert[1], convert[0]]


def polygon_UTM32_to_WGS84(polygon):
    # return map(lambda x: list(utm.to_latlon(x[0], x[1], 32, 'U')), polygon)
    return [_to_WGS84(x) for x in polygon]


#
# ==============================================================================================
#
#
#
_local_loaded_SHN = None


def _SHN_load_DB():
    global _local_loaded_SHN

    if _local_loaded_SHN is None:
        sf2500_sta = shapefile.Reader(_DBpath2500 + "_sta")
        sf2500_lan = shapefile.Reader(_DBpath2500 + "_lan")
        sf2500_rbz = shapefile.Reader(_DBpath2500 + "_rbz")
        sf2500_krs = shapefile.Reader(_DBpath2500 + "_krs")

        sf_250_sta = shapefile.Reader(_DBpath_250 + "_STA")
        sf_250_lan = shapefile.Reader(_DBpath_250 + "_LAN")
        sf_250_rbz = shapefile.Reader(_DBpath_250 + "_RBZ")
        sf_250_krs = shapefile.Reader(_DBpath_250 + "_KRS")
        sf_250_vwg = shapefile.Reader(_DBpath_250 + "_VWG")
        sf_250_gem = shapefile.Reader(_DBpath_250 + "_GEM")

        ## files have different formats (without/with "ebenen", process input separately
        SHP2500_files = [sf2500_sta, sf2500_lan, sf2500_rbz, sf2500_krs]
        SHP_250_files = [sf_250_sta, sf_250_lan, sf_250_rbz, sf_250_krs, sf_250_vwg, sf_250_gem]

        ## SHP2500_files = [] ## uncomment for full detail geometry

        ## lookup together
        SHP_files = SHP2500_files + SHP_250_files

        ## sf_pk = shapefile.Reader(_DBpath+"_PK")
        ## sf_li  = shapefile.Reader(_DBpath+"_LI")

        ## print sf2500_lan.fields,"\n"
        ## print sf2500_lan.record(0),"\n"

        SHN2codedict = {}

        ## now index based on earliest found item in sequence of shapefiles
        ## first process level 2500 items
        for SHPnum in range(len(SHP2500_files)):
            sf = SHP_files[SHPnum]

            for index in range(len(sf.records())):
                record = sf.record(index)
                GF = 4  ## no GF given, assume 4
                RS = ascii(record[1])

                SHN2codedict[RS] = [SHPnum, index, ascii(record[3]), GF]
                if len(RS) < 12:
                    RS_0 = RS + (12 - len(RS)) * b'0'
                    SHN2codedict[RS_0] = [SHPnum, index, ascii(record[3]), GF]

        ##
        ##  now process remaining "ebenen" files at level 250
        for SHPnum in range(len(SHP2500_files), len(SHP_files)):
            sf = SHP_files[SHPnum]

            for index in range(len(sf.records())):
                record = sf.record(index)
                GF = record[1]
                RS = ascii(record[3])

                if RS in SHN2codedict and SHN2codedict[RS][3] == 4:  # prefer land with structure (GF == 4)
                    ## index = SHN2codedict[RS]
                    ## print "already know", RS,"GF", index[3]
                    ## print SHP_files[index[0]].record(index[1])
                    ## print record
                    ## print "\n"
                    continue

                if GF in [3,
                          4] and RS not in SHN2codedict:  # accept only land with/without structures for now, no coasts
                    SHN2codedict[RS] = [SHPnum, index, ascii(record[7] + " " + record[6]), GF]
                    if len(RS) < 12:
                        RS_0 = RS + (12 - len(RS)) * b'0'
                        SHN2codedict[RS_0] = [SHPnum, index, ascii(record[7] + " " + record[6]), GF]

            else:
                ## print "missing",ascii(record[1]), len(ascii(record[1]))
                pass

        _local_loaded_SHN = [SHN2codedict, SHP_files]

    return _local_loaded_SHN


#
# ==============================================================================================
#
#

def CAP_SHN_to_geojson(SHNcode):
    global _local_loaded_SHN
    gjson = None

    if _local_loaded_SHN is None:
        [SHN2codedict, SHPfiles] = _SHN_load_DB()
    else:
        [SHN2codedict, SHPfiles] = _local_loaded_SHN

    # convert codes to bytestring as database index is bytestring now
    SHNcode = bytes(SHNcode,'utf-8')

    if SHNcode in SHN2codedict:
        index = SHN2codedict[SHNcode]

        gobject = SHPfiles[index[0]].shape(index[1]).__geo_interface__
        gtype = gobject['type']

        if gtype == 'Polygon':
            gjson = gobject
            gjson['coordinates'] = [polygon_UTM32_to_WGS84(pol) for pol in gjson['coordinates']]
        elif gtype == 'MultiPolygon':
            gjson = gobject
            gjson['coordinates'] = [[polygon_UTM32_to_WGS84(pol) for pol in ring] for ring in gjson['coordinates']]

    return gjson


#
# ==============================================================================================
#
#
# if run on command line
#

if __name__ == '__main__':

    [SHN2codedict, sf] = _SHN_load_DB()

    print("\n")

    SHN = ["080000000000", "060000000000", "160000000000", "050000000000", "150000000000", "130000000000",
           "070000000000", "010000000000", "030000000000",
           "020000000000", "120000000000", "140000000000", "100000000000", "060000000000", "110000000000",
           "160000000000", "050000000000", "150000000000", "130000000000", "070000000000", "010000000000",
           "030000000000", "020000000000", "120000000000",
           "140000000000", "100000000000", "060000000000", "040000000000", "033590000000"]

    ## 060000000000 ==> Land Hessen
    ## 033590000000 ==> Landkreis Stade

    for code in SHN:
        if code in SHN2codedict:
            index = SHN2codedict[code]

            print("\nCode %s, file index %d, record index %05d, name %s" % (code, index[0], index[1], ascii(index[2])))

        else:
            print("\nCode %s, missing" % code)
