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
# base class for TPEG component parsing
#
#
from .TPEG_error import TPEG_log_error, TPEG_error_set_object, TPEG_error_unset_object
from .TPEG_string import TPEG_string
from .TPEG_data_types import encodeIntUnTi, encodeIntUnLoMB


class TPEG_component_base(object):

    def __init__(self, level=0, componentsDict={}, Cname="Unknown DataStructure", Ctype="BaseDataStructure"):
        self.name = Cname
        self.type = Ctype
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.attr_length = 0
        self.attr_string = b''
        self.annotations = []  # added pairs by visitors
        self.attributes = []

        self.componentsDict = componentsDict  # list of allowed subcomponents to be parsed

    def datastructures(self, dstype=None):
        return [value for [t, value] in self.attributes if
                t == '_complex_' and (dstype is None or value.type == dstype)]

    def parse_n_attributes_of_type(self, TPEGstring, name, func):
        # parse n items in one go
        n = TPEGstring.IntUnLoMB()  # number of items
        for i in range(n):
            if TPEGstring.len() == 0:
                TPEG_log_error(
                    self.levelprefix + "==> From %s %d (of %d) %s attribute length exhausted" % (name, i, n, self.name))
                break
            self.attributes.append(['%s_%d' % (name, i), func()])

        return n

    def parse_datastructure(self, TPEGstring, name, ds_class):
        # parse datastructure: create instance & store as complex attribute
        DataStructure = ds_class(self.level + 1, Cname=name)
        DataStructure.parse(TPEGstring, Registry=self.Registry)
        self.attributes.append(['_complex_', DataStructure])

    def parse_n_datastructures_of_type(self, TPEGstring, name, ds_class):
        # parse n items in one go
        n = TPEGstring.IntUnLoMB()  # number of items
        for i in range(n):
            if TPEGstring.len() == 0:
                TPEG_log_error(
                    self.levelprefix + "==> From %s %d (of %d) %s attribute length exhausted" % (name, i, n, self.name))
                break
            self.parse_datastructure(TPEGstring, name + '_' + str(i), ds_class)

        return n

    def annotations_out(self):
        # print annotations
        # first pass: determine max length of annotations
        length = 0
        for [i, j] in self.annotations:
            if len(i) > length:
                if i not in ['_raw_', '_complex_']:
                    length = len(i)
        # second pass; pretty print annotations (aligned)
        for [i, j] in self.annotations:
            if i not in ['_raw_', '_complex_']:
                if len(i) < length:
                    i = i + ' ' * (length - len(i))
                print(self.levelprefix + "  #", i, "=", j)
            elif i in ['_complex_']:
                j.out()  # print datastructure or component

    def attributes_out(self):
        # print attributes

        # first pass: determine max length of attributes
        length = 0
        for [i, j] in self.attributes:
            if len(i) > length:
                if i not in ['_raw_', '_complex_']:
                    length = len(i)
        # second pass; pretty print attributes (aligned)
        for [i, j] in self.attributes:
            if i not in ['_raw_', '_complex_']:
                if len(i) < length:
                    i = i + ' ' * (length - len(i))
                print(self.levelprefix + "  +", i, "=", j)
            elif i in ['_complex_']:
                j.out()  # print datastructure or component

    def parse_subcomponent(self, level, TPEGstring, Cname=None):
        # get subcomponentID
        CompID = TPEGstring.IntUnTi()
        CompClass = self.componentsDict.get(CompID, TPEG_component)

        if type(CompClass) is list:
            [CompClass, name] = CompClass
            if Cname is None:  # prefer specified name
                Cname = name

        # add override name if given (for external components, e.g. LRC
        if Cname:
            Component = CompClass(CompID, level, Cname=Cname)
        else:
            Component = CompClass(CompID, level)

        Component.parse(TPEGstring, Registry=self.Registry)
        return Component


#
#
class TPEG_datastructure(TPEG_component_base):

    def parse_attributes(self, TPEGstring):
        # default behavior: store attribute bytes as string
        TPEG_log_error(self.levelprefix + "==> " + self.name + " Data structure with unspecified parsing function")
        self.attributes.append(['_raw_', TPEGstring.advance(TPEGstring.len())])

    def parse_n_subcomponents(self, level, TPEGstring, Cname=None):
        '''parse n subcomponent of a data structure'''
        # parse n items in one go
        n = TPEGstring.IntUnLoMB()  # number of items
        for i in range(n):
            if TPEGstring.len() == 0:
                TPEG_log_error(
                    self.levelprefix + "==> From %s %d (of %d) %s attribute length exhausted" % (name, i, n, self.name))
                break

            Component = self.parse_subcomponent(self, level + 1, TPEGstring, Cname=Cname)
            self.attributes.append(['_complex_', Component])

        return n

    def attributes_out(self):
        print(self.levelprefix + "  " + "Attributes")
        super().attributes_out()

    def out(self):
        print(self.levelprefix + self.name + " -- (DataStructure, type=" + self.type + ") ")
        if self.annotations:
            self.annotations_out()

        if self.attributes:
            self.attributes_out()

    #
    #
    # re-compose datastructre as binary string
    def to_binary(self):
        return self.attr_string

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):
        # set error object
        TPEG_error_set_object(self)

        # store Registry for sub components and sub data structures parsing
        self.Registry = Registry

        # parse attributes
        try:
            lb = TPEGstring.len()
            self.attr_string = TPEGstring.data
            self.parse_attributes(TPEGstring)
            la = TPEGstring.len()
            # slice parsed subset for datastructure
            self.attr_string = self.attr_string[:lb - la]

        except IndexError:
            TPEG_log_error(
                self.levelprefix + "==> " + self.name + ", type=" + self.type + " Remaining length too small for attributes")

        # done, unset error object
        TPEG_error_unset_object()

        return


