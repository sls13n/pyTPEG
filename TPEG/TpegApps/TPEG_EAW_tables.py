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
# EAW tables
#
#
#
import os, sys
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))

from Base.TPEG_error   import TPEG_log_error
#
#
# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))

def EAW_code_to_text(code,TPEG_table,switch_code=None):
    global _EAW_tables
    global _EAW_switch_tables
    #
    # determine proper table to use
    if switch_code is not None:
        table = _EAW_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _EAW_tables.get(TPEG_table,None)

    if table is not None:
        error_string = "Invalid/Unknown Code in table %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)

        text = str(code)+": "+table.get(code,error_string)
    else:
        text = str(code)+": Invalid/Unknown EAW table %s"%TPEG_table
        error_string = "==> EAW: unknown table  %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)
            text         += ", switched with code "+str(switch_code)

        TPEG_log_error(error_string)

    return text

# return list of available codes
def EAW_code_list(TPEG_table,switch_code=None):
    global _EAW_tables
    global _EAW_switch_tables

    code_list = None
    #
    # determine proper table to use
    if switch_code is not None:
        table = _EAW_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _EAW_tables.get(TPEG_table,None)

    if table is not None:
        code_list = list(table.keys())
        code_list.sort()

    return code_list

EAW_001={
	0	:"unknown",
	1	:"CAP derived level",
	10	:"alert",
	11	:"statement",
	12	:"advisory",
	13	:"emergency",
	14	:"watch",
	15	:"warning",
	16	:"outlook",
	17	:"test",
	20	:"level 1 alert",
	21	:"level 2 alert",
	22	:"level 3 alert",
	23	:"level 4 alert",
	24	:"amber alert level",
	25	:"monthly test",
	30	:"code green",
	31	:"code yellow",
	32	:"code orange",
	33	:"code red",
	40	:"civil protection and disaster assistance warning level 1",
	41	:"civil protection and disaster assistance warning level 2",
	42	:"civil protection and disaster assistance warning level 3",
	50	:"Cyber Incident Severity Schema level 5 Emergency",
	51	:"Cyber Incident Severity Schema level 4 Severe",
	52	:"Cyber Incident Severity Schema level 3 High",
	53	:"Cyber Incident Severity Schema level 2 Medium",
	54	:"Cyber Incident Severity Schema level 1 Low",
	55	:"Cyber Incident Severity Schema level 0 Baseline",
	255	:"undefined"
	}

EAW_002={
	0	:"unknown",
	1	:"geo",
	2	:"met",
	3	:"safety",
	4	:"security",
	5	:"rescue",
	6	:"fire",
	7	:"health",
	8	:"env",
	9	:"transport",
	10	:"infra",
	11	:"CBRNE",
	12	:"other",
	255	:"undefined"
	}

EAW_003={
	0	:"unknown",
	1	:"immediate",
	2	:"expected",
	3	:"future",
	4	:"past",
	255	:"undefined"
	}

EAW_004={
	0	:"unknown",
	1	:"extreme",
	2	:"severe",
	3	:"moderate",
	4	:"minor",
	255	:"undefined"
	}

EAW_005={
	0	:"unknown",
	1	:"observed",
	2	:"likely",
	3	:"possible",
	4	:"unlikely",
	255	:"undefined"
	}

EAW_006={
	0	:"unknown",
	1	:"new",
	2	:"update",
	3	:"cleared",
	255	:"undefined"
	}

EAW_007={
	0	:"unknown",
	1	:"shelter",
	2	:"evacuate",
	3	:"prepare",
	4	:"execute",
	5	:"avoid",
	6	:"monitor",
	7	:"assess",
	8	:"all clear",
	9	:"none",
	255	:"undefined"
	}

EAW_010={
	0	:"unknown",
	1	:"administration",
	2	:"air quality",
	3	:"animal health",
	4	:"dangerous animals",
	5	:"aviation",
	6	:"civil",
	7	:"criminal activities",
	8	:"fire",
	9	:"flood",
	10	:"fog",
	11	:"geological",
	12	:"hazardous materials",
	13	:"health",
	14	:"ice",
	15	:"marine",
	16	:"missing person",
	17	:"other non-urgent",
	18	:"other urgent",
	19	:"plant health",
	20	:"preparedness reminders",
	21	:"product safety",
	22	:"public services",
	23	:"railway",
	24	:"rescue",
	25	:"roadway",
	26	:"search",
	27	:"storm",
	28	:"temperature",
	29	:"test message",
	30	:"utility",
	31	:"wind",
	32	:"water quality",
	255	:"undefined"
	}

