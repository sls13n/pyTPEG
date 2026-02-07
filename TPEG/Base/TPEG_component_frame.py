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
import sys
#
#
# base class for TPEG component Frame parsing
#
#
from .TPEG_string import TPEG_string
from .TPEG_CRC import TPEG_CRC
from .TPEG_error import TPEG_log_error, TPEG_error_set_context, TPEG_error_unset_context
#
from .TPEG_data_types import encodeIntUnTi, encodeIntUnLi, encodeIntUnLoMB
#
#
from .TPEG_component import TPEG_component
from .TPEG_SNI_base_component import TPEG_SNI_base_component


#
#
class TPEG_component_frame(object):
    def __init__(self, id, level=2, componentsDict={}, Cname="Component Frame", Ctype="ServCompFrame",
                 SID="084.084.078"):
        self.id = id
        self.SID = SID
        self.SCID = -1
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.fieldlength = 0
        self.hdrCRC = 0
        self.attributes = []
        self.frame_continuation = False
        self.continuation_string = ''
        self.componentsDict = componentsDict

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):
        CompFrameString = self.parse_header(TPEGstring)

        # set current SID in the registry
        Registry["SID"] = self.SID

        try:
            # select continuation on basis self.SID, self.SCID (!=0, otherwise SNI) and SNI fast tuning table
            # SNI fast tuning table is stored at location: Registry[self.SID]
            if self.SCID == 0:
                self.frame_continuation = self.componentsDict[0](self.SCID, level=self.level)
            else:
                self.frame_continuation = self.componentsDict[Registry[self.SID][self.SCID][0]](self.SCID,
                                                                                                level=self.level)
            #
            # now parse

        except KeyError:
            self.continuation_string = CompFrameString.string()
            TPEG_log_error(
                "==> TPEG Component frame: no AID registered/frame_type known for SCID %d, skipped\n" % self.SCID)
            return

        # now parse frame continuation

        # check for encryption (when not SNI)
        #
        # Registry[self.SID][self.SCID] = [ AID, OriginatorSID, COID, optime, EncID, SafetyFlag]
        #
        if self.SCID != 0 and Registry[self.SID][self.SCID][4] not in [None, 0]:
            #
            # extract EncID
            EncID = Registry[self.SID][self.SCID][4]
            self.continuation_string = CompFrameString.string()
            TPEG_log_error(
                "==> TPEG Component frame: Encryption ID %d unknown for SCID %d, skipped\n" % (EncID, self.SCID))
            return

        # unencrypted content now, parse
        self.frame_continuation.parse(CompFrameString, Registry=Registry)

    #
    # parsing of standard component header
    #

    def parse_header(self, TPEGstring):
        try:
            self.SCID = TPEGstring.IntUnTi()
            self.fieldlength = TPEGstring.IntUnLi()
            self.hdrCRC = TPEGstring.IntUnLi()
        except IndexError:
            TPEG_log_error("==> TPEG component frame: could not retrieve SCID, fieldlength, or hdrCRC")

        self.attributes.append(["SCID", self.SCID])
        self.attributes.append(["fieldlength", self.fieldlength])
        self.attributes.append(["hdrCRC", "0x%04X" % self.hdrCRC])

        # create string of length of service frame for isolated parsing of service frame
        if TPEGstring.len() < self.fieldlength:
            TPEG_log_error("==> TPEG component frame: component frame length %d does not fit remaining length %d" % (
            self.fieldlength, TPEGstring.len()))

        CompFrameString = TPEGstring.popstring(self.fieldlength)

        # ---- check hdr CRC ------------------------------------------------
        # construct list
        l = [self.SCID, (self.fieldlength >> 8) & 0xFF, (self.fieldlength) & 0xFF]

        # add first 13 bytes payload or rest
        # determine size of TPEGstring max to 13
        flen = min(13, CompFrameString.len())
        for item in CompFrameString.data[:flen]:
            l.append(item)

        # do CRC check
        hdrCRC = TPEG_CRC(l)
        if hdrCRC != self.hdrCRC:
            TPEG_log_error(
                "==> TPEG component frame HDR CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (hdrCRC, self.hdrCRC))
            CompFrameString.clear()

        return CompFrameString

    #
    #
    # binary conversion
    #
    def to_binary(self):
        if not self.frame_continuation:
            return self.continuation_string  # return stored continuation string

        # here a valid frame continuation is present, SCID is known
        frame_continuation_string = self.frame_continuation.to_binary()

        fieldlength = len(frame_continuation_string)

        # calculate header CRC
        l = [self.SCID, (fieldlength >> 8) & 0xFF, (fieldlength) & 0xFF]

        # add first 13 bytes payload or rest
        # determine size of TPEGstring max to 13
        flen = min(13, fieldlength)
        for item in frame_continuation_string[:flen]:
            l.append(ord(item))

        # final calculate header CRC
        hdrCRC = TPEG_CRC(l)

        component_frame_string = encodeIntUnTi(self.SCID) + encodeIntUnLi(fieldlength) + encodeIntUnLi(
            hdrCRC) + frame_continuation_string

        return component_frame_string

    #
    # pretty print attributes
    #
    def attributes_out(self):
        # print attributes
        print(self.levelprefix + "  " + "Header attributes:")
        # first pass: determine max length of attributes
        length = 0
        for [i, j] in self.attributes:
            if len(i) > length:
                if i != '_raw_':
                    length = len(i)
        # second pass; pretty print attributes (aligned)
        for [i, j] in self.attributes:
            if i != '_raw_':
                if len(i) < length:
                    for k in range(length - len(i)):
                        i = i + ' '
                print(self.levelprefix + "  +", i, "=", j)

    #
    # pretty print frame
    #
    def out(self):
        print(self.levelprefix + "TPEG component frame: (fieldlength=%d)" % self.fieldlength)
        self.attributes_out()

        if self.frame_continuation != False:
            self.frame_continuation.out()


#
# Specialisations for continuations
#
class TPEG_comp_frame_continuation(object):
    def __init__(self, id, level=2, componentsDict={}, Cname="Comp Frame Continuation", Ctype="CompFrameContinuation"):
        self.name = Cname
        self.type = Ctype
        self.attributes = []
        self.components = []
        self.componentsDict = componentsDict
        self.SCID = id
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

    def parse(self, TPEGstring, Registry={}):
        #
        # in specialized frames CRC check is done on continuation
        #
        self.parse_continuation(TPEGstring, Registry=Registry)

    def parse_attributes(self, TPEGstring):
        pass

    def parse_continuation(self, TPEGstring, Registry={}):
        #
        # first parse attributes
        self.parse_attributes(TPEGstring)
        #
        # then parse components
        while TPEGstring.len() > 0:
            CompID = TPEGstring.IntUnTi()

            # print "TPEG_frame_continuation: %d components, remaining length %d"%(len(self.components),TPEGstring.len()+1)
            if CompID in self.componentsDict:
                Comp = self.componentsDict[CompID](CompID, level=self.level + 1)
            else:
                # test whether the unknown component is an SNI component or "Normal component"
                # ==> parse accordingly
                if self.SCID != 0:
                    Comp = TPEG_component(CompID, level=self.level + 1)
                else:
                    Comp = TPEG_SNI_base_component(CompID, level=self.level + 1)

            if Comp != False:
                # set context before parsing
                TPEG_error_set_context(Comp)
                Comp.parse(TPEGstring, Registry=Registry)
                TPEG_error_unset_context()

                self.components.append(Comp)

        self.attributes.append(["Components parsed", len(self.components)])

    #
    # to binary
    #
    def to_binary(self):
        frame_continuation_string = b''
        for comp in self.components:
            frame_continuation_string += comp.to_binary()

        return frame_continuation_string

    #
    # pretty print attributes
    #
    def attributes_out(self):
        # print attributes
        print(self.levelprefix + "  " + "Extended Attributes:")
        # first pass: determine max length of attributes
        length = 0
        for [i, j] in self.attributes:
            if len(i) > length:
                if i != '_raw_':
                    length = len(i)
        # second pass; pretty print attributes (aligned)
        for [i, j] in self.attributes:
            if i != '_raw_':
                if len(i) < length:
                    for k in range(length - len(i)):
                        i = i + ' '
                print(self.levelprefix + "  +", i, "=", j)

    def out(self):
        self.attributes_out()
        print("")
        for comp in self.components:
            comp.out()
            #
            # for top-level components print trailer
            comp.component_trailer_out()


class TPEG_ProtectedComp_frame(TPEG_comp_frame_continuation):
    def __init__(self, id, level=2, componentsDict={}, Cname="ComponentFrame", Ctype="TPEG_ProtectedComp_frame"):
        TPEG_comp_frame_continuation.__init__(self, id, level, componentsDict, Cname, Ctype)

    #
    # parse separates dataCRC at end
    #
    def parse_continuation(self, TPEGstring, Registry={}):
        CompString = TPEGstring.popstring(TPEGstring.len() - 2)
        self.dataCRC = TPEGstring.IntUnLi()
        #
        dataCRC = TPEG_CRC(CompString.data)
        if dataCRC != self.dataCRC:
            TPEG_log_error("==> TPEG_ProtectedComp_frame: data CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (
            dataCRC, self.dataCRC))
            CompString.clear()

        TPEG_comp_frame_continuation.parse_continuation(self, CompString, Registry=Registry)

    #
    # to_binary
    #
    def to_binary(self):
        # add attributes and components
        frame_continuation_string = TPEG_comp_frame_continuation.to_binary(self)

        # calculate dataCRC
        dataCRC = TPEG_CRC([i for i in frame_continuation_string])

        frame_continuation_string += encodeIntUnLi(dataCRC)

        return frame_continuation_string


