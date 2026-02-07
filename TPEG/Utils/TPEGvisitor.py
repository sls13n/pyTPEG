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
# TPEG visitor pattern, can be particularized with pre and post handler functions, taking a class instance as attribute
#
# General for TPEG transport frames
#
#
import os, sys
#
#
# add parent directory when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0]+'/..'))

#
#
from . import visitor
#
import Base
#
# import TPEG frame types
from Base.TPEG_frame              import TPEG_Transport_Frame, TPEG_ServiceFrame0, TPEG_ServiceFrame1

from Base.TPEG_component_frame    import TPEG_component_frame, TPEG_comp_frame_continuation
from Base.TPEG_SNI_base_component import TPEG_SNI_base_component
from Base.TPEG_component          import TPEG_component, TPEG_datastructure
#
#
# Now define TPEG Visitor Class
#
class TPEGvisitor(object):
    def __init__(self, pre_handlers={}, post_handlers={}, default_handler=None):
        # install optional pre and post handlers
       self.pre_handlers     = pre_handlers
       self.post_handlers    = post_handlers
       self.default_handler  = default_handler


    @visitor.on('target')
    def visit(self, target):
        """
        This is the generic vist method that initializes the
        dynamic dispatcher.
        """
        pass
    #
    #
    # TPEG Transport frame
    @visitor.when(TPEG_Transport_Frame)
    def visit(self, target):
        """
        Visit method for a TPEG Transport Frames
        """
        #print "TPEG Transport frame:", target.name, target.type
        if self.pre_handlers.get(TPEG_Transport_Frame,False):
            self.pre_handlers.get(TPEG_Transport_Frame)(target)

        self.visit(target.serviceframe)

        if self.post_handlers.get(TPEG_Transport_Frame,False):
            self.post_handlers.get(TPEG_Transport_Frame)(target)



    #
    # TPEG service frame type 0
    @visitor.when(TPEG_ServiceFrame0)
    def visit(self, target):
        """
        Visit method for a TPEG Service Frame of type 0
        """
        #print "TPEG_ServiceFrame0", target.name, target.type
        if self.pre_handlers.get(TPEG_ServiceFrame0,False):
            self.pre_handlers.get(TPEG_ServiceFrame0)(target)

        if self.post_handlers.get(TPEG_ServiceFrame0,False):
            self.post_handlers.get(TPEG_ServiceFrame0)(target)

    #
    # TPEG service frame type 1
    @visitor.when(TPEG_ServiceFrame1)
    def visit(self, target):
         """
         Visit method for a TPEG Service Frame of type 1
         """
         #print "TPEG_ServiceFrame1", target.type, target.name
         if self.pre_handlers.get(TPEG_ServiceFrame1,False):
            self.pre_handlers.get(TPEG_ServiceFrame1)(target)

         for compFrame in target.CompFrames:
             self.visit(compFrame)

         if self.post_handlers.get(TPEG_ServiceFrame1,False):
            self.post_handlers.get(TPEG_ServiceFrame1)(target)

    #
    # TPEG component frame
    @visitor.when(TPEG_component_frame)
    def visit(self, target):
         """
         Visit method for a TPEG component frame
         """
         #print "TPEG_component_frame", target.type, target.name
         if self.pre_handlers.get(TPEG_component_frame,False):
            self.pre_handlers.get(TPEG_component_frame)(target)

         if target.frame_continuation:
             self.visit(target.frame_continuation)

         if self.post_handlers.get(TPEG_component_frame,False):
            self.post_handlers.get(TPEG_component_frame)(target)

    #
    # TPEG component frame continuation
    @visitor.when(TPEG_comp_frame_continuation)
    def visit(self, target):
         """
         Visit method for a TPEG component frame continuation
         """
         #print "TPEG_comp_frame_continuation", target.type, arget.name
         if self.pre_handlers.get(TPEG_comp_frame_continuation,False):
            self.pre_handlers.get(TPEG_comp_frame_continuation)(target)

         for comp in target.components:
             self.visit(comp)

         if self.post_handlers.get(TPEG_comp_frame_continuation,False):
            self.post_handlers.get(TPEG_comp_frame_continuation)(target)




    @visitor.when(TPEG_SNI_base_component)
    def visit(self, target):
         """
         Visit method for a TPEG SNI component
         """
         #print "TPEG_SNI_component", target.type, target.name
         if self.pre_handlers.get(TPEG_SNI_base_component,False):
            self.pre_handlers.get(TPEG_SNI_base_component)(target)

         for comp in target.subcomponents:
            self.visit(comp)

         if self.post_handlers.get(TPEG_SNI_base_component,False):
            self.post_handlers.get(TPEG_SNI_base_component)(target)


    @visitor.when(TPEG_component)
    def visit(self, target):
         """
         Visit method for a TPEG component
         """
         #print "TPEG_component", target.type, target.name
         if self.pre_handlers.get(TPEG_component,False):
            self.pre_handlers.get(TPEG_component)(target)

         # visit datastructures if applicable
         for ds in target.datastructures():
             self.visit(ds)

         for comp in target.subcomponents:
             self.visit(comp)

         if self.post_handlers.get(TPEG_component,False):
            self.post_handlers.get(TPEG_component)(target)

    @visitor.when(TPEG_datastructure)
    def visit(self, target):
         """
         Visit method for a TPEG datastructure
         """
         #print "TPEG_datastructure", target.type, target.name
         if self.pre_handlers.get(TPEG_datastructure,False):
            self.pre_handlers.get(TPEG_datastructure)(target)

         # visit sub datastructures if applicable
         for ds in target.datastructures():
             self.visit(ds)

         if self.post_handlers.get(TPEG_datastructure,False):
            self.post_handlers.get(TPEG_datastructure)(target)


    @visitor.when(object)
    def visit(self, target):
        """ fallback visitor """
        #fallback if nothing else matched
        #print "Default: Visited",target
        if self.default_handler is not None:
            self.default_handler(target)
        pass




if __name__=='__main__':
    print("TPEGvisitor")
