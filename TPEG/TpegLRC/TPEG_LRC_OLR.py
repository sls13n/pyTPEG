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
# OLR LR class for TPEG component parsing
#
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
# --------- OLR --------------------------------------------
#
#
#
#
class OLR_AbsoluteCoordinate(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="OLR_AbsoluteGeoCoordinate",Ctype="OLR_AbsoluteGeoCoordinate"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['longitude',  TPEGstring.IntSi24asWGS84Coord()])
        self.attributes.append(['latitude',   TPEGstring.IntSi24asWGS84Coord()])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
           self.attributes.append(['altitude',      TPEGstring.IntSiLoMB()])

        return

#
#
class OLR_RelativeCoordinate(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="OLR_RelativeGeoCoordinate",Ctype="OLR_RelativeGeoCoordinate"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['delta longitude',  TPEGstring.IntSiLi()])
        self.attributes.append(['delta latitude',   TPEGstring.IntSiLi()])

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
           self.attributes.append(['altitude',      TPEGstring.IntSiLoMB()])

        return

#
# --- components --------------------------------------------
#
#
class OLR_Rectangle(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="OLR_Rectangle",Ctype="OLR_Rectangle"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'lowerLeftCoordinate',         OLR_AbsoluteCoordinate)
        self.parse_datastructure(TPEGstring, 'upperRightCoordinate',        OLR_AbsoluteCoordinate)

        return
#
#
class OLR_LocationDescription(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="OLR_LocationDescription",Ctype="OLR_LocationDescription"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_n_attributes_of_type(TPEGstring, 'description', TPEGstring.LocalisedLongString)
        return

#
#
class OLR_GeoCoordinateLocationReference(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="OLR_GeoCoordinateLR",Ctype="OLR_GeoCoordinateLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'coordinate',         OLR_AbsoluteCoordinate)
        return

#
#
class OLR_RectangleLocationReference(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="OLR_RectangleLR",Ctype="OLR_RectangleLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'rectangle',         OLR_Rectangle)
        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['isFuzzyArea',      True])
        return
#
#
class OLR_CircleLocationReference(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="OLR_CircleLR",Ctype="OLR_CircleLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'centerPoint', OLR_AbsoluteCoordinate)

        self.attributes.append(['radius',                   TPEGstring.DistanceMetres()])

        selector = TPEGstring.BitArray()
        if selector.is_set(0):
            self.attributes.append(['isFuzzyArea',      True])

        return
#
#
class OLR_PolygonLocationReference(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="OLR_PolygonLR",Ctype="OLR_PolygonLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        componentsDict[ 5] = OLR_PolygonLocationReference # holes in polygon

    def parse_attributes(self,TPEGstring):
        self.num_coordinates = 1
        self.parse_datastructure(TPEGstring, 'startCoordinate', OLR_AbsoluteCoordinate)

        self.num_coordinates += self.parse_n_datastructures_of_type(TPEGstring, 'coordinatePath', OLR_RelativeCoordinate)

        selector = TPEGstring.BitArray()
        if selector.is_set(0):
            self.attributes.append(['isFuzzyArea',      True])


        return

#
#
class TPEG_LRC_OLR_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="LRC_OLR",Ctype="LRC_OLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

        componentsDict[ 1] = OLR_GeoCoordinateLocationReference
        componentsDict[ 4] = OLR_CircleLocationReference
        componentsDict[ 5] = OLR_PolygonLocationReference
        componentsDict[ 6] = OLR_RectangleLocationReference
        componentsDict[11] = OLR_LocationDescription
        # others TBD

    def parse_attributes(self,TPEGstring):
        [major,minor] = TPEGstring.MajorMinorVersion()
        self.attributes.append(['version', "%1d.%1d"%(major,minor)])

        return

#
# Test functionality
#

if __name__ == '__main__':
    print("TPEG_LRC_OLR_component")
