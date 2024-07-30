# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import agnph


__tests__ = (
{
    "#url"     : "https://agn.ph/gallery/post/?search=azuu",
    "#category": ("booru", "agnph", "tag"),
    "#class"   : agnph.AgnphTagExtractor,
    "#pattern" : r"http://agn\.ph/gallery/data/../../\w{32}\.jpg",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://agn.ph/gallery/post/show/501604/",
    "#category": ("booru", "agnph", "post"),
    "#class"   : agnph.AgnphPostExtractor,
    "#options" : {"tags": True},
    "#urls"        : "http://agn.ph/gallery/data/7d/a5/7da50021f3e86f6cf1c215652060d772.png",
    "#sha1_content": "93c8b2d3f53e891ad8fa68d5f60f8c7a70acd836",

    "artist"      : "reyn_goldfur",
    "created_at"  : "1722041591",
    "creator_id"  : "-1",
    "date"        : "dt:2024-07-27 00:53:11",
    "description" : None,
    "fav_count"   : "0",
    "file_ext"    : "png",
    "file_url"    : "http://agn.ph/gallery/data/7d/a5/7da50021f3e86f6cf1c215652060d772.png",
    "has_children": False,
    "height"      : "1000",
    "id"          : "501604",
    "md5"         : "7da50021f3e86f6cf1c215652060d772",
    "num_comments": "0",
    "parent_id"   : None,
    "rating"      : "e",
    "source"      : "https://inkbunny.net/s/2886519",
    "status"      : "approved",
    "tags"        : "anthro female hisuian_sneasel regional_form reyn_goldfur shelly_the_sneasel sneasel solo",
    "tags_artist" : "reyn_goldfur",
    "tags_character": "shelly_the_sneasel",
    "tags_general": "anthro female solo",
    "tags_species": "hisuian_sneasel regional_form sneasel",
    "thumbnail_url": "http://agn.ph/gallery/data/thumb/7d/a5/7da50021f3e86f6cf1c215652060d772.png",
    "width"       : "953",

},

)
