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

EPOCH = datetime(1970, 1, 1)
SECOND = timedelta(0, 1)


def parse_datetime(date_string, format="%Y-%m-%dT%H:%M:%S%z", utcoffset=0):
    """Create a datetime object by parsing 'date_string'"""
    try:
        d = datetime.strptime(date_string, format)
        o = d.utcoffset()
        if o is not None:
            # convert to naive UTC
            d = d.replace(tzinfo=None, microsecond=0) - o
        else:
            if d.microsecond:
                d = d.replace(microsecond=0)
            if utcoffset:
                # apply manual UTC offset
                d += timedelta(0, utcoffset * -3600)
        return d
    except (TypeError, IndexError, KeyError):
        return None
    except (ValueError, OverflowError):
        return date_string


def to_datetime(value):
    """Convert 'value' to a datetime object"""
    if not value:
        return EPOCH

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            if value[-1] == "Z":
                # compat for Python < 3.11
                value = value[:-1]
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                if dt.microsecond:
                    dt = dt.replace(microsecond=0)
            else:
                # convert to naive UTC
                dt = dt.astimezone(timezone.utc).replace(
                    microsecond=0, tzinfo=None)
            return dt
        except Exception:
            pass

    return parse_timestamp(value, EPOCH)


def datetime_to_timestamp(dt):
    """Convert naive UTC datetime to Unix timestamp"""
    return (dt - EPOCH) / SECOND


def datetime_to_timestamp_string(dt):
    """Convert naive UTC datetime to Unix timestamp string"""
    try:
        return str((dt - EPOCH) // SECOND)
    except Exception:
        return ""


if sys.hexversion < 0x30c0000:
    # Python <= 3.11
    datetime_utcfromtimestamp = datetime.utcfromtimestamp
    datetime_utcnow = datetime.utcnow
    datetime_from_timestamp = datetime_utcfromtimestamp

    def parse_timestamp(ts, default=None):
        """Create a datetime object from a Unix timestamp"""
        try:
            return datetime_utcfromtimestamp(int(ts))
        except Exception:
            return default
else:
    # Python >= 3.12
    def datetime_from_timestamp(ts=None):
        """Convert Unix timestamp to naive UTC datetime"""
        Y, m, d, H, M, S, _, _, _ = time.gmtime(ts)
        return datetime(Y, m, d, H, M, S)

    def parse_timestamp(ts, default=None):
        """Create a datetime object from a Unix timestamp"""
        try:
            return datetime_from_timestamp(int(ts))
        except Exception:
            return default

    datetime_utcfromtimestamp = datetime_from_timestamp
    datetime_utcnow = datetime_from_timestamp
