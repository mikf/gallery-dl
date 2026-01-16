# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import saint


__tests__ = (
{
    "#url"  : "https://saint2.su/a/2c5iuWHTumH",
    "#class": saint.SaintAlbumExtractor,
    "#results": (
        "https://data.saint2.cr/data/3b1ccebf3576f8d5aac3ee0e5a12da95.mp4",
        "https://data.saint2.cr/data/3b125e3fb4b98693f17d85cb53590215.mp4",
    ),

    "album_id"   : "2c5iuWHTumH",
    "album_name" : "animations",
    "album_size" : 37083862,
    "count"      : 2,
    "date"       : "type:datetime",
    "description": "Descriptions can contain only alphanumeric ASCII characters",
    "extension"  : "mp4",
    "file"       : r"re:https://...",
    "filename"   : {"3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8",
                    "3b125e3fb4b98693f17d85cb53590215-ze10Ohbpoy5"},
    "id"         : {"6lC7mKrJst8",
                    "ze10Ohbpoy5"},
    "id2"        : {"6712834015d67",
                    "671284a627e0e"},
    "id_dl"      : {"M2IxY2NlYmYzNTc2ZjhkNWFhYzNlZTBlNWExMmRhOTUubXA0",
                    "M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0"},
    "name"       : {"3b1ccebf3576f8d5aac3ee0e5a12da95",
                    "3b125e3fb4b98693f17d85cb53590215"},
    "num"        : {1, 2},
},

{
    "#url"     : "https://turbovid.cr/a/FiphGijfJoR",
    "#comment" : "'turbovid' album (#8851)",
    "#category": ("lolisafe", "saint", "album"),
    "#class"   : saint.SaintAlbumExtractor,
    "#results" : (
        "https://data.saint2.cr/data/jZqe1xxqw9bX7.mp4",
        "https://data.saint2.cr/data/eJ9fLurGdaHqS.mp4",
        "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",
    ),

    "album_id"   : "FiphGijfJoR",
    "album_name" : """test-???-"&> album""",
    "album_size" : 37165256,
    "count"      : 3,
    "num"        : range(1, 3),
    "date"       : None,
    "description": """test-???-"&> description""",
    "extension"  : "mp4",
    "file"       : r"re:https://data.saint2.cr/data/\w+.mp4",
    "filename"   : str,
    "id"         : str,
    "id2"        : str,
    "id_dl"      : str,
    "name"       : str,
    "size"       : int,
},

{
    "#url"     : "https://turbo.cr/a/FiphGijfJoR",
    "#comment" : "'turbo' album (#8888)",
    "#class"   : saint.SaintAlbumExtractor,
},

{
    "#url"  : "https://saint2.su/embed/6lC7mKrJst8",
    "#class": saint.SaintMediaExtractor,
    "#results"     : "https://data.saint2.cr/data/3b1ccebf3576f8d5aac3ee0e5a12da95.mp4",
    "#sha1_content": "39037a029b3fe96f838b4545316caaa545c84075",

    "count"    : 1,
    "date"     : "dt:2024-10-18 15:48:16",
    "extension": "mp4",
    "file"     : str,
    "filename" : "3b1ccebf3576f8d5aac3ee0e5a12da95-6lC7mKrJst8",
    "id"       : "6lC7mKrJst8",
    "id2"      : "6712834015d67",
    "id_dl"    : "M2IxY2NlYmYzNTc2ZjhkNWFhYzNlZTBlNWExMmRhOTUubXA0",
    "name"     : "3b1ccebf3576f8d5aac3ee0e5a12da95",
    "num"      : 1,
},

{
    "#url"  : "https://saint2.su/d/M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "#class": saint.SaintMediaExtractor,
    "#results": "https://data.saint2.cr/data/3b125e3fb4b98693f17d85cb53590215.mp4",

    "count"    : 1,
    "extension": "mp4",
    "file"     : str,
    "filename" : "M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "id"       : "M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "id_dl"    : "M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "name"     : "M2IxMjVlM2ZiNGI5ODY5M2YxN2Q4NWNiNTM1OTAyMTUubXA0",
    "num"      : 1,
},

{
    "#url"  : "https://saint2.pk/embed/6lC7mKrJst8",
    "#class": saint.SaintMediaExtractor,
},

{
    "#url"  : "https://saint2.cr/embed/6lC7mKrJst8",
    "#class": saint.SaintMediaExtractor,
},

{
    "#url"  : "https://saint.to/embed/6lC7mKrJst8",
    "#class": saint.SaintMediaExtractor,
},

{
    "#url"     : "https://turbovid.cr/embed/WkD7hRaHdBpBI",
    "#comment" : "'turbovid' URL/video",
    "#category": ("lolisafe", "saint", "media"),
    "#class"   : saint.SaintMediaExtractor,
    "#results" : "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",

    "date"       : None,
    "extension"  : "mp4",
    "file"       : "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",
    "filename"   : "WkD7hRaHdBpBI",
    "id"         : "WkD7hRaHdBpBI",
    "id2"        : "WkD7hRaHdBpBI",
    "id_dl"      : "V2tEN2hSYUhkQnBCSS5tcDQ=",
    "name"       : "WkD7hRaHdBpBI",
},

{
    "#url"     : "https://turbo.cr/embed/WkD7hRaHdBpBI",
    "#comment" : "'turbo' URL/video",
    "#class"   : saint.SaintMediaExtractor,
},

)
