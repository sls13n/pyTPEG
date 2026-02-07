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
from .CAP_base_component import CAP_base_component
#
from .CAP_info_component import CAP_info_component

#
#
# ========================================================================
#
#
_is_string = lambda x: isinstance(x, str)
#
_is_status = lambda x: x in ["Actual", "Exercise", "System", "Test", "Draft"]
#
_is_msgType = lambda x: x in ["Alert", "Update", "Cancel", "Ack", "Error"]
#
_is_scope = lambda x: x in ["Public", "Restricted", "Private"]
#
_is_dateTime = _is_string  # to be made


#
#

class CAP_alert_component(CAP_base_component):
    def __init__(self, id, CAPversion="1.2", level=0, componentsDict={}, Cname="alert", Ctype="CAP_alert"):
        CAP_base_component.__init__(self, id, level, CAPversion, componentsDict, Cname, Ctype)
        componentsDict[0] = [  # simple elements
            # [mandatory, list, name, validation function ]
            [True, False, "identifier", _is_string],
            [True, False, "sender", _is_string],
            [True, False, "sent", _is_dateTime],
            [True, False, "status", _is_status],
            [True, False, "msgType", _is_msgType],
            [False, False, "source", _is_string],
            [True, False, "scope", _is_scope],
            [False, False, "restriction", _is_string],
            [False, False, "addresses", _is_string],
            [False, True, "code", _is_string],
            [False, False, "note", _is_string],
            [False, False, "references", _is_string],
            [False, False, "incidents", _is_string]
        ]

        componentsDict[1] = [  # parameters as valueName, Value pairs
        ]
        componentsDict[2] = [  # sub components
            [False, True, "info", CAP_info_component]
        ]

        self.identifier = None
        self.sender = None
        self.sent = None
        self.status = None
        self.msgType = None
        self.scope = None

    def parse(self, XMLelement, Registry={}):
        #
        # first parse standard elements
        CAP_base_component.parse(self, XMLelement, Registry={})

        # set key attributes
        self.identifier = [x for x in self.elements if x[0] == "identifier"][0][1]
        self.sender = [x for x in self.elements if x[0] == "sender"][0][1]
        self.sent = [x for x in self.elements if x[0] == "sent"][0][1]
        self.status = [x for x in self.elements if x[0] == "status"][0][1]
        self.msgType = [x for x in self.elements if x[0] == "msgType"][0][1]
        self.scope = [x for x in self.elements if x[0] == "scope"][0][1]

        return


if __name__ == '__main__':
    print("CAP_alert_component")
