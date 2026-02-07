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
# TEC tables
#
# 20150423 upgraded to TEC3.2 texts
#
#
import os, sys

from Base.TPEG_error   import TPEG_log_error
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))

def TEC_code_to_text(code,TPEG_table,switch_code=None):
    global _TEC_tables
    global _TEC_switch_tables
    #
    # determine proper table to use
    if switch_code is not None:
        table = _TEC_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _TEC_tables.get(TPEG_table,None)

    if table is not None:
        error_string = "Invalid/Unknown Code in table %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)

        text = str(code)+": "+table.get(code,error_string)
    else:
        text = str(code)+": Invalid/Unknown TEC table %s"%TPEG_table
        error_string = "==> TEC: unknown table  %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)
            text         += ", switched with code "+str(switch_code)

        TPEG_log_error(error_string)

    return text

# return list of available codes
def TEC_code_list(TPEG_table,switch_code=None):
    global _TEC_tables
    global _TEC_switch_tables

    code_list = None
    #
    # determine proper table to use
    if switch_code is not None:
        table = _TEC_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _TEC_tables.get(TPEG_table,None)

    if table is not None:
        code_list = list(table.keys())
        code_list.sort()

    return code_list


TEC_001={
	1	:"traffic flow unknown",
	2	:"free traffic flow",
	3	:"heavy traffic",
	4	:"slow traffic",
	5	:"queuing traffic",
	6	:"stationary traffic",
	7	:"no traffic flow"
	}

TEC_002={
	1	:"traffic congestion",
	2	:"accident",
	3	:"roadworks",
	4	:"narrow lanes",
	5	:"impassability",
	6	:"slippery road",
	7	:"aquaplaning",
	8	:"fire",
	9	:"hazardous driving conditions",
	10	:"objects on the road",
	11	:"animals on roadway",
	12	:"people on roadway",
	13	:"broken down vehicles",
	14	:"vehicle on wrong carriageway",
	15	:"rescue and recovery work in progress",
	16	:"regulatory measure",
	17	:"extreme weather conditions",
	18	:"visibility reduced",
	19	:"precipitation",
	20	:"reckless persons",
	21	:"overheight warning system triggered",
	22	:"traffic regulations changed",
	23	:"major event",
	24	:"service not operating",
	25	:"service not useable",
	26	:"slow moving vehicles",
	27	:"dangerous end of queue",
	28	:"risk of fire",
	29	:"time delay",
	30	:"police checkpoint",
	31	:"malfunctioning roadside equipment",
	100	:"test message",
	255	:"undecodable cause"
	}

TEC_003={
	1	:"informative",
	2	:"danger level 1",
	3	:"danger level 2",
	4	:"danger level 3"
	}

TEC_004={
	1	:"lane(s) closed",
	2	:"lane(s) open",
	3	:"right lane(s) closed",
	4	:"left lane(s) closed"
	}

TEC_005={
	1	:"drive to next available parking place",
	2	:"overtaking not allowed",
	3	:"driving not allowed",
	4	:"use hard shoulder as lane",
	5	:"wait for police patrol",
	6	:"wait for improved weather",
	7	:"make way for vehicles coming from behind to pass",
	8	:"follow diversion",
	9	:"no diversion to recommend",
	10	:"do not divert",
	11	:"follow police instructions",
	12	:"avoid the area",
	13	:"drive carefully",
	14	:"do not leave your vehicle",
	15	:"switch on radio",
	16	:"use toll lanes",
	17	:"wait for convoy",
	255	:"undecodable advice"
	}

TEC_006={
	1	:"slightly increasing",
	2	:"increasing",
	3	:"strongly increasing",
	4	:"slightly decreasing",
	5	:"decreasing",
	6	:"strongly decreasing",
	7	:"constant"
	}

TEC_007={
	1	:"width less than",
	2	:"width greater than",
	3	:"height less than",
	4	:"height greater than",
	5	:"weight less than",
	6	:"weight greater than",
	7	:"without winter tyres",
	8	:"without snow chains",
	9	:"with trailer",
	10	:"with caravan",
	11	:"persons in vehicle less than",
	12	:"persons in vehicle more than",
	13	:"even number plate",
	14	:"odd number plate",
	15	:"length less than",
	16	:"length greater than",
	17	:"axle load less than",
	18	:"axle load greater than",
	19	:"vehicle fulfils emission standard EURO3",
	20	:"vehicle fulfils emission standard EURO3D4",
	21	:"vehicle fulfils emission standard EURO4",
	22	:"vehicle fulfils emission standard EURO5",
	23	:"with petrol engine",
	24	:"with diesel engine",
	25	:"with LPG engine",
	26	:"through traffic",
	27	:"residents traffic",
	28	:"with destination in given area",
	255	:"undecodable restriction"
	}

TEC_008={
	1	:"bypass",
	2	:"access road",
	3	:"limited access road",
	4	:"not recommended road",
	5	:"closed road"
	}

