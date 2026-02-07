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
# Generic utility to synchronise in stream on Transport Frame
#
#
from .TPEG_CRC import TPEG_CRC

#
#
#
# ================================================================================================================
#
TPEG_debug = False
TPEG_log = False
ff_index = 1


#
#
def TPEG_sync_frame(TPEGstring, AppName="TPEG"):
    global ff_index
    global TPEG_debug
    global TPEG_log

    index = 0
    Found = False
    while Found == False and TPEGstring.len() > 0:
        try:
            index = TPEGstring.data.index(0xFF)
            if TPEGstring.data[index + 1] != 0x0F:
                TPEGstring.advance(index + 1)  # move past first 0xFF
                continue

            length = (TPEGstring.data[index + 2] << 8) + (TPEGstring.data[index + 3])
            frameCRC = (TPEGstring.data[index + 4] << 8) + (TPEGstring.data[index + 5])
            #
            # ---- check hdr CRC ------------------------------------------------
            # construct list
            l = [0xFF, 0x0F, (length >> 8) & 0xFF, (length) & 0xFF, (TPEGstring.data[index + 6])]

            # add first 11 bytes payload or rest
            # determine size of TPEGstring max to 11
            len1 = min(11, length)
            l.extend(TPEGstring.data[index + 7:index + 7 + len1])

            # do CRC check
            hdrCRC = TPEG_CRC(l)

            if hdrCRC != frameCRC:  # hdr CRC fails
                TPEGstring.advance(index + 1)  # move past first 0xFF
                if TPEG_debug:
                    print("==> " + AppName + "_sync_frame: incorrect HDR CC for syncword at index %d\n" % (index))
                continue  # next try

            # print("Found frame at index", index)

            # ---- end check hdr CRC ------------------------------------------------
            #
            #

            if TPEGstring.len() > index + 8 + length:
                # follow on string, check for sync word or padding
                w1 = TPEGstring.data[index + 7 + length]
                w2 = TPEGstring.data[index + 8 + length]
            else:
                # check presence of last byte, if not exception will occur
                w0 = TPEGstring.data[index + 6 + length]
                w1 = 0x00
                w2 = 0x00

            if ((w1 == 0x00 and (w2 == 0x00 or w2 == 0xFF)) or (w1 == 0xFF and w2 == 0x0F)):
                Found = True
                TPEGstring.advance(index)
                if TPEG_debug:
                    print("==> " + AppName + "_sync_frame: HDR CRC OK, frame length OK (0x%04x) at index %d\n" % (
                        length, index))
            else:
                if TPEG_debug:
                    print(
                        "==> " + AppName + "_sync_frame: HDR CRC OK, but frame (ff #%d) misformed (incorrect length 0x%04x) at index %d\n" % (
                            ff_index, length, index), w1, w2)
                    if TPEG_log:
                        ff = open('FF_frame_%02d' % ff_index + '.tpeg', 'wb')
                        ff_index += 1
                        ff.write(b''.join([i for i in TPEGstring.data[index:index + 7 + length]]))
                        ff.close()

                TPEGstring.advance(index + 1)  # move past first 0xFF
        except:
            print("==> " + AppName + "_sync_frame: unsynced or insufficient data: %d\n" % (TPEGstring.len()))

            TPEGstring.data = []

    return Found
