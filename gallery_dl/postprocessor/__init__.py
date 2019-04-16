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
    "ugoira",
    "zip",
]

log = logging.getLogger("postprocessor")


def find(name):
    """Return a postprocessor class with the given name"""
    try:
        return _cache[name]
    except KeyError:
        klass = None
        try:
            if name in modules:  # prevent unwanted imports
                module = importlib.import_module("." + name, __package__)
                klass = module.__postprocessor__
        except (ImportError, AttributeError, TypeError):
            pass
        _cache[name] = klass
        return klass


# --------------------------------------------------------------------
# internals

_cache = {}
