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
# MMC tables
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

def MMC_code_to_text(code,TPEG_table,switch_code=None):
    global _MMC_tables
    global _MMC_switch_tables
    #
    # determine proper table to use
    if switch_code is not None:
        table = _MMC_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _MMC_tables.get(TPEG_table,None)

    if table is not None:
        error_string = "Invalid/Unknown Code in table %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)

        text = str(code)+": "+table.get(code,error_string)
    else:
        text = str(code)+": Invalid/Unknown MMC table %s"%TPEG_table
        error_string = "==> MMC: unknown table  %s"%TPEG_table

        if switch_code is not None:
            error_string += ", switched with code "+str(switch_code)
            text         += ", switched with code "+str(switch_code)

        TPEG_log_error(error_string)

    return text

# return list of available codes
def MMC_code_list(TPEG_table,switch_code=None):
    global _MMC_tables
    global _MMC_switch_tables

    code_list = None
    #
    # determine proper table to use
    if switch_code is not None:
        table = _MMC_switch_tables.get(TPEG_table,None)
        if table is not None:
            table = table.get(switch_code,None)
    else:
        table = _MMC_tables.get(TPEG_table,None)

    if table is not None:
        code_list = list(table.keys())
        code_list.sort()

    return code_list

MMC_001={
	1	:"mandatory",
	2	:"additional"
	}

MMC_002={
	1	:"replaceTopLevel",
	2	:"rfu",
	3	:"rfu"
	}


#
# dictionary with all MMC tables
_MMC_tables = {
    "MMC_001":MMC_001,
    "MMC_002":MMC_002,
    }

#
# no switching tables
_MMC_switch_tables = {}
