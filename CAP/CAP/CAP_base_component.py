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
# base class for CAP component XML parsing
#
import xml, optparse
#
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
#
from .CAP_error import CAP_log_error, CAP_error_set_object, CAP_error_unset_object

#
# CAP namespace
#
## capns 1.2      = "{urn:oasis:names:tc:emergency:cap:1.2}"
capns_stem = "{urn:oasis:names:tc:emergency:cap:"
#
_MAX_PRINT_LEN = 200


#
#
class CAP_base_component(object):
    def __init__(self, id, level=0, CAPversion="1.2", componentsDict={}, Cname="Unknown Component", Ctype="BaseComp"):
        self.id = id
        self.name = Cname
        self.type = Ctype
        self.version = CAPversion
        self.level = level
        self.levelprefix = ""
        for i in range(level):
            self.levelprefix += "  "

        self.annotations = []  # added pairs by visitors
        self.elements = []
        self.parameters = []  # complex types as valuename, value pairs
        self.subcomponents = []  # real complex types

        self.componentsDict = componentsDict

        return

    def parse_elements_of_type(self, XMLelement, el_spec):
        # parse n items in one go
        [mandatory, islist, name, func] = el_spec

        capns = capns_stem + self.version + "}"
        el_list = XMLelement.findall(capns + name)

        # error checking on presence and list
        if mandatory and not el_list:
            CAP_log_error(self.levelprefix + "==> no element of type %s: element is mandatory" % name)
        elif len(el_list) > 1 and not islist:
            CAP_log_error(
                self.levelprefix + "==> too many element of type %s: %d, max 1 allowed" % (name, len(el_list)))

        for el in el_list:
            value = "" if el.text is None else el.text

            if (func is None) or func(value):  # validate element if needed
                self.elements.append([name, value])
            else:
                CAP_log_error(self.levelprefix + "==> element %s has invalid value %s" % (name, value))

        return (el_list is not None)

    def parse_parameters_of_type(self, XMLelement, param_spec):
        [mandatory, islist, name, func] = param_spec

        capns = capns_stem + self.version + "}"
        el_list = XMLelement.findall(capns + name)

        # error checking on presence and list
        if mandatory and not el_list:
            CAP_log_error(self.levelprefix + "==> no parameter of type %s: parameter is mandatory" % name)
        elif len(el_list) > 1 and not islist:
            CAP_log_error(
                self.levelprefix + "==> too many parameters of type %s: %d, max 1 allowed" % (name, len(el_list)))

        # Now find valueName, Value pair
        for el in el_list:
            try:
                valueName = el.find(capns + "valueName").text
                value = el.find(capns + "value").text

                valueName = "" if valueName is None else valueName
                value = "" if value is None else value

                if (func is None) or func(valueName, value):  # validate element if needed
                    self.parameters.append([name, valueName, value])
                else:
                    CAP_log_error(self.levelprefix + "==> parameter %s has invalid value %s" % (name, value))
            except:
                CAP_log_error(self.levelprefix + "==> parameter %s has invalid content" % (name))

    def parse_subcomponent(self, level, XMLelement, comp_spec, Cname=None):
        '''parse subcomponent of component'''
        # get subcomponentID
        [mandatory, islist, name, CompClass] = comp_spec

        capns = capns_stem + self.version + "}"
        el_list = XMLelement.findall(capns + name)

        # error checking on presence and list
        if mandatory and not el_list:
            CAP_log_error(self.levelprefix + "==> no component of type %s: component is mandatory" % name)
        elif len(el_list) > 1 and not islist:
            CAP_log_error(
                self.levelprefix + "==> too many components of type %s: %d, max 1 allowed" % (name, len(el_list)))

        CompID = 0
        for comp in el_list:
            CompID += 1
            Component = CompClass(CompID, level, self.version, Cname=name)

            Component.parse(comp, Registry=self.Registry)
            self.subcomponents.append(Component)
        return

    def annotations_out(self, num_only=[], _MAX_PRINT_LEN=0):
        txt = ""
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

                if _MAX_PRINT_LEN > 0 and len(j) > _MAX_PRINT_LEN:
                    j = j[:_MAX_PRINT_LEN] + "..."

                txt += self.levelprefix + "  #" + str(i) + "=" + str(j) + "\n"
            elif i in ['_complex_']:
                txt += j.out()  # print datastructure or component

        return txt

    def elements_out(self, num_only=[], _MAX_PRINT_LEN=0):
        txt = ""
        if self.elements:
            txt += self.levelprefix + "  " + "Elements \n"

        print_elements = [el for el in self.elements if el[0] not in num_only]

        # first pass: determine max length of attributes
        length = 0
        for [i, j] in self.elements:
            if len(i) > length:
                if i not in ['_raw_', '_complex_']:
                    length = len(i)
        # second pass; pretty print attributes (aligned)
        for [i, j] in print_elements:
            if i not in ['_raw_', '_complex_']:
                if len(i) < length:
                    i = i + ' ' * (length - len(i))

                if _MAX_PRINT_LEN > 0 and len(j) > _MAX_PRINT_LEN:
                    j = j[:_MAX_PRINT_LEN] + "..."

                txt += self.levelprefix + "  +" + i + " = " + j + "\n"
            elif i in ['_complex_']:
                txt += j.out()  # print datastructure or component

        for eltype in num_only:
            element_eltype = [el for el in self.elements if el[0] == eltype]
            num = len(element_eltype)
            if num > 0:
                i = element_eltype[0][0]  # element type
                i = i + ' ' * (length - len(i))
                if num == 1:
                    txt += self.levelprefix + "  +" + i + " : %d occurrence\n" % num
                else:
                    txt += self.levelprefix + "  +" + i + " : %d occurrences\n" % num

        return txt

    def parameters_out(self, num_only=[], _MAX_PRINT_LEN=0):
        txt = ""
        if self.parameters:
            txt += self.levelprefix + "  " + "Parameters \n"
        # print attributes
        # print self.levelprefix+"  "+"Parameters "

        print_parameters = [el for el in self.parameters if el[1] not in num_only]

        # first pass: determine max length of parameter names
        length = 0
        for [i, j, k] in self.parameters:
            if len(i) > length:
                if i not in ['_raw_', '_complex_']:
                    length = len(i)
        # second pass; pretty print attributes (aligned)
        for [i, j, k] in print_parameters:
            if i not in ['_raw_', '_complex_']:
                if len(i) < length:
                    i = i + ' ' * (length - len(i))

                txt += self.levelprefix + "  +" + i + "\n"
                txt += self.levelprefix + "      valueName = " + j + "\n"

                if _MAX_PRINT_LEN > 0 and len(k) > _MAX_PRINT_LEN:
                    k = k[:_MAX_PRINT_LEN] + "..."
                txt += self.levelprefix + "      value     = " + k + "\n"

            elif i in ['_complex_']:
                txt += j.out()  # print datastructure or component

        for eltype in num_only:
            params_eltype = [el for el in self.parameters if el[1] == eltype]
            num = len(params_eltype)
            if num > 0:
                i = params_eltype[0][0]  # parameter type
                i = i + ' ' * (length - len(i))
                if num == 1:
                    txt += self.levelprefix + "  +" + i + " : %d occurrence  of valueName \"%s\"\n" % (num, eltype)
                else:
                    txt += self.levelprefix + "  +" + i + " : %d occurrences of valueName \"%s\"\n" % (num, eltype)

        return txt

    def out(self, num_only=[], _MAX_PRINT_LEN=0):
        txt = ""

        txt += self.levelprefix + self.name.upper() + " -- (Component type=" + self.type + ") \n"
        if self.annotations:
            txt += self.annotations_out(num_only, _MAX_PRINT_LEN)

        if self.elements:
            txt += self.elements_out(num_only, _MAX_PRINT_LEN)

        if self.parameters:
            txt += self.parameters_out(num_only, _MAX_PRINT_LEN)

        for comp in self.subcomponents:
            txt += comp.out(num_only, _MAX_PRINT_LEN)

        if self.level == 0:
            txt += self.component_trailer_out()

        return txt

    #
    # Trailer to be printed after toplevel component in frame
    def component_trailer_out(self):
        txt = self.levelprefix + "---- End " + self.name.upper() + " -- (Component type=" + self.type + ") ----\n"

        return txt

    def __str__(self):  # print method, limit to _MAX_PRINT_LEN characters
        txt = self.out(num_only=[], _MAX_PRINT_LEN=_MAX_PRINT_LEN)

        return txt

    #
    #
    # re-compose component as binary string
    def to_XML(self):
        pass
        return self.XML_string

    #
    # overall parse command
    #
    def parse(self, XMLelement, Registry={}):
        # set error object
        CAP_error_set_object(self)

        # store Registry for sub components and sub data structures parsing
        self.Registry = Registry

        # parse elements
        for el_spec in self.componentsDict.get(0, []):
            self.parse_elements_of_type(XMLelement, el_spec)

        # parse parameters
        for par_spec in self.componentsDict.get(1, []):
            self.parse_parameters_of_type(XMLelement, par_spec)

        # parse sub components
        for comp_spec in self.componentsDict.get(2, []):
            self.parse_subcomponent(self.level + 1, XMLelement, comp_spec)  # add sub components internally

        # done, unset error object
        CAP_error_unset_object()

        return
