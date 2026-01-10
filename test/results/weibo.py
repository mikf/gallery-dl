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
    "#results" : "https://weibo.com/u/1758989602?tabtype=feed",
},

{
    "#url"     : "https://weibo.com/1758989602",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://weibo.com/u/1758989602?tabtype=home",
        "https://weibo.com/u/1758989602?tabtype=feed",
        "https://weibo.com/u/1758989602?tabtype=video",
        "https://weibo.com/u/1758989602?tabtype=newVideo",
        "https://weibo.com/u/1758989602?tabtype=article",
        "https://weibo.com/u/1758989602?tabtype=album",
    ),
},

{
    "#url"     : "https://weibo.com/zhouyuxi77",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#results" : "https://weibo.com/u/7488709788?tabtype=feed",
},

{
    "#url"     : "https://www.weibo.com/n/周于希Sally",
    "#category": ("", "weibo", "user"),
    "#class"   : weibo.WeiboUserExtractor,
    "#results" : "https://weibo.com/u/7488709788?tabtype=feed",
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
    "#url"     : "https://weibo.com/u/2142058927?tabtype=album-头像",
    "#comment" : "subalbum",
    "#class"   : weibo.WeiboAlbumExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://weibo.com/ajax/common/download?pid=002kXRnxly8i5b4anvvxbj60u00u078w02",
        "https://weibo.com/ajax/common/download?pid=002kXRnxly8i2b7u68bfhj60u00u0dl002",
        "https://weibo.com/ajax/common/download?pid=002kXRnxly8i2b6rmr1trj60rs0rstdn02",
    ),

    "extension": "jpg",
    "pid"      : str,
    "type"     : "pic",
    "subalbum" : {
        "containerid": "2318262142058927_-_pc_profile_album_-_photo_-_avatar_-_35046512_-_%E5%A4%B4%E5%83%8F",
        "pic"        : "https://wx1.sinaimg.cn/webp720/002kXRnxly8i5b4anvvxbj60u00u078w02.jpg",
        "pic_title"  : "头像",
    },
    "user"     : {
        "id"         : 2142058927,
        "idstr"      : "2142058927",
        "location"   : "上海 黄浦区",
        "profile_url": "/u/2142058927",
        "screen_name": "吴磊LEO",
    },
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
    "#results" : "https://wx4.sinaimg.cn/large/68d80d22gy1h2ryfa8k0kg208w06o7wh.gif",

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
    "#count"   : 9,
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
    "#url"     : "https://weibo.com/1919017185/4246199458129705",
    "#comment" : "'movie'-type video (#3793)",
    "#category": ("", "weibo", "status"),
    "#class"   : weibo.WeiboStatusExtractor,
    "#options" : {"movies": True},
    "#results" : (
        "https://wx4.sinaimg.cn/large/7261e0e1gy1frvyc1xnkfj20qo0zkwjh.jpg",
        "https://wx2.sinaimg.cn/large/7261e0e1gy1frvyc30b1jj20zk0qojwh.jpg",
        "https://wx4.sinaimg.cn/large/7261e0e1gy1frvyc44lx8j20qo0zk7a6.jpg",
        "https://gslb.miaopai.com/stream/KdhuavhOnJ7R6zJFXfEXm-sDthpmC5DIGqrdOg__.mp4?yx=&refer=weibo_app&tags=weibocard",
    ),
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

{
    "#url"     : "https://weibo.com/7926989456/5160875674043425",
    "#comment" : "'replay_hd' video (live replay #8339)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#results" : "ytdl:https://live.video.weibocdn.com/4817f457-c9be-47f7-a5a0-8591fd363cb1_index.m3u8",
},

{
    "#url"     : "https://weibo.com/7117031969/5208376084532264",
    "#comment" : "'.m3u8' manifest (live replay #8339)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"ytdl:https://live.video.weibocdn.com/0f9e059c-3438-49ab-a84c-671a04d37b92_index.m3u8\?media_id=5208391172685924&.+&KID=unistore,video",
    "#count"   : 1,
},

{
    "#url"     : "https://weibo.com/2683260651/3774796733364550",
    "#comment" : "'.m3u8' manifest (from 2014)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#pattern" : r"ytdl:https://us.sinaimg.cn/001xN98Njx06NszB2n15010d0100008H0k01.m3u8\?ori=0&.+&KID=unistore,video",
    "#count"   : 1,
},

{
    "#url"     : "https://weibo.com/3317906495/5217357545080355",
    "#comment" : "stream as 'wblive-out.api.weibo.com' URL (#8339)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#results" : "ytdl:https://live.video.weibocdn.com/5073cc59-42fc-4b9c-9a61-852d44b0ccc3_index.m3u8",
},

