# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import rule34us


__tests__ = (
{
    "#url"     : "https://rule34.us/index.php?r=posts/index&q=[terios]_elysion",
    "#category": ("booru", "rule34us", "tag"),
    "#class"   : rule34us.Rule34usTagExtractor,
    "#pattern" : r"https://img\d*\.rule34\.us/images/../../[0-9a-f]{32}\.\w+",
    "#count"   : 10,

    "search_tags": "[terios]_elysion",
},

{
    "#url"     : "https://rule34.us/index.php?r=posts/index&q=",
    "#comment" : "empty 'q' query parameter (#8546)",
    "#category": ("booru", "rule34us", "tag"),
    "#class"   : rule34us.Rule34usTagExtractor,
},

{
    "#url"     : "https://rule34.us/index.php?r=posts/view&id=3709005",
    "#category": ("booru", "rule34us", "post"),
    "#class"   : rule34us.Rule34usPostExtractor,
    "#pattern"     : r"https://img\d*\.rule34\.us/images/14/7b/147bee6fc2e13f73f5f9bac9d4930b13\.png",
    "#sha1_content": "d714342ea84050f82dda5f0c194d677337abafc5",
},

{
    "#url"     : "https://rule34.us/index.php?r=posts/view&id=4576310",
    "#category": ("booru", "rule34us", "post"),
    "#class"   : rule34us.Rule34usPostExtractor,
    "#results" : "https://video.rule34.us/images/a2/94/a294ff8e1f8e0efa041e5dc9d1480011.mp4",

    "_fallback"    : ("https://video-cdn1.rule34.us/images/a2/94/a294ff8e1f8e0efa041e5dc9d1480011.mp4",),
    "extension"    : "mp4",
    "file_url"     : str,
    "filename"     : "a294ff8e1f8e0efa041e5dc9d1480011",
    "height"       : "3982",
    "id"           : "4576310",
    "md5"          : "a294ff8e1f8e0efa041e5dc9d1480011",
    "score"        : r"re:\d+",
    "tags"         : "tagme, video",
    "tags_general" : "video",
    "tags_metadata": "tagme",
    "uploader"     : "Anonymous",
    "width"        : "3184",
},

)
