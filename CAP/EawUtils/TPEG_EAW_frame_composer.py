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
# TPEG EAW Frame Composer, given service component frames
#
#
import os, sys, getopt, re, zlib, struct

from time import time

#
# add TPEG directories, based on parent directory of executable
sys.path.append(
    os.path.abspath(sys.path[0] + os.sep + os.pardir + os.sep + os.pardir + os.sep + "TPEG"))  ## refer to TPEG branch

#
#
from Base.TPEG_CRC import TPEG_CRC
from Base.TPEG_string import TPEG_string


#
#
#
#
def UShort2ByteString(val):
    s = b''
    if val < 0 or val > 0xFFFF:
        print("UShort2ByteString: value out of range", val)
    else:
        s = bytes([(val & 0xFF00) >> 8]) + bytes([(val & 0x00FF)])

    return s


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
def TpegComponent(fname):
    # create component from file fname
    # add file length to running pack
    s = b''
    # add file contents
    try:
        fin = open(fname, "rb");
        s = fin.read()

        fin.close()
    except:
        print("TpegFrame_composer: could not open file %s" % fname)

    return s


#
#
# given a binary string, count the number of TPEG components in the string
def TPEG_num_components(s, SNI=False):
    n = 0
    TPEGstring = TPEG_string(s)

    while TPEGstring.len() > 0:
        ID = TPEGstring.IntUnTi()
        if SNI:
            l = TPEGstring.IntUnLi()
        else:
            l = TPEGstring.IntUnLoMB()

        TPEGstring.advance(l)
        n += 1
    return n


#
#
#
def TpegServiceComponentFrame(SCID, AID, componentdata):
    # create TpegServiceComponentFrame
    outs = b''

    numcomponents = TPEG_num_components(componentdata, SNI=(AID == 0))

    if AID == 0 or (AID == 15):  # add num components data crc for EAW
        componentdata = bytes([numcomponents]) + componentdata

    elif AID == 5 or AID == 7:  # add dummy group priority for TFP,TEC Service Component Frames
        componentdata = b'\x01' + bytes([numcomponents]) + componentdata
    else:
        print("Component frames for AID", AID, "not done yet!!")

    dataCRC = TPEG_CRC([i for i in componentdata])

    # determine hdrCRC
    flen = len(componentdata) + 2  # include dataCRC at end

    hdrCRCstring = bytes([SCID]) + UShort2ByteString(flen)
    if flen >= 15:  # add two for dataCRC at end
        hdrCRCstring += componentdata[:13]
    else:
        hdrCRCstring += componentdata

    hdrCRC = TPEG_CRC([i for i in hdrCRCstring])

    # component contains type 0, length, and page itself
    outs = bytes([SCID]) + UShort2ByteString(flen) + UShort2ByteString(hdrCRC) + componentdata + UShort2ByteString(dataCRC)

    return outs


#
#
#
# public test SID
CC_SIDa = 0
CC_SIDb = 225
CC_SIDc = 225
CC_ENCID = 0

CC_SID = bytes([CC_SIDa]) + bytes([CC_SIDb]) + bytes([CC_SIDc])


#
#
def TpegServiceFrame1(TpegComponentString, EncID=bytes([CC_ENCID])):
    # static data
    SID = bytes([CC_SIDa]) + bytes([CC_SIDb]) + bytes([CC_SIDc])

    # add ServiceFrameHeader: length, version, lenExtendedHeader
    ServiceFrameString = SID + EncID

    if EncID == bytes([107]):
        TpegComponentString = zlib.compress(TpegComponentString)

    ServiceFrameString += TpegComponentString

    return ServiceFrameString


#
#
#
def TpegTransportFrame(TpegServiceFrameString, Type=1):
    # static data
    SyncWord = b'\xFF\x0F'

    # calculate length of service frame
    fieldlength = len(TpegServiceFrameString)

    fl = UShort2ByteString(fieldlength)

    # calculate and add data CRC
    hdrCRCstring = SyncWord + fl + bytes([Type]);
    if len(TpegServiceFrameString) >= 11:
        hdrCRCstring += TpegServiceFrameString[:11]
    else:
        hdrCRCstring += TpegServiceFrameString

    hdrCRC = TPEG_CRC([i for i in hdrCRCstring])

    # add header
    TransportFrame = SyncWord + fl + UShort2ByteString(hdrCRC) + bytes([Type]) + TpegServiceFrameString

    return TransportFrame


