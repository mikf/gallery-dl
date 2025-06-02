# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cien


__tests__ = (
{
    "#url"     : "https://ci-en.net/creator/7491/article/1194568",
    "#category": ("", "cien", "article"),
    "#class"   : cien.CienArticleExtractor,
    "#pattern" : r"https://media\.ci-en\.jp/private/attachment/creator/00007491/c0c212a93027c8863bdb40668071c1525a4567f94baca13c17989045e5a3d81d/video-web\.mp4\?px-time=.+",

    "author": {
        "@type" : "Person",
        "image" : "https://media.ci-en.jp/public/icon/creator/00007491/9601a2a224245156335aaa839fa408d52c32c87dae5787fc03f455b7fd1d3488/image-200-c.jpg",
        "name"  : "やかろ",
        "url"   : "https://ci-en.net/creator/7491",
        "sameAs": [
            "https://pokapoka0802.wixsite.com/tunousaginoie82",
            "https://www.freem.ne.jp/brand/6001",
            "https://store.steampowered.com/search/?developer=%E3%83%84%E3%83%8E%E3%82%A6%E3%82%B5%E3%82%AE%E3%81%AE%E5%AE%B6",
            "https://plicy.net/User/87381",
            "https://twitter.com/pokapoka0802",
        ],
    },
    "articleBody": str,
    "count"       : 1,
    "date"       : "dt:2024-07-21 15:36:00",
    "dateModified" : "2024-07-22T03:28:40+09:00",
    "datePublished": "2024-07-22T00:36:00+09:00",
    "description": "お知らせ 今回は雨のピリオードの解説をしたいと思うのですが、その前にいくつかお知らせがあります。 電話を使って謎を解いていくフリーゲーム 電話を通して、様々なキャラクターを会話をしていく、ノベルゲーム……",
    "extension"  : "mp4",
    "filename"   : "無題の動画 (1)",
    "headline"   : "角兎図書館「雨のピリオード」No,16",
    "image"      : "https://media.ci-en.jp/public/article_cover/creator/00007491/cb4062e8d885ab93e0d0fb3133265a7ad1056c906fd4ab81da509220620901e1/image-1280-c.jpg",
    "keywords"   : "お知らせ,角兎図書館",
    "mainEntityOfPage": "https://ci-en.net/creator/7491/article/1194568",
    "name"       : "角兎図書館「雨のピリオード」No,16",
    "num"        : 1,
    "post_id"    : 1194568,
    "type"       : "video",
    "url"        : str,
},

{
    "#url"     : "https://ci-en.dlsite.com/creator/25509/article/1172460",
    "#category": ("", "cien", "article"),
    "#class"   : cien.CienArticleExtractor,
    "#options" : {"files": "download"},
    "#pattern" : r"https://media\.ci-en\.jp/private/attachment/creator/00025509/7fd3c039d2277ba9541e82592aca6f6751f6c268404038ccbf1112bcf2f93357/upload/.+\.zip\?px-time=.+",

    "filename" : "VP 1.05.4 Tim-v9 ENG rec v3",
    "extension": "zip",
    "type"     : "download",
},

{
    "#url"     : "https://ci-en.net/creator/11962",
    "#category": ("", "cien", "creator"),
    "#class"   : cien.CienCreatorExtractor,
    "#pattern" : cien.CienArticleExtractor.pattern,
    "#count"   : "> 25",
},

{
    "#url"     : "https://ci-en.net/mypage/recent",
    "#category": ("", "cien", "recent"),
    "#class"   : cien.CienRecentExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://ci-en.net/mypage/subscription/following",
    "#category": ("", "cien", "following"),
    "#class"   : cien.CienFollowingExtractor,
    "#pattern" : cien.CienCreatorExtractor.pattern,
    "#count"   : "> 3",
    "#auth"    : True,
},

{
    "#url"     : "https://ci-en.net/mypage/subscription",
    "#category": ("", "cien", "following"),
    "#class"   : cien.CienFollowingExtractor,
    "#auth"    : True,
},

)
