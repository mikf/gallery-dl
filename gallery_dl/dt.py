# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Date/Time utilities"""

import sys
import time
from datetime import datetime, date, timedelta, timezone  # noqa F401


class NullDatetime(datetime):

    def __bool__(self):
        return False

    def __str__(self):
        return "[Invalid DateTime]"

    def __format__(self, format_spec):
        return "[Invalid DateTime]"


NONE = NullDatetime(1, 1, 1)
EPOCH = datetime(1970, 1, 1)
SECOND = timedelta(0, 1)


def normalize(dt):
    #  if (o := dt.utcoffset()) is not None:
    #      return dt.replace(tzinfo=None, microsecond=0) - o
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None, microsecond=0)
    if dt.microsecond:
        return dt.replace(microsecond=0)
    return dt


def convert(value):
    """Convert 'value' to a naive UTC datetime object"""
    if not value:
        return NONE
    if isinstance(value, datetime):
        return normalize(value)
    if isinstance(value, str) and (dt := parse_iso(value)) is not NONE:
        return dt
    return parse_ts(value)


def parse(dt_string, format):
    """Parse 'dt_string' according to 'format'"""
    try:
        return normalize(datetime.strptime(dt_string, format))
    except Exception:
        return NONE


if sys.hexversion < 0x30c0000:
    # Python <= 3.11
    def parse_iso(dt_string):
        """Parse 'dt_string' as ISO 8601 value"""
        try:
            if dt_string[-1] == "Z":
                # compat for Python < 3.11
                dt_string = dt_string[:-1]
            elif dt_string[-5] in "+-":
                # compat for Python < 3.11
                dt_string = f"{dt_string[:-2]}:{dt_string[-2:]}"
            return normalize(datetime.fromisoformat(dt_string))
        except Exception:
            return NONE

    from_ts = datetime.utcfromtimestamp
    now = datetime.utcnow

else:
    # Python >= 3.12
    def parse_iso(dt_string):
        """Parse 'dt_string' as ISO 8601 value"""
        try:
            return normalize(datetime.fromisoformat(dt_string))
        except Exception:
            return NONE

    def from_ts(ts=None):
        """Convert Unix timestamp to naive UTC datetime"""
        Y, m, d, H, M, S, _, _, _ = time.gmtime(ts)
        return datetime(Y, m, d, H, M, S)

    now = from_ts


def parse_ts(ts, default=NONE):
    """Create a datetime object from a Unix timestamp"""
    try:
        return from_ts(int(ts))
    except Exception:
        return default


def to_ts(dt):
    """Convert naive UTC datetime to Unix timestamp"""
    return (dt - EPOCH) / SECOND


def to_ts_string(dt):
    """Convert naive UTC datetime to Unix timestamp string"""
    try:
        return str((dt - EPOCH) // SECOND)
    except Exception:
        return ""
