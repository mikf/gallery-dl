# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import importlib


def find(scheme):
    """Return downloader class suitable for handling the given scheme"""
    try:
        return _cache[scheme]
    except KeyError:
        try:
            module = importlib.import_module("."+scheme, __package__)
            klass = getattr(module, "Downloader")
            _cache[scheme] = klass
            return klass
        except ImportError:
            return None


# --------------------------------------------------------------------
# internals

_cache = {}
