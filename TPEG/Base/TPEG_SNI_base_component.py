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
# base class for TPEG SNI component parsing (no attribute block/length)
#
# Note: line item attributes are assigned to sub components for
#       parceling out information.
#
#
from .TPEG_error import TPEG_log_error
from .TPEG_data_types import encodeIntUnTi, encodeIntUnLi, encodeIntUnLoMB


#

class TPEG_SNI_base_component(object):
    def __init__(self, id, level=0, componentsDict={}, Cname="Unknown SNI Component", Ctype="SNIBaseComp"):
        self.id = id
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.comp_length = 0
        self.attr_length = 0

        self.attr_string = b''
        self.line_attr_string = b''

        self.attributes = []
        self.subcomponents = []
        self.componentsDict = componentsDict

    def parse_attributes(self, TPEGstring):
        # default behavior: store attribute bytes as string
        pass

    def parse_subcomponent(self, level, TPEGstring, initial_attribs=[], line_attr_string=b''):

        # include line item attr_string in subcomponent string
        len_before = TPEGstring.len() + len(line_attr_string)

        # get subcomponentID

        CompID = TPEGstring.IntUnTi()
        CompClass = self.componentsDict.get(CompID, TPEG_SNI_base_component)
        Component = CompClass(CompID, level)

        # add line item attributes to sub component
        Component.line_attr_string = line_attr_string

        Component.attributes.extend(initial_attribs)

        Component.parse(TPEGstring, Registry=self.Registry)
        len_after = TPEGstring.len()

        # cut-out reconstructed line item sub component (leading attributes and sub component)
        len_attr = len(self.attr_string)
        self.attr_string = self.attr_string[:-len_before] + self.attr_string[len_attr - len_after:]

        return Component

    def attributes_out(self):
        # print attributes
        print(self.levelprefix + "  " + "Attributes:")
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
        # print component
        if self.id == 0:
            print("")

        print(
                          self.levelprefix + self.name + ", ID=%02d" % self.id + ", CompLen=%2d" % self.comp_length + ", type=" + self.type)
        if len(self.attributes) > 0:
            self.attributes_out()

        for comp in self.subcomponents:
            comp.out()

    #
    # Trailer to be printed after toplevel component in frame
    def component_trailer_out(self):
        print(
                          self.levelprefix + "---- End " + self.name + " -- (Component ID=%02d" % self.id + ", CompLen=%2d" % self.comp_length + ", type=" + self.type + ") ----\n")

    #
    #
    # re-compose component as binary string
    def to_binary(self):
        comp_string = b''
        for component in self.subcomponents:
            comp_string += component.to_binary()

        # SNI component does not encode length of attributes; 'line items' including leading attributes are associated with sub components
        binary_string = self.attr_string + comp_string

        # SNI component does encode lenght of component as IntUnLi
        # include line item attribute prefix (e.g. for bearer and linkage information) here
        #
        return self.line_attr_string + self.id.to_bytes(1, 'big') + encodeIntUnLi(len(binary_string)) + binary_string

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):

        # store Registry for sub components and sub data structures parsing
        self.Registry = Registry

        # for SNI component length is an Integer Unsigned Little!!
        self.comp_length = TPEGstring.IntUnLi()

        # create string of length of component for isolated parsing of rest component
        #
        # check length
        if self.comp_length > TPEGstring.len():
            TPEG_log_error(
                self.levelprefix + '==> ' + self.name + " Comp ID %2d, len %2d, does not fit in remaining length frame %d" % (
                self.id, self.comp_length, TPEGstring.len()))

        # create string of length of component for isolated parsing of rest component
        COMPstring = TPEGstring.popstring(self.comp_length)

        # store attribute_string, any sub components are included in this string
        self.attr_string = bytes(COMPstring.data)

        #
        # check original string for reconstruction
        comp_string = self.line_attr_string
        comp_string += encodeIntUnTi(self.id)
        comp_string += encodeIntUnLi(self.comp_length)
        comp_string += self.attr_string

        self.parse_attributes(COMPstring)

        # create reconstruction string
        rec_string = self.to_binary()

        # compare originial and reconstructed string for error logging
        if comp_string != rec_string:
            TPEG_log_error(self.levelprefix + '==> ' + self.name + " Comp ID %2d" % self.id,
                           "to_binary() function does not yield original string")
        #
        return


if __name__ == '__main__':
    print("TPEG_SNI_base_component")