#
# ---------------------------------------------------------------------------------------------------------------
#
def TpegFrame_composer_EAW(content, MAX_TpegFramesize=8000):
    #
    # static data
    #
    TpegFrame_overhead = 12  # syncword, fieldlength, hdrCRC, frametype, LenHdr, Jversion, LenExtHdr, dataCRC
    #
    #
    Frames_list = []
    #
    s = b''  # contains frame string

    content_len = len(content)

    s += content

    # -- full frame contents; create frame
    # create service component frame
    SCID = 5
    AID = 15
    s = TpegServiceComponentFrame(SCID, AID, s)

    t = SNI_generate_for_market(20)
    # create service and transport frame
    s = TpegServiceFrame1(t + s)

    s = TpegTransportFrame(s, Type=1)

    # done, return frame
    return s


#
#
#
def SNI_generate_for_market(market):
    # EAW only SCID 5, AID 15
    #
    sni_comp1 = bytes([market]) + b'\x7D\x05\x00' + bytes([market]) + b'\x00\x0F'

    sni_comp1 = b'\x01' + encodeIntUnLi(len(sni_comp1)) + sni_comp1

    # versioning SNI 3.2, EAW 1.1
    sni_comp14 = bytes([market]) + b'\x00\x03\x02\x05\x01\x01'

    sni_comp14 = b'\x0e' + encodeIntUnLi(len(sni_comp14)) + sni_comp14

    sni_payload = b'\x02' + sni_comp1 + sni_comp14

    # calculate dataCRC
    dataCRC = TPEG_CRC([i for i in sni_payload])

    sni_payload += UShort2ByteString(dataCRC)

    # ---- construct hdr CRC ------------------------------------------------
    # construct list
    length = len(sni_payload)

    l = [0, 0x0, length]

    # add first 13 bytes payload or rest
    # determine size of TPEGstring max to 13
    crclen = min(13, len(sni_payload))
    for item in sni_payload[:crclen]:
        l.append(item)

    # calculate CRC check
    hdrCRC = TPEG_CRC(l)

    # calculate dataCRC
    dataCRC = TPEG_CRC([i for i in sni_payload])

    # construct SNI_component_frame
    SNI_component_frame = b'\x00\x00' + bytes([length]) + UShort2ByteString(hdrCRC) + sni_payload

    return SNI_component_frame


#
#
# ---------------------------------------------------------------------------------------------------------------
MAX_TpegFramesize = 8094 - 64  # subtract some buffer bytes
TpegFrame_overhead = 12 + 60  # SNI additional
# run when file is run on command line
if __name__ == '__main__':

    files = sys.argv[1:]  # contains the list of *.s files

    print("TpegFrame_composer: " + "number of files ", len(files))

    index = 0
    numcomponents = 0
    s = ''

    while len(files) != 0:
        fname = files[0]
        fname_len = os.path.getsize(fname);
        # check for remaining free length of Frame
        while len(files) > 0 and \
                ((len(s) + fname_len + 5 < MAX_TpegFramesize - TpegFrame_overhead) or (numcomponents < 1)):
            files = files[1:]  # remove fname
            print("processing ", fname, "of length", fname_len)

            s += TpegComponent(fname)
            numcomponents += 1

            if len(files) > 0:
                fname = files[0]
                fname_len = os.path.getsize(fname);

        # create EAW service component frame
        SCID = 5
        AID = 15
        s = TpegServiceComponentFrame(SCID, AID, s)

        t = SNI_generate_for_market(20)
        # create service and transport frame
        s = TpegServiceFrame1(t + s)

        s = TpegTransportFrame(s, Type=1)

        # output Frame
        framefile = "TpegFrame%02d" % index + ".tpg"
        print("TpegFrame_composer: writing Frame file %s (size=%4d) with %d components\n" % (
            framefile, len(s), numcomponents))

        fout = open(framefile, "wb")
        fout.write(s)
        fout.close()
        # reset parameters
        index += 1
        numcomponents = 0
        s = ''
