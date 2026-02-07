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
# base class for TPEG Transport and Service Frame parsing
#
#
import zlib
#
from .TPEG_error import TPEG_log_error, TPEG_error_set_context, TPEG_error_unset_context
from .TPEG_string import TPEG_string
from .TPEG_CRC import TPEG_CRC
#
from .TPEG_data_types import encodeIntUnTi, encodeIntUnLi, encodeIntUnLoMB
#
from .TPEG_component_frame import TPEG_component_frame


#

class TPEG_Transport_Frame(object):
    def __init__(self, id, level=0, ApplicationFramesDict={}, Cname="Unknown Frame", Ctype="BaseFrame"):
        self.componentsDict = {}
        self.componentsDict[0] = TPEG_ServiceFrame0
        self.componentsDict[1] = TPEG_ServiceFrame1
        self.id = id
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.serviceFrameLength = -1
        self.hdrCRC = 0xFFFF
        self.ServiceFrameType = -1

        self.frame_length = 0
        self.attr_length = 0
        self.attributes = []
        self.serviceframe = False
        self.AppFrameDict = ApplicationFramesDict

    def service_frame(self, TPEGstring):
        try:
            self.syncword = TPEGstring.IntUnLi()
            if self.syncword != 0xFF0F:
                TPEG_log_error("==> Transport frame does not start with SyncWord FF0F (0x%04x)..." % self.syncword)
        except IndexError:
            TPEG_log_error("==> TPEG transport frame: could not retrieve syncword")
            return -1, TPEG_string("")

        try:
            self.serviceFrameLength = TPEGstring.IntUnLi()
            self.hdrCRC = TPEGstring.IntUnLi()
            self.ServiceFrameType = TPEGstring.IntUnTi()
        except IndexError:
            TPEG_log_error("==> TPEG transport frame: could not retrieve frame header parameters")
            return -1, TPEG_string("")
        # create string of length of service frame for isolated parsing of service frame
        if TPEGstring.len() < self.serviceFrameLength:
            TPEG_log_error("==> TPEG transport frame: Service frame length %d does not fit remaining length %d" % (
            self.serviceFrameLength, TPEGstring.len()))
            # error: return unknown Service Frame
            return -1, TPEG_string("")

        # create ServiceFrameString
        ServiceFrameString = TPEGstring.popstring(self.serviceFrameLength)

        # ---- check hdr CRC ------------------------------------------------
        # construct list
        l = [0xFF, 0x0F, (self.serviceFrameLength >> 8) & 0xFF, (self.serviceFrameLength) & 0xFF, self.ServiceFrameType]

        # add first 11 bytes payload or rest
        # determine size of TPEGstring max to 11
        len = min(11, ServiceFrameString.len())
        l.extend(ServiceFrameString.data[:len])

        # do CRC check
        hdrCRC = TPEG_CRC(l)
        if hdrCRC != self.hdrCRC:
            TPEG_log_error(
                "==> TPEG transport frame HDR CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (hdrCRC, self.hdrCRC))
            # reject service frame
            self.serviceFrameLength = 0
            ServiceFrameString.data = []
        # ---- end check hdr CRC ------------------------------------------------

        return self.ServiceFrameType, ServiceFrameString

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):
        #
        # set context here
        TPEG_error_set_context(self)

        self.ServiceFrameType, ServiceFrameString = self.service_frame(TPEGstring)

        if self.ServiceFrameType in self.componentsDict:  # ServiceFrameType registered
            self.serviceframe = self.componentsDict[self.ServiceFrameType](self.serviceFrameLength, level=1,
                                                                           ApplicationFramesDict=self.AppFrameDict)
            self.serviceframe.parse(ServiceFrameString, Registry=Registry)
        else:
            TPEG_log_error("==> TPEG transport frame: unknown frame type %d: skipped" % self.ServiceFrameType)

        # unset Transport Frame context here
        TPEG_error_unset_context()
        #

    def out(self):
        if self.serviceframe:
            print("TPEG transport frame: (type=%1d), (ServiceFrameLength=%d), (headerCRC=0x%04X)" % (
            self.ServiceFrameType,
            self.serviceFrameLength,
            self.hdrCRC))
            self.serviceframe.out()

        elif self.ServiceFrameType >= 0:
            print("TPEG transport frame: (Unknown type=%1d), (ServiceFrameLength=%d), (headerCRC=0x%04X)" % (
            self.ServiceFrameType,
            self.serviceFrameLength,
            self.hdrCRC))

    def to_binary(self):
        transport_frame_string = b'unknown service frame'
        if self.serviceframe:
            transport_frame_string = self.serviceframe.to_binary()

        serviceFrameLength = len(transport_frame_string)
        serviceFrameType = self.ServiceFrameType

        # ---- hdr CRC ------------------------------------------------
        # construct list
        l = [0xFF, 0x0F, (serviceFrameLength >> 8) & 0xFF, (serviceFrameLength) & 0xFF, serviceFrameType]

        # add first 11 bytes payload or rest
        # determine size of TPEGstring max to 11
        flen = min(11, serviceFrameLength)
        for i in range(flen):
            l.append(transport_frame_string[i])

        # do CRC check
        hdrCRC = TPEG_CRC(l)

        # ---- finalise transport_frame_string
        transport_frame_string = b'\xFF\x0F' + encodeIntUnLi(serviceFrameLength) + encodeIntUnLi(hdrCRC) + \
                                 encodeIntUnTi(serviceFrameType) + transport_frame_string

        return transport_frame_string


