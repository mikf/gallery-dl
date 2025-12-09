# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import sankaku
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://sankaku.app/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/o/[^/]{2}/[^/]{2}/[0-9a-f]{32}\.\w+\?e=\d+&(expires=\d+&)?m=[^&#]+",
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://black.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://white.sankakucomplex.com/?tags=bonocho",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/ja?tags=order%3Apopularity",
    "#comment" : "ISO 639-1",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/no/?tags=order%3Apopularity",
    "#comment" : "ISO 639-1 with trailing '/'",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/zh-CN/?tags=order%3Apopularity",
    "#comment" : "locale code (ISO 639-1 + ISO 3166-1) (#8667)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://sankaku.app/zh_CN/?tags=order%3Apopularity",
    "#comment" : "locale code (ISO 639-1 + ISO 3166-1) (#8667)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/posts?tags=TAG",
    "#comment" : "'/posts' in tag search URL (#4740)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/ja/posts/?tags=あえいおう",
    "#comment" : "'/posts' in tag search URL (#4740)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=bonocho+a+b+c+d",
    "#comment" : "error on five or more tags",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#options"  : {"username": None},
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=marie_rose&page=98&next=3874906&commit=Search",
    "#comment" : "match arbitrary query parameters",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=date:2023-03-20T00:00",
    "#comment" : "'date:' tags (#1790)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#range"   : "1",
    "#count"   : 1,
},

{
    "#url"     : "https://chan.sankakucomplex.com/?tags=date:2023-03-20",
    "#comment" : "'date:' tags (#1790)",
    "#category": ("booru", "sankaku", "tag"),
    "#class"   : sankaku.SankakuTagExtractor,
    "#range"   : "1",
    "#count"   : 1,
},

{
    "#url"     : "https://sankaku.app/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://www.sankakucomplex.com/books/8YEa7EERmD0",
    "#comment" : "alphanumeric book/pool ID (#6757)",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
    "#count"   : 5,
},

{
    "#url"     : "https://www.sankakucomplex.com/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/books/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/pool/show/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/pools/show/90",
    "#category": ("booru", "sankaku", "pool"),
    "#class"   : sankaku.SankakuPoolExtractor,
},

{
    "#url"     : "https://sankaku.app/posts/y0abGlDOr2o",
    "#comment" : "extended tag categories; alphanumeric ID (#5073)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options"     : {
        "tags"     : True,
        "notes"    : True,
        "id-format": "alphanumeric",
    },
    "#sha1_content": "5e255713cbf0a8e0801dc423563c34d896bb9229",

    "id": "y0abGlDOr2o",
    "notes": (),
    "tags_artist": [
        "bonocho",
    ],
    "tags_character": [
        "batman",
        "letty_whiterock",
        "bruce_wayne",
        "the_joker",
        "heath_ledger",
    ],
    "tags_copyright": [
        "batman_(series)",
        "the_dark_knight",
    ],
    "tags_studio": [
        "dc_comics",
    ],
    "tags_general": list,
},

{
    "#url"     : "https://sankaku.app/posts/y0abGlDOr2o",
    "#comment" : "new tag categories (#7333)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": "extended"},

    "id": "y0abGlDOr2o",
    "tags_anatomy": [
        "brown_eyes",
        "male",
        "upper_body",
    ],
    "tags_artist": [
        "bonocho",
    ],
    "tags_character": [
        "batman",
        "letty_whiterock",
        "bruce_wayne",
        "the_joker",
        "heath_ledger",
    ],
    "tags_copyright": [
        "batman_(series)",
        "the_dark_knight",
    ],
    "tags_fashion": [
        "black_bodysuit",
        "bodysuit",
        "clothing",
        "collared_shirt",
        "facepaint",
        "pink_shirt",
        "shirt",
        "wing_collar",
    ],
    "tags_studio": [
        "dc_comics",
    ],
},

