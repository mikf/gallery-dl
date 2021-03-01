# -*- coding: utf-8 -*-

# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Post-processing modules"""

modules = [
    "classify",
    "compare",
    "exec",
    "metadata",
    "mtime",
    "ugoira",
    "zip",
]


def find(name):
    """Return a postprocessor class with the given name"""
    try:
        return _cache[name]
    except KeyError:
        pass

    cls = None
    if name in modules:  # prevent unwanted imports
        try:
            module = __import__(name, globals(), None, (), 1)
        except ImportError:
            pass
        else:
            cls = module.__postprocessor__
    _cache[name] = cls
    return cls


# --------------------------------------------------------------------
# internals

_cache = {}
