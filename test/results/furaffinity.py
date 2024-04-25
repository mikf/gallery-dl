# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import furaffinity


__tests__ = (
{
    "#url"     : "https://www.furaffinity.net/gallery/mirlinthloth/",
    "#category": ("", "furaffinity", "gallery"),
    "#class"   : furaffinity.FuraffinityGalleryExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/mirlinthloth/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,
},

{
    "#url"     : "https://www.furaffinity.net/scraps/mirlinthloth/",
    "#category": ("", "furaffinity", "scraps"),
    "#class"   : furaffinity.FuraffinityScrapsExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+(/stories)?/\d+/\d+.\w+.",
    "#count"   : ">= 3",
},

{
    "#url"     : "https://www.furaffinity.net/favorites/mirlinthloth/",
    "#category": ("", "furaffinity", "favorite"),
    "#class"   : furaffinity.FuraffinityFavoriteExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,

    "favorite_id": int,
},

{
    "#url"     : "https://www.furaffinity.net/search/?q=cute",
    "#category": ("", "furaffinity", "search"),
    "#class"   : furaffinity.FuraffinitySearchExtractor,
    "#pattern" : r"https://d\d?\.f(uraffinity|acdn)\.net/art/[^/]+/\d+/\d+.\w+\.\w+",
    "#range"   : "45-50",
    "#count"   : 6,
},

{
    "#url"     : "https://www.furaffinity.net/search/?q=leaf&range=1day",
    "#comment" : "first page of search results (#2402)",
    "#category": ("", "furaffinity", "search"),
    "#class"   : furaffinity.FuraffinitySearchExtractor,
    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://www.furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#pattern" : r"https://d\d*\.f(uraffinity|acdn)\.net/(download/)?art/mirlinthloth/music/1488278723/1480267446.mirlinthloth_dj_fennmink_-_bude_s_4_ever\.mp3",

    "artist"     : "mirlinthloth",
    "artist_url" : "mirlinthloth",
    "date"       : "dt:2016-11-27 17:24:06",
    "description": "A Song made playing the game Cosmic DJ.",
    "extension"  : "mp3",
    "filename"   : r"re:\d+\.\w+_dj_fennmink_-_bude_s_4_ever",
    "id"         : 21835115,
    "tags"       : list,
    "title"      : "Bude's 4 Ever",
    "url"        : r"re:https://d\d?\.f(uraffinity|acdn)\.net/art",
    "user"       : "mirlinthloth",
    "views"      : int,
    "favorites"  : int,
    "comments"   : int,
    "rating"     : "General",
    "fa_category": "Music",
    "theme"      : "All",
    "species"    : "Unspecified / Any",
    "gender"     : "Any",
    "width"      : 120,
    "height"     : 120,
},

{
    "#url"     : "https://www.furaffinity.net/view/42166511/",
    "#comment" : "'external' option (#1492)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
    "#options" : {"external": True},
    "#pattern" : r"https://d\d*\.f(uraffinity|acdn)\.net/|http://www\.postybirb\.com",
    "#count"   : 2,
},

{
    "#url"     : "https://www.furaffinity.net/view/45331225/",
    "#comment" : "no tags (#2277)",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,

    "artist"     : "Kota_Remminders",
    "artist_url" : "kotaremminders",
    "date"       : "dt:2022-01-03 17:49:33",
    "fa_category": "Adoptables",
    "filename"   : "1641232173.kotaremminders_chidopts1",
    "gender"     : "Any",
    "height"     : 905,
    "id"         : 45331225,
    "rating"     : "General",
    "species"    : "Unspecified / Any",
    "tags"       : [],
    "theme"      : "All",
    "title"      : "REMINDER",
    "width"      : 1280,
},

{
    "#url"     : "https://furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://fxfuraffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://fxraffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://sfw.furaffinity.net/view/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://www.furaffinity.net/full/21835115/",
    "#category": ("", "furaffinity", "post"),
    "#class"   : furaffinity.FuraffinityPostExtractor,
},

{
    "#url"     : "https://www.furaffinity.net/user/mirlinthloth/",
    "#category": ("", "furaffinity", "user"),
    "#class"   : furaffinity.FuraffinityUserExtractor,
    "#pattern" : "/gallery/mirlinthloth/$",
},

{
    "#url"     : "https://www.furaffinity.net/user/mirlinthloth/",
    "#category": ("", "furaffinity", "user"),
    "#class"   : furaffinity.FuraffinityUserExtractor,
    "#options" : {"include": "all"},
    "#pattern" : "/(gallery|scraps|favorites)/mirlinthloth/$",
    "#count"   : 3,
},

{
    "#url"     : "https://www.furaffinity.net/watchlist/by/mirlinthloth/",
    "#category": ("", "furaffinity", "following"),
    "#class"   : furaffinity.FuraffinityFollowingExtractor,
    "#pattern" : furaffinity.FuraffinityUserExtractor.pattern,
    "#range"   : "176-225",
    "#count"   : 50,
},

)
