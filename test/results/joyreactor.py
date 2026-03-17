# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import joyreactor


__tests__ = (
{
    "#url"     : "http://joyreactor.com/post/3721876",
    "#comment" : "single image",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#results" : "https://img2.joyreactor.com/pics/post/full/cartoon-painting-monster-4841316.jpeg",

    "count"    : 1,
    "num"      : 1,
    "date"     : "dt:2018-11-18 20:31:00",
    "extension": "jpeg",
    "file_id"  : "4841316",
    "file_url" : "https://img2.joyreactor.com/pics/post/full/cartoon-painting-monster-4841316.jpeg",
    "filename" : "cartoon-painting-monster-4841316",
    "post_id"  : "3721876",
    "type"     : "image",
    "user"     : "alcortje",
    "user_id"  : "300202",
    "content"  : str,
    "tags"     : [
        "cartoon",
        "painting",
        "monster",
        "lake",
    ],
},



{
    "#url"     : "http://joyreactor.com/post/3713804",
    "#comment" : "4 images",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#results" : (
        "https://img2.joyreactor.com/pics/post/full/movie-tv-godzilla-4827689.jpeg",
        "https://img2.joyreactor.com/pics/post/full/movie-tv-godzilla-4827690.jpeg",
        "https://img2.joyreactor.com/pics/post/full/movie-tv-godzilla-4827691.jpeg",
        "https://img2.joyreactor.com/pics/post/full/movie-tv-godzilla-4827692.jpeg",
    ),

    "count"    : 4,
    "num"      : range(1, 4),
    "date"     : "dt:2018-11-12 18:17:00",
    "extension": "jpeg",
    "file_id"  : r"re:48276[89]\d",
    "file_url" : r"re:https://img2.joyreactor.com/pics/post/full/movie-tv-godzilla-48276\d+\.jpeg",
    "filename" : r"re:movie-tv-godzilla-48276\d+",
    "post_id"  : "3713804",
    "type"     : "image",
    "user"     : "alcortje",
    "user_id"  : "300202",
    "content"  : str,
    "tags"     : [
        "movie",
        "tv",
        "godzilla",
        "monsters",
        "back drop",
        "movie set",
    ],
},

{
    "#url"     : "http://joyreactor.com/post/3726210",
    "#comment" : "video",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#results" : "https://img2.joyreactor.com/pics/post/webm/hose-firefighters-cool-4848292.webm",

    "count"    : 1,
    "date"     : "dt:2018-11-22 09:08:00",
    "extension": "webm",
    "file_id"  : "4848292",
    "file_url" : "https://img2.joyreactor.com/pics/post/webm/hose-firefighters-cool-4848292.webm",
    "filename" : "hose-firefighters-cool-4848292",
    "format"   : "webm",
    "num"      : 1,
    "post_id"  : "3726210",
    "type"     : "video",
    "user"     : "DeadWhale",
    "user_id"  : "41786",
    "tags"     : [
        "hose",
        "firefighters",
        "cool",
        "gif",
        "gadget",
    ],
},

{
    "#url"     : "http://joyreactor.com/post/3726210",
    "#comment" : "'format' option",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#options" : {"format": "mp4,gif"},
    "#results" : (
        "https://img2.joyreactor.com/pics/post/mp4/hose-firefighters-cool-4848292.mp4",
        "https://img2.joyreactor.com/pics/post/gif/hose-firefighters-cool-4848292.gif",
    ),

    "count"    : 2,
    "format"   : {"mp4", "gif"},
    "extension": {"mp4", "gif"},
    "filename" : "hose-firefighters-cool-4848292",
    "file_id"  : "4848292",
},

{
    "#url"     : "http://joyreactor.com/post/3668724",
    "#comment" : "youtube embed",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#options" : {"embeds": True},
    "#results" : "ytdl:https://www.youtube.com/embed/-hwv_v6ObnA?wmode=transparent&amp;rel=0",

    "count"    : 1,
    "date"     : "dt:2018-10-07 14:26:00",
    "extension": "",
    "file_id"  : "hwv_v6ObnA",
    "file_url" : "ytdl:https://www.youtube.com/embed/-hwv_v6ObnA?wmode=transparent&amp;rel=0",
    "filename" : "-hwv_v6ObnA",
    "num"      : 1,
    "post_id"  : "3668724",
    "tags"     : [],
    "type"     : "embed",
    "user"     : "pux0073",
    "user_id"  : "447567",
},

{
    "#url"     : "http://joyreactor.com/post/3668724",
    "#comment" : "youtube embed default",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://joyreactor.cc/post/6279901",
    "#comment" : "'.cc' TLD",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : joyreactor.JoyreactorPostExtractor,
    "#results" : "https://img2.joyreactor.cc/pics/post/full/fasnakegod-Anime-Artist-artist-9294962.jpeg",

    "date"     : "dt:2026-03-14 06:28:00",
    "extension": "jpeg",
    "file_id"  : "9294962",
    "file_url" : "https://img2.joyreactor.cc/pics/post/full/fasnakegod-Anime-Artist-artist-9294962.jpeg",
    "filename" : "fasnakegod-Anime-Artist-artist-9294962",
    "post_id"  : "6279901",
    "type"     : "image",
    "user"     : "kotelnique",
    "user_id"  : "1038132",
    "tags"     : [
        "fasnakegod",
        "Anime Artist",
        "artist",
        "Shameimaru Aya",
        "Touhou Project",
        "Anime",
        "фэндомы",
    ],
},

{
    "#url"     : "https://joyreactor.cc/tag/Touhou Project",
    "#category": ("reactor", "joyreactor", "tag"),
    "#class"   : joyreactor.JoyreactorTagExtractor,
    "#pattern" : r"https://img\d+\.joyreactor\.cc/pics/post/full/\w+",
    "#range"   : "1-50",
    "#count"   : 50,

    "date"       : "type:datetime",
    "search_tags": "Touhou Project",
},

{
    "#url"     : "https://joyreactor.com/tag/Dark%20Souls%202/top",
    "#comment" : "'.com' TLD, 'top' results",
    "#category": ("reactor", "joyreactor", "tag"),
    "#class"   : joyreactor.JoyreactorTagExtractor,
    "#count"   : range(8, 20),

    "date"       : "type:datetime",
    "search_tags": "Dark Souls 2",
},

{
    "#url"     : "http://joyreactor.cc/search/Nature",
    "#category": ("reactor", "joyreactor", "search"),
    "#class"   : joyreactor.JoyreactorSearchExtractor,
    "#pattern" : r"https://img\d+\.joyreactor\.cc/pics/post/full/\w+",
    "#count"   : range(8, 20),

    "search_tags": "Nature",
},

{
    "#url"     : "http://joyreactor.cc/user/hemantic",
    "#category": ("reactor", "joyreactor", "user"),
    "#class"   : joyreactor.JoyreactorUserExtractor,
    "#pattern" : r"https://img\d+\.joyreactor\.cc/pics/post/full/\w+",
    "#range"   : "1-50",
    "#count"   : 11,

    "user"     : "hemantic",
    "user_id"  : "78",
},

{
    "#url"     : "http://joyreactor.com/user/Tacoman123",
    "#category": ("reactor", "joyreactor", "user"),
    "#class"   : joyreactor.JoyreactorUserExtractor,
    "#pattern" : r"https://img\d+\.joyreactor\.com/pics/post/full/\w+",
    "#range"   : "1-50",
    "#count"   : 21,

    "user"     : "Tacoman123",
    "user_id"  : "189143",
},

)
