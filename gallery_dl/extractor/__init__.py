# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re
import importlib

modules = [
    "2chan",
    "35photo",
    "3dbooru",
    "4chan",
    "500px",
    "8chan",
    "artstation",
    "behance",
    "bobx",
    "danbooru",
    "deviantart",
    "dynastyscans",
    "e621",
    "exhentai",
    "fallenangels",
    "flickr",
    "gelbooru",
    "gfycat",
    "hbrowse",
    "hentai2read",
    "hentaicafe",
    "hentaifoundry",
    "hentaifox",
    "hentaihere",
    "hentainexus",
    "hitomi",
    "hypnohub",
    "idolcomplex",
    "imagebam",
    "imagefap",
    "imgbox",
    "imgth",
    "imgur",
    "instagram",
    "khinsider",
    "kissmanga",
    "komikcast",
    "konachan",
    "livedoor",
    "luscious",
    "mangadex",
    "mangafox",
    "mangahere",
    "mangapanda",
    "mangapark",
    "mangareader",
    "mangastream",
    "mangoxo",
    "myportfolio",
    "newgrounds",
    "ngomik",
    "nhentai",
    "nijie",
    "paheal",
    "patreon",
    "photobucket",
    "piczel",
    "pinterest",
    "pixiv",
    "pixnet",
    "plurk",
    "pururin",
    "reactor",
    "readcomiconline",
    "reddit",
    "rule34",
    "safebooru",
    "sankaku",
    "seiga",
    "senmanga",
    "sexcom",
    "simplyhentai",
    "slideshare",
    "smugmug",
    "tsumino",
    "tumblr",
    "twitter",
    "wallhaven",
    "warosu",
    "weibo",
    "wikiart",
    "xvideos",
    "yandere",
    "yaplog",
    "yuki",
    "foolfuuka",
    "foolslide",
    "mastodon",
    "shopify",
    "imagehosts",
    "directlink",
    "recursive",
    "oauth",
    "test",
]


def find(url):
    """Find a suitable extractor for the given URL"""
    for cls in _list_classes():
        match = cls.pattern.match(url)
        if match and cls not in _blacklist:
            return cls(match)
    return None


def add(cls):
    """Add 'cls' to the list of available extractors"""
    cls.pattern = re.compile(cls.pattern)
    _cache.append(cls)
    return cls


def add_module(module):
    """Add all extractors in 'module' to the list of available extractors"""
    classes = _get_classes(module)
    for cls in classes:
        cls.pattern = re.compile(cls.pattern)
    _cache.extend(classes)
    return classes


def extractors():
    """Yield all available extractor classes"""
    return sorted(
        _list_classes(),
        key=lambda x: x.__name__
    )


class blacklist():
    """Context Manager to blacklist extractor modules"""
    def __init__(self, categories, extractors=None):
        self.extractors = extractors or []
        for cls in _list_classes():
            if cls.category in categories:
                self.extractors.append(cls)

    def __enter__(self):
        _blacklist.update(self.extractors)

    def __exit__(self, etype, value, traceback):
        _blacklist.clear()


# --------------------------------------------------------------------
# internals

_cache = []
_blacklist = set()
_module_iter = iter(modules)


def _list_classes():
    """Yield all available extractor classes"""
    yield from _cache

    for module_name in _module_iter:
        module = importlib.import_module("."+module_name, __package__)
        yield from add_module(module)


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        cls for cls in module.__dict__.values() if (
            hasattr(cls, "pattern") and cls.__module__ == module.__name__
        )
    ]