TEC_009={
	1	:"car",
	2	:"lorry",
	3	:"bus",
	4	:"taxi",
	5	:"train",
	6	:"motor cycle",
	7	:"vehicle with trailer",
	8	:"motor vehicle",
	9	:"vehicle transporting hazardous goods",
	10	:"vehicle transporting an abnormal size load",
	11	:"heavy goods vehicle",
	255	:"undecodable vehicle type"
	}

TEC_101={
	1	:"increased volume of traffic"
	}

TEC_102={
	1	:"multi-vehicle accident",
	2	:"major accident",
	3	:"accident involving lorry",
	4	:"accident involving bus",
	5	:"accident involving hazardous materials",
	6	:"accident in opposite lane",
	7	:"unsecured accident"
	}

TEC_103={
	1	:"major roadworks",
	2	:"road marking work",
	3	:"slow moving road maintenance"
	}

TEC_104={
	1	:"contraflow",
	2	:"hard shoulder closed",
	3	:"slip lane closed",
	4	:"crawler lane closed"
	}

TEC_105={
	1	:"flooding",
	2	:"danger of avalanches",
	3	:"blasting of avalanches",
	4	:"landslips",
	5	:"chemical spillage",
	6	:"winter closure"
	}

TEC_106={
	1	:"heavy frost on road",
	2	:"fuel on road",
	3	:"mud on road",
	4	:"snow on road",
	5	:"ice on road",
	6	:"black ice on road",
	7	:"oil on road",
	8	:"loose chippings",
	9	:"instant black ice",
	10	:"roads salted"
	}

TEC_108={
	1	:"major fire",
	2	:"forest fire"
	}

TEC_109={
	1	:"rockfalls",
	2	:"earthquake damage",
	3	:"sewer collapse",
	4	:"subsidence",
	5	:"snow drifts",
	6	:"storm damage",
	7	:"burst pipe",
	8	:"volcano eruption",
	9	:"falling ice"
	}

TEC_110={
	1	:"shed load",
	2	:"parts of vehicles",
	3	:"parts of tyres",
	4	:"large objects",
	5	:"fallen trees",
	6	:"hub caps",
	7	:"stationary vehicle"
	}

TEC_111={
	1	:"wild animals",
	2	:"herd of animals",
	3	:"small animals",
	4	:"large animals"
	}

TEC_112={
	1	:"children on roadway",
	2	:"cyclists on roadway",
	3	:"motorcyclists on roadway"
	}

TEC_113={
	1	:"broken down vehicle on fire",
	2	:"broken down unlit vehicle"
	}

TEC_115={
	1	:"emergency vehicles",
	2	:"rescue helicopter landing",
	3	:"police activity ongoing",
	4	:"medical emergency ongoing",
	5	:"child abduction in progress"
	}

TEC_116={
	1	:"security alert",
	2	:"contagious disease",
	3	:"environmental",
	4	:"smog alert",
	5	:"batch service in progress",
	6	:"road closed by the regulatory authorities"
	}

TEC_117={
	1	:"strong winds",
	2	:"damaging hail",
	3	:"hurricane",
	4	:"thunderstorm",
	5	:"tornado",
	6	:"blizzard"
	}

TEC_118={
	1	:"visibility reduced due to fog",
	2	:"visibility reduced due to smoke",
	3	:"visibility reduced due to heavy snowfall",
	4	:"visibility reduced due to heavy rain",
	5	:"visibility reduced due to heavy hail",
	6	:"visibility reduced due to low sun glare",
	7	:"visibility reduced due to sandstorms",
	8	:"visibility reduced due to swarms of insects"
	}

TEC_119={
	1	:"heavy rain",
	2	:"heavy snowfall",
	3	:"soft hail"
	}

TEC_120={
	1	:"reckless driver",
	2	:"gunfire on road",
	3	:"persons throwing objects"
	}

TEC_123={
	1	:"sports event",
	2	:"demonstration",
	3	:"demonstration with vehicles",
	4	:"concert",
	5	:"fair",
	6	:"military training",
	7	:"emergency training",
	8	:"festival",
	9	:"procession"
	}

TEC_124={
	1	:"ferry service not operating",
	2	:"air service not operating",
	3	:"train service not operating",
	4	:"bus service not operating"
	}

TEC_125={
	1	:"fuel station closed",
	2	:"service area closed",
	3	:"service area busy",
	4	:"parking full",
	5	:"car park closed"
	}

TEC_126={
	1	:"slow moving maintenance vehicle",
	2	:"vehicles slowing to look at accident",
	3	:"abnormal load",
	4	:"abnormal wide load",
	5	:"convoy",
	6	:"snowplough",
	7	:"de-icing",
	8	:"salting vehicles"
	}

TEC_127={
	1	:"sudden end of queue",
	2	:"queue over hill",
	3	:"queue around bend",
	4	:"queue in tunnel"
	}

