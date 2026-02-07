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
# EAW class for TPEG component and frame pparsing
#
#
import os, sys
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))


from Base.TPEG_string             import TPEG_string
from Base.TPEG_component          import TPEG_component, TPEG_datastructure
from Base.TPEG_component_frame    import TPEG_ProtectedCountedComp_frame
#
from TpegMMC.TPEG_MMC             import TPEG_MMC_component
#
from TpegLRC.TPEG_LRC             import TPEG_LRC_component

from .TPEG_EAW_tables              import EAW_code_to_text

#
# Application frame
#

class TPEG_EAW_frame_continuation(TPEG_ProtectedCountedComp_frame):
     def __init__(self,id,level=2,componentsDict={},Cname="EAW",Ctype="EAW_component_frame"):
         componentsDict[0] = TPEG_EAW_component
         TPEG_ProtectedCountedComp_frame.__init__(self,id,level,componentsDict,Cname,Ctype)



## EAWMessage                            0
## MessageManagementContainer            1
## InformationArea                       2
## AlertInformation                      3
## LocalisedAlertTextInfo                4
## AffectedArea                          5
## AlertInfoParameters                   6
## Resource                              7
## CrossLinkage                          8

#
# first define EAW local components, then TPEG_EAW_component
#
#
# helper function to parse table
def _EAW_parse_table(TPEGstring, table):
    return EAW_code_to_text(TPEGstring.IntUnTi(),table)


#
# =========== EAW_AlertInformation_component and data structures ==========================================
#
#

class EAW_AlertInformation_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="AlertInformation",Ctype="EAW_AlertInformation"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        componentsDict[ 4] = EAW_LocalisedAlertTextInfo_component
        componentsDict[ 5] = [TPEG_LRC_component, "AffectedArea"]                       # EAW_AffectedArea
        componentsDict[ 6] = EAW_AlertInfoParameters_component
        componentsDict[ 7] = EAW_Resource_component
        componentsDict[ 8] = EAW_CrossLinkage_component

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['alertLevel', _EAW_parse_table(TPEGstring,"EAW_001")])

        self.parse_n_attributes_of_type(TPEGstring, 'category',         lambda: _EAW_parse_table(TPEGstring,"EAW_002"))

        self.attributes.append(['urgency'   , _EAW_parse_table(TPEGstring,"EAW_003")])
        self.attributes.append(['severity'  , _EAW_parse_table(TPEGstring,"EAW_004")])
        self.attributes.append(['certainty' , _EAW_parse_table(TPEGstring,"EAW_005")])

        self.parse_datastructure(TPEGstring, 'alertTimeInfo',EAW_CapTimeInfo)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['alertUserStatus', _EAW_parse_table(TPEGstring,"EAW_006")])

        if selector.is_set(1):
            self.parse_n_attributes_of_type(TPEGstring, 'responseType', lambda: _EAW_parse_table(TPEGstring,"EAW_007"))

        if selector.is_set(2):
            self.parse_n_datastructures_of_type(TPEGstring, 'alertEvent',      EAW_EventType)

        if selector.is_set(3):
            self.parse_n_datastructures_of_type(TPEGstring, 'alertInstruction',EAW_InstructionType)

        return

#
#
#
# TPEG data structures for inside EAW_AlertInformation_component
#
class EAW_CapTimeInfo(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="CapTimeInfo",Ctype="EAW_CapTimeInfo"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['effective', TPEGstring.DateTime()])

        if selector.is_set(1):
            self.attributes.append(['onset',     TPEGstring.DateTime()])

        if selector.is_set(2):
            self.attributes.append(['expires',   TPEGstring.DateTime()])

        return