EAW_011={
	0	:"unknown",
	1	:"ensure your safety, take precaution",
	2	:"follow instructions of local authorities",
	3	:"expect travel disruptions in the area",
	4	:"inform yourself via all possible media",
	5	:"ensure your safety, take precaution (residential)",
	255	:"undefined"
	}

EAW_103={
	0	:"unknown",
	1	:"animal disease",
	2	:"animal feed",
	3	:"animal pest",
	4	:"aquatic animal disease",
	5	:"aquatic animal pest",
	6	:"animal welfare",
	7	:"marine disease",
	8	:"marine pest",
	9	:"animal quarantine",
	10	:"sheep grazier warning",
	255	:"undefined"
	}

EAW_104={
	0	:"unknown",
	1	:"dangerous animal",
	2	:"plague",
	3	:"plague of insects",
	255	:"undefined"
	}

EAW_105={
	0	:"unknown",
	1	:"aircraft crash",
	2	:"aircraft incident",
	3	:"airport closure",
	4	:"airspace closure",
	5	:"airport lightning threat",
	6	:"airport thunder threat",
	7	:"aviation security",
	8	:"falling object",
	9	:"notice to airmen",
	10	:"satellite/space entry debris",
	255	:"undefined"
	}

EAW_106={
	0	:"unknown",
	1	:"building collapse",
	2	:"civil emergency",
	3	:"demonstration",
	4	:"public event",
	5	:"major event",
	6	:"volunteer request",
	7	:"world war bomb",
	8	:"air raid",
	9	:"missile attack",
	10	:"danger by weapons",
	11	:"attack with nuclear weapons",
	12	:"security warning",
	255	:"undefined"
	}

EAW_107={
	0	:"unknown",
	1	:"cyber crime",
	2	:"dangerous person",
	3	:"home crime",
	4	:"industrial crime",
	5	:"retail crime",
	6	:"terrorism",
	7	:"vehicle crime",
	8	:"life threatening situation",
	9	:"bomb / munition discovery",
	255	:"undefined"
	}

EAW_108={
	0	:"unknown",
	1	:"wildfire",
	2	:"fire ban",
	3	:"fire danger level",
	4	:"forest fire",
	5	:"fire weather",
	6	:"grass fire",
	7	:"industrial fire",
	8	:"urban fire",
	9	:"major fire",
	10	:"smoke alert",
	11	:"structure fire",
	12	:"total fire ban",
	13	:"combustion gases",
	14	:"fire hazard",
	255	:"undefined"
	}

EAW_109={
	0	:"unknown",
	1	:"dam breach",
	2	:"dam overflow",
	3	:"flash flood",
	4	:"overland flow flood",
	5	:"high water level",
	6	:"king tide",
	7	:"levee breach",
	8	:"dike breach",
	9	:"storm surge",
	10	:"riverine flood",
	11	:"flooding",
	255	:"undefined"
	}

EAW_110={
	0	:"unknown",
	1	:"fog",
	255	:"undefined"
	}

EAW_111={
	0	:"unknown",
	1	:"avalanche",
	2	:"avalanche danger",
	3	:"earthquake",
	4	:"karst hazard",
	5	:"lahar",
	6	:"landslide",
	7	:"mudslide",
	8	:"glacial ice avalanche",
	9	:"lava flow",
	10	:"magnetic storm",
	11	:"solar storm",
	12	:"meteorite impact",
	13	:"pyroclastic flow",
	14	:"pyroclastic surge",
	15	:"tsunami",
	16	:"land threat tsunami",
	17	:"beach threat tsunami",
	18	:"volcanic ash cloud",
	19	:"volcano eruption",
	255	:"undefined"
	}

EAW_112={
	0	:"unknown",
	1	:"asbestos",
	2	:"biological hazard",
	3	:"chemical hazard",
	4	:"chemical accident",
	5	:"explosive hazard",
	6	:"major pollution",
	7	:"radiological hazard",
	8	:"falling object",
	9	:"dangerous goods accident",
	10	:"gas leak",
	11	:"nuclear power plant accident",
	255	:"undefined"
	}

