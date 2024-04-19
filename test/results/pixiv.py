# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixiv
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.pixiv.net/en/users/173530",
    "#category": ("", "pixiv", "user"),
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/u/173530",
    "#category": ("", "pixiv", "user"),
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/member.php?id=173530",
    "#category": ("", "pixiv", "user"),
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/mypage.php#id=173530",
    "#category": ("", "pixiv", "user"),
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/#id=173530",
    "#category": ("", "pixiv", "user"),
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/artworks",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
    "#sha1_url": "852c31ad83b6840bacbce824d85f2a997889efb7",
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/artworks/%E6%89%8B%E3%81%B6%E3%82%8D",
    "#comment" : "illusts with specific tag",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
    "#sha1_url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?id=173530&tag=%E6%89%8B%E3%81%B6%E3%82%8D",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
    "#sha1_url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?id=173531",
    "#comment" : "deleted account",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
    "#options"  : {"metadata": True},
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/manga",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/illustrations",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?id=173530",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/member_illust.php?id=173530",
    "#category": ("", "pixiv", "artworks"),
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/avatar",
    "#category": ("", "pixiv", "avatar"),
    "#class"   : pixiv.PixivAvatarExtractor,
    "#sha1_content": "4e57544480cc2036ea9608103e8f024fa737fe66",
},

{
    "#url"     : "https://www.pixiv.net/en/users/194921/background",
    "#category": ("", "pixiv", "background"),
    "#class"   : pixiv.PixivBackgroundExtractor,
    "#pattern" : r"https://i\.pximg\.net/background/img/2021/01/30/16/12/02/194921_af1f71e557a42f499213d4b9eaccc0f8\.jpg",
},

{
    "#url"     : "https://pixiv.me/del_shannon",
    "#category": ("", "pixiv", "me"),
    "#class"   : pixiv.PixivMeExtractor,
    "#sha1_url": "29c295ce75150177e6b0a09089a949804c708fbf",
},

{
    "#url"     : "https://pixiv.me/del_shanno",
    "#category": ("", "pixiv", "me"),
    "#class"   : pixiv.PixivMeExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/artworks/966412",
    "#comment" : "related works (#1237)",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
    "#sha1_url"    : "90c1715b07b0d1aad300bce256a0bc71f42540ba",
    "#sha1_content": "69a8edfb717400d1c2e146ab2b30d2c235440c5a",

    "date"    : "dt:2008-06-12 15:29:13",
    "date_url": "dt:2008-06-12 15:29:13",
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=966411",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=66806629",
    "#comment" : "ugoira",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
    "#sha1_url": "7267695a985c4db8759bebcf8d21dbdd2d2317ef",

    "frames"  : list,
    "date"    : "dt:2018-01-14 15:06:08",
    "date_url": "dt:2018-01-15 04:24:48",
},

