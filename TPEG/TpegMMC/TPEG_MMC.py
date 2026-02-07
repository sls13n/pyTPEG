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
# MMC class for TPEG component parsing
#
#
#
import os, sys
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))

#
#
from .TPEG_MMC_tables     import MMC_code_to_text
#
from Base.TPEG_string    import TPEG_string
from Base.TPEG_component import TPEG_component, TPEG_datastructure

# datetime is needed for unix time conversion
from datetime import datetime
#
#
class TPEG_MMCTemplate(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="MMCTemplate",Ctype="MMCTemplate"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        # default value for ExpiryTime
        self.messageExpiryTime     = 0

        # default values for optional parameters
        self.cancelFlag            = False
        self.messageGenerationTime = None
        self.priority              = None

    def parse_attributes(self,TPEGstring):

        self.messageID         = TPEGstring.IntUnLoMB()
        self.attributes.append(['messageID',self.messageID])

        self.versionID         = TPEGstring.IntUnTi()
        self.attributes.append(['versionID',self.versionID])

        # store binary value for expiryTime
        if TPEGstring.len() >= 4:
            time      = TPEGstring.data[:4]
            timestamp = (time[0]<<24)+(time[1]<<16)+(time[2]<<8)+(time[3])

            self.messageExpiryTime = timestamp

        self.attributes.append(['messageExpiryTime',TPEGstring.DateTime()])

        selector  = TPEGstring.BitArray();

        if selector.is_set(0):
            self.cancelFlag = True
            self.attributes.append(['cancelFlag', self.cancelFlag])

        if selector.is_set(1):
            # store binary value for generation Time
            if TPEGstring.len() >= 4:
                time      = TPEGstring.data[:4]
                timestamp = (time[0]<<24)+(time[1]<<16)+(time[2]<<8)+(time[3])

                self.messageGenerationTime = timestamp
            self.attributes.append(['messageGenerationTime',TPEGstring.DateTime()])

        if selector.is_set(2):
            self.attributes.append(['priority',TPEGstring.IntUnTi()]);

        return selector
#
#
class MMC_MultiPartMessageDirectory(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="MMC_MultiPartMessageDirectory",Ctype="MMC_MultiPartMessageDirectory"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['partID',   TPEGstring.IntUnTi()])
        self.attributes.append(['partType', MMC_code_to_text(TPEGstring.IntUnTi(),"MMC_001")])

        return
#
#
class TPEG_MMC_component(TPEG_MMCTemplate):
    def __init__(self,id,level=1,componentsDict={},Cname="MMC_component",Ctype="MMC_component"):
        TPEG_MMCTemplate.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        TPEG_MMCTemplate.parse_attributes(self,TPEGstring)

        return
#
#
class TPEG_MMCMaster_component(TPEG_MMCTemplate):
    def __init__(self,id,level=1,componentsDict={},Cname="MMCMaster_component",Ctype="MMCMaster_component"):
        TPEG_MMCTemplate.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        selector = TPEG_MMCTemplate.parse_attributes(self,TPEGstring)

        self.parse_n_datastructures_of_type(TPEGstring, 'multiPartMessageDirectory',MMC_MultiPartMessageDirectory)

        return
#
#
class TPEG_MMCMessagePart_component(TPEG_MMCTemplate):
    def __init__(self,id,level=1,componentsDict={},Cname="MMCMessagePart_component",Ctype="MMCMessagePart_component"):
        TPEG_MMCTemplate.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        selector = TPEG_MMCTemplate.parse_attributes(self,TPEGstring)

        self.PartID     = TPEGstring.IntUnTi()
        self.updateMode = TPEGstring.IntUnTi()

        self.attributes.append(['partID',       self.PartID])
        self.attributes.append(['updateMode',   MMC_code_to_text(self.updateMode,"MMC_002")])
        if selector.is_set(3):
            self.parse_n_attributes_of_type(TPEGstring, 'messageVersion', TPEGstring.IntUnTi)

        return

#
# Test functionality
#

if __name__ == '__main__':
    mtype = "TPEG_MMC_component"
