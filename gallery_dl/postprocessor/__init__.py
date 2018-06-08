# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import importlib
import logging

log = logging.getLogger("postprocessor")


def find(name):
    """Return a postprocessor class with the given name"""
    try:
        return _cache[name]
    except KeyError:
        try:
            module = importlib.import_module("."+name, __package__)
            cls = module.__postprocessor__
            _cache[name] = cls
            return cls
        except (ImportError, AttributeError):
            return None


# --------------------------------------------------------------------
# internals

_cache = {}
