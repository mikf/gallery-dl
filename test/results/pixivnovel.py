# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixiv


__tests__ = (
{
    "#url"     : "https://www.pixiv.net/novel/show.php?id=12101012",
    "#class"   : pixiv.PixivNovelNovelExtractor,
    "#count"       : 1,
    "#sha1_content": "20f4a62f0e87ae2cb9f5a787b6c641bfa4eabf93",

    "caption"        : "<br />第一印象から決めてました！<br /><br />素敵な表紙はいもこは妹さん(<strong><a href=\"pixiv://illusts/53802907\">illust/53802907</a></strong>)からお借りしました。<br /><br />たくさんのコメント、タグありがとうございます、本当に嬉しいです。お返事できていませんが、一つ一つ目を通させていただいてます。タイトルも込みで読んでくださってすごく嬉しいです。ありがとうございます……！！<br /><br />■12/19付けルキラン20位を頂きました…！大変混乱していますがすごく嬉しいです。ありがとうございます！　<br /><br />■2019/12/20デイリー15位、女子に人気8位をを頂きました…！？！？！？！？て、手が震える…。ありがとうございます…ひえええ。感謝してもしきれないです…！",
    "create_date"    : "2019-12-19T23:14:36+09:00",
    "date"           : "dt:2019-12-19 14:14:36",
    "extension"      : "txt",
    "id"             : 12101012,
    "image_urls"     : dict,
    "is_bookmarked"  : False,
    "is_muted"       : False,
    "is_mypixiv_only": False,
    "is_original"    : False,
    "is_x_restricted": False,
    "novel_ai_type"  : 0,
    "page_count"     : 1,
    "rating"         : "General",
    "restrict"       : 0,
    "series"         : {
        "id"   : 1479656,
        "title": "一目惚れした彼らの話",
    },
    "tags"           : [
        "鬼滅の夢",
        "女主人公",
        "煉獄杏寿郎",
        "涙腺崩壊",
        "なにこれすごい",
        "来世で幸せになって欲しい",
        "キメ学世界線できっと幸せになってる!!",
        "あなたが神か!!",
        "キメ学編を·····",
        "鬼滅の夢小説10000users入り",
    ],
    "text_length"    : 9569,
    "title"          : "本当は、一目惚れだった",
    "total_bookmarks": range(17900, 20000),
    "total_comments" : range(200, 400),
    "total_view"     : range(158000, 300000),
    "user"           : {
        "account": "46_maru",
        "id"     : 888268,
    },
    "visible"        : True,
    "x_restrict"     : 0,
},

{
    "#url"     : "https://www.pixiv.net/novel/show.php?id=16422450",
    "#comment" : "embeds // covers (#5373)",
    "#class"   : pixiv.PixivNovelNovelExtractor,
    "#options" : {
        "embeds": True,
        "covers": True,
    },
    "#count"   : 4,
},

{
    "#url"     : "https://www.pixiv.net/novel/show.php?id=12101012",
    "#comment" : "full series",
    "#class"   : pixiv.PixivNovelNovelExtractor,
    "#options" : {"full-series": True},
    "#count"   : 2,
},

{
    "#url"     : "https://www.pixiv.net/n/19612040",
    "#comment" : "short URL",
    "#class"   : pixiv.PixivNovelNovelExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/77055466/novels",
    "#class"   : pixiv.PixivNovelUserExtractor,
    "#pattern" : "^text:",
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://www.pixiv.net/novel/series/1479656",
    "#class"   : pixiv.PixivNovelSeriesExtractor,
    "#count"       : 2,
    "#sha1_content": "243ce593333bbfe26e255e3372d9c9d8cea22d5b",
},

{
    "#url"     : "https://www.pixiv.net/en/users/77055466/bookmarks/novels",
    "#class"   : pixiv.PixivNovelBookmarkExtractor,
    "#count"       : 1,
    "#sha1_content": "7194e8faa876b2b536f185ee271a2b6e46c69089",
},

{
    "#url"     : "https://www.pixiv.net/en/users/11/bookmarks/novels/TAG?rest=hide",
    "#class"   : pixiv.PixivNovelBookmarkExtractor,
},

)
