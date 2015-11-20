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
    "exhentai",
    "gelbooru",
    "3dbooru",
    "4chan",
    "8chan",
    "batoto",
    "danbooru",
    "deviantart",
    "e621",
    "hbrowse",
    "hentaifoundry",
    "hitomi",
    "imagebam",
    "imgbox",
    "imgchili",
    "imgth",
    "imgur",
    "kissmanga",
    "konachan",
    "mangapanda",
    "mangareader",
    "mangashare",
    "mangastream",
    "nhentai",
    "nijie",
    "powermanga",
    "redhawkscans",
    "safebooru",
    "sankaku",
    "spectrumnexus",
    "yandere",
]

def find(url):
    """Find extractor suitable for handling the given url"""
    for pattern, info, klass in _list_patterns():
        match = re.match(pattern, url)
        if match:
            return klass(match)
    return None

# --------------------------------------------------------------------
# internals

_cache = []
_module_iter = iter(modules)

def _list_patterns():
    """Yield all available (pattern, info, class) tuples"""
    for entry in _cache:
        yield entry

    for module_name in _module_iter:
        module = importlib.import_module("."+module_name, __package__)
        try:
            klass = getattr(module, module.info["extractor"])
            userpatterns = config.get(("extractor", module_name, "pattern"), default=[])
            for pattern in userpatterns + module.info["pattern"]:
                etuple = (pattern, module.info, klass)
                _cache.append(etuple)
                yield etuple
        except AttributeError:
            for klass in _get_classes(module):
                for pattern in klass.pattern:
                    etuple = (pattern, klass.info, klass)
                    _cache.append(etuple)
                    yield etuple

def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        klass for klass in module.__dict__.values() if (
            hasattr(klass, "pattern") and klass.__module__ == module.__name__
        )
    ]
