# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions"""

import sys
from . import exception


def parse_range(rangespec):
    """Parse an integer range string and return the resulting ranges

    Examples
        parse_range("-2,4,6-8,10-")      -> [(1,2), (4,4), (6,8), (10,INTMAX)]
        parse_range(" - 3 , 4-  4, 2-6") -> [(1,3), (4,4), (2,6)]
    """
    ranges = []

    for group in rangespec.split(","):
        parts = group.split("-", maxsplit=1)
        try:
            if len(parts) == 1:
                beg = int(parts[0])
                end = beg
            else:
                beg = int(parts[0]) if parts[0].strip() else 1
                end = int(parts[1]) if parts[1].strip() else sys.maxsize
            ranges.append((beg, end) if beg <= end else (end, beg))
        except ValueError:
            pass

    return ranges


def optimize_range(ranges):
    """Simplify/Combine a parsed list of ranges

    Examples
        optimize_range([(2,4), (4,6), (5,8)])         -> [(2,8)]
        optimize_range([(1,1), (2,2), (3,6), (8,9))]) -> [(1,6), (8-9)]
    """
    if len(ranges) <= 1:
        return ranges

    ranges.sort()
    riter = iter(ranges)
    result = []

    beg, end = next(riter)
    for lower, upper in riter:
        if lower > end+1:
            result.append((beg, end))
            beg, end = lower, upper
        elif upper > end:
            end = upper
    result.append((beg, end))
    return result


class RangePredicate():
    """Predicate; is True if the current index is in the given range"""
    def __init__(self, rangespec):
        self.ranges = optimize_range(parse_range(rangespec))
        self.index = 0
        if self.ranges:
            self.lower, self.upper = self.ranges[0][0], self.ranges[-1][1]
        else:
            self.lower, self.upper = 0, 0

    def __bool__(self):
        self.index += 1

        if self.index > self.upper:
            raise exception.StopExtraction()

        for lower, upper in self.ranges:
            if lower <= self.index <= upper:
                return True
        return False
