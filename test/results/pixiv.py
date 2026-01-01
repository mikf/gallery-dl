# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixiv
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.pixiv.net/en/users/173530",
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530",
    "#class"   : pixiv.PixivUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://www.pixiv.net/users/173530/avatar",
        "https://www.pixiv.net/users/173530/background",
        "https://www.pixiv.net/users/173530/artworks",
        "https://www.pixiv.net/users/173530/bookmarks/artworks",
        "https://www.pixiv.net/users/173530/bookmarks/novels",
        "https://www.pixiv.net/users/173530/novels",
        "https://sketch.pixiv.net/@del_shannon",
        "https://www.pixiv.net/users/173530/bookmarks/novels",
        "https://www.pixiv.net/users/173530/novels",
    ),
},

{
    "#url"     : "https://www.pixiv.net/u/173530",
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/member.php?id=173530",
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/mypage.php#id=173530",
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/#id=173530",
    "#class"   : pixiv.PixivUserExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/artworks",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#options" : {"metadata": True},
    "#sha1_url": "852c31ad83b6840bacbce824d85f2a997889efb7",

    "profile": {
        "address_id": 0,
        "background_image_url": None,
        "birth": "",
        "birth_day": "",
        "birth_year": 0,
        "country_code": "",
        "gender": "male",
        "is_premium": False,
        "is_using_custom_profile_image": True,
        "job": "",
        "job_id": 0,
        "pawoo_url": None,
        "region": "",
        "total_follow_users": 16,
        "total_illust_bookmarks_public": range(5, 20),
        "total_illust_series": 0,
        "total_illusts": 17,
        "total_manga": 0,
        "total_mypixiv_users": 0,
        "total_novel_series": 0,
        "total_novels": 0,
        "twitter_account": "",
        "twitter_url": None,
        "webpage": None,
    },
    "profile_publicity": {
        "birth_day": "public",
        "birth_year": "public",
        "gender": "public",
        "job": "public",
        "pawoo": True,
        "region": "public",
    },
    "user": {
        "account": "del_shannon",
        "comment": "基本　お絵かき掲示板で書いたものＵＰしております。\r\nVistaとの相性最悪で泣きそうな毎日です。\r\nメモリは大幅増で一般使用はサクサクなだけに・・・。orz",
        "id": 173530,
        "is_access_blocking_user": False,
        "is_followed": False,
        "name": "syuri",
        "profile_image_urls": {
            "medium": "https://i.pximg.net/user-profile/img/2008/06/17/01/28/01/171098_fc06efd15628e2ee252941ae5298b5ff_170.jpg",
        },
    },
    "workspace": {
        "chair": "",
        "comment": "",
        "desk": "",
        "desktop": "",
        "monitor": "",
        "mouse": "",
        "music": "古い陸軍行進曲「ジェッディン・デデン」",
        "pc": "",
        "printer": "",
        "scanner": "",
        "tablet": "わこむ",
        "tool": "",
        "workspace_image_url": None,
    },
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/artworks",
    "#comment" : "Invalid PHPSESSID cookie",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#options" : {"cookies": {"PHPSESSID": "12345_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}},
    "#log"     : "Invalid 'PHPSESSID' cookie",
    "#sha1_url": "852c31ad83b6840bacbce824d85f2a997889efb7",
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/artworks/%E6%89%8B%E3%81%B6%E3%82%8D",
    "#comment" : "illusts with specific tag",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#sha1_url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?id=173530&tag=%E6%89%8B%E3%81%B6%E3%82%8D",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#sha1_url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?id=173531",
    "#comment" : "deleted account",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#options"  : {"metadata": True},
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/users/91306124/artworks",
    "#comment" : "deleted account with a different error",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#log"     : "'User has left pixiv or the user ID does not exist.'",
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/en/users/56514424/artworks",
    "#comment" : "limit_sanity_level_360.png in artworks results (#5435, #6339)",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#count"   : ">= 39",
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/manga",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/illustrations",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?id=173530",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/member_illust.php?id=173530",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://www.phixiv.net/member_illust.php?id=173530",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"     : "https://phixiv.net/en/users/56514424/artworks",
    "#class"   : pixiv.PixivArtworksExtractor,
},

