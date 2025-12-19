# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
from ..text import re_compile

modules = [
    "2ch",
    "2chan",
    "2chen",
    "35photo",
    "3dbooru",
    "4chan",
    "4archive",
    "4chanarchives",
    "500px",
    "8chan",
    "8muses",
    "adultempire",
    "agnph",
    "ao3",
    "arcalive",
    "architizer",
    "arena",
    "artstation",
    "aryion",
    "audiochan",
    "batoto",
    "bbc",
    "behance",
    "bellazon",
    "bilibili",
    "blogger",
    "bluesky",
    "boosty",
    "booth",
    "bunkr",
    "catbox",
    "cfake",
    "chevereto",
    "cien",
    "civitai",
    "comedywildlifephoto",
    "comick",
    "comicvine",
    "cyberdrop",
    "cyberfile",
    "danbooru",
    "dandadan",
    "dankefuerslesen",
    "desktopography",
    "deviantart",
    "discord",
    "dynastyscans",
    "e621",
    "eporner",
    "erome",
    "everia",
    "exhentai",
    "facebook",
    "fanbox",
    "fansly",
    "fantia",
    "fapello",
    "fapachi",
    "fikfap",
    "fitnakedgirls",
    "flickr",
    "furaffinity",
    "furry34",
    "fuskator",
    "gelbooru",
    "gelbooru_v01",
    "gelbooru_v02",
    "girlsreleased",
    "girlswithmuscle",
    "gofile",
    "hatenablog",
    "hdoujin",
    "hentai2read",
    "hentaicosplays",
    "hentaifoundry",
    "hentaihand",
    "hentaihere",
    "hentainexus",
    "hiperdex",
    "hitomi",
    "hotleak",
    "idolcomplex",
    "imagebam",
    "imagechest",
    "imagefap",
    "imgbb",
    "imgbox",
    "imgpile",
    "imgth",
    "imgur",
    "imhentai",
    "inkbunny",
    "instagram",
    "issuu",
    "itaku",
    "itchio",
    "iwara",
    "jschan",
    "kabeuchi",
    "keenspot",
    "kemono",
    "khinsider",
    "komikcast",
    "koofr",
    "leakgallery",
    "lensdump",
    "lexica",
    "lightroom",
    "livedoor",
    "lofter",
    "luscious",
    "lynxchan",
    "madokami",
    "mangadex",
    "mangafire",
    "mangafox",
    "mangahere",
    "manganelo",
    "mangapark",
    "mangaread",
    "mangareader",
    "mangataro",
    "mangoxo",
    "misskey",
    "motherless",
    "myhentaigallery",
    "myportfolio",
    "naverblog",
    "naverchzzk",
    "naverwebtoon",
    "nekohouse",
    "newgrounds",
    "nhentai",
    "nijie",
    "nitter",
    "nozomi",
    "nsfwalbum",
    "nudostar",
    "okporn",
    "paheal",
    "patreon",
    "pexels",
    "philomena",
    "photovogue",
    "picarto",
    "picazor",
    "pictoa",
    "piczel",
    "pillowfort",
    "pinterest",
    "pixeldrain",
    "pixiv",
    "pixnet",
    "plurk",
    "poipiku",
    "poringa",
    "pornhub",
    "pornpics",
    "pornstarstube",
    "postmill",
    "rawkuma",
    "reactor",
    "readcomiconline",
    "realbooru",
    "reddit",
    "redgifs",
    "rule34us",
    "rule34vault",
    "rule34xyz",
    "s3ndpics",
    "saint",
    "sankaku",
    "sankakucomplex",
    "schalenetwork",
    "scrolller",
    "seiga",
    "senmanga",
    "sexcom",
    "shimmie2",
    "simplyhentai",
    "sizebooru",
    "skeb",
    "slickpic",
    "slideshare",
    "smugmug",
    "soundgasm",
    "speakerdeck",
    "steamgriddb",
    "subscribestar",
    "sxypix",
    "szurubooru",
    "tapas",
    "tcbscans",
    "telegraph",
    "tenor",
    "thehentaiworld",
    "tiktok",
    "tmohentai",
    "toyhouse",
    "tsumino",
    "tumblr",
    "tumblrgallery",
    "tungsten",
    "twibooru",
    "twitter",
    "urlgalleries",
    "unsplash",
    "uploadir",
    "urlshortener",
    "vanillarock",
    "vichan",
    "vipergirls",
    "vk",
    "vsco",
    "wallhaven",
    "wallpapercave",
    "warosu",
    "weasyl",
    "webmshare",
    "webtoons",
    "weebcentral",
    "weebdex",
    "weibo",
    "wikiart",
    "wikifeet",
    "wikimedia",
    "xasiat",
    "xenforo",
    "xfolio",
    "xhamster",
    "xvideos",
    "yiffverse",
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
    "noop",
    "ytdl",
    "generic",
]


def find(url):
    """Find a suitable extractor for the given URL"""
    for cls in _list_classes():
        if match := cls.pattern.match(url):
            return cls(match)
    return None


def add(cls):
    """Add 'cls' to the list of available extractors"""
    if isinstance(cls.pattern, str):
        cls.pattern = re_compile(cls.pattern)
    _cache.append(cls)
    return cls


def add_module(module):
    """Add all extractors in 'module' to the list of available extractors"""
    if classes := _get_classes(module):
        if isinstance(classes[0].pattern, str):
            for cls in classes:
                cls.pattern = re_compile(cls.pattern)
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


def _list_classes():
    """Yield available extractor classes"""
    yield from _cache

    for module in _module_iter:
        yield from add_module(module)

    globals()["_list_classes"] = lambda : _cache


def _modules_internal():
    globals_ = globals()
    for module_name in modules:
        yield __import__(module_name, globals_, None, None, 1)


def _modules_path(path, files):
    sys.path.insert(0, path)
    try:
        return [
            __import__(name[:-3])
            for name in files
            if name.endswith(".py")
        ]
    finally:
        del sys.path[0]


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [
        cls for cls in module.__dict__.values() if (
            hasattr(cls, "pattern") and cls.__module__ == module.__name__
        )
    ]


_cache = []
_module_iter = _modules_internal()
