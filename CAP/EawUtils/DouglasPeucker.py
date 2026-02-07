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
# Douglas Peucker algorithm
#
# source https://stackoverflow.com/questions/37946754/python-ramer-douglas-peucker-rdp-algorithm-with-number-of-points-instead-of
#
#
import math

def sqr(x):
    return x*x

def distSquared(p1, p2): # adapted to WGS84 coordinates
    [lat1, lon1] = p1
    [lat2, lon2] = p2
    radius = 6371000 # m

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    c = c*180.0/math.pi

    return c*c

    ## return sqr(p1[0] - p2[0]) + sqr(p1[1] - p2[1])

class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.lengthSquared = distSquared(self.p1, self.p2)

    def getRatio(self, point):
        segmentLength = self.lengthSquared
        if segmentLength == 0:
            return distSquared(point, self.p1)
        return ((point[0] - self.p1[0]) * (self.p2[0] - self.p1[0]) + \
        (point[1] - self.p1[1]) * (self.p2[1] - self.p1[1])) / segmentLength

    def distanceToSquared(self, point):
        t = self.getRatio(point)

        if t < 0:
            return distSquared(point, self.p1)
        if t > 1:
            return distSquared(point, self.p2)

        return distSquared(point, [
            self.p1[0] + t * (self.p2[0] - self.p1[0]),
            self.p1[1] + t * (self.p2[1] - self.p1[1])
        ])

    def distanceTo(self, point):
        return math.sqrt(self.distanceToSquared(point))


def simplifyDouglasPeucker(points, pointsToKeep):
    weights = []
    length = len(points)

    def douglasPeucker(start, end):
        if (end > start + 1):
            line = Line(points[start], points[end])
            maxDist = -1
            maxDistIndex = 0

            for i in range(start + 1, end):
                dist = line.distanceToSquared(points[i])
                if dist > maxDist:
                    maxDist = dist
                    maxDistIndex = i

            weights.insert(maxDistIndex, maxDist)

            douglasPeucker(start, maxDistIndex)
            douglasPeucker(maxDistIndex, end)

    douglasPeucker(0, length - 1)
    weights.insert(0, float("inf"))
    weights.append(float("inf"))

    weightsDescending = weights
    weightsDescending = sorted(weightsDescending, reverse=True)

    maxTolerance = weightsDescending[pointsToKeep - 1]
    result = [
        point for i, point in enumerate(points) if weights[i] >= maxTolerance
    ]

    return result
