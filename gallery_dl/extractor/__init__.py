# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import re

modules = [
    "2chan",
    "2chen",
    "35photo",
    "3dbooru",
    "420chan",
    "4chan",
    "500px",
    "8chan",
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
    "bunkr",
    "catbox",
    "comicvine",
    "cyberdrop",
    "danbooru",
    "desktopography",
    "deviantart",
    "dynastyscans",
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
    "gofile",
    "hbrowse",
    "hentai2read",
    "hentaicosplays",
    "hentaifoundry",
    "hentaifox",
    "hentaihand",
    "hentaihere",
    "hiperdex",
    "hitomi",
    "hotleak",
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
    "itaku",
    "kabeuchi",
    "keenspot",
    "kemonoparty",
    "khinsider",
    "kissgoddess",
    "kohlchan",
    "komikcast",
    "lightroom",
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
    "mememuseum",
    "myhentaigallery",
    "myportfolio",
    "nana",
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
    "picarto",
    "piczel",
    "pillowfort",
    "pinterest",
    "pixiv",
    "pixnet",
    "plurk",
    "poipiku",
    "pornhub",
    "pururin",
    "reactor",
    "readcomiconline",
    "reddit",
    "redgifs",
    "rule34us",
    "sankaku",
    "sankakucomplex",
    "seiga",
    "senmanga",
    "sexcom",
    "simplyhentai",
    "skeb",
    "slickpic",
    "slideshare",
    "smugmug",
    "speakerdeck",
    "subscribestar",
    "tapas",
    "telegraph",
    "toyhouse",
    "tsumino",
    "tumblr",
    "tumblrgallery",
    "twibooru",
    "twitter",
    "unsplash",
    "vanillarock",
    "vk",
    "vsco",
    "wallhaven",
    "wallpapercave",
    "warosu",
    "weasyl",
    "webtoons",
    "weibo",
    "wikiart",
    "wikieat",
    "xhamster",
    "xvideos",
    "zerochan",
    "booru",
    "moebooru",
    "foolfuuka",
    "foolslide",
    "mastodon",
    "shopify",
    "lolisafe",
    "imagehosts",
    "directlink",
    "recursive",
    "oauth",
    "test",
    "ytdl",
    "generic",
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