{
    "#url"      : "https://www.pixiv.net/users/70060776/artworks",
    "#comment"  : "suspended account (#7990)",
    "#class"    : pixiv.PixivArtworksExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/users/84930793/artworks",
    "#comment" : "empty profile (#8066)",
    "#class"   : pixiv.PixivArtworksExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/avatar",
    "#class"   : pixiv.PixivAvatarExtractor,
    "#sha1_content": "4e57544480cc2036ea9608103e8f024fa737fe66",
},

{
    "#url"     : "https://www.pixiv.net/en/users/194921/background",
    "#class"   : pixiv.PixivBackgroundExtractor,
    "#pattern" : r"https://i\.pximg\.net/background/img/2021/01/30/16/12/02/194921_af1f71e557a42f499213d4b9eaccc0f8\.jpg",
},

{
    "#url"     : "https://pixiv.me/del_shannon",
    "#class"   : pixiv.PixivMeExtractor,
    "#sha1_url": "29c295ce75150177e6b0a09089a949804c708fbf",
},

{
    "#url"     : "https://pixiv.me/del_shanno",
    "#class"   : pixiv.PixivMeExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/artworks/966412",
    "#class"   : pixiv.PixivWorkExtractor,
    "#sha1_url"    : "90c1715b07b0d1aad300bce256a0bc71f42540ba",
    "#sha1_content": "69a8edfb717400d1c2e146ab2b30d2c235440c5a",

    "count"   : 1,
    "num"     : 0,
    "date"    : "dt:2008-06-12 15:29:13",
    "date_url": "dt:2008-06-12 15:29:13",
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=966411",
    "#class"   : pixiv.PixivWorkExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=66806629",
    "#comment" : "ugoira",
    "#class"   : pixiv.PixivWorkExtractor,
    "#results" : "https://i.pximg.net/img-zip-ugoira/img/2018/01/15/13/24/48/66806629_ugoira1920x1080.zip",

    "frames"  : list,
    "count"   : 1,
    "date"    : "dt:2018-01-14 15:06:08",
    "date_url": "dt:2018-01-15 04:24:48",
},

{
    "#url"     : "https://www.pixiv.net/artworks/101003492",
    "#comment" : "original ugoira frames (#6056)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"ugoira": "original"},
    "#results" : (
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira0.png",
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira1.png",
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira2.png",
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira3.png",
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira4.png",
        "https://i.pximg.net/img-original/img/2022/09/04/23/54/19/101003492_ugoira5.png",
    ),

    "frames": list,
    "count" : 6,
},

