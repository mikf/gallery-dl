# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Post-processing modules"""

import importlib
import logging

modules = [
    "classify",
    "exec",
    "metadata",
    "mtime",
    "ugoira",
    "zip",
]

log = logging.getLogger("postprocessor")


def find(name):
    """Return a postprocessor class with the given name"""
    try:
        return _cache[name]
    except KeyError:
        pass

    klass = None
    if name in modules:  # prevent unwanted imports
        try:
            module = importlib.import_module("." + name, __package__)
        except ImportError:
            pass
        else:
            klass = module.__postprocessor__
    _cache[name] = klass
    return klass


# --------------------------------------------------------------------
# internals

_cache = {}