class TPEG_ProtectedCountedComp_frame(TPEG_comp_frame_continuation):
    def __init__(self, id, level=2, componentsDict={}, Cname="ComponentFrame", Ctype="TPEG_ProtCountComp_frame"):
        TPEG_comp_frame_continuation.__init__(self, id, level, componentsDict, Cname, Ctype)

        self.dataCRC = 0
        self.messageCount = 0

        #
        # parse separates dataCRC at end
        #

    def parse_continuation(self, TPEGstring, Registry={}):
        CompString = TPEGstring.popstring(TPEGstring.len() - 2)
        self.dataCRC = TPEGstring.IntUnLi()
        #
        dataCRC = TPEG_CRC(CompString.data)
        if dataCRC != self.dataCRC:
            TPEG_log_error(
                "==> TPEG_ProtectedCountedComp_frame: data CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (
                dataCRC, self.dataCRC))

        TPEG_comp_frame_continuation.parse_continuation(self, CompString, Registry=Registry)

        if len(self.components) != self.messageCount:
            TPEG_log_error("==> TPEG_ProtectedCountedComp_frame: messageCount (actual=%d, sent=%d) not correct ..."
                           % (len(self.components), self.messageCount))

    def parse_attributes(self, TPEGstring):
        self.messageCount = TPEGstring.IntUnTi()
        self.attributes.append(["Message count", self.messageCount])
        self.attributes.append(["dataCRC", "0x%04X" % self.dataCRC])

    #
    # to_binary
    #
    def to_binary(self):
        # add attributes and components
        messageCount = len(self.components)
        frame_continuation_string = encodeIntUnTi(messageCount) + TPEG_comp_frame_continuation.to_binary(self)

        # calculate dataCRC
        dataCRC = TPEG_CRC([ord(i) for i in frame_continuation_string])

        frame_continuation_string += encodeIntUnLi(dataCRC)

        return frame_continuation_string


