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
# ETL LR class for TPEG component parsing
#
#
#
import os, sys
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))



from Base.TPEG_string    import TPEG_string
from Base.TPEG_component import TPEG_component, TPEG_datastructure

#
#
# -------- ETL -----------------------------------------------------------------------
#
class ETL_TMC_datastructure(TPEG_datastructure):
    def __init__(self,level=1,componentsDict={},Cname="ETL_TMC",Ctype="ETL_TMC"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        # default attributes
        self.bothDirections      = False
        self.extent              = 0
        self.extendedCountryCode = None
        self.locationTableVersion= None
        #
        self.useInternalPrimaryLocation   = False
        self.useInternalSecondaryLocation = False
        #
        #
        self.locationID          = TPEGstring.IntUnLi()
        self.countryCode         = TPEGstring.IntUnTi()
        self.locationTableNumber = TPEGstring.IntUnTi()

        self.attributes.append(['locationID' ,        self.locationID])
        self.attributes.append(['countryCode',  '%1x'%self.countryCode])
        self.attributes.append(['locationTableNumber',self.locationTableNumber])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.direction = 'Positive'
        else:
            self.direction = 'Negative'

        self.attributes.append(['direction', self.direction])

        if selector.is_set(1):
            self.bothDirections = True
            self.attributes.append(['bothDirections', True])

        if selector.is_set(2):
            self.extent = TPEGstring.IntUnTi()
            self.attributes.append(['extent',  self.extent])

        if selector.is_set(3):
            self.extendedCountryCode = TPEGstring.IntUnTi()
            self.attributes.append(['extendedCountryCode', '%02x'%self.extendedCountryCode])

        if selector.is_set(4):
            self.locationTableVersion = TPEGstring.IntUnLoMB()
            MajorVersion = MinorVersion = 0
            if self.locationTableVersion > 127: # 2 bytes, 7bits major, 7bits minor
                MajorVersion = ((self.locationTableVersion>>7)&0x007F) # 7bits major version
                MinorVersion = ((self.locationTableVersion   )&0x007F) # 7bits minor version
            else:
                MajorVersion = ((self.locationTableVersion>>3)&0x0F)   # 4bits major version
                MinorVersion = ((self.locationTableVersion   )&0x07)   # 3bits minor version

            self.attributes.append(['locationTableVersion', "%d.%d"%(MajorVersion, MinorVersion)])

        if selector.is_set(5):
            self.parse_datastructure(TPEGstring, 'preciseTMCInformation',ETL_preciseTMCinformation)

        # selector.is_set(6)
        self.useInternalPrimaryLocation   = selector.is_set(6)
        self.attributes.append(['useInternalPrimaryLocation',self.useInternalPrimaryLocation])

        # selector.is_set(7)
        self.useInternalSecondaryLocation = selector.is_set(7)
        self.attributes.append(['useInternalSecondaryLocation',self.useInternalSecondaryLocation])
#
#
#
class ETL_DirLocation_datastructure(TPEG_datastructure):
    def __init__(self,level=1,componentsDict={},Cname="DirLocation",Ctype="ETL_DirLocation"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # default attributes
        self.attributes.append(['dirLocationID', TPEGstring.IntUnLi()])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['dirLocationDirection', 'Positive'])
        else:
            self.attributes.append(['dirLocationDirection', 'Negative'])

        return
#
#
#
class ETL_SequenceNumberExitEntry_datastructure(TPEG_datastructure):
    def __init__(self,level=1,componentsDict={},Cname="SequenceNumberExitEntry",Ctype="ETL_SequenceNumberExitEntry"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # default attributes
        self.sequenceNumberExitEntry = TPEGstring.IntUnTi()
        self.totalNumberOfExitEntries= TPEGstring.IntUnTi()
        self.attributes.append(['sequenceNumberExitEntry' , self.sequenceNumberExitEntry ])
        self.attributes.append(['totalNumberOfExitEntries', self.totalNumberOfExitEntries])

        return
#
#
class ETL_WGS84coordinate(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="WGS84coordinate",Ctype="ETL_WGS84coordinate"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['WGS84longitude',  TPEGstring.IntSi24asWGS84Coord()])
        self.attributes.append(['WGS84latitude',   TPEGstring.IntSi24asWGS84Coord()])

        return
#
#
#
class ETL_ExitEntry_datastructure(TPEG_datastructure):
    def __init__(self,level=1,componentsDict={},Cname="ETL_ExitEntry",Ctype="ETL_ExitEntry"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        # default attributes
        selector = TPEGstring.BitArray();

        if selector.is_set(0):
            self.isExitOrEntry = True
        else:
            self.isExitOrEntry = False

        # create more legible text
        ExitEntryDict = {True:"True (Exit)",False:"False (Entry)"}

        self.attributes.append(['isExitOrEntry', ExitEntryDict[self.isExitOrEntry]])

        if selector.is_set(1):
            self.oppositeDir = True
            self.attributes.append(['oppositeDir', True ])
        else:
            self.oppositeDir = False

        if selector.is_set(2):
            self.parse_datastructure(TPEGstring, 'dirLocation',ETL_DirLocation_datastructure)

        if selector.is_set(3):
            self.parse_datastructure(TPEGstring, 'exitEntryPoint',ETL_WGS84coordinate)

        if selector.is_set(4):
            self.parse_datastructure(TPEGstring, 'sequenceNumberExitEntry',ETL_SequenceNumberExitEntry_datastructure)

        return
#
#
#
class ETL_TMC_ExitEntry_datastructure(TPEG_datastructure):
    def __init__(self,level=1,componentsDict={},Cname="ETL_TMC_ExitEntry",Ctype="ETL_TMC_ExitEntry"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'tmcLocation',ETL_TMC_datastructure)
        # default attributes
        self.parse_n_datastructures_of_type(TPEGstring, 'exitEntryInformation', ETL_ExitEntry_datastructure)
#
#
#
class ETL_preciseTMCinformation(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="preciseTMCinformation",Ctype="_preciseTMCinformation"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        #
        # mapping of distance codes to values
        distAccyDict = {0:"100m",1:"500m",2:"1Km",3:"more than 1Km"}

        selector = TPEGstring.BitArray();

        distanceAccuracy = 0
        if selector.is_set(0):
            distanceAccuracy = TPEGstring.IntUnTi()

        self.attributes.append(['distanceAccuracy',  distAccyDict.get(distanceAccuracy, distAccyDict[0])])

        if selector.is_set(1):
            self.attributes.append(['hazardDistance1',   TPEGstring.IntUnTi()])

        if selector.is_set(2):
            self.attributes.append(['hazardDistance2',   TPEGstring.IntUnLi()])

        if selector.is_set(3):
            self.attributes.append(['problemLength1',   TPEGstring.IntUnTi()])

        if selector.is_set(4):
            self.attributes.append(['problemLength2',   TPEGstring.IntUnLi()])

        return
#
#
#
class TPEG_LRC_ETL_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="LRC_ETL",Ctype="LRC_ETL"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        MajorMinorVersion = TPEGstring.IntUnTi()
        self.attributes.append(['specVersionID', "%1d.%1d"%(MajorMinorVersion>>0x4, MajorMinorVersion&0x0F)])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.parse_datastructure(TPEGstring, 'tmcLocation',ETL_TMC_datastructure)

        if selector.is_set(1):
            self.parse_datastructure(TPEGstring, 'tmcExitEntryLocation',ETL_TMC_ExitEntry_datastructure)

#
# Test functionality
#

if __name__ == '__main__':
    print("TPEG_LRC_ETL_component")
