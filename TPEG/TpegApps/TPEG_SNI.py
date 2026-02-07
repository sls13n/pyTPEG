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
# class for TPEG SNI component and frame parsing
#
#
#
import os, sys
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))


import Base
from Base.TPEG_string             import TPEG_string
from Base.TPEG_SNI_base_component import TPEG_SNI_base_component
from Base.TPEG_component_frame    import TPEG_ProtectedCountedComp_frame
#
from Base.TPEG_error              import TPEG_log_error

#
# Application frame
#
class TPEG_SNI_frame_continuation(TPEG_ProtectedCountedComp_frame):
     def __init__(self,id,level=2,componentsDict={},Cname="SNI",Ctype="SNI_component_frame"):
         componentsDict[ 0] = TPEG_SNI_component_00
         componentsDict[ 1] = TPEG_SNI_component_01
         componentsDict[ 3] = TPEG_SNI_component_03
         componentsDict[ 4] = TPEG_SNI_component_04
         componentsDict[ 6] = TPEG_SNI_component_06
         componentsDict[ 7] = TPEG_SNI_component_07
         componentsDict[ 8] = TPEG_SNI_component_08
         componentsDict[11] = TPEG_SNI_component_11
         componentsDict[14] = TPEG_SNI_component_14
         componentsDict[33] = TPEG_SNI_component_33
         TPEG_ProtectedCountedComp_frame.__init__(self,id,level,componentsDict,Cname,Ctype)

#
# Application component
#

class TPEG_SNI_component(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component",Ctype="SNI"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        return
#
# ==============================================================================================
#
# 00
#
class TPEG_SNI_component_00(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Service name and service description\"",Ctype="SNI_00"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Service Name",        TPEGstring.ShortString()])
        self.attributes.append(["Service Description", TPEGstring.ShortString()])
#
#
# 01
#
class TPEG_SNI_component_01(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Guide to the service table 1 (Fast Tuning)\"",Ctype="SNI_01"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):

        self.sni_table_version = TPEGstring.IntUnTi()
        self.character_table   = TPEGstring.IntUnTi()
        self.attributes.append(["Table version",   self.sni_table_version])
        self.attributes.append(["Character table", self.character_table  ])

        self.ServiceComponents = []
        #
        # parse service components table
        while TPEGstring.len()>0:
            SCID     = TPEGstring.IntUnTi();
            selector = TPEGstring.IntUnTi();

            if (selector & 0x01) > 0:
                SIDa = TPEGstring.IntUnTi()
                SIDb = TPEGstring.IntUnTi()
                SIDc = TPEGstring.IntUnTi()
                OriginatorSID = str(SIDa)+"."+str(SIDb)+"."+str(SIDc)
            else:
                OriginatorSID = None

            COID = TPEGstring.IntUnTi()
            AID  = TPEGstring.IntUnLi()

            if (selector & 0x04) > 0:
                optime_start = TPEGstring.IntUnLo()
                optime_end   = TPEGstring.IntUnLo()

                optime=[optime_start,optime_end]
            else:
                optime=None

            if (selector & 0x08) > 0:
                EncID = TPEGstring.IntUnTi()
            else:
                EncID = None

            SafetyFlag = False
            if (selector & 0x10) > 0:
                SafetyFlag = True

            if SafetyFlag:
                self.attributes.append(["SCID %2d"%SCID, "(COID=%2d, AID=%2d, SafetyFlag set)"%(COID,AID)])
            else:
                self.attributes.append(["SCID %2d"%SCID, "(COID=%2d, AID=%2d)"%(COID,AID)])

            # maintain list of ServiceComponent tuples
            self.ServiceComponents.append([SCID, AID, OriginatorSID, COID, optime, EncID, SafetyFlag])

            # store application table in registry
            SID = self.Registry["SID"]
            if SID not in self.Registry:
                self.Registry[SID] = {}

            for comp in self.ServiceComponents:
                SCID = comp[0]
                self.Registry[SID][SCID] = comp[1:]

#
#
# 03
#
class TPEG_SNI_component_03(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Content description\"",Ctype="SNI_03"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])

        while TPEGstring.len()>0:
            SCID      =  TPEGstring.IntUnTi();
            Content   =  TPEGstring.ShortString()
            self.attributes.append(["Content SCID %d"%SCID, Content])
#
#
#
# 04
#
class TPEG_SNI_component_04(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Guide to the service table 4 (geographical coverage)\"",Ctype="SNI_04"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])

        # now parse coverage areas
        while TPEGstring.len()>0:
            SCID      =  TPEGstring.IntUnTi();
            NW_corner0 = TPEGstring.IntSiLi()*0.01
            NW_corner1 = TPEGstring.IntSiLi()*0.01
            SE_corner0 = TPEGstring.IntSiLi()*0.01
            SE_corner1 = TPEGstring.IntSiLi()*0.01

            self.attributes.append(["SCID %2d"%SCID, "geo coverage: NW: (lon=%5.2f, lat=%5.2f), SE:(lon=%5.2f, lat=%5.2f)"%(NW_corner0, NW_corner1,SE_corner0, SE_corner1)])

