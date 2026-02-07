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
# resource class for CAP component XML parsing
#
import xml, optparse
#
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
#
from .CAP_error             import CAP_log_error,CAP_error_set_object, CAP_error_unset_object
#
from .CAP_base_component    import CAP_base_component
#
#
# ========================================================================
#
#
_is_string   = lambda x: isinstance(x,str)
#
_is_dateTime = _is_string # to be made
#
_is_parameter= None # to be made
#
_is_integer = lambda x: x.isdigit()
#
_is_URI         = _is_string # to be made
#
#
def _is_decimal(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
#

class CAP_resource_component(CAP_base_component):
    def __init__(self,id,level=0,CAPversion="1.2",componentsDict={},Cname="resource",Ctype="CAP_resource"):
        CAP_base_component.__init__(self,id,level,CAPversion,componentsDict,Cname,Ctype)
        componentsDict[ 0] = [ # simple elements
            # [mandatory, list, name, validation function ]
            [True,  False, "resourceDesc",_is_string  ],
            [True,  False, "mimeType",    _is_string  ],
            [False, False, "size",        _is_integer ],
            [False, False, "uri",         _is_URI     ],
            [False, False, "derefUri",    _is_string  ],
            [False, False, "digest",      _is_string  ],
    ]

        componentsDict[ 1] = []
        componentsDict[ 2] = []


if __name__ == '__main__':
    print("CAP_resource_component")
