# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fanbox


__tests__ = (
{
    "#url"     : "https://xub.fanbox.cc",
    "#category": ("", "fanbox", "creator"),
    "#class"   : fanbox.FanboxCreatorExtractor,
    "#range"   : "1-15",
    "#count"   : ">= 15",

    "creatorId": "xub",
    "tags"     : list,
    "title"    : str,
},

{
    "#url"     : "https://xub.fanbox.cc/posts",
    "#category": ("", "fanbox", "creator"),
    "#class"   : fanbox.FanboxCreatorExtractor,
},

{
    "#url"     : "https://www.fanbox.cc/@xub/",
    "#category": ("", "fanbox", "creator"),
    "#class"   : fanbox.FanboxCreatorExtractor,
},

{
    "#url"     : "https://www.fanbox.cc/@xub/posts",
    "#category": ("", "fanbox", "creator"),
    "#class"   : fanbox.FanboxCreatorExtractor,
},

{
    "#url"     : "https://www.fanbox.cc/@xub/posts/1910054",
    "#category": ("", "fanbox", "post"),
    "#class"   : fanbox.FanboxPostExtractor,
    "#count"   : 3,

    "title"          : "えま★おうがすと",
    "tags"           : list,
    "hasAdultContent": True,
    "isCoverImage"   : False,
},

{
    "#url"     : "https://nekoworks.fanbox.cc/posts/915",
    "#comment" : "entry post type, image embedded in html of the post",
    "#category": ("", "fanbox", "post"),
    "#class"   : fanbox.FanboxPostExtractor,
    "#count"   : 2,

    "title"          : "【SAYORI FAN CLUB】お届け内容",
    "tags"           : list,
    "html"           : str,
    "hasAdultContent": True,
},

{
    "#url"     : "https://steelwire.fanbox.cc/posts/285502",
    "#comment" : "article post type, imageMap, 2 twitter embeds, fanbox embed",
    "#category": ("", "fanbox", "post"),
    "#class"   : fanbox.FanboxPostExtractor,
    "#options" : {"embeds": True},
    "#count"   : 10,

    "title"          : "イラスト+SS｜義足の炭鉱少年が義足を見せてくれるだけ 【全体公開版】",
    "tags"           : list,
    "articleBody"    : dict,
    "hasAdultContent": True,
},

{
    "#url"     : "https://www.fanbox.cc/@official-en/posts/4326303",
    "#comment" : "'content' metadata (#3020)",
    "#category": ("", "fanbox", "post"),
    "#class"   : fanbox.FanboxPostExtractor,

    "content": r"re:(?s)^Greetings from FANBOX.\n \nAs of Monday, September 5th, 2022, we are happy to announce the start of the FANBOX hashtag event #MySetupTour ! \nAbout the event\nTo join this event .+ \nPlease check this page for further details regarding the Privacy & Terms.\nhttps://fanbox.pixiv.help/.+/10184952456601\n\n\nThank you for your continued support of FANBOX.$",
},

{
    "#url"     : "https://mochirong.fanbox.cc/posts/3746116",
    "#comment" : "imageMap file order (#2718)",
    "#category": ("", "fanbox", "post"),
    "#class"   : fanbox.FanboxPostExtractor,
    "#sha1_url": "c92ddd06f2efc4a5fe30ec67e21544f79a5c4062",
},

{
    "#url"     : "https://www.pixiv.net/fanbox/creator/52336352",
    "#category": ("", "fanbox", "redirect"),
    "#class"   : fanbox.FanboxRedirectExtractor,
    "#pattern" : fanbox.FanboxCreatorExtractor.pattern,
},

)