{
    "#url"     : "https://www.pixiv.net/artworks/966412",
    "#comment" : "related works (#1237)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"related": True},
    "#range"   : "1-10",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.pixiv.net/artworks/85960783",
    "#comment" : "limit_sanity_level_360.png (#4327, #5180)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"sanity": False},
    "#count"   : 0,
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/102932581",
    "#comment" : "limit_sanity_level_360.png (#4327, #5180)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"sanity": True, "comments": True},
    "#results" : "https://i.pximg.net/img-original/img/2022/11/20/00/00/49/102932581_p0.jpg",

    "caption"       : "Meet a deer .",
    "comment_access_control": 0,
    "comments"      : (),
    "count"         : 1,
    "create_date"   : "2022-11-19T15:00:00+00:00",
    "date"          : "dt:2022-11-19 15:00:00",
    "date_url"      : "dt:2022-11-19 15:00:49",
    "extension"     : "jpg",
    "filename"      : "102932581_p0",
    "height"        : 3840,
    "id"            : 102932581,
    "illust_ai_type": 1,
    "illust_book_style": 0,
    "is_bookmarked" : False,
    "is_muted"      : False,
    "num"           : 0,
    "page_count"    : 1,
    "rating"        : "General",
    "restrict"      : 0,
    "sanity_level"  : 2,
    "series"        : None,
    "suffix"        : "",
    "title"         : "《 Bridge and Deer 》",
    "tools"         : [],
    "total_bookmarks": range(1900, 3000),
    "total_comments": range(3, 10),
    "total_view"    : range(11000, 20000),
    "type"          : "illust",
    "url"           : "https://i.pximg.net/img-original/img/2022/11/20/00/00/49/102932581_p0.jpg",
    "visible"       : False,
    "width"         : 2160,
    "x_restrict"    : 0,
    "image_urls"    : {
        "mini"    : "https://i.pximg.net/c/48x48/custom-thumb/img/2022/11/20/00/00/49/102932581_p0_custom1200.jpg",
        "original": "https://i.pximg.net/img-original/img/2022/11/20/00/00/49/102932581_p0.jpg",
        "regular" : "https://i.pximg.net/img-master/img/2022/11/20/00/00/49/102932581_p0_master1200.jpg",
        "small"   : "https://i.pximg.net/c/540x540_70/img-master/img/2022/11/20/00/00/49/102932581_p0_master1200.jpg",
        "thumb"   : "https://i.pximg.net/c/250x250_80_a2/custom-thumb/img/2022/11/20/00/00/49/102932581_p0_custom1200.jpg",
    },
    "tags"          : [
        "オリジナル",
        "風景",
        "イラスト",
        "illustration",
        "美しい",
        "女の子",
        "少女",
        "deer",
        "flower",
        "spring",
    ],
    "user"          : {
        "account"    : "805482263",
        "id"         : 7386235,
        "is_followed": False,
        "name"       : "岛的鲸",
        "profile_image_urls": {},
    },
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/109487939",
    "#comment" : "R-18 limit_sanity_level_360.png (#4327, #5180)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#results" : (
        "https://i.pximg.net/img-original/img/2023/07/01/00/06/28/109487939_p0.png",
        "https://i.pximg.net/img-original/img/2023/07/01/00/06/28/109487939_p1.png",
        "https://i.pximg.net/img-original/img/2023/07/01/00/06/28/109487939_p2.png",
        "https://i.pximg.net/img-original/img/2023/07/01/00/06/28/109487939_p3.png",
    ),
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/103841583",
    "#comment" : "Ugoira limit_sanity_level_360.png (#4327 #6297 #7285)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#auth"    : True,
    "#results" : "https://i.pximg.net/img-zip-ugoira/img/2022/12/23/23/36/13/103841583_ugoira1920x1080.zip",
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/104582860",
    "#comment" : "deleted limit_sanity_level_360.png work (#6339)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#count"   : 0,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/103983466",
    "#comment" : "empty 'caption' in App API response (#4327, #5191)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"captions": True},

    "caption": r"re:Either she doesn't know how to pose or she can't move with that much clothing on her, in any case she's very well dressed for a holiday trip around town. Lots of stuff to see and a perfect day to grab some sweet pastries at the bakery.<br />...",
},

{
    "#url"     : "https://www.pixiv.net/artworks/56360615",
    "#comment" : "fallback; 'original' version results in HTTP 500 error (#6762)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#options" : {"retries": 0},
    "#range"   : "4",
    "#sha1_content": "aa119c27fec0a36bbd06e7491987acf5f1be6293",
},

{
    "#url"     : "https://www.pixiv.net/artworks/56360615",
    "#comment" : "limit_unviewable_s / unavailable without cookies (#7940)",
    "#class"   : pixiv.PixivWorkExtractor,
    "#count"   : 11,
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/966412",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=96641",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://i1.pixiv.net/c/600x600/img-master/img/2008/06/13/00/29/13/966412_p0_master1200.jpg",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://i.pximg.net/img-original/img/2017/04/25/07/33/29/62568267_p0.png",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://www.pixiv.net/i/966412",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://img.pixiv.net/img/soundcross/42626136.jpg",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "http://i2.pixiv.net/img76/img/snailrin/42672235.jpg",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://www.phixiv.net/en/artworks/966412",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://phixiv.net/member_illust.php?mode=medium&illust_id=966412",
    "#class"   : pixiv.PixivWorkExtractor,
},

{
    "#url"     : "https://www.pixiv.net/en/artworks/unlisted/eE3fTYaROT9IsZmep386",
    "#class"   : pixiv.PixivUnlistedExtractor,
    "#results" : "https://i.pximg.net/img-original/img/2020/10/15/00/46/12/85017704-149014193e4d3e23a6b8bd5e38b51ed4_p0.png",

    "id"         : 85017704,
    "id_unlisted": "eE3fTYaROT9IsZmep386",
},