EAW_113={
	0	:"unknown",
	1	:"health hazard",
	2	:"infection hazard",
	3	:"infectious disease",
	4	:"ambulance",
	5	:"blood supply",
	6	:"communicable disease",
	7	:"drinking water",
	8	:"drinking water contamination",
	9	:"drug safety",
	10	:"drug supply",
	11	:"food safety",
	12	:"food supply",
	13	:"food and drug supply",
	14	:"hospital",
	15	:"human quarantine",
	16	:"zoonotic disease",
	17	:"odour nuisance",
	18	:"noise nuisance",
	19	:"untreated sewage",
	20	:"high UV radiation",
	21	:"air pollution",
	255	:"undefined"
	}

EAW_114={
	0	:"unknown",
	1	:"ice pressure",
	2	:"rapid closing of coastal leads",
	3	:"special ice",
	255	:"undefined"
	}

EAW_115={
	0	:"unknown",
	1	:"freezing spray",
	2	:"strong wind",
	3	:"gale wind",
	4	:"storm force wind",
	5	:"hurricane force wind",
	6	:"iceberg",
	7	:"large coastal surf",
	8	:"large swell waves",
	9	:"marine security",
	10	:"nautical incident",
	11	:"shipping accident",
	12	:"special marine",
	13	:"oil spill",
	14	:"squall",
	15	:"waterspout",
	255	:"undefined"
	}

EAW_116={
	0	:"unknown",
	1	:"amber alert",
	2	:"missing vulnerable person",
	3	:"silver alert",
	255	:"undefined"
	}

EAW_117={
	0	:"unknown",
	255	:"undefined"
	}

EAW_118={
	0	:"unknown",
	1	:"warning",
	255	:"undefined"
	}

EAW_119={
	0	:"unknown",
	1	:"plant infectious disease",
	2	:"plant pest",
	3	:"plant quarantine",
	255	:"undefined"
	}

EAW_122={
	0	:"unknown",
	1	:"facility closure",
	2	:"facility lockdown",
	3	:"emergency support facilities",
	4	:"emergency support services",
	5	:"school bus",
	6	:"school closure",
	7	:"school lockdown",
	8	:"service or facility",
	9	:"transit",
	255	:"undefined"
	}

EAW_123={
	0	:"unknown",
	1	:"rail incident",
	2	:"rail accident",
	255	:"undefined"
	}

EAW_124={
	0	:"unknown",
	1	:"distress beacon",
	255	:"undefined"
	}

EAW_125={
	0	:"unknown",
	1	:"bridge closure",
	2	:"bridge collapse",
	3	:"hazardous road conditions",
	4	:"black ice",
	5	:"traffic accident",
	6	:"roadway closure",
	7	:"traffic delay",
	8	:"traffic incident",
	9	:"road usage conditions",
	10	:"traffic report",
	11	:"traffic warning",
	255	:"undefined"
	}

EAW_126={
	0	:"unknown",
	1	:"over land search",
	2	:"over water search",
	3	:"air search",
	255	:"undefined"
	}

EAW_127={
	0	:"unknown",
	1	:"blizzard",
	2	:"blowing snow",
	3	:"snowdrifts",
	4	:"dust storm",
	5	:"freezing drizzle",
	6	:"hail",
	7	:"freezing rain",
	8	:"hurricane",
	9	:"typhoon",
	10	:"rainfall",
	11	:"heavy rain",
	12	:"thunderstorm",
	13	:"snowfall",
	14	:"snow squall",
	15	:"tornado",
	16	:"tropical cyclone",
	17	:"tropical storm",
	18	:"winter storm",
	19	:"weather",
	255	:"undefined"
	}

EAW_128={
	0	:"unknown",
	1	:"exposure",
	2	:"arctic outflow",
	3	:"cold wave",
	4	:"cold",
	5	:"flash freeze",
	6	:"frost",
	7	:"heat wave",
	8	:"heat",
	9	:"extreme heat",
	10	:"high heat and humidity",
	11	:"wind chill",
	255	:"undefined"
	}

EAW_129={
	0	:"unknown",
	1	:"siren test",
	2	:"exercise warning",
	255	:"undefined"
	}

