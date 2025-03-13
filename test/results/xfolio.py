# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xfolio
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://xfolio.jp/portfolio/yutakashii/works/23977",
    "#class"   : xfolio.XfolioWorkExtractor,
    "#urls"    : (
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
    "#exception": exception.StopExtraction,
},

{
    "#url"     : "https://xfolio.jp/portfolio/donguri/series/1391402",
    "#class"   : xfolio.XfolioSeriesExtractor,
    "#auth"    : True,
    "#urls"    : (
        "https://xfolio.jp/portfolio/donguri/works/2472402",
        "https://xfolio.jp/portfolio/donguri/works/2470700",
    ),
},

)
