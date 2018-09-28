# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import importlib

modules = [
    "2chan",
    "3dbooru",
    "4chan",
    "4plebs",
    "8chan",
    "archivedmoe",
    "archiveofsins",
    "artstation",
    "b4k",
    "behance",
    "bobx",
    "danbooru",
    "desuarchive",
    "deviantart",
    "dokireader",
    "dynastyscans",
    "e621",
    "exhentai",
    "fallenangels",
    "fireden",
    "flickr",
    "gelbooru",
    "gfycat",
    "hbrowse",
    "hentai2read",
    "hentaicafe",
    "hentaifoundry",
    "hentaihere",
    "hitomi",
    "idolcomplex",
    "imagebam",
    "imagefap",
    "imgbox",
    "imgth",
    "imgur",
    "jaiminisbox",
    "khinsider",
    "kireicake",
    "kissmanga",
    "komikcast",
    "konachan",
    "luscious",
    "mangadex",
    "mangafox",
    "mangahere",
    "mangapanda",
    "mangapark",
    "mangareader",
    "mangastream",
    "myportfolio",
    "ngomik",
    "nhentai",
    "nijie",
    "nyafuu",
    "paheal",
    "pawoo",
    "piczel",
    "pinterest",
    "pixiv",
    "powermanga",
    "readcomiconline",
    "rebeccablacktech",
    "reddit",
    "rule34",
    "safebooru",
    "sankaku",
    "seaotterscans",
    "seiga",
    "senmanga",
    "sensescans",
    "simplyhentai",
    "slideshare",
    "smugmug",
    "thebarchive",
    "tumblr",
    "twitter",
    "wallhaven",
    "warosu",
    "worldthree",
    "yandere",
    "xvideos",
    "yuki",
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
        if match and klass not in _blacklist:
            return klass(match)
    return None


def add(klass):
    """Add 'klass' to the list of available extractors"""
    for pattern in klass.pattern:
        _cache.append((re.compile(pattern), klass))


def add_module(module):
    """Add all extractors in 'module' to the list of available extractors"""
    tuples = [
        (re.compile(pattern), klass)
        for klass in _get_classes(module)
        for pattern in klass.pattern
    ]
    _cache.extend(tuples)
    return tuples


def extractors():
    """Yield all available extractor classes"""
    return sorted(
        set(klass for _, klass in _list_patterns()),
        key=lambda x: x.__name__
    )


class blacklist():
    """Context Manager to blacklist extractor modules"""
    def __init__(self, categories, extractors=None):
        self.extractors = extractors or []
        for _, klass in _list_patterns():
            if klass.category in categories:
                self.extractors.append(klass)

    def __enter__(self):
        _blacklist.update(self.extractors)

    def __exit__(self, etype, value, traceback):
        _blacklist.clear()


# --------------------------------------------------------------------
# internals

_cache = []
_blacklist = set()
_module_iter = iter(modules)


def _list_patterns():
    """Yield all available (pattern, class) tuples"""
    yield from _cache

    for module_name in _module_iter:
        yield from add_module(
            importlib.import_module("."+module_name, __package__)
        )


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        klass for klass in module.__dict__.values() if (
            hasattr(klass, "pattern") and klass.__module__ == module.__name__
        )
    ]
