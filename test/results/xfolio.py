# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xfolio
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://xfolio.jp/portfolio/yutakashii/works/23977",
    "#comment" : "original 'fullscale_image' files",
    "#class"   : xfolio.XfolioWorkExtractor,
    "#results" : (
        "https://xfolio.jp/user_asset.php?id=113179&work_id=23977&work_image_id=113179&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113182&work_id=23977&work_image_id=113182&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113185&work_id=23977&work_image_id=113185&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113188&work_id=23977&work_image_id=113188&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113191&work_id=23977&work_image_id=113191&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113194&work_id=23977&work_image_id=113194&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113197&work_id=23977&work_image_id=113197&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113200&work_id=23977&work_image_id=113200&type=work_image",
        "https://xfolio.jp/user_asset.php?id=113203&work_id=23977&work_image_id=113203&type=work_image",
    ),

    "count"          : 9,
    "num"            : range(1, 9),
    "creator_id"     : "1495",
    "creator_name"   : "香椎ゆたか",
    "creator_profile": "連載中：「いつまでも可愛くしてると思うなよ！」 https://booklive.jp/product/index/title_id/10003104/vol_no/001\r\n 過去作：「まじとら！」「男友達ガール」\r\npixiv：http://pixiv.me/yutakashii\r\nskeb：http://skeb.jp/@yutakashii",
    "creator_slug"   : "yutakashii",
    "creator_userid" : "3778",
    "description"    : "BookLive NINOにて「男友達ガール」連載開始しました。ルームシェア＋TSFで、ある日突然同居人が可愛い女の子になったら…という感じのラブ(？)コメディ...",
    "extension"      : "jpg",
    "image_id"       : r"re:113\d\d\d",
    "series_id"      : "",
    "title"          : "新連載「男友達ガール」冒頭試し読み",
    "url"            : str,
    "work_id"        : "23977",
},

{
    "#url"     : "https://xfolio.jp/en/portfolio/amakawatamawono/works/87495",
    "#comment" : "'.webp' image",
    "#class"   : xfolio.XfolioWorkExtractor,
    "#results" : "https://assets.xfolio.jp/secure/1359786657/creator/6030/works/87495/305223_ryhzvHjwcY.webp?hash=IBd5Zt2fWIzYkJGR3AvRCQ&expires=1774386000",
    "#sha1_content": "4c2a471360268f50c8b49db3431ebe53b599635d",

    "count"          : 1,
    "creator_id"     : "6030",
    "creator_name"   : "天川たまを〜",
    "creator_profile": "",
    "creator_slug"   : "amakawatamawono",
    "creator_userid" : "12192",
    "description"    : "",
    "extension"      : "webp",
    "image_id"       : "1359786657",
    "num"            : 1,
    "series_id"      : "1257",
    "title"          : "鈴の音も聞こえない",
    "url"            : "https://assets.xfolio.jp/secure/1359786657/creator/6030/works/87495/305223_ryhzvHjwcY.webp?hash=IBd5Zt2fWIzYkJGR3AvRCQ&expires=1774386000",
    "work_id"        : "87495",
},

{
    "#url"     : "https://xfolio.jp/en/portfolio/solanokoart/works/190895",
    "#comment" : "'fullsize' zip archive",
    "#class"   : xfolio.XfolioWorkExtractor,
    "#auth"    : True,
    "#results" : "https://xfolio.jp/user_asset.php?id=190895&type=work_zip",

    "creator_id"     : "15773",
    "creator_name"   : "solanoko",
    "creator_userid" : "30248",
    "description"    : "過去に公開済みの作品。",
    "extension"      : "zip",
    "image_id"       : 0,
    "title"          : "The Jorts Incident",
    "work_id"        : "190895",
},

{
    "#url"     : "https://xfolio.jp/portfolio/yutakashii",
    "#class"   : xfolio.XfolioUserExtractor,
    "#pattern" : xfolio.XfolioWorkExtractor.pattern,
    "#count"   : range(50, 100),
},

{
    "#url"     : "https://xfolio.jp/portfolio/yutakashii/works",
    "#class"   : xfolio.XfolioUserExtractor,
},
{
    "#url"     : "https://xfolio.jp/portfolio/yutakashii/works?page=3",
    "#class"   : xfolio.XfolioUserExtractor,
},
{
    "#url"     : "https://xfolio.jp/en/portfolio/yutakashii",
    "#class"   : xfolio.XfolioUserExtractor,
},
{
    "#url"     : "https://xfolio.jp/ko/portfolio/yutakashii",
    "#class"   : xfolio.XfolioUserExtractor,
},
{
    "#url"     : "https://xfolio.jp/zh-CN/portfolio/yutakashii",
    "#class"   : xfolio.XfolioUserExtractor,
},

{
    "#url"      : "https://xfolio.jp/portfolio/donguri/series/1391402",
    "#class"    : xfolio.XfolioSeriesExtractor,
    "#auth"     : False,
    "#exception": exception.AbortExtraction,
},

{
    "#url"     : "https://xfolio.jp/portfolio/donguri/series/1391402",
    "#class"   : xfolio.XfolioSeriesExtractor,
    "#auth"    : True,
    "#results" : (
        "https://xfolio.jp/portfolio/donguri/works/2472402",
        "https://xfolio.jp/portfolio/donguri/works/2470700",
    ),
},

)