#
# ==============================================================================================================================
#
class TPEG_ServiceFrame0(object):
    def __init__(self, id, level=1, ApplicationFramesDict={}, Cname="Stream Directory", Ctype="ServiceFrame_0"):
        self.id = id
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.frame_length = 0
        self.numSIDs = 0
        self.SIDs = []
        self.frameCRC = 0
        self.componentsDict = {}
        self.AppFrameDict = ApplicationFramesDict

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):

        # calculate expected hdr CRC
        dataCRC = -1
        if TPEGstring.len() > 2:
            dataCRC = TPEG_CRC(TPEGstring.data[:-2])

        try:
            self.attr_length = TPEGstring.IntUnTi()
        except IndexError:
            TPEG_log_error("==> TPEG stream directory: could not retrieve number of services")

        for i in range(self.attr_length):
            try:
                SIDa = TPEGstring.IntUnTi()
                SIDb = TPEGstring.IntUnTi()
                SIDc = TPEGstring.IntUnTi()
                self.SIDs.append(str(SIDa) + "." + str(SIDb) + "." + str(SIDc))
            except IndexError:
                TPEG_log_error("==> TPEG stream directory: could not retrieve SID number %d" % i)
                break

        self.frameCRC = TPEGstring.IntUnLi()
        # check data CRC
        if dataCRC != self.frameCRC:
            TPEG_log_error("==> TPEG Stream Directory data CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (
            dataCRC, self.frameCRC))

    def out(self):
        print(self.levelprefix + "TPEG stream directory: (# SIDs= %d)" % self.attr_length)
        for i in range(self.attr_length):
            print(self.levelprefix + "SID %2d   = %s" % (i, self.SIDs[i]))

        print(self.levelprefix + "data CRC = 0x%04X" % (self.frameCRC))

    #
    # binary conversion for service frame 0
    #
    def to_binary(self):
        service_frame_string = encodeIntUnTi(len(self.SIDs))

        for SID in self.SIDs:
            SID = SID.split('.')
            SID_string = b''
            for SIDel in SID:
                SID_string += int(SIDel).to_bytes(1, 'big') # is 1 enough for length?

            service_frame_string += SID_string

        dataCRC = TPEG_CRC([ord(i) for i in service_frame_string])
        service_frame_string += encodeIntUnLi(dataCRC)

        return service_frame_string


class TPEG_ServiceFrame1(object):
    def __init__(self, id, level=1, ApplicationFramesDict={}, Cname="Service Data Frame", Ctype="ServiceFrame_1"):
        self.id = id
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.SID = ""
        self.EncID = 0
        self.LTE = None
        self.CompFrames = []
        self.componentsDict = {}
        self.AppFrameDict = ApplicationFramesDict

    #
    # parse header and decompress/decrypt if needed
    #
    def service_component_frame_bundle(self, TPEGstring):
        try:
            SIDa = TPEGstring.IntUnTi()
            SIDb = TPEGstring.IntUnTi()
            SIDc = TPEGstring.IntUnTi()
            self.SID = str(SIDa) + "." + str(SIDb) + "." + str(SIDc)
        except IndexError:
            TPEG_log_error("==> TPEG Service data Frame: could not retrieve SID of frame")

        try:
            self.EncID = TPEGstring.IntUnTi()
        except IndexError:
            TPEG_log_error("==> TPEG Service data Frame: could not retrieve Encryption ID")

        if self.EncID in [12, 31, 42, 127]:
            print("Note: Found TPEG PAC ServEncID: (partially) access controlled data, still parsed......\n")

        # zlib decompression
        if self.EncID in [31, 42, 107]:
            TPEGstring.decompress()
        # non-standard Encryption IDs to be signalled as error, and not parsed
        elif self.EncID > 127:
            TPEG_log_error("==> TPEG Service data Frame: could not decrypt EncID%d" % self.EncID)
            TPEGstring = TPEG_string(b'')

        return TPEGstring

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):
        TPEGstring = self.service_component_frame_bundle(TPEGstring)

        while TPEGstring.len() > 0:
            ServCompFrame = TPEG_component_frame(1, level=self.level + 1, componentsDict=self.AppFrameDict,
                                                 SID=self.SID)
            ServCompFrame.parse(TPEGstring, Registry=Registry)
            self.CompFrames.append(ServCompFrame)

    def out(self):
        print(self.levelprefix + "TPEG service data frame: (SID = %s), (ServEncID=%d)" % (self.SID, self.EncID))
        if self.LTE:
            print("")
            self.LTE.out()
            self.LTE.component_trailer_out()

        for frame in self.CompFrames:
            frame.out()

    #
    # binary conversion for service frame 1
    #
    def to_binary(self):

        # first string component frames together
        service_frame_string = b''
        for frame in self.CompFrames:
            service_frame_string += frame.to_binary()

        if len(service_frame_string) > 8181:  # 8KB - 11 bytes overhead
            TPEG_log_error("==> TPEG Service data Frame: uncompressed size too large: %d" % len(service_frame_string))

        # then apply zlib compression / encryption
        if self.EncID == 107:
            service_frame_string = zlib.compress(service_frame_string)

        if self.EncID != 0 and len(service_frame_string) > 8181:  # 8KB - 11 bytes overhead
            TPEG_log_error("==> TPEG Service data Frame: compressed size too large: %d" % len(service_frame_string))

        # then add header information
        SID = self.SID.split('.')
        SID_string = b''
        for SIDel in SID:
            SID_string += int(SIDel).to_bytes(1, 'big')     # is 1 enough for length?

        service_frame_string = SID_string + encodeIntUnTi(self.EncID) + service_frame_string

        return service_frame_string

#
# ===================================================================================================
#
