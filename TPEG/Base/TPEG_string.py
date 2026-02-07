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
# base class for TPEG string parsing for standard data types
#
#
import sys, zlib, struct, math
#
#
from .TPEG_error import TPEG_log_error
#
# datetime is needed for unix time conversion
from datetime import datetime
from functools import reduce


#
# Utilities
#
def UShort2ByteString(val):
    s = b''
    if val < 0 or val > 0xFFFF:
        print("UShort2ByteString: value out of range", val)
    else:
        s += ((val & 0xFF00) >> 8).to_bytes(1, 'big') + (val & 0x00FF).to_bytes(1, 'big')

    return s


#
#
def _tostring(a, b):
    return a + chr(b)


#
# Helper class for selectors
#
class TPEG_BitArray:
    def __init__(self, value):
        ''' given a list of unsigned integers (incl possible continuation flags, return TPEG_BitArray class '''
        self.value = value
        self.bits = []

        # convert to options
        for el in value:
            self.bits.extend([el & 0x40, el & 0x20, el & 0x10, el & 0x08, el & 0x04, el & 0x02, el & 0x01])

        # convert to True/False
        self.options = [x > 0 and True or False for x in self.bits]

        return

    def is_set(self, bit):
        val = False
        try:
            val = self.options[bit]
        except:
            pass

        # print "BitArray Option %d has value"%bit, val, self.options
        return val


#
# === class TPEG_string ===============================================
#