class TPEG_ProtectedPrioComp_frame(TPEG_comp_frame_continuation):
    def __init__(self, id, level=2, componentsDict={}, Cname="CompenentFrame", Ctype="TPEG_ProtPrioComp_frame"):
        TPEG_comp_frame_continuation.__init__(self, id, level, componentsDict, Cname, Ctype)

        self.dataCRC = 0
        self.groupPriority = 0

    #
    # parse separates dataCRC at end
    #
    def parse_continuation(self, TPEGstring, Registry={}):
        CompString = TPEGstring.popstring(TPEGstring.len() - 2)
        self.dataCRC = TPEGstring.IntUnLi()
        #
        dataCRC = TPEG_CRC(CompString.data)
        if dataCRC != self.dataCRC:
            TPEG_log_error("==> TPEG_ProtectedPrioComp_frame: data CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (
            dataCRC, self.dataCRC))

        TPEG_comp_frame_continuation.parse_continuation(self, CompString, Registry=Registry)

    def parse_attributes(self, TPEGstring):
        self.groupPriority = TPEGstring.IntUnTi()
        self.attributes.append(["Group Priority", self.groupPriority])
        self.attributes.append(["dataCRC", "0x%04X" % self.dataCRC])

    #
    # to_binary
    #
    def to_binary(self):
        # add attributes and components
        frame_continuation_string = encodeIntUnTi(self.groupPriority) + TPEG_comp_frame_continuation.to_binary(self)

        # calculate dataCRC
        dataCRC = TPEG_CRC([ord(i) for i in frame_continuation_string])

        frame_continuation_string += encodeIntUnLi(dataCRC)

        return frame_continuation_string