EAW_130={
	0	:"unknown",
	1	:"cable service",
	2	:"communications service",
	3	:"failure IT-systems",
	4	:"attack on IT-systems",
	5	:"power outage",
	6	:"diesel supply",
	7	:"electricity supply",
	8	:"heating oil supply",
	9	:"gasoline supply",
	10	:"internet service",
	11	:"landline service",
	12	:"mobile service",
	13	:"natural gas supply",
	14	:"natural gas supply failure",
	15	:"pipeline rupture",
	16	:"satellite communications service",
	17	:"sewer system",
	18	:"telephone service",
	19	:"telecommunications failure",
	20	:"emergency communication service",
	21	:"failure of emergency communication service",
	22	:"waste management",
	23	:"water supply",
	255	:"undefined"
	}

EAW_131={
	0	:"unknown",
	1	:"wind change",
	255	:"undefined"
	}

EAW_132={
	0	:"unknown",
	1	:"blue green algae",
	255	:"undefined"
	}

EAW_201={
	0	:"unknown",
	1	:"no action to recommend",
	2	:"stop in a safe place to read detailed instructions",
	3	:"evacuate the area",
	4	:"be prepared to evacuate at any time",
	5	:"move to a safe shelter",
	6	:"protect yourself from flying debris",
	7	:"stay away from damaged buildings and downed power lines",
	8	:"do not cross fast flowing or rising waters",
	9	:"do not cross flooded areas",
	10	:"move off the beach and out of harbours and marinas",
	11	:"avoid unnecessary travel",
	12	:"keep roads clear for rescue and emergency vehicles",
	13	:"drive carefully",
	14	:"adjust your driving speed",
	15	:"keep sufficient distance",
	16	:"do not leave your vehicle",
	17	:"do not leave your vehicle, close windows",
	18	:"turn off ventilation and A/C",
	19	:"avoid road travel",
	20	:"immediately seek out higher ground",
	21	:"protect yourself from the sun",
	22	:"quickly move into interior rooms",
	23	:"there is no danger",
	24	:"seek shelter in a building",
	25	:"seek shelter in a building immediately",
	26	:"seek shelter in a place where you cannot be hit by hail",
	27	:"seek shelter if you cannot leave the area immediately",
	28	:"if a building is nearby, seek shelter in that building",
	29	:"if you cannot reach a building, lie flat on the ground and protect your head with your hands",
	30	:"if you cannot find shelter, lie face-down on the ground and protect your head and neck with your hands",
	31	:"if you are in open terrain, crouch on the balls of your feet with your feet close together, in a hollow where possible",
	32	:"take cover and wait until the earthquake is over",
	33	:"hide",
	34	:"leave the area immediately",
	35	:"leave the impact site immediately",
	36	:"move wherever possible at a right angle to the wind direction",
	37	:"do not touch any debris",
	38	:"do not touch any dead animals",
	39	:"do not touch any suspicious objects",
	40	:"keep away from trees and buildings from which roof avalanches can come loose",
	41	:"keep away from trees and power lines",
	42	:"keep away from crevices and slopes",
	43	:"keep away from affected farms",
	44	:"keep a sufficient distance from the building",
	45	:"if there is a risk of flooding, do not enter cellars or underground car parks",
	46	:"do not go near flooded waters",
	47	:"do not drive through flooded roads",
	48	:"close all windows",
	49	:"close all windows and doors",
	50	:"exit the vehicle",
	51	:"if you cannot exit the vehicle, lower your head and protect it with your hands",
	52	:"cover your mouth and nose with improvised respiratory protection (cloth, garment, surgical mask)",
	53	:"have iodine tablets ready. DO NOT take the iodine tablets now",
	54	:"take the iodine tablets NOW according to the package insert",
	55	:"do not drink any tap water",
	56	:"only drink mineral water from a bottle",
	57	:"protect yourself from direct sunlight",
	58	:"be prepared for aftershocks",
	255	:"undefined"
	}

EAW_202={
	0	:"unknown",
	1	:"driving not allowed",
	2	:"stop vehicle at next possible place",
	3	:"drive to next available parking place",
	4	:"wait for police patrol",
	5	:"follow police instructions",
	6	:"follow evacuation routes",
	7	:"follow orders to evacuate when instructed",
	8	:"do not throw away any burning cigarettes",
	9	:"do not throw away any burning cigarettes or matches",
	10	:"follow the instructions of the emergency services",
	11	:"use public transport",
	12	:"stop on the hard shoulder or on the edge of the road",
	13	:"if you are in a vehicle - stop on the hard shoulder or on the edge of the road",
	14	:"warn other people. Ask them to flee",
	15	:"warn other people to prevent them from entering the danger zone",
	16	:"keep all access routes to the scene of the fire clear",
	17	:"inform the emergency services of the location of the suspicious objects",
	18	:"if you have made any relevant observations, inform the police",
	19	:"inform the emergency services about damage and debris",
	20	:"report any findings of dead wild animals to the authorities",
	21	:"find out the location of the information points set up by the authorities",
	22	:"approach police forces in a calm and reasonable manner. Keep your hands up",
	23	:"only call the emergency numbers of the police and fire brigades in emergencies",
	24	:"only make phone calls in serious emergencies to avoid overloading the telephone lines",
	25	:"observe the quarantine measures by the authorities",
	255	:"undefined"
	}

