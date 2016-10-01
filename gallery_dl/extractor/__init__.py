# -*- coding: utf-8 -*-

# Copyright 2015,2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import importlib
from .. import config

modules = [
    "pixiv",
    "3dbooru",
    "4chan",
    "8chan",
    "batoto",
    "chronos",
    "coreimg",
    "danbooru",
    "deviantart",
    "dokireader",
    "doujinmode",
    "dynastyscans",
    "e621",
    "exhentai",
    "gelbooru",
    "hbrowse",
    "hentai2read",
    "hentaibox",
    "hentaifoundry",
    "hitomi",
    "imagebam",
    "imagefap",
    "imagetwist",
    "imgbox",
    "imgcandy",
    "imgchili",
    "imgth",
    "imgtrex",
    "imgur",
    "imgyt",
    "khinsider",
    "kissmanga",
    "konachan",
    "luscious",
    "mangahere",
    "mangamint",
    "mangapanda",
    "mangapark",
    "mangareader",
    "mangashare",
    "mangastream",
    "nhentai",
    "nijie",
    "pinterest",
    "powermanga",
    "rule34",
    "safebooru",
    "sankaku",
    "seiga",
    "senmanga",
    "spectrumnexus",
    "tumblr",
    "turboimagehost",
    "yandere",
    "recursive",
]

def find(url):
    """Find suitable extractor for the given url"""
    for pattern, klass in _list_patterns():
        match = pattern.match(url)
        if match:
            return klass(match)
    return None

def extractors():
    """Yield all available extractor classes"""
    return sorted(
        set(klass for _, klass in _list_patterns()),
        key=lambda x: x.__name__
    )

# --------------------------------------------------------------------
# internals

_cache = []
_module_iter = iter(modules)

def _list_patterns():
    """Yield all available (pattern, class) tuples"""
    yield from _cache

    for module_name in _module_iter:
        module = importlib.import_module("."+module_name, __package__)
        tuples = [
            (re.compile(pattern), klass)
            for klass in _get_classes(module)
            for pattern in klass.pattern
        ]
        _cache.extend(tuples)
        yield from tuples

def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        klass for klass in module.__dict__.values() if (
            hasattr(klass, "pattern") and klass.__module__ == module.__name__
        )
    ]