{
    "#url"     : "https://www.pixiv.net/artworks/966412",
    "#comment" : "related works (#1237)",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"related": True},
    "#range"   : "1-10",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.pixiv.net/artworks/966412",
    "#comment" : "limit_sanity_level_360.png (#4327, #5180)",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/966412",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=96641",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://i1.pixiv.net/c/600x600/img-master/img/2008/06/13/00/29/13/966412_p0_master1200.jpg",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://i.pximg.net/img-original/img/2017/04/25/07/33/29/62568267_p0.png",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://www.pixiv.net/i/966412",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://img.pixiv.net/img/soundcross/42626136.jpg",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://i2.pixiv.net/img76/img/snailrin/42672235.jpg",
    "#category": ("", "pixiv", "work"),
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/bookmarks/artworks",
    "#category": ("", "pixiv", "favorite"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#sha1_url": "85a3104eaaaf003c7b3947117ca2f1f0b1cfc949",
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?id=173530",
    "#category": ("", "pixiv", "favorite"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#sha1_url": "85a3104eaaaf003c7b3947117ca2f1f0b1cfc949",
},

{
    "#url"     : "https://www.pixiv.net/en/users/3137110/bookmarks/artworks/%E3%81%AF%E3%82%93%E3%82%82%E3%82%93",
    "#comment" : "bookmarks with specific tag",
    "#category": ("", "pixiv", "favorite"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#sha1_url": "379b28275f786d946e01f721e54afe346c148a8c",
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?id=3137110&tag=%E3%81%AF%E3%82%93%E3%82%82%E3%82%93&p=1",
    "#comment" : "bookmarks with specific tag (legacy url)",
    "#category": ("", "pixiv", "favorite"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#sha1_url": "379b28275f786d946e01f721e54afe346c148a8c",
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php",
    "#comment" : "own bookmarks",
    "#category": ("", "pixiv", "bookmark"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#options" : {"metadata-bookmark": True},
    "#sha1_url": "90c1715b07b0d1aad300bce256a0bc71f42540ba",

    "tags_bookmark": [
        "47",
        "hitman",
    ],
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?tag=foobar",
    "#comment" : "own bookmarks with tag (#596)",
    "#category": ("", "pixiv", "bookmark"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/following",
    "#comment" : "followed users (#515)",
    "#category": ("", "pixiv", "following"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#pattern" : pixiv.PixivUserExtractor.pattern,
    "#count"   : ">= 12",
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?id=173530&type=user",
    "#comment" : "followed users (legacy url) (#515)",
    "#category": ("", "pixiv", "following"),
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#pattern" : pixiv.PixivUserExtractor.pattern,
    "#count"   : ">= 12",
},

{
    "#url"     : "https://touch.pixiv.net/bookmark.php?id=173530",
    "#comment" : "touch URLs",
    "#category": ("", "pixiv", "favorite"),
    "#class"   : pixiv.PixivFavoriteExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/bookmark.php",
    "#category": ("", "pixiv", "bookmark"),
    "#class"   : pixiv.PixivFavoriteExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php?mode=daily&date=20170818",
    "#category": ("", "pixiv", "ranking"),
    "#class"   : pixiv.PixivRankingExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php",
    "#category": ("", "pixiv", "ranking"),
    "#class"   : pixiv.PixivRankingExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/ranking.php",
    "#category": ("", "pixiv", "ranking"),
    "#class"   : pixiv.PixivRankingExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php?mode=unknown",
    "#category": ("", "pixiv", "ranking"),
    "#class"   : pixiv.PixivRankingExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://www.pixiv.net/en/tags/Original",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://pixiv.net/en/tags/foo/artworks?order=week&s_mode=s_tag",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://pixiv.net/en/tags/foo/artworks?order=date&s_mode=tag",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://www.pixiv.net/search.php?s_mode=s_tag&name=Original",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://www.pixiv.net/en/tags/foo/artworks?order=date&s_mode=s_tag",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://www.pixiv.net/search.php?s_mode=s_tag&word=Original",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/search.php?word=Original",
    "#category": ("", "pixiv", "search"),
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://www.pixiv.net/bookmark_new_illust.php",
    "#category": ("", "pixiv", "follow"),
    "#class"   : pixiv.PixivFollowExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/bookmark_new_illust.php",
    "#category": ("", "pixiv", "follow"),
    "#class"   : pixiv.PixivFollowExtractor,
},

{
    "#url"     : "https://www.pixivision.net/en/a/2791",
    "#category": ("", "pixiv", "pixivision"),
    "#class"   : pixiv.PixivPixivisionExtractor,
},

{
    "#url"     : "https://pixivision.net/a/2791",
    "#category": ("", "pixiv", "pixivision"),
    "#class"   : pixiv.PixivPixivisionExtractor,
    "#count"   : 7,

    "pixivision_id"   : "2791",
    "pixivision_title": "What's your favorite music? Editor’s picks featuring: “CD Covers”!",
},

{
    "#url"     : "https://www.pixiv.net/user/10509347/series/21859",
    "#category": ("", "pixiv", "series"),
    "#class"   : pixiv.PixivSeriesExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "num_series": int,
    "series"    : {
        "canonical"  : "https://www.pixiv.net/user/10509347/series/21859",
        "description": str,
        "ogp"        : dict,
        "title"      : "先輩がうざい後輩の話",
        "total"      : int,
        "twitter"    : dict,
    },
},

{
    "#url"     : "https://www.pixiv.net/novel/show.php?id=12101012",
    "#category": ("", "pixiv", "novel"),
    "#class"   : pixiv.PixivNovelExtractor,
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
    "#category": ("", "pixiv", "novel"),
    "#class"   : pixiv.PixivNovelExtractor,
    "#options" : {
        "embeds": True,
        "covers": True,
    },
    "#count"   : 4,
},

{
    "#url"     : "https://www.pixiv.net/novel/show.php?id=12101012",
    "#comment" : "full series",
    "#category": ("", "pixiv", "novel"),
    "#class"   : pixiv.PixivNovelExtractor,
    "#options" : {"full-series": True},
    "#count"   : 2,
},

{
    "#url"     : "https://www.pixiv.net/n/19612040",
    "#comment" : "short URL",
    "#category": ("", "pixiv", "novel"),
    "#class"   : pixiv.PixivNovelExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/77055466/novels",
    "#category": ("", "pixiv", "novel-user"),
    "#class"   : pixiv.PixivNovelUserExtractor,
    "#pattern" : "^text:",
    "#range"   : "1-5",
    "#count"   : 5,
},

{
    "#url"     : "https://www.pixiv.net/novel/series/1479656",
    "#category": ("", "pixiv", "novel-series"),
    "#class"   : pixiv.PixivNovelSeriesExtractor,
    "#count"       : 2,
    "#sha1_content": "243ce593333bbfe26e255e3372d9c9d8cea22d5b",
},

{
    "#url"     : "https://www.pixiv.net/en/users/77055466/bookmarks/novels",
    "#category": ("", "pixiv", "novel-bookmark"),
    "#class"   : pixiv.PixivNovelBookmarkExtractor,
    "#count"       : 1,
    "#sha1_content": "7194e8faa876b2b536f185ee271a2b6e46c69089",
},

{
    "#url"     : "https://www.pixiv.net/en/users/11/bookmarks/novels/TAG?rest=hide",
    "#category": ("", "pixiv", "novel-bookmark"),
    "#class"   : pixiv.PixivNovelBookmarkExtractor,
},

{
    "#url"     : "https://sketch.pixiv.net/@nicoby",
    "#category": ("", "pixiv", "sketch"),
    "#class"   : pixiv.PixivSketchExtractor,
    "#pattern" : r"https://img\-sketch\.pixiv\.net/uploads/medium/file/\d+/\d+\.(jpg|png)",
    "#count"   : ">= 35",
},

)