#
#
# 06
#
class TPEG_SNI_component_06(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Service table accelerator\"",Ctype="SNI_06"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])
#
#
# 07
#
class TPEG_SNI_component_07(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Service logo\"",Ctype="SNI_07"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.graphic_type = TPEGstring.IntUnTi()

        sni001 = {1:"BMP",2:"PNG",3:"JPG"}

        if self.graphic_type in sni001:
            GT = sni001[self.graphic_type]
        else:
            GT =str(self.graphic_type)+": unknown graphic type"
            TPEG_log_error("==> SNI 07: unknown graphic type: "+str(self.graphic_type))


        self.attributes.append(["Graphic Type", GT])
#
#
# 08
#
class TPEG_SNI_component_08(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Linkage table to same service components\"",Ctype="SNI_08"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        #componentsDict[ 0] = DAB_bearer_linkage_component
        #componentsDict[ 1] = INTERNET_bearer_linkage_component
        #componentsDict[ 2] = DARC_bearer_linkage_component
        #componentsDict[ 3] = DVB_bearer_linkage_component
        componentsDict[ 0] = TPEG_SNI_base_component
        componentsDict[ 1] = TPEG_SNI_base_component
        componentsDict[ 2] = TPEG_SNI_base_component
        componentsDict[ 3] = TPEG_SNI_base_component
        componentsDict[15] = HD_RADIO_bearer_linkage_component

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])

        # parse now linkage info per SCID
        while TPEGstring.len()>0:
            line_attr_string = TPEGstring.string()[:5]

            SCID     = TPEGstring.IntUnTi();
            selector = TPEGstring.IntUnTi();

            SIDa = TPEGstring.IntUnTi()
            SIDb = TPEGstring.IntUnTi()
            SIDc = TPEGstring.IntUnTi()
            OriginatorSID = str(SIDa)+"."+str(SIDb)+"."+str(SIDc)

            RegionalizedFlag = False
            if (selector & 0x02) > 0:
                RegionalizedFlag = True

            if RegionalizedFlag:
                attrib = ["Linking SCID %2d in SNI-08 to"%SCID, "(SID=%s, RegionalizedFlag set)"%(OriginatorSID)]
            else:
                attrib = ["Linking SCID %2d in SNI-08 to"%SCID, "(SID=%s)"%(OriginatorSID)]

            if (selector & 0x01) == 0:
                self.attributes.append(attrib)
            elif (selector & 0x01) > 0:
                self.subcomponents.append(self.parse_subcomponent(self.level+1,TPEGstring,
                                                                  initial_attribs=[attrib],
                                                                  line_attr_string = line_attr_string))
#
# bearer_linkage_info components
class HD_RADIO_bearer_linkage_component(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"HD Radio bearer and linkage information\"",Ctype="SNI_HD"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        HDRadioTransmitter = TPEGstring.IntUnLo()
        self.attributes.append(["HD Radio Transmitter Station", "Station ID 0x%04X"%HDRadioTransmitter])

        # parse lists of AM and FM stations
        m1 = TPEGstring.IntUnTi()
        for i in range(m1):
            if TPEGstring.len() == 0:
                TPEG_log_error("==> HD_RADIO_bearer_linkage: not enough room for %d FM alt frequencies"%m1)
                break

            StationID = TPEGstring.IntUnLo()
            FMfreq    = TPEGstring.IntUnTi()

            if FMfreq > 0 and FMfreq < 205:
                FMfreq = 87.5 +FMfreq/10.0
            else:
                TPEG_log_error("==> Wrong FM frequency code %d for StationID 0x%04X, TransmitterStation 0x%04X"%(FMfreq,StationID,HDRadioTransmitter))

            self.attributes.append(["HD Radio alt FM Station %d"%(i+1), "Station ID 0x%04X, FM Freq %6.2f MHz"%(StationID,FMfreq)])

        m2 = TPEGstring.IntUnTi()
        for i in range(m2):
            if TPEGstring.len() == 0:
                TPEG_log_error("==> HD_RADIO_bearer_linkage: not enough room for %d AM alt frequencies"%m1)
                break

            StationID = TPEGstring.IntUnLo()
            AMfreq    = TPEGstring.IntUnTi()

            if AMfreq < 123: #ITU region
                AMfreq = AMfreq       *  9 + 522 #KHz
            elif AMfreq >= 128:
                AMfreq = (AMfreq-128) * 10 + 530 #KHz
            else:
                TPEG_log_error("==> Wrong AM frequency code %d for StationID 0x%04X, TransmitterStation 0x%04X"%(AMfreq,StationID,HDRadioTransmitter))

            self.attributes.append(["HD Radio alt AM Station %d"%(i+1), "Station ID 0x%04X, AM Freq %4d KHz"%(StationID,AMfreq)])
#
#
# 11
#
class TPEG_SNI_component_11(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Free text\"",Ctype="SNI_11"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):

        FreeText =  TPEGstring.ShortString()
        self.attributes.append(["Free text", FreeText])
#
#
# 14 ==> 0E hex
#
class TPEG_SNI_component_14(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Guide to the Service Table 7 (Versioning)\"",Ctype="SNI_14"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])

        while TPEGstring.len()>0:
            SCID      =  TPEGstring.IntUnTi();
            Major     =  TPEGstring.IntUnTi();
            Minor     =  TPEGstring.IntUnTi();
            self.attributes.append(["SCID %2d"%SCID, "Specification Version: (Major=%2d, Minor=%2d)"%(Major,Minor)])
#
#
# 33 = 21 hex
#
class TPEG_SNI_component_33(TPEG_SNI_base_component):
    def __init__(self,id,level=0,componentsDict={},Cname="SNI component \"Service Information Table 1 (Number of Messages)\"",Ctype="SNI_33"):
        TPEG_SNI_base_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(["Table version", TPEGstring.IntUnTi()])

        while TPEGstring.len()>0:
            SCID        =  TPEGstring.IntUnTi();
            numMessages =  TPEGstring.IntUnLo();
            self.attributes.append(["number of messages for SCID %2d"%SCID, "%d"%numMessages])


#
# Test functionality
#

if __name__ == '__main__':
    print("TPEG_SNI_component")
