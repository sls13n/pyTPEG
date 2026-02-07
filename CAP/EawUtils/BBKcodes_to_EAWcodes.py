#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
# Conversion of BBK codes to EAW codes
#
# NB reduced subset for sample BBK CAP messages only
#

# ==============================================================================================
#
#

def BBKevents_to_EAWevents(BBKeventCodes):
    EAWcodestring = b""
    n = 0

    for BBKeventCode in BBKeventCodes:
        if BBKeventCode in EventCode_mapping:
            event_list = EventCode_mapping[BBKeventCode]
            for event in event_list:
                n += 1
                [main, sub] = event

                EAWcodestring += bytes([main])
                if sub >= 0:
                    EAWcodestring += b'\x40' + bytes([sub])
                else:
                    EAWcodestring += b'\x00'
        else:
            print("BBK event code", BBKeventCode, "could not be converted to EAW")

    EAWcodestring = bytes([n]) + EAWcodestring

    return EAWcodestring


#
# To Do: shortcode (special treatment / or rather not?)
#
def BBKinstructions_to_EAWinstructions(BBKinstructionCodes):
    EAWcodestring = b""
    n = 0

    for instructionCode in BBKinstructionCodes:

        if instructionCode in InstructionCode_mapping:
            instruction_list = InstructionCode_mapping[instructionCode]
            for instruction in instruction_list:
                n += 1
                [main, sub] = instruction

                if sub >= 0:
                    EAWcodestring += bytes([main, 0x40, sub])
                else:
                    EAWcodestring += bytes([main, 0])
        else:
            print("BBK instruction code", instructionCode, "could not be converted to EAW")

    EAWcodestring = bytes([n]) + EAWcodestring

    return EAWcodestring


#
# EventCode mapping list, to be extended for multi-codes
#

EventCode_mapping = {
    "BBK-EVC-044": [[7, 8]],
    "BBK-EVC-053": [[5, 10]]
}

#
# InstructionCode mapping, to be extended for multi-codes
#

InstructionCode_mapping = {
    "BBK-ISC-001": [[3, 1]],
    "BBK-ISC-003": [[1, 34]],
    "BBK-ISC-004": [[3, 3]],
    "BBK-ISC-005": [[1, 13]],
    "BBK-ISC-006": [[1, 19]],
    "BBK-ISC-009": [[4, 6]],
    "BBK-ISC-011": [[4, 4]],
    "BBK-ISC-016": [[2, 10]],
    "BBK-ISC-021": [[5, 3]],
    "BBK-ISC-038": [[5, 15]],
    "BBK-ISC-086": [[1, 25]]
}
