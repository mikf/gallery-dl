# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions"""


def apply_range(iterable, rangespec):
    """Return a new iterable containing only the items specified in the given
    integer range
    """
    try:
        maxval = len(iterable)
    except TypeError:
        maxval = 0
    rset = parse_range(rangespec, maxval)
    return (
        item
        for index, item in enumerate(iterable, 1)
        if index in rset
    )


def parse_range(rangespec, maxval=0):
    """Parse an integer range and return the resulting set

    Examples
        parse_range("-2,4,6-8,10-", 12)  -> set(1, 2, 4, 6, 7, 8, 10, 11, 12)
        parse_range(" - 3 , 4-  4, 6-2") -> set(1, 2, 3, 4)
    """
    result = set()
    for group in rangespec.split(","):
        parts = group.split("-", maxsplit=1)
        try:
            if len(parts) == 1:
                result.add(int(parts[0]))
            else:
                beg = int(parts[0]) if parts[0].strip() else 1
                end = int(parts[1]) if parts[1].strip() else maxval
                result.update(range(beg, end+1))
        except ValueError:
            pass
    return result
