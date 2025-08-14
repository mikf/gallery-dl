# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import skeb


__tests__ = (
{
    "#url"     : "https://skeb.jp/@kanade_cocotte/works/38",
    "#class"   : skeb.SkebPostExtractor,
    "#count"   : 2,

    "anonymous"       : False,
    "body"            : r"re:はじめまして。私はYouTubeにてVTuberとして活動をしている湊ラ",
    "count"           : 2,
    "num"             : range(1, 2),
    "client"          : {
        "avatar_url" : r"re:https://pbs.twimg.com/profile_images/\d+/\w+\.jpg",
        "header_url" : None,
        "id"         : 1196514,
        "name"       : str,
        "screen_name": "minato_ragi",
    },
    "content_category": "preview",
    "creator"         : {
        "avatar_url" : "https://pbs.twimg.com/profile_images/1225470417063645184/P8_SiB0V.jpg",
        "header_url" : "https://pbs.twimg.com/profile_banners/71243217/1647958329/1500x500",
        "id"         : 159273,
        "name"       : "イチノセ奏",
        "screen_name": "kanade_cocotte",
    },
    "file_id"         : int,
    "file_url"        : str,
    "genre"           : "art",
    "nsfw"            : False,
    "original"        : {
        "byte_size" : int,
        "duration"  : None,
        "extension" : {"psd", "png"},
        "frame_rate": None,
        "height"    : 3727,
        "is_movie"  : False,
        "width"     : 2810,
    },
    "post_num"        : "38",
    "post_url"        : "https://skeb.jp/@kanade_cocotte/works/38",
    "source_body"     : None,
    "source_thanks"   : None,
    "tags"            : list,
    "thanks"          : None,
    "translated_body" : False,
    "translated_thanks": None,
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte",
    "#class"   : skeb.SkebUserExtractor,
    "#results" : (
        "https://skeb.jp/@kanade_cocotte/works",
    ),
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte",
    "#class"   : skeb.SkebUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://skeb.jp/@kanade_cocotte/works",
        "https://skeb.jp/@kanade_cocotte/sentrequests",
    ),
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte",
    "#class"   : skeb.SkebUserExtractor,
    "#options" : {"sent-requests": True},
    "#results" : (
        "https://skeb.jp/@kanade_cocotte/works",
        "https://skeb.jp/@kanade_cocotte/sentrequests",
    ),
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte/works",
    "#class"   : skeb.SkebWorksExtractor,
    "#pattern" : r"https://si\.imgix\.net/\w+/uploads/origins/[\w-]+",
    "#range"   : "1-5",

    "count": int,
    "num"  : int,
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte/works",
    "#class"   : skeb.SkebWorksExtractor,
    "#pattern" : r"https://si\.imgix\.net/\w+/uploads/origins/[\w-]+",
    "#range"   : "1-5",

    "count": int,
    "num"  : int,
},

{
    "#url"     : "https://skeb.jp/@kanade_cocotte/sent-requests",
    "#class"   : skeb.SkebSentrequestsExtractor,
},

{
    "#url"     : "https://skeb.jp/@4ra_su4/sentrequests",
    "#class"   : skeb.SkebSentrequestsExtractor,
    "#pattern" : (
        r"https://si.imgix.net/4e44b668/uploads/origins/e42cbd8e-44af-4aaa-a11b-6a174f42202c\?bg=%23fff&auto=format&fm=webp&w=800&s=\w+",
        r"https://si.imgix.net/4d30e75e/uploads/origins/6d3bb612-3f45-4d8e-9d31-49dceb3dab11\?bg=%23fff&auto=format&fm=webp&w=800&s=\w+",
    ),

    "anonymous"       : False,
    "body"            : """\
リクエスト失礼致します。
うちの子の福良ことりちゃん（https://twitter.com/sousaku_suru/status/1404393369564946432）（https://twitter.com/sousaku_suru/status/1523336440062820354）がナース衣装のコスプレをしている作品をご依頼したいです！コス衣装にカチューシャについているクローバーが反映されていると嬉しいです。ご検討よろしくお願い致します！

https://twitter.com/sousaku_suru/status/1404393369564946432\
""",
    "content_category": "preview",
    "count"           : 2,
    "extension"       : "",
    "file_id"         : {950467, 950468},
    "file_url"        : r"re:https://si.imgix.net/.+",
    "filename"        : str,
    "genre"           : "art",
    "nsfw"            : False,
    "num"             : range(1, 2),
    "post_id"         : 802511,
    "post_num"        : "2",
    "post_url"        : "https://skeb.jp/@okonimi_hyu/works/2",
    "source_body"     : None,
    "source_thanks"   : None,
    "thanks"          : None,
    "translated_body" : False,
    "translated_thanks": None,
    "tags"            : [
        "よろしく",
        "お願い",
        "作品",
        "嬉しい",
        "うちの子",
        "コスプレ",
        "カチューシャ",
        "ナース",
        "クローバー",
        "ことりちゃん",
    ],
    "client"          : {
        "avatar_url" : "https://pbs.twimg.com/profile_images/1916152385107632128/pygB7-jf.jpg",
        "header_url" : "https://pbs.twimg.com/profile_banners/1134460426006159360/1717082866/1500x500",
        "id"         : 2017625,
        "name"       : "しろえ",
        "screen_name": "4ra_su4",
    },
    "creator"         : {
        "avatar_url" : "https://pbs.twimg.com/profile_images/1943287378149543937/EaUIMtnM.jpg",
        "header_url" : "https://pbs.twimg.com/profile_banners/2931377426/1523678757/1500x500",
        "id"         : 341737,
        "name"       : "Hyu@はゆ〜",
        "screen_name": "okonimi_hyu",
    },
    "original"        : {
        "byte_size" : {18463023, 793631},
        "duration"  : None,
        "extension" : {"psd", "png"},
        "frame_rate": None,
        "height"    : 1754,
        "is_movie"  : False,
        "software"  : None,
        "transcoder": "image",
        "width"     : 1275,
    },
},

{
    "#url"     : "https://skeb.jp/search?q=bunny%20tree&t=works",
    "#class"   : skeb.SkebSearchExtractor,
    "#count"   : ">= 18",

    "search_tags": "bunny tree",
},

{
    "#url"     : "https://skeb.jp/@user/following_creators",
    "#class"   : skeb.SkebFollowingExtractor,
},

{
    "#url"     : "https://skeb.jp/following_users",
    "#class"   : skeb.SkebFollowingUsersExtractor,
    "#pattern" : skeb.SkebUserExtractor.pattern,
    "#auth"    : True,
},

)
