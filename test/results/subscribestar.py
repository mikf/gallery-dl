# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import subscribestar
import datetime


__tests__ = (
{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#pattern" : r"https://(www\.subscribestar\.com/uploads\?payload=.+|(ss-uploads-prod\.b-cdn|\w+\.cloudfront)\.net/uploads(_v2)?/users/11/)",
    "#count"   : range(15, 25),

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : str,
    "date"       : datetime.datetime,
    "id"         : int,
    "num"        : int,
    "post_id"    : int,
    "tags"       : list,
    "title"      : str,
    "type"       : r"re:image|video|attachment",
    "url"        : str,
    "?pinned"    : bool,
},

{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#options" : {"metadata": True},
    "#range"   : "1",

    "date": datetime.datetime,
},

{
    "#url"     : "https://subscribestar.adult/kanashiipanda",
    "#category": ("", "subscribestar", "user-adult"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#auth"    : True,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.subscribestar.com/posts/102468",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#count"   : 1,

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : r"re:<h1>Brand Guidelines and Assets</h1>",
    "date"       : "dt:2020-05-07 12:33:00",
    "extension"  : "jpg",
    "filename"   : "8ff61299-b249-47dc-880a-cdacc9081c62",
    "group"      : "imgs_and_videos",
    "height"     : 291,
    "id"         : 203885,
    "num"        : 1,
    "pinned"     : False,
    "post_id"    : 102468,
    "tags"       : [],
    "title"      : "Brand Guidelines and Assets",
    "type"       : "image",
    "width"      : 700,
},

{
    "#url"     : "https://www.subscribestar.com/posts/920015",
    "#comment" : "attachment (#6721)",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#range"   : "2",
    "#pattern" : r"https://ss-uploads-prod\.b-cdn\.net/uploads_v2/users/11/posts/920015/bc018a55-9668-47f4-a664-b5fd66b56aaa\.pdf",

    "date"     : "dt:2023-05-30 09:20:00",
    "extension": "pdf",
    "filename" : "Training for freelancers - Fiverr",
    "id"       : 1957727,
    "name"     : "Training for freelancers - Fiverr.pdf",
    "num"      : 2,
    "post_id"  : 920015,
    "title"    : "",
    "type"     : "attachment",
},

{
    "#url"     : "https://www.subscribestar.com/posts/1851025",
    "#comment" : "content / title not inside <body> (#7486)",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,

    "author_id"  : 581352,
    "author_name": "inelia-benz",
    "author_nick": "Inelia Benz",
    "content"    : "<h1>Listening to Sasquatch - Driving to the Rez - Episode 243 - Part One</h1>\n\n<p>Topics we cover:</p>\n\n<p>Tree breaks, Foot stomps, Tracks and trackways, Hoots/calls with answers, \nTree structures, nests, Portal Cracks, Shapeshifting, Shimmer/invisibility \ncloaking, direct physical interaction inside the cloaking field, manipulation \nof canoe while we are in it, face to face interactions with multiple individuals \nteen aged and adult, male and female, cloaked and not cloaked, \nand vocalizations like drops of water. Truly amazing stories.</p>\n\n<p><a href=\"https://www.subscribestar.com/posts/1853792\" data-href=\"https://www.subscribestar.com/posts/1853792\">Go To Part Two</a></p>\n\n<p><a href=\"/away?url=aHR0cHM6Ly92aWRlby5pbmVsaWFiZW56LmNvbS9saXN0ZW5pbmctdG8tc2Fz%0AcXVhdGNoLWRyaXZpbmctdG8tdGhlLXJlei1lcGlzb2RlLTI0My1wYXJ0LW9u%0AZQ==%0A\" data-href=\"https://video.ineliabenz.com/listening-to-sasquatch-driving-to-the-rez-episode-243-part-one\">Watch the Video</a></p>\n\n<p><a href=\"/away?url=aHR0cHM6Ly9pbmVsaWEuc3Vic3RhY2suY29tL3AvbGlzdGVuaW5nLXRvLXNh%0Ac3F1YXRjaA==%0A\" data-href=\"https://inelia.substack.com/p/listening-to-sasquatch\">Read the article</a></p>\n\n<p>Audio is attached to this post.</p>",
    "date"       : "dt:2025-05-07 13:23:00",
    "extension"  : {"mp3", "jpg"},
    "filename"   : {"dttr-243-sasquatch-part1", "38cba130-3a31-4d8d-b326-7e5d3704801f"},
    "id"         : {0, 4627253},
    "num"        : range(1, 2),
    "post_id"    : 1851025,
    "tags"       : [],
    "title"      : "Listening to Sasquatch - Driving to the Rez - Episode 243 - Part One",
    "type"       : {"audio", "image"},
},

{
    "#url"     : "https://subscribestar.adult/posts/22950",
    "#category": ("", "subscribestar", "post-adult"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#auth"    : True,
    "#count"   : 1,

    "date": "dt:2019-04-28 07:32:00",
},

)
