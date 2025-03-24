# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import sys
import re

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
    "artstation",
    "aryion",
    "batoto",
    "bbc",
    "behance",
    "bilibili",
    "blogger",
    "bluesky",
    "boosty",
    "bunkr",
    "catbox",
    "chevereto",
    "cien",
    "civitai",
    "comicvine",
    "cyberdrop",
    "danbooru",
    "desktopography",
    "deviantart",
    "discord",
    "dynastyscans",
    "e621",
    "erome",
    "everia",
    "exhentai",
    "facebook",
    "fanbox",
    "fantia",
    "fapello",
    "fapachi",
    "flickr",
    "furaffinity",
    "furry34",
    "fuskator",
    "gelbooru",
    "gelbooru_v01",
    "gelbooru_v02",
    "gofile",
    "hatenablog",
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
    "imgth",
    "imgur",
    "imhentai",
    "inkbunny",
    "instagram",
    "issuu",
    "itaku",
    "itchio",
    "jschan",
    "kabeuchi",
    "keenspot",
    "kemonoparty",
    "khinsider",
    "koharu",
    "komikcast",
    "lensdump",
    "lexica",
    "lightroom",
    "livedoor",
    "lofter",
    "luscious",
    "lynxchan",
    "mangadex",
    "mangafox",
    "mangahere",
    "mangakakalot",
    "manganelo",
    "mangapark",
    "mangaread",
    "mangasee",
    "mangoxo",
    "misskey",
    "motherless",
    "myhentaigallery",
    "myportfolio",
    "naver",
    "naverwebtoon",
    "nekohouse",
    "newgrounds",
    "nhentai",
    "nijie",
    "nitter",
    "nozomi",
    "nsfwalbum",
    "paheal",
    "patreon",
    "pexels",
    "philomena",
    "photovogue",
    "picarto",
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
    "postmill",
    "reactor",
    "readcomiconline",
    "realbooru",
    "reddit",
    "redgifs",
    "rule34us",
    "rule34vault",
    "rule34xyz",
    "saint",
    "sankaku",
    "sankakucomplex",
    "scrolller",
    "seiga",
    "senmanga",
    "sexcom",
    "shimmie2",
    "simplyhentai",
    "skeb",
    "slickpic",
    "slideshare",
    "smugmug",
    "soundgasm",
    "speakerdeck",
    "steamgriddb",
    "subscribestar",
    "szurubooru",
    "tapas",
    "tcbscans",
    "telegraph",
    "tenor",
    "tiktok",
    "tmohentai",
    "toyhouse",
    "tsumino",
    "tumblr",
    "tumblrgallery",
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
    "weibo",
    "wikiart",
    "wikifeet",
    "wikimedia",
    "xfolio",
    "xhamster",
    "xvideos",
    "yiffverse",
    "zerochan",
    "zzup",
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


def _list_classes():
    """Yield available extractor classes"""
    yield from _cache

    for module in _module_iter:
        yield from add_module(module)

    globals()["_list_classes"] = lambda : _cache


def _modules_internal():
    globals_ = globals()
    for module_name in modules:
        yield __import__(module_name, globals_, None, (), 1)


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