class TPEG_ProtPrioCountedComp_frame(TPEG_comp_frame_continuation):
    def __init__(self, id, level=2, componentsDict={}, Cname="CompenentFrame", Ctype="TPEG_ProtCountComp_frame"):
        TPEG_comp_frame_continuation.__init__(self, id, level, componentsDict, Cname, Ctype)

        self.dataCRC = 0
        self.groupPriority = 0
        self.messageCount = 0

    #
    # parse separates dataCRC at end
    #
    def parse_continuation(self, TPEGstring, Registry={}):
        CompString = TPEGstring.popstring(TPEGstring.len() - 2)
        self.dataCRC = TPEGstring.IntUnLi()

        dataCRC = TPEG_CRC(CompString.data)
        if dataCRC != self.dataCRC:
            TPEG_log_error(
                "==> TPEG_ProtPrioCountedComp_frame: data CRC (actual=0x%04X, sent=0x%04X) not correct ..." % (
                dataCRC, self.dataCRC))

        TPEG_comp_frame_continuation.parse_continuation(self, CompString, Registry=Registry)

        if len(self.components) != self.messageCount:
            TPEG_log_error("==> TPEG_ProtPrioCountedComp_frame: messageCount (actual=%d, sent=%d) not correct ..."
                           % (len(self.components), self.messageCount))

    def parse_attributes(self, TPEGstring):
        self.groupPriority = TPEGstring.IntUnTi()
        self.attributes.append(["Group priority", self.groupPriority])
        self.messageCount = TPEGstring.IntUnTi()
        self.attributes.append(["Message count", self.messageCount])
        # append dataCRC as last attribute
        self.attributes.append(["dataCRC", "0x%04X" % self.dataCRC])

    #
    # to_binary
    #
    def to_binary(self):
        # add attributes and components
        messageCount = len(self.components)
        frame_continuation_string = encodeIntUnTi(self.groupPriority) + encodeIntUnTi(
            messageCount) + TPEG_comp_frame_continuation.to_binary(self)

        # calculate dataCRC
        dataCRC = TPEG_CRC([ord(i) for i in frame_continuation_string])

        frame_continuation_string += encodeIntUnLi(dataCRC)

        return frame_continuation_string


#
# =========================================================================
#

if __name__ == '__main__':
    print("TPEG_component_frame")

    files = sys.argv[1:]  # contains the list of *.s files

    print("TPEG parser: " + "number of files ", len(files))

    for fname in files:
        print(" === start parsing " + fname + "=========================================\n")

        f = open(fname, "rb")
        string = f.read()

        print("Length of file %s = %d" % (fname, len(string)))

        TPEGstring = TPEG_string(string)
        f.close()
        frames = []

        while TPEGstring.len() > 0:
            TPEG_compframe = TPEG_component_frame(0)
            TPEG_compframe.parse(TPEGstring)
            frames.append(TPEG_compframe)

        print("\n\n")
        for frame in frames:
            frame.out()
            print("\n")

        print("\n === end parsing " + fname + "=========================================\n")
