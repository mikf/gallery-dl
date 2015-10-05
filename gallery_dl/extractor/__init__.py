# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import importlib
from .. import config

modules = [
    "pixiv",
    # "exhentai",
    "gelbooru",
    "3dbooru",
    "4chan",
    "8chan",
    "batoto",
    "danbooru",
    "deviantart",
    "e621",
    "imagebam",
    "imgbox",
    "imgchili",
    "mangareader",
    "nijie",
    "redhawkscans",
    "yandere",
]

def find(url):
    """Find extractor suitable for handling the given url"""
    for pattern, module, klass in _list_patterns():
        match = re.match(pattern, url)
        if match:
            return klass(match), module.info

# --------------------------------------------------------------------
# internals

_cache = []
_module_iter = iter(modules)

def _list_patterns():
    """Yield all available (pattern, module, klass) tuples"""
    for entry in _cache:
        yield entry

    for module_name in _module_iter:
        module = importlib.import_module("."+module_name, __package__)
        klass = getattr(module, module.info["extractor"])
        userpatterns = config.get(("extractor", module_name, "pattern"), default=[])
        for pattern in userpatterns + module.info["pattern"]:
            etuple = (pattern, module, klass)
            _cache.append(etuple)
            yield etuple