{
    "#url"     : "https://weibo.com/7130470964/5217692969600188",
    "#comment" : "stream without replay (#8339)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#count"   : 0,
    "#log"     : "HttpError: '404 ' for 'https://wblive-out.api.weibo.com/2/wblive/room/play?id=1022:2321325216257942356128'",
},

{
    "#url"     : "https://weibo.com/1893905030/Q9yKt97ID",
    "#comment" : "truncated 'text' / 'isLongText: true' (#8422)",
    "#class"   : weibo.WeiboStatusExtractor,
    "#results" : (
        "https://wx1.sinaimg.cn/large/70e2b286gy1i6fho7ydx0j20fa08lt8u.jpg",
        "https://wx1.sinaimg.cn/large/70e2b286gy1i6fho7zwhmj20u00gvmzg.jpg",
        "https://wx4.sinaimg.cn/large/70e2b286gy1i6fho80b47j21u8112wh3.jpg",
    ),

    "status"   : {
        "id"              : 5222785292174627,
        "isLongText"      : True,
        "textLength"      : 750,
        "text"            : """【加快生产速度！曝任天堂明年3月生产2500万台<a href="//s.weibo.com/weibo?q=%23Switch2%23" target="_blank">#Switch2#</a>】据彭博社报道，<a href="//s.weibo.com/weibo?q=%23%E4%BB%BB%E5%A4%A9%E5%A0%82%23" target="_blank">#任天堂#</a>已要求供应商在2026年3月底之前生产多达2500万台Switch 2。<br /><br />知情人士透露，考虑到今年假期旺季（黑色星期五、圣诞节和新年假期）以及明年初的持续需求，任天堂已要求制造合作伙伴加快生产进度。尽管任天堂计划自2024年底开始组装Switch 2，但根据年底购物季的实际需求情况，最终产量目标仍有可能进行调整。<br /><br />彭博社分析认为，任天堂的出货量很可能轻松超越分析师预测的1760万台，甚至超出公司自身更为保守的公开预期。根据组装厂商的发货估算，任天堂在本财年（截至2026年3月）预计将售出约2000万台Switch 2，剩余库存则将结转到下一财年。<br /><br />市场研究机构Circana的数据显示，美国为任天堂最大市场，Switch 2的销售表现比2017年发售的初代Switch高出77%。按照这一趋势，任天堂很可能提前几个月就能超额完成其保守的销售目标。""",
        "text_raw"        : """\
【加快生产速度！曝任天堂明年3月生产2500万台#Switch2#】据彭博社报道，#任天堂#已要求供应商在2026年3月底之前生产多达2500万台Switch 2。

知情人士透露，考虑到今年假期旺季（黑色星期五、圣诞节和新年假期）以及明年初的持续需求，任天堂已要求制造合作伙伴加快生产进度。尽管任天堂计划自2024年底开始组装Switch 2，但根据年底购物季的实际需求情况，最终产量目标仍有可能进行调整。

彭博社分析认为，任天堂的出货量很可能轻松超越分析师预测的1760万台，甚至超出公司自身更为保守的公开预期。根据组装厂商的发货估算，任天堂在本财年（截至2026年3月）预计将售出约2000万台Switch 2，剩余库存则将结转到下一财年。

市场研究机构Circana的数据显示，美国为任天堂最大市场，Switch 2的销售表现比2017年发售的初代Switch高出77%。按照这一趋势，任天堂很可能提前几个月就能超额完成其保守的销售目标。\
""",
        "longText"        : {
            "created_at"    : "Fri Oct 17 17:15:11 +0800 2025",
            "mblog_vip_type": 0,
            "show_attitude_bar": 0,
            "weibo_position": 1,
            "content"       : """\
【加快生产速度！曝任天堂明年3月生产2500万台#Switch2#】据彭博社报道，#任天堂#已要求供应商在2026年3月底之前生产多达2500万台Switch 2。

知情人士透露，考虑到今年假期旺季（黑色星期五、圣诞节和新年假期）以及明年初的持续需求，任天堂已要求制造合作伙伴加快生产进度。尽管任天堂计划自2024年底开始组装Switch 2，但根据年底购物季的实际需求情况，最终产量目标仍有可能进行调整。

彭博社分析认为，任天堂的出货量很可能轻松超越分析师预测的1760万台，甚至超出公司自身更为保守的公开预期。根据组装厂商的发货估算，任天堂在本财年（截至2026年3月）预计将售出约2000万台Switch 2，剩余库存则将结转到下一财年。

市场研究机构Circana的数据显示，美国为任天堂最大市场，Switch 2的销售表现比2017年发售的初代Switch高出77%。按照这一趋势，任天堂很可能提前几个月就能超额完成其保守的销售目标。\
""",
        },
    },
},

)
