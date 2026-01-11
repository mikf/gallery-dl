# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import booth


__tests__ = (
{
    "#url"     : "https://booth.pm/ja/items/4693741",
    "#class"   : booth.BoothItemExtractor,
    "#pattern" : r"https://booth.pximg.net/792d497b-6e82-4df3-86de-31577e10f476/i/4693741/[\w-]{36}\.(jpg|png)",
    "#count"   : 10,

    "!_fallback"      : ...,
    "buyee_variations": [],
    "count"           : 10,
    "num"             : range(1, 10),
    "date"            : "dt:2023-04-16 14:25:29",
    "description"     : """※※英語版※※
【踏切の音はもう聞こえない。の英訳ver.のダウンロード版になります。】
【This is the downloadable version of the English translation ver.】

Goto Hitori is 25 years old.
She loses all hope and tries to jump into a railroad crossing.
But at that moment, She is transported back in time to that era...?

The story is spun by the tag-team of manga and music,
The story of Bocchi-chan's inspiration and courage.

The set includes the manga book and a download card for the music (doujin music)!
Please enjoy the world of Bocchi ·the·rock! brought to you by "Futari Bocchi no Solitude".

wano-Twitter
https://twitter.com/wano49

Japanese version
https://www.melonbooks.co.jp/detail/detail.php?product_id=1872452""",
    "embeds"          : [],
    "extension"       : "jpg",
    "factory_description": None,
    "filename"        : str,
    "gift"            : None,
    "id"              : 4693741,
    "is_adult"        : False,
    "is_buyee_possible": False,
    "is_end_of_sale"  : False,
    "is_placeholder"  : False,
    "is_sold_out"     : False,
    "name"            : "※英語版※ I can no longer hear the railway crossing.【Bocchi the rock!】",
    "order"           : None,
    "price"           : "¥ 700",
    "published_at"    : "2023-04-16T23:25:29.000+09:00",
    "purchase_limit"  : None,
    "report_url"      : "https://wanoazayaka.booth.pm/items/4693741/report",
    "shipping_info"   : "支払いから発送までの日数：4日以内",
    "small_stock"     : None,
    "sound"           : None,
    "tracks"          : None,
    "url"             : str,
    "wish_list_url"   : "https://booth.pm/items/4693741/wish_list",
    "wish_lists_count": range(80, 120),
    "wished"          : False,
    "tag_banners"     : "len:list:5",
    "booth_category"  : {
        "id"    : 56,
        "name"  : "漫画・マンガ",
        "url"   : "https://booth.pm/ja/browse/%E6%BC%AB%E7%94%BB%E3%83%BB%E3%83%9E%E3%83%B3%E3%82%AC",
        "parent": {
            "name": "漫画",
            "url" : "https://booth.pm/ja/browse/%E6%BC%AB%E7%94%BB",
        },
    },
    "share"           : {
        "hashtags": ["booth_pm"],
        "text"    : "※英語版※ I can no longer hear the railway crossing.【Bocchi the rock!】 | ふたりぼっちのSolitude",
    },
    "shop"            : {
        "id"           : 5742915,
        "uuid"         : "792d497b-6e82-4df3-86de-31577e10f476",
        "name"         : "ふたりぼっちのSolitude",
        "subdomain"    : "wanoazayaka",
        "thumbnail_url": "https://booth.pximg.net/c/48x48/users/5742915/icon_image/1448e5d8-f93f-445e-8e1e-acb29aa45aa4_base_resized.jpg",
        "url"          : "https://wanoazayaka.booth.pm/",
        "verified"     : False,
    },
    "tag_combination" : {
        "category": "漫画・マンガ",
        "tag"     : "ぼっち・ざ・ろっく!",
        "url"     : "https://booth.pm/ja/browse/%E6%BC%AB%E7%94%BB%E3%83%BB%E3%83%9E%E3%83%B3%E3%82%AC?tags%5B%5D=%E3%81%BC%E3%81%A3%E3%81%A1%E3%83%BB%E3%81%96%E3%83%BB%E3%82%8D%E3%81%A3%E3%81%8F%21",
    },
    "tags"            : [
        "ぼっち・ざ・ろっく!",
        "ぼっちざろっく",
        "ぼっち・ざ・ろっく",
        "Bocchi the Rock!",
        "BocchiTheRock",
    ],
    "variations"      : [{
        "buyee_html"     : None,
        "downloadable"   : None,
        "factory_image_url": None,
        "has_download_code": False,
        "id"             : 7869860,
        "is_anshin_booth_pack": False,
        "is_empty_allocatable_stock_with_preorder": False,
        "is_empty_stock" : False,
        "is_factory_item": False,
        "is_mailbin"     : False,
        "is_waiting_on_arrival": False,
        "name"           : None,
        "order_url"      : None,
        "price"          : 700,
        "small_stock"    : None,
        "status"         : "addable_to_cart",
        "type"           : "digital",
    }],
},

{
    "#url"     : "https://caramel-crunch.booth.pm/items/7236173?utm_source=pixiv&utm_medium=popboard&utm_campaign=popboard",
    "#class"   : booth.BoothItemExtractor,
    "#results" : (
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/131bf61c-0534-4af3-9408-f19f08cb3622.jpg",
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/fb65233a-7a93-4219-ba9f-b63e11329fda.jpg",
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/e18c16a0-b285-4cd8-aacc-6b3c4f4c6ce3.jpeg",
    ),

    "!_fallback"      : ...,
    "count"           : 3,
    "date"            : "dt:2025-07-28 07:00:43",
    "description"     : """C106新作おっぱいマウスパッドです
コミケ開始時間に合わせてカート開放します
■お届け9月中旬頃～予定
印刷：熱転写
素材：表面/SuperSmooth Fabric　裏面/PUゲル

乳首パーツ付き
ブリスターパック封入

納品済みの為数量限定です。
数がなくなり次第終了となります。

当日コミケにも持ち込みます。
2日目,東7ホール Ａ26ab CARAMEL CRUNCH!""",
    "id"              : 7236173,
    "is_adult"        : True,
    "is_buyee_possible": False,
    "is_end_of_sale"  : False,
    "is_placeholder"  : False,
    "is_sold_out"     : False,
    "name"            : "こ〇ちゃんおっぱいマウスパッド(乳首パーツ付き)",
    "price"           : "¥ 6,500",
    "published_at"    : "2025-07-28T16:00:43.000+09:00",
    "purchase_limit"  : 1,
    "shipping_info"   : "支払いから発送までの日数：7日以内",
    "booth_category"  : {
        "id"    : 171,
        "name"  : "マウスパッド",
        "url"   : "https://booth.pm/ja/browse/%E3%83%9E%E3%82%A6%E3%82%B9%E3%83%91%E3%83%83%E3%83%89",
        "parent": {
            "name": "グッズ",
            "url" : "https://booth.pm/ja/browse/%E3%82%B0%E3%83%83%E3%82%BA",
        },
    },
    "shop"            : {
        "id"           : 49832,
        "uuid"         : "74488d0d-e533-443c-82ce-fa961d5cbaf0",
        "name"         : "ＣＡＲＡＭＥＬ　ＣＲＵＮＣＨ！",
        "subdomain"    : "caramel-crunch",
        "thumbnail_url": "https://booth.pximg.net/c/48x48/users/49832/icon_image/a240e313-6a0f-4155-8310-a0d6abb299e6_base_resized.jpg",
        "url"          : "https://caramel-crunch.booth.pm/",
        "verified"     : False,
    },
    "tag_combination" : {
        "category": "マウスパッド",
        "tag"     : "おっぱいマウスパッド",
        "url"     : "https://booth.pm/ja/browse/%E3%83%9E%E3%82%A6%E3%82%B9%E3%83%91%E3%83%83%E3%83%89?tags%5B%5D=%E3%81%8A%E3%81%A3%E3%81%B1%E3%81%84%E3%83%9E%E3%82%A6%E3%82%B9%E3%83%91%E3%83%83%E3%83%89",
    },
    "tags"            : [
        "おっぱいマウスパッド",
        "C106",
        "c106新作",
    ],
},

{
    "#url"     : "https://caramel-crunch.booth.pm/items/7236173",
    "#class"   : booth.BoothItemExtractor,
    "#options" : {"strategy": "fallback"},
    "#results" : (
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/131bf61c-0534-4af3-9408-f19f08cb3622.jpg",
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/fb65233a-7a93-4219-ba9f-b63e11329fda.jpg",
        "https://booth.pximg.net/74488d0d-e533-443c-82ce-fa961d5cbaf0/i/7236173/e18c16a0-b285-4cd8-aacc-6b3c4f4c6ce3.jpg",
    ),

    "_fallback": "len:3",
},

{
    "#url"     : "https://booth.pm/zh-cn/items/1895090",
    "#comment" : "URL with language code",
    "#class"   : booth.BoothItemExtractor,
},

{
    "#url"     : "https://wanoazayaka.booth.pm/",
    "#class"   : booth.BoothShopExtractor,
    "#results" : (
        "https://wanoazayaka.booth.pm/items/4972816",
        "https://wanoazayaka.booth.pm/items/4855567",
        "https://wanoazayaka.booth.pm/items/4693741",
    ),

    "event"         : None,
    "id"            : int,
    "is_adult"      : False,
    "is_end_of_sale": False,
    "is_placeholder": False,
    "is_sold_out"   : False,
    "is_vrchat"     : False,
    "minimum_stock" : None,
    "music"         : None,
    "name"          : str,
    "price"         : "700 JPY",
    "url"           : r"re:https://booth.pm/en/items/\d+",
    "shop_item_url" : r"re:https://wanoazayaka.booth.pm/items/\d+",
    "wish_list_url" : r"re:https://wanoazayaka.booth.pm/items/\d+/wish_list",
    "thumbnail_image_urls": list,
    "shop"          : {
        "name"         : "ふたりぼっちのSolitude",
        "thumbnail_url": "https://booth.pximg.net/c/48x48/users/5742915/icon_image/1448e5d8-f93f-445e-8e1e-acb29aa45aa4_base_resized.jpg",
        "url"          : "https://wanoazayaka.booth.pm/",
        "verified"     : False,
    },
    "tracking_data" : {
        "product_brand"   : "wanoazayaka",
        "product_category": 56,
        "product_event"   : None,
        "product_id"      : int,
        "product_name"    : str,
        "product_price"   : 700,
        "tracking"        : "impression_item",
    },
},

{
    "#url"     : "https://caramel-crunch.booth.pm/items",
    "#class"   : booth.BoothShopExtractor,
    "#pattern" : booth.BoothItemExtractor.pattern,
    "#count"   : range(90, 120),

    "shop": {
        "name"         : "ＣＡＲＡＭＥＬ　ＣＲＵＮＣＨ！",
        "thumbnail_url": "https://booth.pximg.net/c/48x48/users/49832/icon_image/a240e313-6a0f-4155-8310-a0d6abb299e6_base_resized.jpg",
        "url"          : "https://caramel-crunch.booth.pm/",
        "verified"     : False,
    },
},

{
    "#url"     : "https://booth.pm/en/browse/Audio%20Goods?adult=only&max_price=3000",
    "#class"   : booth.BoothCategoryExtractor,
    "#pattern" : booth.BoothItemExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://booth.pm/zh-cn/browse/Books%20(Other)",
    "#class"   : booth.BoothCategoryExtractor,
    "#pattern" : booth.BoothItemExtractor.pattern,
    "#range"   : "1-100",
    "#count"   : 100,
},

)
