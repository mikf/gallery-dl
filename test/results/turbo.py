# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import turbo


__tests__ = (
{
    "#url"  : "https://turbo.cr/a/2c5iuWHTumH",
    "#class": turbo.TurboAlbumExtractor,
    "#comment" : "turbovid' album",
    "album_id"   : "2c5iuWHTumH",
    "album_name" : "animations",
    "album_size" : 37083862,
    "count"      : 2,
    # "date"       : "type:datetime",
    "description": "Descriptions can contain only alphanumeric ASCII characters",
    "extension"  : "mp4",
    "filename"   : {"3b125e3fb4b98693f17d85cb53590215",
                    "3b1ccebf3576f8d5aac3ee0e5a12da95"},
    "id"         : {"ze10Ohbpoy5",
                    "6lC7mKrJst8"},
},

{
    "#url"     : "https://turbovid.cr/a/FiphGijfJoR",
    "#comment" : "'turbovid' album (#8851)",
    "#category": ("extractor", "turbo", "album"),
    "#class"   : turbo.TurboAlbumExtractor,
    # "#results" : (
    #     "https://data.saint2.cr/data/jZqe1xxqw9bX7.mp4",
    #     "https://data.saint2.cr/data/eJ9fLurGdaHqS.mp4",
    #     "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",
    # ),

    "album_id"   : "FiphGijfJoR",
    "album_name" : """test-???-"&> album""",
    "album_size" : 37165256,
    "count"      : 3,
    # "date"       : None,
    "description": """test-???-"&> description""",
    "extension"  : "mp4",
    # "file"       : r"re:https://data.saint2.cr/data/\w+.mp4",
    "filename"   : str,
    "id"         : str,
    "size"       : int,
},

{
    "#url"     : "https://turbo.cr/a/FiphGijfJoR",
    "#comment" : "'turbo' album (#8888)",
    "#class"   : turbo.TurboAlbumExtractor,
},

{
    "#url"     : "https://turbovid.cr/embed/WkD7hRaHdBpBI",
    "#comment" : "'turbovid' URL/video",
    "#category": ("extractor", "turbo", "media"),
    "#class"   : turbo.TurboMediaExtractor,
    # "#results" : "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",
    # "date"       : None,
    "extension"  : "mp4",
    # "file"       : "https://data.saint2.cr/data/WkD7hRaHdBpBI.mp4",
    "filename"   : "WkD7hRaHdBpBI",
    "id"         : "WkD7hRaHdBpBI",
    # "name"       : "WkD7hRaHdBpBI",
},

{
    "#url"     : "https://turbo.cr/embed/WkD7hRaHdBpBI",
    "#comment" : "'turbo' URL/video",
    "#class"   : turbo.TurboMediaExtractor,
},

)
