# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
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
    "8kun",
    "8muses",
    "adultempire",
    "artstation",
    "aryion",
    "bcy",
    "behance",
    "blogger",
    "danbooru",
    "derpibooru",
    "deviantart",
    "dynastyscans",
    "e621",
    "exhentai",
    "fallenangels",
    "flickr",
    "furaffinity",
    "fuskator",
    "gelbooru",
    "gfycat",
    "hbrowse",
    "hentai2read",
    "hentaicafe",
    "hentaifoundry",
    "hentaifox",
    "hentaihand",
    "hentaihere",
    "hentainexus",
    "hiperdex",
    "hitomi",
    "idolcomplex",
    "imagebam",
    "imagechest",
    "imagefap",
    "imgbb",
    "imgbox",
    "imgth",
    "imgur",
    "inkbunny",
    "instagram",
    "issuu",
    "kabeuchi",
    "keenspot",
    "kemonoparty",
    "khinsider",
    "komikcast",
    "lineblog",
    "livedoor",
    "luscious",
    "mangadex",
    "mangafox",
    "mangahere",
    "mangakakalot",
    "mangapark",
    "mangareader",
    "mangastream",
    "mangoxo",
    "myhentaigallery",
    "myportfolio",
    "naver",
    "newgrounds",
    "ngomik",
    "nhentai",
    "nijie",
    "nozomi",
    "nsfwalbum",
    "paheal",
    "patreon",
    "photobucket",
    "photovogue",
    "piczel",
    "pinterest",
    "pixiv",
    "pixnet",
    "plurk",
    "pornhub",
    "pururin",
    "reactor",
    "readcomiconline",
    "reddit",
    "redgifs",
    "sankaku",
    "sankakucomplex",
    "seiga",
    "senmanga",
    "sexcom",
    "simplyhentai",
    "slickpic",
    "slideshare",
    "smugmug",
    "speakerdeck",
    "subscribestar",
    "tsumino",
    "tumblr",
    "twitter",
    "unsplash",
    "vanillarock",
    "vsco",
    "wallhaven",
    "warosu",
    "weasyl",
    "webtoons",
    "weibo",
    "wikiart",
    "xhamster",
    "xvideos",
    "yuki",
    "booru",
    "moebooru",
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
        if match:
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


# --------------------------------------------------------------------
# internals

_cache = []
_module_iter = iter(modules)


def _list_classes():
    """Yield all available extractor classes"""
    yield from _cache

    for module_name in _module_iter:
        module = importlib.import_module("."+module_name, __package__)
        yield from add_module(module)

    globals()["_list_classes"] = lambda : _cache


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        cls for cls in module.__dict__.values() if (
            hasattr(cls, "pattern") and cls.__module__ == module.__name__
        )
    ]