{
    "#url"     : "https://sankaku.app/posts/9PMwlDWjXaB",
    "#comment" : ">100 tags",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": True},

    "id"  : "9PMwlDWjXaB",
    "md5" : "dc9a3cbfcfee836779bc4f8d5d95c346",
    "tags": "len:106",

    "tags_copyright": [
        "mahou_shoujo_madoka_magica",
        "mahou_shoujo_madoka_magica:_hangyaku_no_monogatari",
    ],
    "tags_studio": [
        "pixiv",
    ],
    "tags_character": [
        "akemi_homura",
        "kaname_madoka",
        "akuma_homura",
        "kaname_madoka_(magical_girl)",
    ],
    "tags_artist": [
        "mie_haha",
    ],
    "tags_genre": [
        "size_difference",
        "giant",
        "giantess",
    ],
    "tags_general": [
        "clothing",
        "tied_hair",
        "headwear",
        "hair_ornament",
        "bangs",
        "skirt",
        "footwear",
        "gloves",
        "dress",
        "twintails",
        "ribbon",
        "bow",
        "shoes",
        "hair_ribbon",
        "boots",
        "hairband",
        "hair_bow",
        "short_sleeves",
        "choker",
        "frills",
        "makeup",
        "high_heels",
        "white_gloves",
        "puffy_sleeves",
        "miniskirt",
        "black_footwear",
        "black_dress",
        "red_bow",
        "red_ribbon",
        "puffy_short_sleeves",
        "eyeshadow",
        "short_twintails",
        "frilled_dress",
        "white_skirt",
        "pink_bow",
        "pink_dress",
        "frilled_skirt",
        "high_heel_boots",
        "frilled_sleeves",
        "white_sleeves",
        "red_hairband",
        "center_frills",
        "red_choker",
        "pink_choker",
        "pink_eyeshadow",
        "crystal_wings",
        "female",
        "long_hair",
        "short_hair",
        "black_hair",
        "pink_hair",
        "wings",
        "pink_eyes",
        "eyelashes",
        "feathers",
        "feathered_wings",
        "black_wings",
        "standing",
        "closed_mouth",
        "frown",
        "outstretched_arms",
        "holding",
        "looking_at_another",
        "looking_down",
        "holding_doll",
        "magical_girl",
        "sparkle",
        "buttons",
        "glass",
        "doll",
        "character_doll",
        "broken_glass",
        "pink_gemstone",
        "bodily_fluids",
        "tears",
        "1girl",
        "solo",
        "multiple_girls",
        "2girls",
        "stairs",
        "bow_choker",
        "button_eyes",
        "chest_jewel",
        "mahou_shoujo_madoka_magica_(anime)",
        "pendant_choker",
        "shards",
        "soul_gem",
        "square_neckline",
        "surreal",
        "high_resolution",
        "very_high_resolution",
        "large_filesize",
    ],
    "tags_medium": [
        "gradient",
        "gradient_background",
        "black_background",
    ],
},

{
    "#url"     : "https://www.sankakucomplex.com/posts/26MPkn6JRKx",
    "#comment" : "each tag is tripled, wrong 'total' count in /tags API",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": True},

    "id": "26MPkn6JRKx",
    "md5": "a115c0cfbad8e915f046a72973bbd47e",
    "total_tags": 39,
    "tags": [
        "tengen_toppa_gurren-lagann",
        "tengen_toppa_gurren-lagann",
        "tengen_toppa_gurren-lagann",
        "yoko_littner",
        "yoko_littner",
        "yoko_littner",
        "high_resolution",
        "high_resolution",
        "high_resolution",
        "bangs",
        "bangs",
        "bangs",
        "female",
        "female",
        "female",
        "golden_eyes",
        "golden_eyes",
        "golden_eyes",
        "long_hair",
        "long_hair",
        "long_hair",
        "ponytail",
        "ponytail",
        "ponytail",
        "red_hair",
        "red_hair",
        "red_hair",
        "solo",
        "solo",
        "solo",
        "tied_hair",
        "tied_hair",
        "tied_hair",
        "yellow_eyes",
        "yellow_eyes",
        "yellow_eyes",
        "potential_duplicate",
        "potential_duplicate",
        "potential_duplicate",
    ],
    "tags_copyright": [
        "tengen_toppa_gurren-lagann",
    ],
    "tags_character": [
        "yoko_littner",
    ],
    "tags_general": [
        "tied_hair",
        "bangs",
        "ponytail",
        "female",
        "long_hair",
        "yellow_eyes",
        "red_hair",
        "golden_eyes",
        "solo",
        "high_resolution",
    ],
    "tags_meta": [
        "potential_duplicate",
    ],
},

