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
    """Parse an integer range and return the resulting ranges and upper limit

    Examples
        parse_range("-2,4,6-8,10-")
            -> [(1,2), (4,4), (6,8), (10,INTMAX)], INTMAX

        parse_range(" - 3 , 4-  4, 2-6")
            -> [(1,3), (4,4), (2,6)], 6
    """
    ranges = []
    limit = 0
    for group in rangespec.split(","):
        parts = group.split("-", maxsplit=1)
        try:
            if len(parts) == 1:
                beg = int(parts[0])
                end = beg
            else:
                beg = int(parts[0]) if parts[0].strip() else 1
                end = int(parts[1]) if parts[1].strip() else sys.maxsize
            ranges.append((beg, end))
            limit = max(limit, end)
        except ValueError:
            pass
    return ranges, limit


class RangePredicate():
    """Predicate; is True if the current index is in the given range"""
    def __init__(self, rangespec):
        self.ranges, self.limit = parse_range(rangespec)
        self.index = 0

    def __bool__(self):
        self.index += 1

        if self.index > self.limit:
            raise exception.StopExtraction()

        for lower, upper in self.ranges:
            if lower <= self.index <= upper:
                return True
        return False
