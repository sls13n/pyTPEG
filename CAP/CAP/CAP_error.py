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
# base class for CAP error logging
#
import copy

_error_context = None
_error_object_stack = []
_error_log = []
_suppress_error_reports = False


#
# Option to suppress error reporting for e.g. KML generation
#
def CAP_error_suppress_reports(suppress=False):
    global _suppress_error_reports

    if suppress:
        _suppress_error_reports = True
    else:
        _suppress_error_reports = False

    return


def CAP_error_set_context(context):
    global _error_context
    global _error_object_stack
    global _error_log

    _error_context = context

    return


def CAP_error_unset_context():
    global _error_context
    global _error_object_stack
    global _error_log

    _error_context = None

    return


def CAP_error_set_object(error_object):
    global _error_context
    global _error_object_stack
    global _error_log

    _error_object_stack.append(error_object)

    return


def CAP_error_unset_object():
    global _error_context
    global _error_object_stack
    global _error_log

    if _error_object_stack:
        _error_object_stack.pop()
    else:
        _error_object_stack = []


def CAP_error_reset():
    global _error_context
    global _error_object_stack
    global _error_log

    _error_context = None
    _error_object_stack = []
    _error_log = []
    return


def CAP_log_error(error_text, show=True):
    global _error_context
    global _error_object_stack
    global _error_log
    global _suppress_error_reports

    _error_log.append([_error_context, _error_object_stack[:], error_text])

    if show and not _suppress_error_reports:
        i = len(_error_log)
        print("====== CAP ERROR REPORT %d START ==============================================" % i)

        if _error_context is not None:
            print("\nIn context of...\n")
            try:
                _error_context.out()
            except:
                try:
                    print(_error_context)
                except:
                    pass

        print("\nLogged Error...\n")

        print(error_text)

        print("")

        if _error_object_stack:
            try:
                # get last object on the stack
                _error_object = _error_object_stack[-1]
                print("while parsing ...\n")

                try:
                    _error_object.out()
                except:
                    try:
                        print(_error_object)
                    except:
                        pass
            except:
                pass
            print("")

        print("====== CAP ERROR REPORT %d END   ==============================================" % i)
        print("\n")
