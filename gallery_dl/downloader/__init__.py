# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader modules"""

modules = [
    "http",
    "text",
    "ytdl",
]


def find(scheme):
    """Return downloader class suitable for handling the given scheme"""
    try:
        return _cache[scheme]
    except KeyError:
        pass

    cls = None
    if scheme == "https":
        scheme = "http"
    if scheme in modules:  # prevent unwanted imports
        try:
            module = __import__(scheme, globals(), None, (), 1)
        except ImportError:
            pass
        else:
            cls = module.__downloader__

    if scheme == "http":
        _cache["http"] = _cache["https"] = cls
    else:
        _cache[scheme] = cls
    return cls


# --------------------------------------------------------------------
# internals

_cache = {}
