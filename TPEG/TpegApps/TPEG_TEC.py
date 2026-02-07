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
# TEC class for TPEG component and frame pparsing
#
#
import os, sys
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))


import Base
#
from Base.TPEG_error              import TPEG_log_error
#
from Base.TPEG_string             import TPEG_string
from Base.TPEG_component          import TPEG_component, TPEG_datastructure
from Base.TPEG_component_frame    import TPEG_ProtPrioCountedComp_frame
#
from TpegMMC.TPEG_MMC             import TPEG_MMC_component
#
from TpegLRC.TPEG_LRC             import TPEG_LRC_component

# TEC tables
from .TPEG_TEC_tables              import TEC_code_to_text
#
# Application frame
#

class TPEG_TEC_frame_continuation(TPEG_ProtPrioCountedComp_frame):
     def __init__(self,id,level=2,componentsDict={},Cname="TEC",Ctype="TEC_component_frame"):
         componentsDict[0] = TPEG_TEC_component
         TPEG_ProtPrioCountedComp_frame.__init__(self,id,level,componentsDict,Cname,Ctype)

#
# =================================================================================================
#
# first define TEC local components, then TPEG_TEC_component
#
class TEC_Event_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="Event",Ctype="TEC_Event"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[ 4] = TEC_DirectCause_component
        componentsDict[ 5] = TEC_LinkedCause_component
        componentsDict[ 6] = TEC_Advice_component
        componentsDict[ 7] = TEC_Restriction_component
        componentsDict[ 8] = TEC_DiversionRoute_component
        componentsDict[11] = TEC_TemporarySpeedLimit_component

    def parse_attributes(self,TPEGstring):

        self.effectCode  = TPEGstring.IntUnTi();
        self.attributes.append(['effectCode',TEC_code_to_text(self.effectCode,"TEC_001")])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['startTime', TPEGstring.DateTime()])

        if selector.is_set(1):
             self.attributes.append(['stopTime', TPEGstring.DateTime()])

        if selector.is_set(2):
            self.tendency = TPEGstring.IntUnTi()
            self.attributes.append(['Tendency', TEC_code_to_text(self.tendency,"TEC_006")]);

        if selector.is_set(3):
            self.lengthAffected = TPEGstring.DistanceMetres()
            self.attributes.append(['lengthAffected', self.lengthAffected]);

        if selector.is_set(4):
            self.attributes.append(['averageSpeedAbsolute', TPEGstring.Velocity()]);

        if selector.is_set(5):
            self.attributes.append(['delay', TPEGstring.IntUnLoMB()]);

        if selector.is_set(6):
            self.attributes.append(['segmentSpeedLimit', TPEGstring.Velocity()]);

        if selector.is_set(7):
            self.attributes.append(['expectedSpeedAbsolute', TPEGstring.Velocity()]);

        if selector.is_set(8):
          self.parse_n_datastructures_of_type(TPEGstring, 'temporarySpeedLimt',
                                              TemporarySpeedLimit)
#
#
#
class TEC_DirectCause_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="DirectCause",Ctype="TEC_DirectCause"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.unverifiedInformation = False
        self.subCause              = None
        self.lengthAffected        = None
        self.laneRestriction       = None
        self.numberOfLanes         = None
        self.free_text             = []
        self.causeOffset           = False

        self.causeCode  = TPEGstring.IntUnTi();
        self.attributes.append(['mainCause',TEC_code_to_text(self.causeCode,"TEC_002")])

        self.warningLevel  = TPEGstring.IntUnTi();
        self.attributes.append(['warningLevel',TEC_code_to_text(self.warningLevel,"TEC_003")])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['unverifiedinformation', True])
            self.unverifiedInformation = True

        if selector.is_set(1):
            self.subCause  = TPEGstring.IntUnTi();
            self.attributes.append(['subCause',TEC_code_to_text(self.subCause,"TEC_002",switch_code=self.causeCode)])

        if selector.is_set(2):
            self.lengthAffected = TPEGstring.DistanceMetres()
            self.attributes.append(['lengthAffected', self.lengthAffected]);

        if selector.is_set(3):
            self.laneRestriction = TPEGstring.IntUnTi()
            self.attributes.append(['laneRestriction',TEC_code_to_text(self.laneRestriction,"TEC_004")])


        if selector.is_set(4):
            self.numberOfLanes  = TPEGstring.IntUnTi()
            self.attributes.append(['numberOfLanes', self.numberOfLanes]);

        if selector.is_set(5):
            self.parse_n_attributes_of_type(TPEGstring, 'freeText', TPEGstring.LocalisedShortString)

        if selector.is_set(6):
            self.causeOffset = TPEGstring.DistanceMetres()
            self.attributes.append(['causeOffset',self.causeOffset])
#
#
#
class TEC_LinkedCause_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="LinkedCause",Ctype="TEC_LinkedCause"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['linkedMessage', TPEGstring.IntUnLoMB()]);

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['COID', TPEGstring.IntUnTi()]);

        if selector.is_set(1):
            try:
                SIDa = TPEGstring.IntUnTi();
                SIDb = TPEGstring.IntUnTi();
                SIDc = TPEGstring.IntUnTi();
                self.attributes.append(['SID', str(SIDa)+"."+str(SIDb)+"."+str(SIDc)])
            except IndexError:
                TPEG_log_error("==> TEC LinkedCause: could not retrieve SID")


