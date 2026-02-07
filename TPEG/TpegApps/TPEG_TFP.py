#!/usr/bin/env python3
#
# Copyright 2022-2024 TISA ASBL
#
# Minimal TFP support added for evaluation purposes.
#
# This module follows the existing coding style used by TPEG_TEC.py / TPEG_EAW.py:
# - Provide a frame continuation class for AID=7
# - Provide a message root component (id=0)
# - Decode MMC (id=1), TFPData (id=6), and LRC (id=2)
# - Decode FlowVector (id=7) attribute blocks into a readable structure

import os
import sys


# add parent directory find when run as main
if __name__ == '__main__':
    sys.path.append(os.path.abspath(sys.path[0] + '/..'))


import Base
from Base.TPEG_component import TPEG_component
from Base.TPEG_component_frame import TPEG_ProtPrioCountedComp_frame

from TpegMMC.TPEG_MMC import TPEG_MMC_component
from TpegLRC.TPEG_LRC import TPEG_LRC_component


class TPEG_TFP_frame_continuation(TPEG_ProtPrioCountedComp_frame):
    """TFP application frame continuation (AID=7)."""

    def __init__(self, id, level=2, componentsDict=None, Cname="TFP", Ctype="TFP_component_frame"):
        if componentsDict is None:
            componentsDict = {}
        componentsDict[0] = TPEG_TFP_component
        TPEG_ProtPrioCountedComp_frame.__init__(self, id, level, componentsDict, Cname, Ctype)


class TPEG_TFP_component(TPEG_component):
    """TFP message root (Component ID = 0)."""

    def __init__(self, id, level=0, componentsDict=None, Cname="TFPmessage", Ctype="TFP"):
        if componentsDict is None:
            componentsDict = {}
        TPEG_component.__init__(self, id, level, componentsDict, Cname, Ctype)
        componentsDict[1] = TPEG_MMC_component
        componentsDict[2] = TPEG_LRC_component
        componentsDict[6] = TFP_FlowMatrix_component


class TFP_FlowMatrix_component(TPEG_component):
    """TFP data component (Flow Matrix) (Component ID = 6).

    Attributes observed in sample payload:
    - startTime (DateTime)
    - selector (BitArray)
    - optional duration (IntUnLoMB)
    - spatialResolution (IntUnTi)

    Remaining bytes are FlowVector components (id=7).
    """

    def __init__(self, id, level=1, componentsDict=None, Cname="TFP data component (Flow Matrix)", Ctype="TFP_FlowMatrix"):
        if componentsDict is None:
            componentsDict = {}
        TPEG_component.__init__(self, id, level, componentsDict, Cname, Ctype)
        componentsDict[7] = TFP_FlowVector_component

    def parse_attributes(self, TPEGstring):
        # startTime is a 4-byte UTC timestamp
        self.attributes.append(['startTime', TPEGstring.DateTime()])

        selector = TPEGstring.BitArray()
        self.attributes.append(['selector', selector.bits])

        # selector bit 0 commonly indicates presence of duration
        if selector.is_set(0):
            self.attributes.append(['duration', TPEGstring.IntUnLoMB()])

        # spatialResolution is a 1 byte value
        if TPEGstring.len() > 0:
            self.attributes.append(['spatialResolution', TPEGstring.IntUnTi()])


class TFP_FlowVector_component(TPEG_component):
    """FlowVector component (Component ID = 7) parsed from attribute block.

    We implement a minimal decoder based on observed payloads:
    - timeOffset (varlen)
    - sectionCount (varlen)
    - sections[]:
      - spatialOffset (varlen)
      - status selector (1 byte)
        - bits 0x10 LOS, 0x20 averageSpeed, 0x40 delay (as observed)
      - section selector (1 byte)
        - bit 0x40 indicates per-section spatialResolution override
    - flowVector selector (1 byte) + optional spatialResolution
    """

    def __init__(self, id, level=2, componentsDict=None, Cname="FlowVector", Ctype="TFP_FlowVector"):
        if componentsDict is None:
            componentsDict = {}
        TPEG_component.__init__(self, id, level, componentsDict, Cname, Ctype)

    def parse_attributes(self, TPEGstring):
        self.attributes.append(['timeOffset', TPEGstring.IntUnLoMB()])
        section_count = TPEGstring.IntUnLoMB()
        self.attributes.append(['sectionCount', section_count])

        LOS_BIT = 0x10
        AVG_BIT = 0x20
        DELAY_BIT = 0x40
        SEC_SPATIALRES_BIT = 0x40
        FV_SPATIALRES_BIT = 0x40

        for i in range(section_count):
            spatial_offset = TPEGstring.IntUnLoMB()
            status_sel = TPEGstring.IntUnTi()
            los = avg = delay = None
            if status_sel & LOS_BIT:
                los = TPEGstring.IntUnTi()
            if status_sel & AVG_BIT:
                avg = TPEGstring.IntUnTi()
            if status_sel & DELAY_BIT:
                delay = TPEGstring.IntUnLoMB()

            sec_sel = TPEGstring.IntUnTi()
            sec_spatial_res = None
            if sec_sel & SEC_SPATIALRES_BIT:
                sec_spatial_res = TPEGstring.IntUnTi()

            self.attributes.append([
                f'section_{i}',
                {
                    'spatialOffset': spatial_offset,
                    'statusSel': status_sel,
                    'los': los,
                    'averageSpeed': avg,
                    'delay': delay,
                    'selector': sec_sel,
                    'spatialResolution': sec_spatial_res,
                },
            ])

        # Optional flowVector selector at end
        if TPEGstring.len() > 0:
            fv_sel = TPEGstring.IntUnTi()
            fv_spatial_res = None
            if fv_sel & FV_SPATIALRES_BIT and TPEGstring.len() > 0:
                fv_spatial_res = TPEGstring.IntUnTi()
            self.attributes.append(['flowVectorSelector', fv_sel])
            if fv_spatial_res is not None:
                self.attributes.append(['flowVectorSpatialResolution', fv_spatial_res])
