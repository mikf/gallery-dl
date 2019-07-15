# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader modules"""

import importlib

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

    klass = None
    if scheme == "https":
        scheme = "http"
    if scheme in modules:  # prevent unwanted imports
        try:
            module = importlib.import_module("." + scheme, __package__)
        except ImportError:
            pass
        else:
            klass = module.__downloader__

    if scheme == "http":
        _cache["http"] = _cache["https"] = klass
    else:
        _cache[scheme] = klass
    return klass


# --------------------------------------------------------------------
# internals

_cache = {}
