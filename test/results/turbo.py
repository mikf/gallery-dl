# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import turbo


__tests__ = (
{
    "#url"  : "https://turbo.cr/a/2c5iuWHTumH",
    "#class": turbo.TurboAlbumExtractor,
    "#pattern": (
        r"https://dl\d+.turbocdn.st/data/3b125e3fb4b98693f17d85cb53590215.mp4\?exp=\d+&token=\w+&fn=3b125e3fb4b98693f17d85cb53590215.mp4",
        r"https://dl\d+.turbocdn.st/data/3b1ccebf3576f8d5aac3ee0e5a12da95.mp4\?exp=\d+&token=\w+&fn=3b1ccebf3576f8d5aac3ee0e5a12da95.mp4",
    ),

    "album_id"   : "2c5iuWHTumH",
    "album_name" : "animations",
    "album_size" : 37083862,
    "count"      : 2,
    "description": "Descriptions can contain only alphanumeric ASCII characters",
    "extension"  : "mp4",
    "file"       : r"re:https://...",
    "filename"   : {"3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8",
                    "3b125e3fb4b98693f17d85cb53590215-ze10Ohbpoy5"},
    "id"         : {"6lC7mKrJst8",
                    "ze10Ohbpoy5"},
    "name"       : {"3b1ccebf3576f8d5aac3ee0e5a12da95",
                    "3b125e3fb4b98693f17d85cb53590215"},
    "num"        : {1, 2},
},

{
    "#url"     : "https://turbovid.cr/a/FiphGijfJoR",
    "#comment" : "'turbovid' album (#8851)",
    "#category": ("lolisafe", "turbo", "album"),
    "#class"   : turbo.TurboAlbumExtractor,
    "#pattern" : (
        r"https://dl\d+.turbocdn.st/data/WkD7hRaHdBpBI.mp4\?exp=\d+&token=\w+&fn=3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8.mp4",
        r"https://dl\d+.turbocdn.st/data/eJ9fLurGdaHqS.mp4\?exp=\d+&token=\w+&fn=3b125e3fb4b98693f17d85cb53590215-ze10Ohbpoy5.mp4",
        r"https://dl\d+.turbocdn.st/data/jZqe1xxqw9bX7.mp4\?exp=\d+&token=\w+&fn=test-%E3%83%86%E3%82%B9%E3%83%88-%2522%26%3E.mp4",
    ),

    "album_id"   : "FiphGijfJoR",
    "album_name" : """test-テスト-"&> album""",
    "album_size" : 37165256,
    "count"      : 3,
    "num"        : range(1, 3),
    "description": """test-テスト-"&> description""",
    "extension"  : "mp4",
    "file"       : r"re:https://dl\d+.turbocdn.st/data/.+",
    "filename"   : str,
    "id"         : str,
    "name"       : str,
    "size"       : int,
},

{
    "#url"     : "https://saint2.su/a/FiphGijfJoR",
    "#comment" : "'saint' album (#8888)",
    "#class"   : turbo.TurboAlbumExtractor,
},

{
    "#url"  : "https://turbo.cr/embed/6lC7mKrJst8",
    "#class": turbo.TurboMediaExtractor,
    "#pattern"     : r"https://dl\d+.turbocdn.st/data/3b1ccebf3576f8d5aac3ee0e5a12da95.mp4",
    "#sha1_content": "39037a029b3fe96f838b4545316caaa545c84075",

    "count"    : 1,
    "date"     : "dt:2024-10-18 00:00:00",
    "extension": "mp4",
    "file"     : str,
    "filename" : "3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8",
    "id"       : "6lC7mKrJst8",
    "name"     : "3b1ccebf3576f8d5aac3ee0e5a12da95",
    "num"      : 1,
},

{
    "#url"    : "https://turbo.cr/d/M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "#comment": "'Page not found'",
    "#class"  : turbo.TurboMediaExtractor,
    "#count"  : 0,
},

{
    "#url"  : "https://saint2.pk/embed/6lC7mKrJst8",
    "#class": turbo.TurboMediaExtractor,
},

{
    "#url"  : "https://saint2.cr/embed/6lC7mKrJst8",
    "#class": turbo.TurboMediaExtractor,
},

{
    "#url"  : "https://saint.to/embed/6lC7mKrJst8",
    "#class": turbo.TurboMediaExtractor,
},

{
    "#url"     : "https://turbovid.cr/embed/WkD7hRaHdBpBI",
    "#comment" : "'turbovid' URL",
    "#category": ("lolisafe", "turbo", "media"),
    "#class"   : turbo.TurboMediaExtractor,
    "#pattern" : r"https://dl\d+.turbocdn.st/data/\w+.mp4",

    "extension"  : "mp4",
    "file"       : str,
    "filename"   : "3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8-WkD7hRaHdBpBI",
    "id"         : "WkD7hRaHdBpBI",
    "name"       : "3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8",
},

{
    "#url"     : "https://saint2.su/embed/WkD7hRaHdBpBI",
    "#comment" : "'saint' URL",
    "#category": ("lolisafe", "turbo", "media"),
    "#class"   : turbo.TurboMediaExtractor,
},

{
    "#url"     : "https://turbo.cr/v/6lC7mKrJst8",
    "#comment" : "'/v/' URL",
    "#category": ("lolisafe", "turbo", "media"),
    "#class"   : turbo.TurboMediaExtractor,
},

)