TEC_128={
	1	:"leakage of fuel",
	2	:"leakage of gas"
	}

TEC_129={
	1	:"time delay at frontier",
	2	:"time delay at ferry port",
	3	:"time delay at vehicle-on-rail terminal"
	}

TEC_130={
	1	:"permanent police checkpoint",
	2	:"temporary police checkpoint"
	}

TEC_131={
	1	:"road-rail crossing failure",
	2	:"tunnel ventilation not working",
	3	:"traffic control signals working incorrectly",
	4	:"emergency telephones not working",
	5	:"automatic payment lanes not working"
	}

TEC_202={
	1	:"do not use overtaking lanes",
	2	:"overtaking not allowed, drive on crawler lane",
	3	:"overtaking not allowed, drive on left most lane",
	4	:"overtaking not allowed, drive on right most lane"
	}

TEC_203={
	1	:"driving not allowed, find a safe place to pull over and stop the vehicle"
	}

TEC_207={
	1	:"make way for rescue vehicles to pass",
	2	:"make way for service vehicles to pass"
	}

TEC_208={
	1	:"follow diversion signs"
	}

TEC_213={
	1	:"drive carefully, dangerous situation on entry slip road",
	2	:"drive carefully, dangerous situation on exit slip road",
	3	:"drive carefully, ice buildup on cable structure"
	}

TEC_214={
	1	:"do not leave your vehicle",
	2	:"do not leave your vehicle, close windows"
	}

TEC_216={
	1	:"use manual payment toll lanes",
	2	:"use automatic payment toll lanes"
	}

_TEC_tables={
	"TEC_001": TEC_001,
	"TEC_002": TEC_002,
	"TEC_003": TEC_003,
	"TEC_004": TEC_004,
	"TEC_005": TEC_005,
	"TEC_006": TEC_006,
	"TEC_007": TEC_007,
	"TEC_008": TEC_008,
	"TEC_009": TEC_009,
	"TEC_101": TEC_101,
	"TEC_102": TEC_102,
	"TEC_103": TEC_103,
	"TEC_104": TEC_104,
	"TEC_105": TEC_105,
	"TEC_106": TEC_106,
	"TEC_108": TEC_108,
	"TEC_109": TEC_109,
	"TEC_110": TEC_110,
	"TEC_111": TEC_111,
	"TEC_112": TEC_112,
	"TEC_113": TEC_113,
	"TEC_115": TEC_115,
	"TEC_116": TEC_116,
	"TEC_117": TEC_117,
	"TEC_118": TEC_118,
	"TEC_119": TEC_119,
	"TEC_120": TEC_120,
	"TEC_123": TEC_123,
	"TEC_124": TEC_124,
	"TEC_125": TEC_125,
	"TEC_126": TEC_126,
	"TEC_127": TEC_127,
	"TEC_128": TEC_128,
	"TEC_129": TEC_129,
	"TEC_130": TEC_130,
	"TEC_131": TEC_131,
	"TEC_202": TEC_202,
	"TEC_203": TEC_203,
	"TEC_207": TEC_207,
	"TEC_208": TEC_208,
	"TEC_213": TEC_213,
	"TEC_214": TEC_214,
	"TEC_216": TEC_216
	}

#
# dictionary with all TEC tables
_TEC_tables = {
    "TEC_001":TEC_001,
    "TEC_002":TEC_002,
    "TEC_003":TEC_003,
    "TEC_004":TEC_004,
    "TEC_005":TEC_005,
    "TEC_006":TEC_006,
    "TEC_007":TEC_007,
    "TEC_008":TEC_008,
    "TEC_009":TEC_009
    }

TEC_002_switch_tables = {
    1	:TEC_101,
    2	:TEC_102,
    3	:TEC_103,
    4	:TEC_104,
    5	:TEC_105,
    6	:TEC_106,
    8	:TEC_108,
    9	:TEC_109,
    10	:TEC_110,
    11	:TEC_111,
    12	:TEC_112,
    13	:TEC_113,
    15	:TEC_115,
    16	:TEC_116,
    17	:TEC_117,
    18	:TEC_118,
    19	:TEC_119,
    20	:TEC_120,
    23	:TEC_123,
    24	:TEC_124,
    25	:TEC_125,
    26	:TEC_126,
    27	:TEC_127,
    28	:TEC_128,
    29	:TEC_129,
    30	:TEC_130,
    31	:TEC_131
    }

#
#
TEC_005_switch_tables = {
    2	:TEC_202,
    3	:TEC_203,
    7	:TEC_207,
    8	:TEC_208,
    13	:TEC_213,
    14	:TEC_214,
    16	:TEC_216
    }


#================================
_TEC_switch_tables = {
    "TEC_002":TEC_002_switch_tables,
    "TEC_005":TEC_005_switch_tables
    }
