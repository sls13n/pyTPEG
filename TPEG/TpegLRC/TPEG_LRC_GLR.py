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
# GLR LR class for TPEG component parsing
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
# --------- GLR ---------------------------------

#
#
class GLR_WGS84coordinate(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="WGS84coordinate",Ctype="GLR_WGS84coordinate"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['WGS84longitude',  TPEGstring.IntSi24asWGS84Coord()])
        self.attributes.append(['WGS84latitude',   TPEGstring.IntSi24asWGS84Coord()])

        return

#
#
class GLR_Polygon(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="Polygon",Ctype="GLR_Polygon"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.num_coordinates = self.parse_n_datastructures_of_type(TPEGstring, 'polygonPoints', GLR_WGS84coordinate)

        return

#
#
class GLR_HierarchicalAreaName(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="HierarchicalAreaName",Ctype="_HierarchicalAreaName"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.attributes.append(['languageCode',    TPEGstring.IntUnTi()])
        self.attributes.append(['areaName',        TPEGstring.ShortString()])

        self.parse_n_attributes_of_type(TPEGstring, 'detailAreaName', TPEGstring.ShortString)

        return
#
#
#
#
class GLR_GeographicBoundingBox(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicBoundingBox",Ctype="GLR_GeographicBoundingBox"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'northWestCorner',GLR_WGS84coordinate)
        self.parse_datastructure(TPEGstring, 'southEastCorner',GLR_WGS84coordinate)

        selector = TPEGstring.BitArray()
        if selector.is_set(0):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(1):
            self.parse_n_attributes_of_type(TPEGstring, 'areaFeatureName', TPEGstring.LocalisedShortString)

        return

#
#
class GLR_GeographicBoundingCircleSector(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicBoundingCircleSector",Ctype="GLR_GeographicBoundingCircleSector"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'centerPoint',GLR_WGS84coordinate)

        self.attributes.append(['radius',      TPEGstring.DistanceMetres()])

        selector = TPEGstring.BitArray()
        if selector.is_set(0):
            self.parse_datastructure(TPEGstring, 'circleSector', GLR_CircleSector)

        if selector.is_set(1):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(2):
            self.parse_n_attributes_of_type(TPEGstring, 'areaFeatureName', TPEGstring.LocalisedShortString)

        return


#
#
class GLR_GeographicPointReference(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicPointReference",Ctype="GLR_GeographicPointReference"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'point',GLR_WGS84coordinate)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['isFuzzyPoint',     'True'])

        if selector.is_set(1):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(2):
            self.parse_n_attributes_of_type(TPEGstring, 'pointFeatureName', TPEGstring.LocalisedShortString)

        if selector.is_set(3):
            self.parse_n_attributes_of_type(TPEGstring, 'adjacentRoadSideDescriptor', TPEGstring.LocalisedShortString)

        if selector.is_set(4):
            self.attributes.append(['adjacentRoadSideTravelDirection',      TPEGstring.IntUnTi()])

        return

#
#
class GLR_GeographicLineReference(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicLineReference",Ctype="GLR_GeographicLineReference"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_n_datastructures_of_type(TPEGstring, 'linePoints',GLR_WGS84coordinate)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['isFuzzyLine',     'True'])

        if selector.is_set(1):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(2):
            self.parse_n_attributes_of_type(TPEGstring, 'lineFeatureName', TPEGstring.LocalisedShortString)

        return

#
#
class GLR_GeographicAreaReference(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicAreaReference",Ctype="GLR_GeographicAreaReference"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.num_coordinates = self.parse_n_datastructures_of_type(TPEGstring, 'polygonPoints',GLR_WGS84coordinate)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['isFuzzyArea',     'True'])

        if selector.is_set(1):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(2):
            self.parse_n_attributes_of_type(TPEGstring, 'areaFeatureName', TPEGstring.LocalisedShortString)

        if selector.is_set(3):
            self.parse_n_datastructures_of_type(TPEGstring, 'hierarchicalAreaFeatureName',GLR_HierarchicalAreaName)

        return

#
#
class GLR_GeographicAreaWithHolesReference(TPEG_datastructure):
    def __init__(self,level=0,componentsDict={},Cname="GeographicAreaWithHolesReference",Ctype="GLR_GeographicAreaWithHolesReference"):
        TPEG_datastructure.__init__(self,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):
        self.parse_datastructure(TPEGstring, 'exteriorPolygon',GLR_Polygon)
        self.parse_n_datastructures_of_type(TPEGstring, 'interiorPolygons',GLR_Polygon)

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.attributes.append(['isFuzzyArea',     'True'])

        if selector.is_set(1):
            self.attributes.append(['altitudeMSL',      TPEGstring.IntSiLoMB()])

        if selector.is_set(2):
            self.parse_n_attributes_of_type(TPEGstring, 'areaFeatureName', TPEGstring.LocalisedShortString)

        if selector.is_set(3):
            self.parse_n_datastructures_of_type(TPEGstring, 'hierarchicalAreaFeatureName',GLR_HierarchicalAreaName)

        return


#
#
class TPEG_LRC_GLR_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="LRC_GLR",Ctype="LRC_GLR"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)

    def parse_attributes(self,TPEGstring):

        selector = TPEGstring.BitArray();
        if selector.is_set(0):
            self.parse_datastructure(TPEGstring, 'geographicBoundingBox',           GLR_GeographicBoundingBox)

        if selector.is_set(1):
            self.parse_datastructure(TPEGstring, 'geographicBoundingCircleSector',  GLR_GeographicBoundingCircleSector)

        if selector.is_set(2):
            self.parse_datastructure(TPEGstring, 'geographicPointReference',        GLR_GeographicPointReference)

        if selector.is_set(3):
            self.parse_datastructure(TPEGstring, 'geographicLineReference',         GLR_GeographicLineReference)

        if selector.is_set(4):
            self.parse_datastructure(TPEGstring, 'geographicAreaReference',         GLR_GeographicAreaReference)

        if selector.is_set(5):
            self.parse_datastructure(TPEGstring, 'geographicAreaWithHolesReference',GLR_GeographicAreaWithHolesReference)

        return


#
#
# Test functionality
#

if __name__ == '__main__':
    print("TPEG_LRC_GLR_component")
