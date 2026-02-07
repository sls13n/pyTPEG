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
# class for CAP info component XML parsing
#
import xml, optparse
#
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
#
from .CAP_error import CAP_log_error, CAP_error_set_object, CAP_error_unset_object
#
from .CAP_base_component import CAP_base_component
from .CAP_resource_component import CAP_resource_component
from .CAP_area_component import CAP_area_component

#
#
# ========================================================================
#
#
_is_string = lambda x: isinstance(x, str)
#
_is_stringOrNone = lambda x: (x is None) or isinstance(x, str)
#
_is_category = lambda x: x in ["Geo", "Met", "Safety", "Security",
                               "Rescue", "Fire", "Health", "Env",
                               "Transport", "Infra", "CBRNE", "Other"]
#
_is_responseType = lambda x: x in ["Shelter", "Evacuate", "Prepare",
                                   "Execute", "Avoid", "Monitor",
                                   "Assess", "AllClear", "None"]
#
_is_urgency = lambda x: x in ["Immediate", "Expected", "Future", "Past", "Unknown"]
#
_is_severity = lambda x: x in ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
#
_is_certainty = lambda x: x in ["Observed", "Likely", "Possible", "Unlikely", "Unknown"]
#
#
_is_URI = _is_string  # to be made
#
_is_dateTime = _is_string  # to be made
#
_is_parameter = None  # to be made


#
#

class CAP_info_component(CAP_base_component):
    def __init__(self, id, level=0, CAPversion="1.2", componentsDict={}, Cname="info", Ctype="CAP_info"):
        CAP_base_component.__init__(self, id, level, CAPversion, componentsDict, Cname, Ctype)
        componentsDict[0] = [  # simple elements
            # [mandatory, list, name, validation function ]
            [False, False, "language", _is_string],
            [True, True, "category", _is_category],
            [True, False, "event", _is_string],
            [False, True, "responseType", _is_responseType],
            [True, False, "urgency", _is_urgency],
            [True, False, "severity", _is_severity],
            [True, False, "certainty", _is_certainty],
            [False, False, "audience", _is_string],
            [False, False, "effective", _is_dateTime],
            [False, False, "onset", _is_dateTime],
            [False, False, "expires", _is_dateTime],
            [False, False, "senderName", _is_string],
            [False, False, "headline", _is_string],
            [False, False, "description", _is_string],
            [False, False, "instruction", _is_stringOrNone],
            [False, False, "web", _is_URI],
            [False, False, "contact", _is_string]
        ]

        componentsDict[1] = [  # parameters
            [False, True, "eventCode", _is_parameter],
            [False, True, "parameter", _is_parameter]
        ]
        componentsDict[2] = [
            [False, True, "resource", CAP_resource_component],
            [False, True, "area", CAP_area_component]
        ]
        return

    def parse(self, XMLelement, Registry={}):
        #
        # first parse standard elements
        CAP_base_component.parse(self, XMLelement, Registry={})

        # set mandatory attributes
        self.category = [x for x in self.elements if x[0] == "category"][0][1]
        self.event = [x for x in self.elements if x[0] == "event"][0][1]
        self.urgency = [x for x in self.elements if x[0] == "urgency"][0][1]
        self.severity = [x for x in self.elements if x[0] == "severity"][0][1]
        self.certainty = [x for x in self.elements if x[0] == "certainty"][0][1]

        return


if __name__ == '__main__':
    print("CAP_info_component")
