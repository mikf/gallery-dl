# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import weibo
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://weibo.com/1758989602",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#urls"    : "https://weibo.com/u/1758989602?tabtype=feed",
},

{
    "#url"     : "https://weibo.com/1758989602",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#options" : {"include": "all"},
    "#urls"    : (
        "https://weibo.com/u/1758989602?tabtype=home",
        "https://weibo.com/u/1758989602?tabtype=feed",
        "https://weibo.com/u/1758989602?tabtype=video",
        "https://weibo.com/u/1758989602?tabtype=newVideo",
        "https://weibo.com/u/1758989602?tabtype=album",
    ),
},

{
    "#url"     : "https://weibo.com/zhouyuxi77",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#urls"    : "https://weibo.com/u/7488709788?tabtype=feed",
},

{
    "#url"     : "https://www.weibo.com/n/周于希Sally",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#urls"    : "https://weibo.com/u/7488709788?tabtype=feed",
},

{
    "#url"     : "https://weibo.com/u/1758989602",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
},

{
    "#url"     : "https://weibo.com/p/1758989602",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
},

{
    "#url"     : "https://m.weibo.cn/profile/2314621010",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
},

{
    "#url"     : "https://m.weibo.cn/p/2304132314621010_-_WEIBO_SECOND_PROFILE_WEIBO",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
},

{
    "#url"     : "https://www.weibo.com/p/1003062314621010/home",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
},

{
    "#url"     : "https://weibo.com/1758989602?tabtype=home",
    "#comment" : "'tabtype=home' is broken on website itself",
    "#category": ("", "weibo", "home"),
    "#class"   : weibo.WeiboHomeExtractor,
    "#range"   : "1-30",
    "#count"   : 0,
},

{
    "#url"     : "https://weibo.com/2553930725?tabtype=feed",
    "#category": ("", "weibo", "feed"),
    "#class"   : weibo.WeiboFeedExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://weibo.com/zhouyuxi77?tabtype=feed",
    "#category": ("", "weibo", "feed"),
    "#class"   : weibo.WeiboFeedExtractor,
    "#range"   : "1",

    "status": {
        "user": {
            "id": 7488709788,
        },
    },
},

{
    "#url"     : "https://www.weibo.com/n/周于希Sally?tabtype=feed",
    "#category": ("", "weibo", "feed"),
    "#class"   : weibo.WeiboFeedExtractor,
    "#range"   : "1",


    "status": {
        "user": {
            "id": 7488709788,
        },
    },
},

{
    "#url"     : "https://weibo.com/u/7500315942?tabtype=feed",
    "#comment" : "deleted (#2521)",
    "#category": ("", "weibo", "feed"),
    "#class"   : weibo.WeiboFeedExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://weibo.com/1758989602?tabtype=video",
    "#category": ("", "weibo", "videos"),
    "#class"   : weibo.WeiboVideosExtractor,
    "#pattern" : r"https://f\.(video\.weibocdn\.com|us\.sinaimg\.cn)/(../)?\w+\.mp4\?label=mp",
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://weibo.com/1758989602?tabtype=newVideo",
    "#category": ("", "weibo", "newvideo"),
    "#class"   : weibo.WeiboNewvideoExtractor,
    "#pattern" : r"https://f\.video\.weibocdn\.com/(../)?\w+\.mp4\?label=mp",
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://weibo.com/1758989602?tabtype=article",
    "#category": ("", "weibo", "article"),
    "#class"   : weibo.WeiboArticleExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://weibo.com/1758989602?tabtype=album",
    "#category": ("", "weibo", "album"),
    "#class"   : weibo.WeiboAlbumExtractor,
    "#pattern" : r"https://(wx\d+\.sinaimg\.cn/large/\w{32}\.(jpg|png|gif)|g\.us\.sinaimg\.cn/../\w+\.mp4)",
    "#range"   : "1-3",
    "#count"   : 3,
},

{
    "#url"     : "https://m.weibo.cn/detail/4323047042991618",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"https?://wx\d+.sinaimg.cn/large/\w+.jpg",

    "status": {
        "count": 1,
        "date" : "dt:2018-12-30 13:56:36",
    },
},

{
    "#url"     : "https://m.weibo.cn/detail/4339748116375525",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"https?://f.us.sinaimg.cn/\w+\.mp4\?label=mp4_1080p",
},

{
    "#url"     : "https://m.weibo.cn/status/4268682979207023",
    "#comment" : "unavailable video (#427)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://weibo.com/3314883543/Iy7fj4qVg",
    "#comment" : "non-numeric status ID (#664)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
},

{
    "#url"     : "https://weibo.cn/detail/4600272267522211",
    "#comment" : "retweet",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://weibo.cn/detail/4600272267522211",
    "#comment" : "retweet",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#options" : {"retweets": True},
    "#count"   : 2,

    "status": {
        "id"                     : 4600272267522211,
        "retweeted_status": {"id": 4600167083287033},
    },
},

{
    "#url"     : "https://m.weibo.cn/detail/4600272267522211",
    "#comment" : "original retweets (#1542)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#options" : {"retweets": "original"},

    "status": {"id": 4600167083287033},
},

{
    "#url"     : "https://weibo.com/3194672795/OuxSwgUrC",
    "#comment" : "type == livephoto (#2146, #6471)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"https://livephoto\.us\.sinaimg\.cn/\w+\.mov\?Expires=\d+&ssig=[^&#]+&KID=unistore,video",
    "#range"   : "2,4",

    "filename" : {"000yfKhRjx08hBAXxdZ60f0f0100tBPr0k01", "000GEYrCjx08hBAXUFo40f0f0100vS5G0k01"},
    "extension": "mov",
},

{
    "#url"     : "https://weibo.com/1758989602/LvBhm5DiP",
    "#comment" : "type == gif",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#urls"    : "https://wx4.sinaimg.cn/large/68d80d22gy1h2ryfa8k0kg208w06o7wh.gif",

    "extension": "gif",
},

{
    "#url"     : "https://weibo.com/1758989602/LvBhm5DiP",
    "#comment" : "type == gif as video (#5183)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#options" : {"gifs": "video"},
    "#pattern" : r"https://g\.us\.sinaimg.cn/o0/qNZcaAAglx07Wuf921CM0104120005tc0E010\.mp4\?label=gif_mp4",
},

{
    "#url"     : "https://weibo.com/2909128931/4409545658754086",
    "#comment" : "missing 'playback_list' (#2792)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#count"   : 10,
},

{
    "#url"     : "https://weibo.com/1501933722/4142890299009993",
    "#comment" : "empty 'playback_list' (#3301)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"https://f\.us\.sinaimg\.cn/004zstGKlx07dAHg4ZVu010f01000OOl0k01\.mp4\?label=mp4_hd&template=template_7&ori=0&ps=1CwnkDw1GXwCQx.+&KID=unistore,video",
    "#count"   : 1,
},

{
    "#url"     : "https://weibo.com/2427303621/MxojLlLgQ",
    "#comment" : "mix_media_info (#3793)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#count"   : 9,
},

{
    "#url"     : "https://m.weibo.cn/status/4339748116375525",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
},

{
    "#url"     : "https://m.weibo.cn/5746766133/4339748116375525",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
},

)
