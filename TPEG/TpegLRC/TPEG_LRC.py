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
# LRC class for TPEG component parsing
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
# Import main component from specific location referencing methods
#
from .TPEG_LRC_ETL        import TPEG_LRC_ETL_component
from .TPEG_LRC_TMC        import TPEG_LRC_TMC_component
from .TPEG_LRC_GLR        import TPEG_LRC_GLR_component
from .TPEG_LRC_OLR        import TPEG_LRC_OLR_component


#
# --------- LRC ---------------------------------

class TPEG_LRC_component(TPEG_component):
    def __init__(self,id,level=1,componentsDict={},Cname="LocationReferencingContainer",Ctype="LRC"):
        TPEG_component.__init__(self,id,level,componentsDict,Cname,Ctype)
        componentsDict[2] = TPEG_LRC_TMC_component
        componentsDict[5] = TPEG_LRC_ETL_component
        componentsDict[6] = TPEG_LRC_GLR_component
        componentsDict[8] = TPEG_LRC_OLR_component


#
# Test functionality
#

if __name__ == '__main__':
    print("TPEG_LRC_component")
