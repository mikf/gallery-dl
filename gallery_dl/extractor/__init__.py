# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re

modules = [
    "2chan",
    "35photo",
    "3dbooru",
    "420chan",
    "4chan",
    "500px",
    "8kun",
    "8muses",
    "adultempire",
    "architizer",
    "artstation",
    "aryion",
    "bbc",
    "bcy",
    "behance",
    "blogger",
    "comicvine",
    "cyberdrop",
    "danbooru",
    "desktopography",
    "deviantart",
    "dynastyscans",
    "e621",
    "erome",
    "exhentai",
    "fallenangels",
    "fanbox",
    "fantia",
    "flickr",
    "furaffinity",
    "fuskator",
    "gelbooru",
    "gelbooru_v01",
    "gelbooru_v02",
    "gfycat",
    "hbrowse",
    "hentai2read",
    "hentaicosplays",
    "hentaifoundry",
    "hentaifox",
    "hentaihand",
    "hentaihere",
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
    "manganelo",
    "mangapark",
    "mangasee",
    "mangoxo",
    "myhentaigallery",
    "myportfolio",
    "naver",
    "naverwebtoon",
    "newgrounds",
    "ngomik",
    "nhentai",
    "nijie",
    "nozomi",
    "nsfwalbum",
    "paheal",
    "patreon",
    "philomena",
    "photobucket",
    "photovogue",
    "piczel",
    "pillowfort",
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
    "seisoparty",
    "senmanga",
    "sexcom",
    "simplyhentai",
    "slickpic",
    "slideshare",
    "smugmug",
    "speakerdeck",
    "subscribestar",
    "tapas",
    "tsumino",
    "tumblr",
    "tumblrgallery",
    "twitter",
    "unsplash",
    "vanillarock",
    "vk",
    "vsco",
    "wallhaven",
    "warosu",
    "weasyl",
    "webtoons",
    "weibo",
    "wikiart",
    "wikieat",
    "xhamster",
    "xvideos",
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
    "ytdl",
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

    globals_ = globals()
    for module_name in _module_iter:
        module = __import__(module_name, globals_, None, (), 1)
        yield from add_module(module)

    globals_["_list_classes"] = lambda : _cache


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        cls for cls in module.__dict__.values() if (
            hasattr(cls, "pattern") and cls.__module__ == module.__name__
        )
    ]
