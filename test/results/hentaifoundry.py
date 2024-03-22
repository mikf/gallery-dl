# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaifoundry
import datetime


__tests__ = (
{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/profile",
    "#category": ("", "hentaifoundry", "user"),
    "#class"   : hentaifoundry.HentaifoundryUserExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura",
    "#category": ("", "hentaifoundry", "pictures"),
    "#class"   : hentaifoundry.HentaifoundryPicturesExtractor,
    "#sha1_url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/page/3",
    "#category": ("", "hentaifoundry", "pictures"),
    "#class"   : hentaifoundry.HentaifoundryPicturesExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Ethevian/scraps",
    "#category": ("", "hentaifoundry", "scraps"),
    "#class"   : hentaifoundry.HentaifoundryScrapsExtractor,
    "#pattern" : r"https://pictures\.hentai-foundry\.com/e/Ethevian/.+",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps/page/3",
    "#category": ("", "hentaifoundry", "scraps"),
    "#class"   : hentaifoundry.HentaifoundryScrapsExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/faves/pictures",
    "#category": ("", "hentaifoundry", "favorite"),
    "#class"   : hentaifoundry.HentaifoundryFavoriteExtractor,
    "#sha1_url": "56f9ae2e89fe855e9fe1da9b81e5ec6212b0320b",
},

{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/faves/pictures/page/3",
    "#category": ("", "hentaifoundry", "favorite"),
    "#class"   : hentaifoundry.HentaifoundryFavoriteExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/recent/2018-09-20",
    "#category": ("", "hentaifoundry", "recent"),
    "#class"   : hentaifoundry.HentaifoundryRecentExtractor,
    "#pattern" : r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
    "#range"   : "20-30",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/popular",
    "#category": ("", "hentaifoundry", "popular"),
    "#class"   : hentaifoundry.HentaifoundryPopularExtractor,
    "#pattern" : r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
    "#range"   : "20-30",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/407501/shimakaze",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#sha1_url"    : "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
    "#sha1_content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",

    "artist"     : "Tenpura",
    "date"       : "dt:2016-02-22 14:41:19",
    "description": "Thank you!",
    "height"     : 700,
    "index"      : 407501,
    "media"      : "Other digital art",
    "ratings"    : [
        "Sexual content",
        "Contains female nudity",
    ],
    "score"      : int,
    "tags"       : [
        "collection",
        "kancolle",
        "kantai",
        "shimakaze",
    ],
    "title"      : "shimakaze",
    "user"       : "Tenpura",
    "views"      : int,
    "width"      : 495,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Soloid/186714/Osaloop",
    "#comment" : "SWF / rumble embed (#4641)",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#urls"    : "https://pictures.hentai-foundry.com/s/Soloid/186714/Soloid-186714-Osaloop.swf",

    "artist"     : "Soloid",
    "date"       : "dt:2013-02-07 17:25:54",
    "description": "It took me ages.\nI hope you'll like it.\nSorry for the bad quality, I made it on after effect because Flash works like shit when you have 44 layers to animate, and the final ae SWF file is 55mo big.",
    "extension"  : "swf",
    "filename"   : "Soloid-186714-Osaloop",
    "height"     : 768,
    "index"      : 186714,
    "media"      : "Digital drawing or painting",
    "ratings"    : [
        "Nudity",
        "Sexual content",
        "Contains female nudity",
    ],
    "score"      : range(80, 120),
    "src"        : "https://pictures.hentai-foundry.com/s/Soloid/186714/Soloid-186714-Osaloop.swf",
    "tags"       : [
        "soloid",
    ],
    "title"      : "Osaloop",
    "user"       : "Soloid",
    "views"      : range(45000, 60000),
    "width"      : 613,
},

{
    "#url"     : "http://www.hentai-foundry.com/pictures/user/Tenpura/407501/",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#pattern" : "http://pictures.hentai-foundry.com/t/Tenpura/407501/",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/407501/",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
},

{
    "#url"     : "https://pictures.hentai-foundry.com/t/Tenpura/407501/Tenpura-407501-shimakaze.png",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/stories/user/SnowWolf35",
    "#category": ("", "hentaifoundry", "stories"),
    "#class"   : hentaifoundry.HentaifoundryStoriesExtractor,
    "#count"   : ">= 35",

    "author"     : "SnowWolf35",
    "chapters"   : int,
    "comments"   : int,
    "date"       : datetime.datetime,
    "description": str,
    "index"      : int,
    "rating"     : int,
    "ratings"    : list,
    "status"     : r"re:(Inc|C)omplete",
    "title"      : str,
    "user"       : "SnowWolf35",
    "views"      : int,
    "words"      : int,
},

{
    "#url"     : "https://www.hentai-foundry.com/stories/user/SnowWolf35/26416/Overwatch-High-Chapter-Voting-Location",
    "#category": ("", "hentaifoundry", "story"),
    "#class"   : hentaifoundry.HentaifoundryStoryExtractor,
    "#sha1_url": "5a67cfa8c3bf7634c8af8485dd07c1ea74ee0ae8",

    "title": "Overwatch High Chapter Voting Location",
},

)