{
    "#url"     : "https://www.pixiv.net/en/users/173530/bookmarks/artworks",
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#results" : (
        "https://i.pximg.net/img-original/img/2025/06/25/02/06/58/131943241_p0.png",
        "https://i.pximg.net/img-original/img/2025/07/02/03/22/51/132200601_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/10/31/17/54/01/2005108_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/09/27/12/22/40/1719386_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/04/15/01/43/46/669358_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/06/19/21/52/15/1005851_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/06/17/22/16/54/994965_p0.jpg",
    ),
    "#log": (
        ("warning", "1679677: 'My pixiv' locked"),
    ),
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?id=173530",
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#results" : (
        "https://i.pximg.net/img-original/img/2025/06/25/02/06/58/131943241_p0.png",
        "https://i.pximg.net/img-original/img/2025/07/02/03/22/51/132200601_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/10/31/17/54/01/2005108_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/09/27/12/22/40/1719386_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/04/15/01/43/46/669358_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/06/19/21/52/15/1005851_p0.jpg",
        "https://i.pximg.net/img-original/img/2008/06/17/22/16/54/994965_p0.jpg",
    ),
    "#log": (
        ("warning", "1679677: 'My pixiv' locked"),
    ),
},

{
    "#url"     : "https://www.pixiv.net/en/users/3137110/bookmarks/artworks/%E3%81%AF%E3%82%93%E3%82%82%E3%82%93",
    "#comment" : "bookmarks with specific tag",
    "#class"   : pixiv.PixivFavoriteExtractor,
    "#sha1_url": "379b28275f786d946e01f721e54afe346c148a8c",
},

{
    "#url"     : "https://www.pixiv.net/bookmark.php?id=3137110&tag=%E3%81%AF%E3%82%93%E3%82%82%E3%82%93&p=1",
    "#comment" : "bookmarks with specific tag (legacy url)",
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
    "#class"   : pixiv.PixivFavoriteExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/bookmark.php",
    "#category": ("", "pixiv", "bookmark"),
    "#class"   : pixiv.PixivFavoriteExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php?mode=daily&date=20170818",
    "#class"   : pixiv.PixivRankingExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php",
    "#class"   : pixiv.PixivRankingExtractor,
    "#options" : {"max-posts": 10},

    "ranking": {
        "date": r"re:\d\d\d\d-\d\d-\d\d",
        "mode": "day",
        "rank": range(1, 10),
    },
},

{
    "#url"     : "https://touch.pixiv.net/ranking.php",
    "#class"   : pixiv.PixivRankingExtractor,
},

{
    "#url"     : "https://www.pixiv.net/ranking.php?mode=unknown",
    "#class"   : pixiv.PixivRankingExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://www.pixiv.net/en/tags/Original",
    "#class"   : pixiv.PixivSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://pixiv.net/en/tags/foo/artworks?order=week&s_mode=s_tag",
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://pixiv.net/en/tags/foo/artworks?order=date&s_mode=tag",
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://www.pixiv.net/search.php?s_mode=s_tag&name=Original",
    "#class"   : pixiv.PixivSearchExtractor,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://www.pixiv.net/en/tags/foo/artworks?order=date&s_mode=s_tag",
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://www.pixiv.net/search.php?s_mode=s_tag&word=Original",
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/search.php?word=Original",
    "#class"   : pixiv.PixivSearchExtractor,
},

{
    "#url"     : "https://www.pixiv.net/bookmark_new_illust.php",
    "#class"   : pixiv.PixivFollowExtractor,
},

{
    "#url"     : "https://touch.pixiv.net/bookmark_new_illust.php",
    "#class"   : pixiv.PixivFollowExtractor,
},

{
    "#url"     : "https://www.pixivision.net/en/a/2791",
    "#class"   : pixiv.PixivPixivisionExtractor,
},

{
    "#url"     : "https://pixivision.net/a/2791",
    "#class"   : pixiv.PixivPixivisionExtractor,
    "#count"   : 7,

    "pixivision_id"   : "2791",
    "pixivision_title": "What's your favorite music? Editor’s picks featuring: “CD Covers”!",
},

{
    "#url"     : "https://www.pixiv.net/user/10509347/series/21859",
    "#class"   : pixiv.PixivSeriesExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "num_series": int,
    "series"    : {
        "create_date": "2017-10-22T14:07:42+09:00",
        "width" : 4250,
        "height": 3009,
        "id"    : 21859,
        "title" : "先輩がうざい後輩の話",
        "total" : range(100, 500),
        "user"  : dict,
        "watchlist_added": False,
    },
},

{
    "#url"     : "https://sketch.pixiv.net/@nicoby",
    "#class"   : pixiv.PixivSketchExtractor,
    "#pattern" : r"https://img\-sketch\.pixiv\.net/uploads/medium/file/\d+/\d+\.(jpg|png)",
    "#count"   : ">= 35",

    "date": "type:datetime",
},

)