#
#
#
class TEC_Advice_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="Advice",Ctype="TEC_Advice"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[7] = TEC_Restriction_component

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.adviceCode    = None
        self.subAdviceCode = None

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
           self.adviceCode = TPEGstring.IntUnTi()
           self.attributes.append([   'adviceCode', TEC_code_to_text(self.adviceCode,"TEC_005")]);

        if selector.is_set(1):
           self.subAdviceCode = TPEGstring.IntUnTi()
           self.attributes.append(['subAdviceCode', TEC_code_to_text(self.subAdviceCode,"TEC_005", self.adviceCode)]);

        if selector.is_set(2):
           self.parse_n_attributes_of_type(TPEGstring, 'freeText', TPEGstring.LocalisedShortString)

        return
#
#
#
class TEC_Restriction_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="Restriction",Ctype="TEC_Restriction"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.vehicleType = None

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
           self.vehicleType = TPEGstring.IntUnTi()
           self.attributes.append([ 'vehicleType', TEC_code_to_text(self.vehicleType,"TEC_009")]);

        if selector.is_set(1):
           self.parse_n_datastructures_of_type(TPEGstring,"restriction",TEC_RestrictionType)


        return
#
#
#
# TPEG data structure for inside TEC_Restriction_component
#
class TEC_RestrictionType(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="RestrictionType",Ctype="TEC_RestrictionType"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)
        componentsDict[9] = TPEG_LRC_component # restriction location

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.restrictionType = TPEGstring.IntUnTi()
        self.attributes.append([ 'restrictionType', TEC_code_to_text(self.restrictionType,"TEC_007")]);

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
           self.restrictionValue = TPEGstring.IntUnLoMB()
           self.attributes.append([ 'restrictionValue', self.restrictionValue])

        if selector.is_set(1):
            self.parse_subcomponent(self.level+1,TPEGstring,Cname="restrictionLocation")
#
        return
#
#
#
class TEC_DiversionRoute_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="DiversionRoute",Ctype="TEC_DiversionRoute"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[7] = TEC_Restriction_component

    def parse_attributes(self,TPEGstring):
        self.parse_n_datastructures_of_type(TPEGstring,"segmentModifier",TEC_SegmentModifier)
        return
#
#
# TPEG data structure for inside TEC_DiversionRoute_component
#
class TEC_SegmentModifier(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="SegmentModifier",Ctype="TEC_SegmentModifier"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)
        componentsDict[10] = TPEG_LRC_component # segment location

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.diversionRoadType = TPEGstring.IntUnTi()
        self.attributes.append([ 'diversionRoadType', TEC_code_to_text(self.diversionRoadType,"TEC_008")]);
        self.parse_subcomponent(self.level+1,TPEGstring,Cname="segmentLocation")
#
#
# TemporarySpeedLimit component inside TEC Event component
#
class TEC_TemporarySpeedLimit_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="TemporarySpeedLimit",Ctype="TEC_TemporarySpeedLimit"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[7] = TEC_Restriction_component

    def parse_attributes(self,TPEGstring):
        # defaults for optional params
        self.unitIsMPH = False

        self.parse_n_datastructures_of_type(TPEGstring,"TemporarySpeedLimitSection",TemporarySpeedLimitSection)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.unitIsMPH = True
            self.attributes.append([ 'unitIsMPH', self.unitIsMPH ]);

        if selector.is_set(1):
            self.offset = TPEGstring.DistanceMetres()
            self.attributes.append([ 'offset', self.offset ]);

        return

#
# TPEG data structure for inside TEC_TemporarySpeedLimit
#
class TemporarySpeedLimitSection(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="TemporarySpeedLimitSection",Ctype="TemporarySpeedLimitSection"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # defaults for optiopnal params
        self.speedLimitValue = TPEGstring.IntUnTi()
        self.attributes.append([ 'speedLimitValue', self.speedLimitValue]);

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.speedLimitValueWet = TPEGstring.IntUnTi()
            self.attributes.append([ 'speedLimitValueWet', self.speedLimitValueWet])

        if selector.is_set(1):
            self.speedLimitLength = TPEGstring.DistanceMetres()
            self.attributes.append([ 'speedLimitLength', self.speedLimitLength])
#
        return
#
#
#
#
class TPEG_TEC_component(TPEG_component):
    def __init__(self,id,level=0,componentsDict={},Cname="TECmessage",Ctype="TEC"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[1] = TPEG_MMC_component
        componentsDict[2] = TPEG_LRC_component
        componentsDict[3] = TEC_Event_component


#
# Test functionality
#
import os,sys,re, getopt
#
#
if __name__ == '__main__':

    files = sys.argv[1:] #contains the list of TEC binary files

    if not files:
        print("\n\nUSAGE: TPEG_TEC_component <binary TECmessage files>\n")
        exit(0)

    for fname in files:
        print("\n === start parsing " + fname +"=======================================")

        try:
            f = open(os.path.expanduser(fname),"rb")
        except:
            print("TPEG_TEC_component: Could not open file", fname)
            continue

        string = f.read()

        print("\nLength of file %s = %d"%(fname, len(string)))

        TPEGstring = TPEG_string(string)
        f.close();

        CompID = TPEGstring.IntUnTi()
        if CompID == 0:
            TECdict = {}
            TECdict[1] = TPEG_MMC_component;

            TEC = TPEG_TEC_component(0);
            TEC.parse(TPEGstring)

            print("\n\n")
            TEC.out()
        else:
            print("Wrong Component ID", CompID)

        print("\n === end parsing " + fname +"=========================================\n")
