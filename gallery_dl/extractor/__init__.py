# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import importlib

modules = [
    "pixiv",
    "3dbooru",
    "4chan",
    "8chan",
    "batoto",
    "danbooru",
    "deviantart",
    "dokireader",
    "dynastyscans",
    "e621",
    "exhentai",
    "fallenangels",
    "flickr",
    "gelbooru",
    "gfycat",
    "gomanga",
    "hbrowse",
    "hentai2read",
    "hentaifoundry",
    "hentaihere",
    "hitomi",
    "imagebam",
    "imagefap",
    "imgbox",
    "imgchili",
    "imgth",
    "imgur",
    "jaiminisbox",
    "khinsider",
    "kireicake",
    "kisscomic",
    "kissmanga",
    "konachan",
    "luscious",
    "mangafox",
    "mangahere",
    "mangapanda",
    "mangapark",
    "mangareader",
    "mangastream",
    "nhentai",
    "nijie",
    "pawoo",
    "pinterest",
    "powermanga",
    "readcomiconline",
    "reddit",
    "rule34",
    "safebooru",
    "sankaku",
    "seaotterscans",
    "seiga",
    "senmanga",
    "sensescans",
    "spectrumnexus",
    "tumblr",
    "twitter",
    "worldthree",
    "yandere",
    "yonkouprod",
    "imagehosts",
    "directlink",
    "recursive",
    "oauth",
    "test",
]


def find(url):
    """Find suitable extractor for the given url"""
    for pattern, klass in _list_patterns():
        match = pattern.match(url)
        if match and klass.category not in _blacklist:
            return klass(match)
    return None


def extractors():
    """Yield all available extractor classes"""
    return sorted(
        set(klass for _, klass in _list_patterns()),
        key=lambda x: x.__name__
    )


class blacklist():
    """Context Manager to blacklist extractor modules"""
    def __init__(self, categories):
        self.categories = categories

    def __enter__(self):
        _blacklist.extend(self.categories)

    def __exit__(self, etype, value, traceback):
        _blacklist.clear()


# --------------------------------------------------------------------
# internals

_cache = []
_blacklist = []
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