{
    "#url"     : "https://sankaku.app/posts/VAr2mjLJ2av",
    "#comment" : "notes (#5073)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"notes": True},

    "notes": [
        {
            "body"      : "A lonely person, is a lonely person, because he or she is lonely.",
            "created_at": 1643733759,
            #  "creator_id": 1370766,
            "creator_id": "WKaoQv7VRJ0",
            "height"    : 871,
            #  "id"        : 1832643,
            "id"        : "e8M5EmNZMzv",
            "is_active" : True,
            #  "post_id"   : 23688624,
            "post_id"   : "VAr2mjLJ2av",
            "updated_at": 1643733759,
            "width"     : 108,
            "x"         : 703,
            "y"         : 83,
        },
    ],
},

{
    #  "#url"     : "https://sankaku.app/post/show/360451",
    "#url"     : "https://sankaku.app/post/show/y0abGlDOr2o",
    "#comment" : "legacy post URL",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/o/ac/8e/ac8e3b92ea328ce9cf7211e69c905bf9\.jpg\?e=.+",

    #  "id": 360451,
    "id": "y0abGlDOr2o",
},

{
    "#url"     : "https://www.sankakucomplex.com/posts/8JaGbKW4eML",
    "#comment" : "'contentious_content'",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#auth"    : True,
    "#pattern" : r"https://s\.sankakucomplex\.com/o/13/3c/133cda3bfde249c504284493903fb985\.jpg",

    "md5": "133cda3bfde249c504284493903fb985",
},

{
    "#url"     : "https://sankaku.app/post/show/20758561",
    "#comment" : "empty tags (#1617)",
    "#skip"    : "legacy, now unsupported, numerical post ID",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#options" : {"tags": True},
    "#count"   : 1,

    "id"          : 20758561,
    "tags"        : list,
    "tags_general": [
        "key(mangaka)",
        "key(mangaka)",
        "english_language",
        "english_language",
        "high_resolution",
        "tagme",
        "very_high_resolution",
        "large_filesize",
    ],
},

{
    "#url"     : "https://chan.sankakucomplex.com/post/show/f8ba89043078f0e4be2d9c46550b840a",
    "#comment" : "md5 hexdigest instead of ID (#3952)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/o/f8/ba/f8ba89043078f0e4be2d9c46550b840a\.jpg",
    "#count"   : 1,

    #  "id" : 33195194,
    "id" : "k3R93nWBqaG",
    "md5": "f8ba89043078f0e4be2d9c46550b840a",
},

{
    "#url"     : "https://chan.sankakucomplex.com/posts/f8ba89043078f0e4be2d9c46550b840a",
    "#comment" : "/posts/ instead of /post/show/ (#4688)",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
    "#pattern" : r"https://s\.sankakucomplex\.com/o/f8/ba/f8ba89043078f0e4be2d9c46550b840a\.jpg",
    "#count"   : 1,

    #  "id" : 33195194,
    "id" : "k3R93nWBqaG",
    "md5": "f8ba89043078f0e4be2d9c46550b840a",
},

{
    "#url"     : "https://chan.sankakucomplex.com/en/posts/show/ac8e3b92ea328ce9cf7211e69c905bf9",
    "#comment" : "/en/posts/show/HEX",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,

    #  "id" : 360451,
    "id" : "y0abGlDOr2o",
    "md5": "ac8e3b92ea328ce9cf7211e69c905bf9",
},

{
    "#url"     : "https://chan.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://chan.sankakucomplex.com/ja/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://beta.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://white.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://black.sankakucomplex.com/post/show/360451",
    "#category": ("booru", "sankaku", "post"),
    "#class"   : sankaku.SankakuPostExtractor,
},

{
    "#url"     : "https://sankaku.app/books?tags=aiue_oka",
    "#category": ("booru", "sankaku", "books"),
    "#class"   : sankaku.SankakuBooksExtractor,
    "#auth"    : True,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://beta.sankakucomplex.com/books?tags=aiue_oka",
    "#category": ("booru", "sankaku", "books"),
    "#class"   : sankaku.SankakuBooksExtractor,
},

)