EAW_203={
	0	:"unknown",
	1	:"avoid the area",
	2	:"detour the area",
	3	:"detour the area by a wide margin",
	4	:"give priority to travellers evacuating the area",
	5	:"expect travel restrictions in the area",
	6	:"expect travel problems in the area",
	255	:"undefined"
	}

EAW_204={
	0	:"unknown",
	1	:"switch on radio",
	2	:"be alert to further information",
	3	:"monitor the situation carefully",
	4	:"listen to regional radio stations",
	5	:"switch on the car radio and listen for further information",
	6	:"get information from the media, for example on local radio",
	7	:"pay attention to announcements made by the police and fire brigade",
	8	:"we will inform you when the danger has passed",
	255	:"undefined"
	}

EAW_205={
	0	:"unknown",
	1	:"inform your neighbours",
	2	:"provide first aid if necessary but do not put yourself in any danger",
	3	:"help children and other people in need but do not put yourself at risk",
	4	:"take only the essentials with you, especially ID cards and cash",
	5	:"if you need help leaving your home, contact your city using the telephone number provided",
	6	:"close all windows and shutters and keep away from unprotected openings",
	7	:"stay in the building and await instructions",
	8	:"avoid going outdoors",
	9	:"watch out for flying objects",
	10	:"avoid rooms directly underneath the roof truss",
	11	:"avoid very large rooms, such as halls, in which the ceiling is not supported by pillars",
	12	:"disconnect sensitive equipment from the mains",
	13	:"avoid all items with metal parts such as umbrellas and bicycles",
	14	:"do not bathe or shower during a thunderstorm",
	15	:"do not leave pets or livestock outside",
	16	:"move to higher parts of the building",
	17	:"move personal valuables into higher parts of the building",
	18	:"turn off the gas, water and electricity supply",
	19	:"turn off all gas lines",
	20	:"switch off the electricity and heating in rooms that are at risk",
	21	:"switch off the electricity, gas and heating in rooms that are at risk",
	22	:"if the junction box is located in a flooded room, do not enter it, but instead inform the fire brigade",
	23	:"do not swim in flooded streets, nor walk through flooded underpasses",
	24	:"keep drains and shafts clear so that the water can drain away",
	25	:"if possible, move into safe rooms in the building on the side facing away from the slope",
	26	:"be aware of additional hazards, e.g. electricity",
	27	:"watch out for escaping gas",
	28	:"if possible, stay in cool rooms and buildings",
	29	:"avoid doing activities and spending prolonged periods outdoors",
	30	:"wear sunglasses with 100% UV protection outdoors",
	31	:"drink plenty of water and make sure you eat light food",
	32	:"boil water before drinking it or using it in the kitchen",
	33	:"avoid any skin contact with tap water. Turn off the water supply to your house",
	34	:"temporarily take in any endangered persons",
	35	:"stay away from glass surfaces such as windows and glass doors",
	36	:"leave damaged buildings immediately. Beware of falling objects",
	37	:"do not use any lifts",
	38	:"prepare for a possible power outage - check your supplies of water, food, cash, batteries and medicine",
	39	:"use bicycle or motorcycle helmets to protect your head from falling rocks",
	40	:"stay in the building and await further information",
	41	:"do not enter smoke-filled rooms",
	42	:"do not make a fire outdoors",
	43	:"use permanent fireplaces when barbecuing. Make sure your fire is completely extinguished before you leave",
	44	:"do not light any fireworks",
	45	:"only light fireworks with the permission of the municipality, keep a safe distance from the forest and have water at hand",
	46	:"the fault will be rectified as soon as possible",
	47	:"the power supply will be restored as quickly as possible",
	48	:"reduce your power consumption using batteries to a minimum",
	49	:"switch off all mains-operated devices",
	50	:"reduce your water consumption to a minimum",
	51	:"get batteries for torches and radios",
	52	:"check and restock your equipment and supplies of water, food, medicine, cash and batteries",
	53	:"quickly move into interior rooms",
	54	:"immediately move into an underground or interior room with as few exterior walls, windows and doors as possible",
	55	:"avoid parts of buildings with glass surfaces",
	56	:"lie on the floor, away from windows and doors",
	57	:"lie flat on the floor and protect your head with your hands",
	58	:"seek out a cellar or interior room on lower floors",
	59	:"pregnant women and children should stay in closed rooms",
	60	:"before entering the building, take off your outer clothing and shoes and leave them outside the building",
	61	:"wash your hands first, then your face, hair, nose and ears",
	62	:"if possible, always disinfect your hands after contact with possible pathogens",
	63	:"wash your hands regularly and thoroughly",
	64	:"keep a safe distance to any conversation partner",
	65	:"avoid physical contact with other people such as kissing and shaking hands",
	66	:"avoid group activities such as team sports",
	255	:"undefined"
	}



