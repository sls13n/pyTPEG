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
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))
#
#
import xml, optparse
#
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
#
from .CAP_error             import CAP_log_error,CAP_error_set_object, CAP_error_unset_object
#
from .CAP_base_component    import CAP_base_component

from .geomet import wkt

import EawUtils.CAP_SHN_database
#
#
# ========================================================================
#
#
# Type checking functions
#
_is_string   = lambda x: isinstance(x,str)
#
_is_dateTime = _is_string # to be made
#
_is_parameter= None # to be made
#
def _is_decimal(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
#
#
# function to parse SHN code and return a geojson object
#
def parse_SHN_code(code):
    #
    geojson = EawUtils.CAP_SHN_database.CAP_SHN_to_geojson(code)
    if geojson is None:
        geojson = []

    ##geojson = {"type":"Polygon","coordinates":[]}  ## empty polygon
    ##geojson = []

    return geojson

#
#
# function to parse polygon and return a geojson object
#
def parse_CAP_polygon(polygon_string):
    # coordinates in Lat,Lon format

    coordinates = polygon_string.replace("\n"," ").split(" ")

    coordinates = [i for i in coordinates if not not i] # filter empty parts

    coords = []
    for coord in coordinates:
        coordpair = coord.split(",")

        #store in lon,lat format
        coords.append([float(coordpair[1]),float(coordpair[0])])

    geojson = {"type":"Polygon","coordinates":[coords]}

    return geojson
#
#
# function to parse circle and return a geojson object
#
def parse_CAP_circle(circle_string):
    # coordinates in Lat,Lon radius format
    coordinates_radius = circle_string.split(" ")

    coordinates_radius = [i for i in coordinates_radius if not not i] # filter empty parts

    if len(coordinates_radius) == 3: # if comma between lat,lon is forgotten
        coordpair = coordinates_radius[:2]
        radius    = coordinates_radius[ 2]
    else:
        coordpair = coordinates_radius[0].split(",")
        radius    = coordinates_radius[ 1]

    #store in lon,lat format
    coords = ([float(coordpair[1]),float(coordpair[0])])
    radius = float(radius)

    # properties is optional (default readi
    geojson = {"type":"Circle","coordinates":coords,"radius":radius,"properties": { "radius_units": "km" }}

    return geojson

#
#
#
class CAP_area_component(CAP_base_component):
    def __init__(self,id,level=0,CAPversion="1.2",componentsDict={},Cname="area",Ctype="CAP_area"):
        CAP_base_component.__init__(self,id,level,CAPversion,componentsDict,Cname,Ctype)
        componentsDict[ 0] = [ # simple elements
            # [mandatory, list, name, validation function ]
            [True,  False, "areaDesc",    _is_string  ],
            [False, True,  "polygon",     _is_string  ],
            [False, True,  "circle",      _is_string  ],
            [False, False, "altitude",    _is_decimal ],
            [False, False, "ceiling",     _is_decimal ]
            ]

        componentsDict[ 1] = [ # parameters as valueName, Value pairs
            [False, True,  "geocode",     _is_parameter    ]]
        componentsDict[ 2] = [# sub components
            ]


    def parse(self,XMLelement, Registry={}):
        #
        # first parse standard elements
        CAP_base_component.parse(self, XMLelement, Registry={})

        # set mandatory attributes
        self.areaDesc   = [x for x in self.elements if x[0] == "areaDesc"  ][0][1]

        #
        # Now transform geographic areas to geojson objects if possible
        #
        # Polygon, MultiPolygon and Circle supported

        self.geojson_areas=[]

        # transform polygon element into geojson polygon format
        for polygon in [x[1] for x in self.elements if x[0] == "polygon"]:
            self.geojson_areas.append(parse_CAP_polygon(polygon))

        # process "EXCLUDE_POLYGON" geocodes for DWD CAP
        for code in [x[2] for x in self.parameters if x[1] == "EXCLUDE_POLYGON"]:
            exclude_polygon = parse_CAP_polygon(code)

            geojson =self.geojson_areas[-1] # add exclusion to last area parsed
            if geojson['type'] == "MultiPolygon":
                CAP_log_error("EXCLUDE_POLYGON code not implemented for multi polygon")
            elif geojson['type'] == "Polygon":
                geojson['coordinates'] = geojson['coordinates']+exclude_polygon['coordinates']


        # transform circle element into geojson circle format
        for circle in [x[1] for x in self.elements if x[0] == "circle"]:
            self.geojson_areas.append(parse_CAP_circle(circle))

        # process "WKT" geocodes
        for code in [x[2] for x in self.parameters if x[1] == "WKT"]:
            geojson = wkt.loads(code)
            self.geojson_areas.append(geojson)

        # process "SHN" geocodes
        for code in [x[2] for x in self.parameters if x[1] == "SHN"]:
            ## convert SHN code to geojson
            area = parse_SHN_code(code)
            ## check area
            if area:
                self.geojson_areas.append(area)
            else:
                CAP_log_error(" ==> Could not decode SHN area: "+code+" ,for AreaDesc "+self.areaDesc)
        return

if __name__ == '__main__':
    print("CAP_area_component")