class TPEG_string:
    def __init__(self, bytestring):
        self.data = bytestring
        pass

    def clear(self):
        """ empty out string"""
        self.data = []
        return

    def len(self):
        """ return length of string data"""
        return len(self.data)

    def advance(self, length):
        """ skip over first elements"""
        subdata = []
        try:
            if length > 0:
                subdata = self.data[:length]
                self.data = self.data[length:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for advance()")

        return subdata

    def string(self):
        return bytes(self.data)

    def compress(self):
        string = bytes(self.data)
        try:
            string = zlib.compress(string)
            self.data = [i for i in string]
        except:
            TPEG_log_error("==> TPEG string: zlib compression failed")

    def decompress(self):
        # l1 = len(self.data)
        string = bytes(self.data)
        try:
            string = zlib.decompress(string)
            self.data = [i for i in string]
            # l2 = len(self.data)
            # sys.stderr.write('compressed length %d, original length %d, compression %3.2f \n'%(l1,l2,100-l1*100.0/l2))
        except:
            TPEG_log_error("==> TPEG string: zlib decompression failed")
            self.data = []  # eliminate corrupted data

    def popstring(self, length):
        """ return new TEPGstring class with first items"""
        TPEGstring = TPEG_string(b'')
        try:
            if length > 0:
                TPEGstring.data = self.data[:length]
                self.data = self.data[length:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for popstring(%d)" % length)

        return TPEGstring

    def BitArray(self):
        """ decode a BitArray"""
        val = []
        try:
            i = 0
            done = False

            while not (done):
                el = self.data[i]
                val.append(el)
                if (el & 0x80) == 0:
                    done = True
                else:
                    i += 1
                    if i == 5:
                        TPEG_log_error("==> TPEG string: very long BitArray?!")

            self.data = self.data[i + 1:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for BitArray")

        return TPEG_BitArray(val)

    def ByteFieldAttribute(self):
        data = []
        try:
            length = self.IntUnLi()
            data = self.advance(length)
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for ByteFieldAttribute")

        s = ''
        for i in data:
            s = s + chr(i)

        return s

    def IntUnTi(self):
        """ decode an Unsigned Integer Tiny"""
        val = -1
        try:
            val = self.data[0]
            self.data = self.data[1:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntUnTi")

        return val

    def IntSiTi(self):
        """ decode an Signed Integer Tiny"""
        val = -1
        try:
            val = bytes([self.data[0]])
            val = struct.unpack('>b', val)[0]

            self.data = self.data[1:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntSiTi")

        return val

    def IntSi24(self):
        """ decode an Signed Integer 24 bit"""
        val = -1
        try:
            if (self.data[0] & 0x80):
                val = -1
            else:
                val = 0

            val = (val << 8) + (self.data[0] & 0xFF)
            val = (val << 8) + (self.data[1] & 0xFF)
            val = (val << 8) + (self.data[2] & 0xFF)

            # advance
            self.data = self.data[3:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntSi24")

        return val

    # ISO way of coordinate conversion
    def IntSi24asWGS84Coord(self):
        val = self.IntSi24()

        return round((1.0 * val - math.copysign(0.5, val)) * 360.0 / 2 ** 24, 5)

    def IntUnLi(self):
        """ decode an Unsigned Integer Little"""
        val = -1
        try:
            val = (self.data[0] << 8) + (self.data[1])
            self.data = self.data[2:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntUnLi")

        return val

    def IntSiLi(self):
        """ decode an Signed Integer Tiny"""
        val = -1
        try:
            val = bytes([self.data[0], self.data[1]])
            val = struct.unpack('>h', val)[0]

            self.data = self.data[2:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntSiLi")

        return val

    def IntUnLo(self):
        """ decode an Unsigned Integer Long"""
        val = -1
        try:
            val = (self.data[0] << 24) + (self.data[1] << 16) + (self.data[2] << 8) + (self.data[3])
            self.data = self.data[4:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntUnLo")

        return val

    def IntUnLoMB(self):
        """ decode an Unsigned Integer MultiByte"""
        val = -1
        try:
            val = 0
            i = 0
            done = False
            while not (done):
                el = self.data[i]
                val = (val << 7) + (el & 0x7F)
                if (el & 0x80) == 0:
                    done = True
                else:
                    i += 1

            self.data = self.data[i + 1:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntUnLoMB")

        return val

    def IntSiLoMB(self):
        """ decode an Signed Integer MultiByte"""
        val = -1
        try:
            if (self.data[0] & 0x40) != 0:
                val = -1
            else:
                val = 0

            i = 0
            done = False

            while not (done):
                el = self.data[i]
                val = (val << 7) + (el & 0x7F)
                if (el & 0x80) == 0:
                    done = True
                else:
                    i += 1

            self.data = self.data[i + 1:]

        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for IntSiLoMB")

        return val

    def MajorMinorVersion(self):
        """ decode a version indicator"""
        major = minor = val = -1
        try:
            val = self.data[0]
            self.data = self.data[1:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for MajorMinorVersion")

        if val >= 0:
            major = (val & 0xF0) >> 4
            minor = (val & 0x0F)

        return [major, minor]

    def DateTime(self):
        """ decode an UTC timestamp"""
        val = -1
        try:
            val = (self.data[0] << 24) + (self.data[1] << 16) + (self.data[2] << 8) + (self.data[3])
            try:
                val = datetime.utcfromtimestamp(val)
            except ValueError:
                TPEG_log_error("==> TPEG string: invalid data for DateTime: 0x%08X" % val)

            self.data = self.data[4:]
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for DateTime")

        return val

    def DistanceCentriMetres(self):
        """ decode distance in centimeters"""
        val = self.IntUnLoMB()
        return val

    def DistanceMetres(self):
        """ decode distance in meters"""
        val = self.IntUnLoMB()
        return val

    def Weight(self):
        """ decode weight in Kg"""
        val = self.IntUnLoMB()
        return val

    def Velocity(self):
        """ decode velocity in m/s"""
        val = -1
        try:
            val = self.data[0]
            self.data = self.data[1:]

        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for Velocity")

    def ShortString(self):
        data = []
        try:
            length = self.IntUnTi()
            data = self.advance(length)
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for ShortString")

        s = ''
        for i in data:
            s = s + chr(i)

        return '"' + s + '"'

    def LongString(self):
        data = []
        try:
            length = self.IntUnLi()
            data = self.advance(length)
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for LongString")

        s = ''
        for i in data:
            s = s + chr(i)

        return '"' + s + '"'

    def LocalisedShortString(self):
        data = []
        LCcode = -1
        try:
            LCcode = self.IntUnTi()
            length = self.IntUnTi()
            data = self.advance(length)
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for LocalisedShortString")

        s = 'LangCode: %d, ' % LCcode + "\""
        for i in data:
            s = s + chr(i)
        s += "\""
        return s

    def LocalisedLongString(self):
        data = []
        LCcode = -1
        try:
            LCcode = self.IntUnTi()
            length = self.IntUnLi()
            data = self.advance(length)
        except IndexError:
            TPEG_log_error("==> TPEG string: not enough data for LongString")

        s = 'LangCode: %d, ' % LCcode + "\""
        for i in data:
            s = s + chr(i)

        return s + "\""

    def ServiceIdentifier(self):
        SIDa = self.IntUnTi()
        SIDb = self.IntUnTi()
        SIDc = self.IntUnTi()

        SID = str(SIDa) + "." + str(SIDb) + "." + str(SIDc)

        return SID

    def TimePoint(self):
        val = '<TimePoint>: '
        selector = self.BitArray()
        prev = False
        if selector.is_set(0):  # years
            val += 'year:' + (self.IntUnTi() + 1970)
            prev = True
        if selector.is_set(1):  # month
            val = val + ', ' if prev else val
            val += 'month:' + (self.IntUnTi())
            prev = True
        if selector.is_set(2):  # days
            val = val + ', ' if prev else val
            val += 'day:' + (self.IntUnTi())
            prev = True
        if selector.is_set(3):  # hour
            val = val + ', ' if prev else val
            val += 'hour:' + (self.IntUnTi())
            prev = True
        if selector.is_set(4):  # min
            val = val + ', ' if prev else val
            val += 'minutes:' + (self.IntUnTi())
            prev = True
        if selector.is_set(5):  # sec
            val = val + ', ' if prev else val
            val += 'seconds:' + (self.IntUnTi())

        return val

    def TimeInterval(self):
        val = '<TimeInterval>: '
        selector = self.BitArray()
        prev = False
        if selector.is_set(0):  # years
            val += 'years:' + (self.IntUnTi())
            prev = True
        if selector.is_set(1):  # month
            val = val + ', ' if prev else val
            val += 'months:' + (self.IntUnTi())
            prev = True
        if selector.is_set(2):  # days
            val = val + ', ' if prev else val
            val += 'days:' + (self.IntUnTi())
            prev = True
        if selector.is_set(3):  # hour
            val = val + ', ' if prev else val
            val += 'hours:' + (self.IntUnTi())
            prev = True
        if selector.is_set(4):  # min
            val = val + ', ' if prev else val
            val += 'minutes:' + (self.IntUnTi())
            prev = True
        if selector.is_set(5):  # sec
            val = val + ', ' if prev else val
            val += 'seconds:' + (self.IntUnTi())

        return val

    def TimeToolkit(self):  # not yet pretty printed, could be modified into a data structure
        val = '<TimeToolkit>: '
        selector = self.BitArray()
        prev = False
        if selector.is_set(0):  # start time
            val += 'startTime:' + (self.TimePoint())
            prev = True
        if selector.is_set(1):  # stop time
            val = val + ', ' if prev else val
            val += 'stopTime:' + (self.TimePoint())
            prev = True
        if selector.is_set(2):  # days
            val = val + ', ' if prev else val
            val += 'duration:' + (self.TimeInterval())
            prev = True
        if selector.is_set(3):  # hour
            val = val + ', ' if prev else val
            val += 'SpecialDay (typ002):' + (self.IntUnTi())
            prev = True
        if selector.is_set(4):  # Day
            val = val + ', ' if prev else val
            val += 'Day:' + (self.DaySelector())
            prev = True

        return val

    def DaySelector(self):

        values = ['Saturday', 'Friday', 'Thursday', 'Wednesday', 'Tuesday', 'Monday', 'Sunday']
        s = ''
        selector = self.BitArray()

        for i in range(6, -1, -1):  # run reverse order such that days are ordered Sun->Sat
            if selector.is_set(i):
                if len(s) > 0:
                    s += ' or '
                s += values[i]
        #
        return s


if __name__ == '__main__':
    print("TPEG_string")

    ## t = TPEG_string('abcdeeeeeeeeeeeeeeeeeeeeeeeefffffffffffffffffgggggggggggggghhhhhh')
    ## print reduce(_tostring,t.data,'')
    ## t.compress()
    ## print reduce(_tostring,t.data,'')
    ## t.decompress()
    ## print reduce(_tostring,t.data,'')

    ## a = [0xFF, 0x00, 0x00]

    ## s = reduce(_tostring,a,'')

    ## t = TPEG_string(s)

    ## print t.data

    ## v = t.IntSi24()
    ## print -2**23,"val",v