_EAW_tables={
	"EAW_001": EAW_001,
	"EAW_002": EAW_002,
	"EAW_003": EAW_003,
	"EAW_004": EAW_004,
	"EAW_005": EAW_005,
	"EAW_006": EAW_006,
	"EAW_007": EAW_007,
	"EAW_010": EAW_010,
	"EAW_011": EAW_011,
	"EAW_103": EAW_103,
	"EAW_104": EAW_104,
	"EAW_105": EAW_105,
	"EAW_106": EAW_106,
	"EAW_107": EAW_107,
	"EAW_108": EAW_108,
	"EAW_109": EAW_109,
	"EAW_110": EAW_110,
	"EAW_111": EAW_111,
	"EAW_112": EAW_112,
	"EAW_113": EAW_113,
	"EAW_114": EAW_114,
	"EAW_115": EAW_115,
	"EAW_116": EAW_116,
	"EAW_117": EAW_117,
	"EAW_118": EAW_118,
	"EAW_119": EAW_119,
	"EAW_122": EAW_122,
	"EAW_123": EAW_123,
	"EAW_124": EAW_124,
	"EAW_125": EAW_125,
	"EAW_126": EAW_126,
	"EAW_127": EAW_127,
	"EAW_128": EAW_128,
	"EAW_129": EAW_129,
	"EAW_130": EAW_130,
	"EAW_131": EAW_131,
	"EAW_132": EAW_132,
	"EAW_201": EAW_201,
	"EAW_202": EAW_202,
	"EAW_203": EAW_203,
	"EAW_204": EAW_204,
	"EAW_205": EAW_205
	}

_EAW_010_switch_tables = {
    3	:EAW_103,
    4	:EAW_104,
    5	:EAW_105,
    6	:EAW_106,
    7	:EAW_107,
    8	:EAW_108,
    9	:EAW_109,
    10	:EAW_110,
    11	:EAW_111,
    12	:EAW_112,
    13	:EAW_113,
    14	:EAW_114,
    15	:EAW_115,
    16	:EAW_116,
    17	:EAW_117,
    18	:EAW_118,
    19	:EAW_119,
    22	:EAW_122,
    23	:EAW_123,
    24	:EAW_124,
    25	:EAW_125,
    26	:EAW_126,
    27	:EAW_127,
    28	:EAW_128,
    29	:EAW_129,
    30	:EAW_130,
    31	:EAW_131,
    32	:EAW_132
    }

#
#
#
#
_EAW_011_switch_tables = {
    1	:EAW_201,
    2	:EAW_202,
    3	:EAW_203,
    4	:EAW_204,
    5	:EAW_205
    }


#================================
_EAW_switch_tables = {
    "EAW_010":_EAW_010_switch_tables,
    "EAW_011":_EAW_011_switch_tables
    }

#
# ==============================================================================================
#

if __name__=='__main__':
    sum_events       = len(EAW_010)-2 # do not count "unknown" and "undefined"
    sum_instructions = len(EAW_011)-2

    for key in _EAW_010_switch_tables:
        sum_events += len(_EAW_010_switch_tables[key])-2

    for key in _EAW_011_switch_tables:
        sum_instructions += len(_EAW_011_switch_tables[key])-2

    print("Number events      :",sum_events)
    print("Number instructions:",sum_instructions)
