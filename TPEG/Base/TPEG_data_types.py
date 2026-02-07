#!/usr/bin/env python3
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
# TPEG data types encoding
#
#
import os, sys, getopt, re, zlib, struct

from time import time, mktime
from calendar import timegm

#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + '/..'))
#
#
from .TPEG_string import TPEG_string


#
#
#
#
def UShort2ByteString(val):
    s = b''
    if val < 0 or val > 0xFFFF:
        print("UShort2ByteString: value out of range", val)
    else:
        s = bytes([(val & 0xFF00) >> 8, val & 0x00FF])

    return s


#
#
# encode multi-byte
def encodeIntUnLoMB(val):
    result = b''
    sizes = [0x80, 0x4000, 0x200000, 0x10000000]

    nbytes = 5
    for i, size in enumerate(sizes):
        if val < size:
            nbytes = i + 1
            break

    for i in range(nbytes):
        byte = (val & 0x7F)
        if i > 0:  # turn on continuity
            byte += 0x80
        result = bytes([byte]) + result
        val = val >> 7

    return result


#
#
def encodeIntSiLoMB(val):
    result = b''

    sizes = [0x40, 0x2000, 0x100000, 0x80000000]

    nbytes = 1
    absval = abs(val)
    for i, size in enumerate(sizes):
        if absval < size:
            nbytes = i + 1
            break

    for i in range(nbytes):
        byte = val & 0x7f
        val = val >> 7

        if i > 0:  # turn on continuity
            byte += 0x80
        result = bytes([byte]) + result

    return result


#
#
def encodeIntSiTi(val):
    s = b''
    if val < -128 or val > 127:
        print("==> encodeIntSiTi: value out of range", val)
    else:
        s = struct.pack('>b', val)

    return s


#
#
#
def encodeIntUnTi(val):
    s = b''
    if val < 0 or val > 0xFF:
        print("==> encodeIntUnTi: value out of range", val)
    else:
        s = struct.pack('>B', val)
        # s = chr(val)

    return s


#
#
#
def encodeIntUnLi(val):
    s = b''
    if val < 0 or val > 0xFFFF:
        print("==> encodeIntUnLi: value out of range", val)
    else:
        s = struct.pack('>H', val)
        # s = chr((val&0xFF00)>>8)+ chr((val&0x00FF))

    return s


#
#
#
def encodeIntSiLi(val):
    s = b'\xFF\xFF'

    if val < -32768 or val > 32767:
        print("==> encodeIntSiLi: value out of range", val)
    else:
        s = struct.pack('>h', val)
        # s = chr((val&0xFF00)>>8)+ chr((val&0x00FF))

    return s


#
#
#
def encodeIntUn24(intval):
    result = []

    if intval < 0 or intval > 0xFFFFFF:
        print("==> encodeIntUn24: value out of range", intval)
    else:
        for i in range(3):
            result.append(intval & 0xFF)
            intval = intval >> 8

        result.reverse()

    ret = b''
    for x in result:
        ret += bytes([x])

    return ret


#
#
#
def encodeIntSi24(intval):
    result = []

    if intval < -8388608 or intval > 8388607:
        print("==> encodeIntSi24: value out of range", intval)
    else:
        for i in range(3):
            result.append(intval & 0xFF)
            intval = intval >> 8

        result.reverse()

    ret = b''
    for x in result:
        ret += bytes([x])

    return ret


#
#
#
def encodeIntUnLo(intval):
    result = []
    if intval < 0 or intval > 0xFFFFFFFF:
        print("==> encodeIntUnLo: value out of range", intval)
    else:
        for i in range(4):
            result.append(intval & 0xFF)
            intval = intval >> 8

        result.reverse()

    ret = b''
    for x in result:
        ret += bytes([x])

    return ret


#
#
#
def encodeMajorMinorVersion(major, minor):
    if major > 15 or major < 0:
        print("==> encodeMajorMinorVersion: value Major out of range", major)
    if minor > 15 or minor < 0:
        print("==> encodeMajorMinorVersion: value Minor out of range", minor)

    intval = (((major & 0x0F) << 4) | (minor & 0x0F))

    return encodeIntUnTi(intval)


#
#
#
def encodeDateTimeUTC(timeval):
    intval = int(timegm(timeval.timetuple()))
    return encodeIntUnLo(intval)


#
def encodeDateTimeLocal(timeval):
    intval = int(mktime(timeval.timetuple()))
    return encodeIntUnLo(intval)


#
#
def encodeDateTime(timeval):
    intval = int(mktime(timeval.timetuple()))
    return encodeIntUnLo(intval)


#
#
def encodeShortString(string):
    s = b''
    # all strings are converted to UTF-8 first
    string = string.encode('utf-8')

    l = len(string)
    if l > 255:
        print("==> encodeShortString: string too long", l, string, "truncated")
        l = 255
        string = string[:255]

    s += encodeIntUnTi(l)
    s += string

    return s


#
#
def encodeLongString(string):
    s = b''
    # all strings are converted to UTF-8 first
    string = string.encode('utf-8')

    l = len(string)
    if l > 65535:
        print("==> encodeLongString: string too long", l, string, "truncated")
        l = 65335
        string = string[:65535]

    s += encodeIntUnLi(l)
    s += string

    return s


#
#
#
def encodeLocalisedShortString(string, LC=38):  # default language is English
    s = b''

    # all strings are converted to UTF-8 first
    string = string.encode('utf-8')

    s += encodeIntUnTi(LC)
    l = len(string)
    if l > 255:
        print("==> encodeLocalisedShortString: string too long", l, string, "truncated")
        l = 255
        string = string[:255]

    s += encodeIntUnTi(l)
    s += string

    return s


#
#
#
def encodeLocalisedLongString(string, LC=38):  # default language is English
    s = b''

    # all strings are converted to UTF-8 first
    string = string.encode('utf-8')

    s += encodeIntUnTi(LC)
    l = len(string)
    if l > 65535:
        print("==> encodeLocalisedLongString: string too long", l, string, "truncated")
        l = 65535
        string = string[:65535]

    s += encodeIntUnLi(l)
    s += string

    return s


#
#
# Not a base type but common occurrence
#
#
def encodeWGS84coordinate(lon, lat):
    # WGS84 coordinate: Lon/Lat only
    #
    ## lon = (float(lon)*2**24)/360.0
    lon = (((1.0 * lon) / 360.0) * 2 ** 24)
    if lon < 0:
        lon -= 0.5
    else:
        lon += 0.5
    #
    lon = int(lon)
    #
    #
    ##lat = (float(lat)*2**24)/360.0
    lat = (((1.0 * lat) / 360.0) * 2 ** 24)
    if lat < 0:
        lat -= 0.5
    else:
        lat += 0.5
    #
    lat = int(lat)

    return encodeIntSi24(lon) + encodeIntSi24(lat)


#
#
def encodeByteFieldAttribute(string):
    s = b''

    l = len(string)
    if l > 65535:
        print("==> encodeByteFieldAttribute: string too long", l, string, "truncated")
        l = 65535
        string = string[:65535]

    s += encodeIntUnLi(l)
    s += string

    return s


#
# ---------------------------------------------------------------------------------------------------------------

# run when file is run on command line
if __name__ == '__main__':
    files = sys.argv[1:]  # contains the list of *.s files

    print("TPEG_data_types: dummy test")

    s = 65536

    t = TPEG_string(encodeIntUnLoMB(s))
    print(t.len(), t.IntUnLoMB())