#
#
#
# TPEG data structures for inside EAW_AlertInformation_component
#
class EAW_EventType(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="EventType",Ctype="EAW_EventType"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.mainEvent  = TPEGstring.IntUnTi();
        self.attributes.append(['mainEvent',EAW_code_to_text(self.mainEvent,"EAW_010")])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.subEvent  = TPEGstring.IntUnTi();
            self.attributes.append(['subEvent',EAW_code_to_text(self.subEvent,"EAW_010",switch_code=self.mainEvent)])

        return
#
#
#
# TPEG data structures for inside EAW_AlertInformation_component
#
class EAW_InstructionType(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="InstructionType",Ctype="EAW_InstructionType"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.mainInstruction  = TPEGstring.IntUnTi();
        self.attributes.append(['mainInstruction',EAW_code_to_text(self.mainInstruction,"EAW_011")])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.subInstruction  = TPEGstring.IntUnTi();
            self.attributes.append(['subInstruction',EAW_code_to_text(self.subInstruction,"EAW_011",switch_code=self.mainInstruction)])

        return
#
#

#
#
# =========== EAW_LocalisedAlertTextInfo_component and data structures ==========================================
#
#
class EAW_LocalisedAlertTextInfo_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="LocalisedAlertTextInfo",Ctype="EAW_LocalisedAlertTextInfo"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        self.attributes.append(['rfc3066LanguageCode', TPEGstring.ShortString()])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['eventText',       TPEGstring.LongString()])

        if selector.is_set(1):
            self.attributes.append(['audience',        TPEGstring.LongString()])

        if selector.is_set(2):
            self.attributes.append(['senderName',      TPEGstring.LongString()])

        if selector.is_set(3):
            self.attributes.append(['headline',        TPEGstring.LongString()])

        if selector.is_set(4):
            self.attributes.append(['description',     TPEGstring.LongString()])

        if selector.is_set(5):
            self.attributes.append(['instruction',     TPEGstring.LongString()])

        if selector.is_set(6):
            self.parse_datastructure(TPEGstring, 'web',EAW_AnyURI)

        if selector.is_set(7):
            self.attributes.append(['contact',         TPEGstring.LongString()])

        return
#
#
#
# TPEG data structures for inside EAW_LocalisedAlertTextInfo_component, EAW_Resource_component
#
class EAW_AnyURI(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="AnyURI",Ctype="EAW_AnyURI"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['uriString',     TPEGstring.LongString()])

        return
#
#
# =========== EAW_AlertInfoParameters_component and data structures ==========================================
#
#
class EAW_AlertInfoParameters_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="AlertInfoParameters",Ctype="EAW_AlertInfoParameters"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
             self.attributes.append(['profile',       TPEGstring.LongString()])

        if selector.is_set(1):
            self.parse_n_datastructures_of_type(TPEGstring, 'profileParameter', EAW_Parameter)

        return
#
#
#
# TPEG data structures for inside AW_AlertInfoParameters_component
#
class EAW_Parameter(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="Parameter",Ctype="EAW_Parameter"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['valueName', TPEGstring.LongString()])
        self.attributes.append(['value',     TPEGstring.LongString()])

        return
#
#
# =========== EAW_Resource_component and data structures ==========================================
#
#
class EAW_Resource_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="Resource",Ctype="EAW_Resource"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[11] = EAW_CrossLinkage_component

    def parse_attributes(self,TPEGstring):
        self.parse_n_attributes_of_type(TPEGstring, 'resourceDesc', TPEGstring.LocalisedShortString)

        self.attributes.append(['mimeType',               TPEGstring.ShortString()])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['size',               TPEGstring.IntUnLoMB()])

        if selector.is_set(1):
            self.parse_datastructure(TPEGstring, 'uri',   EAW_AnyURI)

        if selector.is_set(2):
            self.attributes.append(['derefURI',           TPEGstring.ByteFieldAttribute()])

        if selector.is_set(2):
            self.attributes.append(['digest',            TPEGstring.ByteFieldAttribute()])

        return
#
# =========== EAW_CrossLinkage_component and data structures ==========================================
#
#
class EAW_CrossLinkage_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="CrossLinkage",Ctype="EAW_CrossLinkage"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.parse_datastructure(TPEGstring,            'capSourceContent',   EAW_SourceContentCapMsgID)

        if selector.is_set(1):
            self.parse_n_datastructures_of_type(TPEGstring, 'linkedSourceContent',AW_SourceContentCapMsgID)

        if selector.is_set(2):
            self.parse_datastructure(TPEGstring,            'linkedTPEGMessage',  EAW_LinkedTPEGMessage)

        return

#
#
# TPEG data structure for inside EAW_CrossLinkage_component
#
class EAW_SourceContentCapMsgID(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="SourceContentCapMsgID",Ctype="EAW_SourceContentCapMsgID"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['capMsgID',     TPEGstring.LongString()])

        return
#
# TPEG data structure for inside EAW_CrossLinkage_component
#
class EAW_LinkedTPEGMessage(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="LinkedTPEGMessage",Ctype="EAW_LinkedTPEGMessage"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        self.attributes.append(    ['linkedMessage',   TPEGstring.IntUnLoMB()])
        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['applicationID',   TPEGstring.IntUnLi()])

        if selector.is_set(1):
            self.attributes.append(['contentID',       TPEGstring.IntUnTi()])

        if selector.is_set(2):
            self.attributes.append(['originatorSID',   TPEGstring.ServiceIdentifer()])


        return

#
# =========== main EAW_message ==========================================
#
#

class TPEG_EAW_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="EAWmessage",Ctype="EAW"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        componentsDict[ 1] = [TPEG_MMC_component,"MessageManagementContainer"]
        componentsDict[ 2] = [TPEG_LRC_component,"InformationArea"]
        componentsDict[ 3] = EAW_AlertInformation_component


#
# Test functionality
#
import os,sys,re, getopt
#
#

if __name__ == '__main__':

    files = sys.argv[1:] #contains the list of EAW binary files

    if not files:
        print("\n\nUSAGE: TPEG_EAW_component <binary EAWmessage files>\n")
        exit(0)

    for fname in files:
        print("\n === start parsing " + fname +"=======================================")

        try:
            f = open(os.path.expanduser(fname),"rb")
        except:
            print("TPEG_EAW_component: Could not open file", fname)
            continue

        string = f.read()

        print("\nLength of file %s = %d"%(fname, len(string)))

        TPEGstring = TPEG_string(string)
        f.close();

        CompID = TPEGstring.IntUnTi()
        if CompID == 0:

            EAW = TPEG_EAW_component(0);
            EAW.parse(TPEGstring)

            print("\n\n")
            EAW.out()
        else:
            print("Wrong Component ID", CompID)

        print("\n === end parsing " + fname +"=========================================\n")
