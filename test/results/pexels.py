# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pexels


__tests__ = (
{
    "#url"     : "https://www.pexels.com/search/garden/",
    "#class"   : pexels.PexelsSearchExtractor,
    "#pattern" : r"https://images\.pexels\.com/photos/\d+/[\w-]+\.jpe?g",
    "#range"   : "1-40",
    "#count"   : 40,

    "alt"           : str,
    "aspect_ratio"  : float,
    "collection_ids": list,
    "colors"        : list,
    "created_at"    : str,
    "date"          : "type:datetime",
    "description"   : str,
    "extension"     : "jpg",
    "feed_at"       : str,
    "filename"      : r"re:pexels-[\w-]+-\d+",
    "width"         : int,
    "height"        : int,
    "id"            : int,
    "image"         : dict,
    "license"       : str,
    "liked"         : False,
    "main_color"    : "len:3",
    "pending"       : False,
    "publish_at"    : str,
    "published"     : True,
    "reactions"     : dict,
    "search_tags"   : "garden",
    "slug"          : str,
    "starred"       : bool,
    "status"        : "approved",
    "tags"          : list,
    "title"         : str,
    "type"          : "photo",
    "updated_at"    : str,
    "user"          : {
        "avatar"    : dict,
        "first_name": str,
        "following" : False,
        "hero"      : bool,
        "id"        : int,
        "last_name" : {str, None},
        "location"  : {str, None},
        "slug"      : str,
        "username"  : {str, None},
    },
},

{
    "#url"     : "https://www.pexels.com/collections/summer-solstice-j2zdph3/",
    "#class"   : pexels.PexelsCollectionExtractor,
    "#pattern" : r"https://(images\.pexels\.com/photos/\d+/[\w-]+\.jpe?g|www\.pexels\.com/download/video/\d+/)",
    "#range"   : "1-40",
    "#count"   : 40,

    "collection"   : "summer-solstice-j2zdph3",
    "collection_id": "j2zdph3",
},

{
    "#url"     : "https://www.pexels.com/@ehioma-osih-109764575",
    "#class"   : pexels.PexelsUserExtractor,
    "#pattern" : r"https://(images\.pexels\.com/photos/\d+/[\w-]+\.jpe?g|www\.pexels\.com/download/video/\d+/)",
    "#range"   : "1-40",
    "#count"   : 40,

    "user": {
        "id": 109764575,
    },
},

{
    "#url"     : "https://www.pexels.com/@azizico/",
    "#comment" : "user URL without ID",
    "#class"   : pexels.PexelsUserExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "user": {
        "id": 423972809,
    },
},

{
    "#url"     : "https://www.pexels.com/@109764575",
    "#comment" : "user URL with only ID",
    "#class"   : pexels.PexelsUserExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "user": {
        "id": 109764575,
    },
},

{
    "#url"     : "https://www.pexels.com/photo/sun-shining-between-the-trees-in-the-forest-onto-an-asphalt-road-17213600/",
    "#class"   : pexels.PexelsImageExtractor,
    "#urls"    : "https://images.pexels.com/photos/17213600/pexels-photo-17213600.jpeg",
},

)