#
#
#
class TPEG_component(TPEG_component_base):
    def __init__(self, id, level=0, componentsDict={}, Cname="Unknown Component", Ctype="BaseComp"):
        super().__init__(level=level, componentsDict=componentsDict, Cname=Cname, Ctype=Ctype)
        self.id = id
        self.comp_length = 0
        self.subcomponents = []

    def parse_attributes(self, TPEGstring):
        # default behavior: store attribute bytes as string
        self.attributes.append(['_raw_', TPEGstring.advance(self.attr_length)])

    def attributes_out(self):
        print(self.levelprefix + "  " + "Attributes (length Attribute block %2d):" % self.attr_length)
        super().attributes_out()

    def out(self):
        # print self, self.id, self.name

        print(
                self.levelprefix + self.name + " -- (Component ID=%02d" % self.id + ", CompLen=%2d" % self.comp_length + ", type=" + self.type + ") ")
        if self.annotations:
            self.annotations_out()

        if self.attributes:
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

        binary_string = encodeIntUnLoMB(len(self.attr_string)) + self.attr_string + comp_string
        return bytes([self.id]) + encodeIntUnLoMB(len(binary_string)) + binary_string

    #
    # overall parse command
    #
    def parse(self, TPEGstring, Registry={}):
        # set error object
        TPEG_error_set_object(self)

        # store Registry for sub components and sub data structures parsing
        self.Registry = Registry

        self.comp_length = TPEGstring.IntUnLoMB()

        # create string of length of component for isolated parsing of rest component
        #
        # check length
        if self.comp_length > TPEGstring.len():
            TPEG_log_error(self.levelprefix + "==> " + self.name +
                           " Comp ID %2d, len %2d, does not fit in remaining length available %d" % (
                               self.id, self.comp_length, TPEGstring.len()))

        # create substring of needed length
        COMPstring = TPEGstring.popstring(self.comp_length)

        self.attr_length = COMPstring.IntUnLoMB()

        # print self.levelprefix+self.name+" Comp ID %2d, len %2d, and attribute len %2d"%(self.id,self.comp_length, self.attr_length)

        # parse attributes
        if self.attr_length > 0:
            # create string of lenght attribute block for isolated parsing of attribute block
            ATTRstring = COMPstring.popstring(self.attr_length)

            #
            # store attribute_string for re-assembly
            self.attr_string = ATTRstring.data
            try:
                self.parse_attributes(ATTRstring)
            except IndexError:
                TPEG_log_error(
                    self.levelprefix + '==> ' + self.name + " CompID %2d (attribute block length %2d) too small for attributes" % (
                        self.id, self.attr_length))

            len2 = ATTRstring.len()
            if len2 > 0:
                # not all attributes parsed
                TPEG_log_error(
                    self.levelprefix + "==> " + self.name + " CompID %2d (attribute block length %2d) has unknown attributes of length %2d" % (
                        self.id, self.attr_length, len2))

        # parse subcomponents
        try:
            while COMPstring.len() > 0:
                component = self.parse_subcomponent(self.level + 1, COMPstring)  # add sub components internally
                self.subcomponents.append(component)

        except IndexError:
            TPEG_log_error(
                self.levelprefix + "==> " + self.name + " CompID %2d (component length %2d) too small for subcomponents" % (
                    self.id, self.comp_length))

        len2 = COMPstring.len()
        if len2 > 0:
            TPEG_log_error(
                self.levelprefix + "==> " + self.name + " CompID %2d has wrong component length %2d (actual %2d)" % (
                    self.id, self.comp_length, self.comp_length - len2))

        # done, unset error object
        TPEG_error_unset_object()

        return


if __name__ == '__main__':
    mtype = "TFP"
    f = open("examples/" + mtype + "message0.bin", "rb")

    bytestring = f.read()

    #print("Length of file %s = %d" % (mtype + "message0.bin", len(string)))

    TPEGstring = TPEG_string(bytestring)
    f.close()

    CompID = TPEGstring.IntUnTi()
    if CompID == 0:

        TFP = TPEG_component(0, Cname=mtype + "message")
        TFP.parse(TPEGstring)
        print("")
        TFP.out()
    else:
        print("Wrong Component ID", CompID)
