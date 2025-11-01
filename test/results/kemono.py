# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kemono
from gallery_dl import util, exception


__tests__ = (
{
    "#url"     : "https://kemono.cr/fanbox/user/6993449",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoUserExtractor,
    "#options" : {"endpoint": "legacy"},
    "#range"   : "1-500",
    "#count"   : 500,

    "archives"   : list,
    "attachments": list,
    "count"      : int,
    "num"        : int,
    "date"       : "type:datetime",
    "id"         : str,
    "published"  : str,
    "service"    : "fanbox",
    "subcategory": "fanbox",
    "substring"  : str,
    "title"      : str,
    "user"       : "6993449",
    "username"   : "かえぬこ",
    "file"       : {
        "extension": str,
        "filename" : str,
        "hash"     : "len:str:64",
        "name"     : str,
        "path"     : str,
        "type"     : "file",
        "url"      : str,
    },
},

{
    "#url"     : "https://kemono.cr/fanbox/user/6993449",
    "#comment" : "endpoint: legacy+ (#7438 #7450 #7462)",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoUserExtractor,
    "#options" : {"endpoint": "legacy+"},
    "#range"   : "1-10",

    "added"      : {str, None},
    "archives"   : [],
    "attachments": list,
    "captions"   : None,
    "content"    : str,
    "count"      : int,
    "num"        : int,
    "date"       : "type:datetime",
    "edited"     : str,
    "embed"      : dict,
    "id"         : str,
    "poll"       : None,
    "published"  : str,
    "service"    : "fanbox",
    "shared_file": False,
    "subcategory": "fanbox",
    "tags"       : list,
    "title"      : str,
    "user"       : "6993449",
    "username"   : "かえぬこ",
    "file"       : {
        "hash"   : "len:str:64",
        "name"   : str,
        "path"   : str,
        "type"   : "file",
        "url"    : str,
    },
},

{
    "#url"     : "https://kemono.cr/patreon/user/881792?o=150",
    "#comment" : "'max-posts' and 'endpoint' option, 'o' query parameter (#1674)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoUserExtractor,
    "#options" : {"max-posts": 100, "endpoint": "posts"},
    "#count"   : range(200, 400),

    "archives"   : [],
    "attachments": list,
    "count"      : int,
    "num"        : int,
    "id"         : str,
    "date"       : "type:datetime",
    "published"  : str,
    "service"    : "patreon",
    "subcategory": "patreon",
    "title"      : str,
    "user"       : "881792",
    "username"   : "diives",

    "!added"      : {str, None},
    "!captions"   : None,
    "!content"    : str,
    "!edited"     : {str, None},
    "!embed"      : dict,
    "!poll"       : None,
    "!shared_file": False,
    "!tags"       : {str, None},
},

{
    "#url"     : "https://kemono.cr/fanbox/user/6993449?q=お蔵入りになった",
    "#comment" : "search / 'q' query parameter (#3385, #4057)",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoUserExtractor,
    "#results" : (
        "https://kemono.cr/data/ef/7b/ef7b4398a2f4ada597421fd3c116cff86e85695911f7cd2a459b0e566b864e46.png",
        "https://kemono.cr/data/73/e6/73e615f6645b9d1af6329448601673c9275f07fd11eb37670c97e307e29a9ee9.png",
    ),

    "id": "8779",
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935?tag=pin-up",
    "#comment" : "'tag' query parameter",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoUserExtractor,
    "#results" : (
        "https://kemono.cr/data/83/61/8361560887a09c7b828d326b3e1a2f0288673741569a09d74bcd01e602d20db1.png",
        "https://kemono.cr/data/03/e6/03e62592c3b616b8906c1aaa130bd9ceaa24d7f601b31f90cc11956a57ca1d82.png",
        "https://kemono.cr/data/83/0d/830d017873157d2e6544a0f23a47622ec1e91be09b5d7795eb22e32b3150c837.png",
        "https://kemono.cr/data/6a/9b/6a9b6d93dcb86c24a48def1bb93ce2a9ad77393941f3469d87d39400433cf825.png",
        "https://kemono.cr/data/96/43/9643ac03888f3b199f4e769242477b8d4d4f96025b10ab3f28affc3a1ae6bf52.jpg",
        "https://kemono.cr/data/f7/a8/f7a87ccac5736f46190a53a2bb1ff3828230e90f480776759895fcba28375909.jpg",
        "https://kemono.cr/data/b0/38/b03882c8b0ab3b1cf9fc658a2bb2f9ac6ad4f3449015311dcd2d7ee7f748db31.png",
    ),

    "tags": list,
},

{
    "#url"     : "https://kemono.cr/subscribestar/user/alcorart",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoUserExtractor,
},

{
    "#url"     : "https://kemono.cr/subscribestar/user/alcorart",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoUserExtractor,
},

{
    "#url"     : "https://kemono.cr/fanbox/user/6993449/post/506575",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoPostExtractor,
    "#pattern"     : r"https://kemono.cr/data/21/0f/210f35388e28bbcf756db18dd516e2d82ce75[0-9a-f]+\.jpg",
    "#sha1_content": "900949cefc97ab8dc1979cc3664785aac5ba70dd",

    "added"      : None,
    "archives"   : [],
    "content"    : str,
    "count"      : 1,
    "date"       : "dt:2019-08-10 17:09:04",
    "edited"     : None,
    "embed"      : dict,
    "extension"  : "jpeg",
    "filename"   : "P058kDFYus7DbqAkGlfWTlOr",
    "hash"       : "210f35388e28bbcf756db18dd516e2d82ce758e0d32881eeee76d43e1716d382",
    "id"         : "506575",
    "num"        : 1,
    "published"  : "2019-08-10T17:09:04",
    "service"    : "fanbox",
    "shared_file": False,
    "subcategory": "fanbox",
    "title"      : "c96取り置き",
    "type"       : "file",
    "user"       : "6993449",
},

{
    "#url"     : "https://kemono.cr/fanbox/user/7356311/post/802343",
    "#comment" : "inline image (#1286)",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoPostExtractor,
    "#pattern" : r"https://kemono\.cr/data/47/b5/47b5c014ecdcfabdf2c85eec53f1133a76336997ae8596f332e97d956a460ad2\.jpg",

    "hash": "47b5c014ecdcfabdf2c85eec53f1133a76336997ae8596f332e97d956a460ad2",
},

{
    "#url"     : "https://kemono.su/gumroad/user/3101696181060/post/tOWyf",
    "#category": ("", "kemono", "gumroad"),
    "#class"   : kemono.KemonoPostExtractor,
    "#count"   : 12,
},

{
    "#url"     : "https://kemono.party/gumroad/user/3252870377455/post/aJnAH",
    "#comment" : "username (#1548, #1652)",
    "#category": ("", "kemono", "gumroad"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"metadata": True},

    "username": "Kudalyn's Creations",
},

{
    "#url"     : "https://kemono.cr/patreon/user/4158582/post/32099982",
    "#comment" : "allow duplicates (#2440)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://kemono.cr/patreon/user/4158582/post/32099982",
    "#comment" : "allow duplicates (#2440)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"duplicates": True},
    "#count"   : 3,
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/23445732",
    "#comment" : "comments (#2008)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"comments": True},

    "comments": "len:12",
},

{
    "#url"     : "https://kemono.cr/patreon/user/34134344/post/38129255",
    "#comment" : "DMs (#2008); no comments",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"dms": True, "comments": True},

    "comments": [],
    "dms": [
        {
            "added"    : "2021-07-31T02:47:51.327865",
            "artist"   : None,
            "content"  : "Hi! Thank you very much for supporting the work I did in May. Here's your reward pack! I hope you find something you enjoy in it. :)\n\nhttps://www.mediafire.com/file/n9ppjpip0r3f01v/Set13_tier_2.zip/file",
            "embed"    : {},
            "file"     : {},
            "hash"     : "f8d4962fb7908614c9b7c8c0de1b5f8985f01b62a9b06d74d640c5b2bcedf758",
            "published": "2021-06-09T03:28:51.431000",
            "service"  : "patreon",
            "user"     : "34134344",
        },
    ],
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/68231671",
    "#comment" : "announcements",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"announcements": True},

    "announcements": [
        {
            "added"    : "2023-02-01T22:44:34.670719",
            "content"  : "<div style=\"text-align: center;\"><strong>Thank you so much for the support!</strong><strong><br></strong>This Patreon is more of a tip jar for supporting what I make. I have to clarify that there are <strong>no exclusive Patreon animations</strong>&nbsp;because all are released for the public. You will get earlier access to WIPs. Direct downloads to my works are also available for $5 and $10 Tiers.</div>",
            "hash"     : "815648d41c60d1d546437e475a0888fd4a77fd098b1ec61a3648ea6da30c1034",
            "published": None,
            "service"  : "patreon",
            "user_id"  : "3161935",
        },
    ],
},

{
    "#url"     : "https://kemono.cr/patreon/user/19623797/post/29035449",
    "#comment" : "invalid file (#3510)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#pattern"     : r"907ba78b4545338d3539683e63ecb51cf51c10adc9dabd86e92bd52339f298b9\.txt",
    "#sha1_content": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
},

{
    "#url"     : "https://kemono.cr/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://kemono.cr/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://www.kemono.cr/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://beta.kemono.cr/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemono", "subscribestar"),
    "#class"   : kemono.KemonoPostExtractor,
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/68231671/revision/142470",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#results" : "https://kemono.cr/data/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86.jpg",

    "file": {
        "hash": "88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86",
        "name": "wip update.jpg",
        "path": "/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86.jpg",
        "type": "file",
    },
    "attachments": [
        {
            "hash": "88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86",
            "name": "wip update.jpg",
            "path": "/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86.jpg",
            "type": "attachment",
        },
    ],
    "filename"      : "wip update",
    "extension"     : "jpg",
    "hash"          : "88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86",
    "revision_id"   : 142470,
    "revision_index": 2,
    "revision_count": 11,
    "revision_hash" : "e0e93281495e151b11636c156e52bfe9234c2a40",
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/68231671",
    "#comment" : "unique revisions (#5013)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"revisions": "unique"},
    "#results" : "https://kemono.cr/data/e3/e6/e3e6287dbc0468dd2a9d28ed276ae86788907143acf2ba10ab886a3add4c436c.jpg",
    "#archive" : False,

    "filename"      : "wip update",
    "hash"          : {
        "88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86",
        "e3e6287dbc0468dd2a9d28ed276ae86788907143acf2ba10ab886a3add4c436c",
    },
    "revision_id"   : {9277608, 10619155, 0},
    "revision_index": {1, 2, 3},
    "revision_count": 3,
    "revision_hash" : {
        "e0e93281495e151b11636c156e52bfe9234c2a40",
        "bc5713195e14799da40c525381216c5a1a340b0f",
        "9872bfb536a47cc69d95d2f195cd5c825808f089",
    },
},

{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/68231671/revisions",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#pattern" : r"https://kemono\.cr/data/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86\.jpg",
    "#count"   : 11,
    "#archive" : False,

    "revision_id": range(134996, 10619155),
    "revision_index": range(1, 11),
    "revision_count": 11,
    "revision_hash": {
        "9872bfb536a47cc69d95d2f195cd5c825808f089",
        "e0e93281495e151b11636c156e52bfe9234c2a40",
        "eb2fa4385af730509a42f8f0424bd0b9a0e4bc21",
    },
},


{
    "#url"     : "https://kemono.cr/patreon/user/3161935/post/68231671/revision/12345",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://kemono.cr/patreon/user/6298789/post/69764693",
    "#comment" : "'published' metadata with extra microsecond data",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,

    "date"     : "dt:2022-07-29 21:12:11",
    "published": "2022-07-29T21:12:11.483000",
},

{
    "#url"     : "https://kemono.cr/gumroad/user/3267960360326/post/jwwag",
    "#comment" : "empty 'file' with no 'path' (#5368)",
    "#category": ("", "kemono", "gumroad"),
    "#class"   : kemono.KemonoPostExtractor,
    "#count"   : 8,

    "type"     : "attachment",
},

{
    "#url"     : "https://kemono.cr/fanbox/user/49494721/post/9457614",
    "#comment" : "archives",
    "#category": ("", "kemono", "fanbox"),
    "#class"   : kemono.KemonoPostExtractor,
    "#options" : {"archives": True},
    "#range"   : "1-2",

    "archives": [
        {
            "file": {
                "added": "2025-03-03T02:11:28.153911",
                "ctime": "2025-03-03T02:05:15.810201",
                "ext"  : ".zip",
                "hash" : "c22c7e979355f633aaae4929b010816895a47ec37a9cfc25186a0952ec6e5774",
                "id"   : 190824068,
                "ihash": None,
                "mime" : "application/zip",
                "mtime": "2025-03-03T02:11:28.807462",
                "size" : 18634288,
            },
            "file_list": [
                "モナmp4形式まとめ/",
                "モナmp4形式まとめ/Movie_1.mp4",
                "モナmp4形式まとめ/Movie_2.mp4",
                "モナmp4形式まとめ/Movie_3.mp4",
                "モナmp4形式まとめ/Movie_4.mp4",
                "モナmp4形式まとめ/Movie_5.mp4",
                "モナmp4形式まとめ/Movie_End_3.mp4",
            ],
            "filename": "モナmp4形式まとめ",
            "extension": "zip",
            "hash": "c22c7e979355f633aaae4929b010816895a47ec37a9cfc25186a0952ec6e5774",
            "name": "モナmp4形式まとめ.zip",
            "password": None,
            "path": "/c2/2c/c22c7e979355f633aaae4929b010816895a47ec37a9cfc25186a0952ec6e5774.zip",
            "type": "archive",
            "url": "https://kemono.cr/data/c2/2c/c22c7e979355f633aaae4929b010816895a47ec37a9cfc25186a0952ec6e5774.zip",
        },
        {
            "file": {
                "added": "2025-03-03T02:11:00.541142",
                "ctime": "2025-03-03T02:04:56.754326",
                "ext"  : ".zip",
                "hash" : "f7b4dedd9742aeb8da56dc6fe07deb7639880d0800ac0b7a6e91f64ff6b40178",
                "id"   : 190824029,
                "ihash": None,
                "mime" : "application/zip",
                "mtime": "2025-03-03T02:11:01.110281",
                "size" : 84738158,
            },
            "file_list": "len:229",
            "filename": "モナUnity",
            "extension": "zip",
            "hash": "f7b4dedd9742aeb8da56dc6fe07deb7639880d0800ac0b7a6e91f64ff6b40178",
            "name": "モナUnity.zip",
            "password": None,
            "path": "/f7/b4/f7b4dedd9742aeb8da56dc6fe07deb7639880d0800ac0b7a6e91f64ff6b40178.zip",
            "type": "archive",
            "url": "https://kemono.cr/data/f7/b4/f7b4dedd9742aeb8da56dc6fe07deb7639880d0800ac0b7a6e91f64ff6b40178.zip"
        },
    ],

    "title": "モナ（Live2Dアニメ）",
    "type": "archive",
    "user": "49494721",
    "username": "soso",
    "user_profile": {
        "id": "49494721",
        "indexed": "2021-04-02T23:50:57.138135",
        "name": "soso",
        "public_id": "soso",
        "relation_id": None,
        "service": "fanbox",
        "updated": "iso:datetime",
    },
    "tags": [
        "うごイラ",
        "原神",
    ],
},

{
    "#url"     : "https://kemono.cr/boosty/user/felixf/post/d9d8d670-16be-4e06-8ff9-65b13e322ba8",
    "#comment" : r"'\' in file paths",
    "#category": ("", "kemono", "boosty"),
    "#class"   : kemono.KemonoPostExtractor,
    "#results" : (
        "https://kemono.cr/data/dd/35/dd35c43d8a93f1806f094d9331a17c5037ed5d93e0f30c28d3cca2056b400aa6.png",
        "https://kemono.cr/data/25/48/254864eb2523ab48be8d3fb7ad21ab3a127d61736b76602f8421cde88700a174.png",
    ),

    "hash": {
        "dd35c43d8a93f1806f094d9331a17c5037ed5d93e0f30c28d3cca2056b400aa6",
        "254864eb2523ab48be8d3fb7ad21ab3a127d61736b76602f8421cde88700a174",
    },
    "path": {
        "/dd/35/dd35c43d8a93f1806f094d9331a17c5037ed5d93e0f30c28d3cca2056b400aa6.png",
        "/25/48/254864eb2523ab48be8d3fb7ad21ab3a127d61736b76602f8421cde88700a174.png",
    },
},

{
    "#url"     : "https://kemono.cr/patreon/user/108002999/post/136454591",
    "#comment" : "'.zip' archive with '.bin' extension (#8156)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#range"   : "0",
    "#metadata": "post",

    "archives": [{
        "extension": "zip",
        "filename": "#5 Kitagawa Marin",
        "hash": "46cc99d4114906524fe52a6f772c51ab59ca1c3c0f6a8a0d3588a861b0d59ced",
        "name": "#5 Kitagawa Marin.zip",
        "path": "/46/cc/46cc99d4114906524fe52a6f772c51ab59ca1c3c0f6a8a0d3588a861b0d59ced.bin",
        "type": "archive",
        "url": "https://kemono.cr/data/46/cc/46cc99d4114906524fe52a6f772c51ab59ca1c3c0f6a8a0d3588a861b0d59ced.bin"
    }],
},

{
    "#url"     : "https://kemono.cr/patreon/user/34792417/post/137409895",
    "#comment" : "user profile data unavailable (#8382)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,
    "#log"     : "patreon/34792417/137409895: 'Creator not found'",
    "#results" : (
        "https://kemono.cr/data/a9/87/a9874d7e1229396b0b2706fd7fa9949eac924e86256d84d077c10ecbace8bd17.bin",
        "https://kemono.cr/data/a2/eb/a2eba02204086c789d59bc7112510aebf0428455ad1664153bfbb92eb8aa5643.jpg",
    ),

    "title"       : "Capella - Re:zero (20P)",
    "user"        : "34792417",
    "user_profile": util.NONE,
    "username"    : util.NONE,
},

{
    "#url"     : "https://kemono.cr/patreon/user/2570882/post/79311665",
    "#comment" : "patreon file URL as 'name' / long 'extension' (#8491)",
    "#category": ("", "kemono", "patreon"),
    "#class"   : kemono.KemonoPostExtractor,

    "name"     : "https://www.patreon.com/media-u/Z0FBQUFBQmpfWFNLWHpRakFlYjVNeWpuTlRuRnJBdHY3VVA2UmRhVHFpOFBHMW9QZUdVOHQ3b2pXSV9XMkJlaHFuN2JyVk5VNDBqdV9lZVRLR2NkUXUwSjgwdndDQlk3VzBCUXI5TW5iejlVWVZaUmJoTktIX3B5aGVCS3dUQk11a2hxajd4TUx2MFN2UHpKa0pfOWZQeS1UeDlzNEhpbG9pRzJsZE54MG5OcnZDOUllTGhyY01rNjVRaGgyaVFycjFSUUFIaV92OU9wdktuVjlMeFJNLXhYejdDNWZTVXZEc2l0TVZCR1A0YXM3RVMzbmsxSjh2ND0=#190833153_",
    "filename" : "https://www.patreon.com/media-u/Z0FBQUFBQmpfWFNLWHpRakFlYjVNeWpuTlRuRnJBdHY3VVA2UmRhVHFpOFBHMW9QZUdVOHQ3b2pXSV9XMkJlaHFuN2JyVk5VNDBqdV9lZVRLR2NkUXUwSjgwdndDQlk3VzBCUXI5TW5iejlVWVZaUmJoTktIX3B5aGVCS3dUQk11a2hxajd4TUx2MFN2UHpKa0pfOWZQeS1UeDlzNEhpbG9pRzJsZE54MG5OcnZDOUllTGhyY01rNjVRaGgyaVFycjFSUUFIaV92OU9wdktuVjlMeFJNLXhYejdDNWZTVXZEc2l0TVZCR1A0YXM3RVMzbmsxSjh2ND0=#190833153_",
    "extension": "jpg",
},

{
    "#url"     : "https://kemono.cr/discord/server/488668827274444803/608504710906904576",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#results" : (
        "https://kemono.cr/data/6e/6a/6e6a4a048e6f3c047edac851d1f66eca4a4f0a823faa1d9395892378fcb700b1.png",
        "https://kemono.cr/data/55/e1/55e1ddf540ded5e6651de65c059529d1f51451cde523ec103dc696f1cc3595a4.png",
        "https://kemono.cr/data/9d/98/9d983fd163d5f5335c896c93b9f363198d6ca14a7e5bf0fa823aa86268732f85.png",
        "https://kemono.cr/data/fb/54/fb54ff75f1c879b25bf031a55a1730002049337693443f1b57c08b07e35c452f.png",
    ),

    "channel"      : "finish-work",
    "channel_id"   : "608504710906904576",
    "channel_nsfw" : False,
    "channel_topic": None,
    "channel_type" : 0,
    "server"       : "ABFMMD NSFW Server",
    "server_id"    : "488668827274444803",
},

{
    "#url"     : "https://kemono.cr/discord/server/488668827274444803/608504710906904576",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#options" : {"order-posts": "reverse"},
    "#results" : (
        "https://kemono.cr/data/fb/54/fb54ff75f1c879b25bf031a55a1730002049337693443f1b57c08b07e35c452f.png",
        "https://kemono.cr/data/9d/98/9d983fd163d5f5335c896c93b9f363198d6ca14a7e5bf0fa823aa86268732f85.png",
        "https://kemono.cr/data/55/e1/55e1ddf540ded5e6651de65c059529d1f51451cde523ec103dc696f1cc3595a4.png",
        "https://kemono.cr/data/6e/6a/6e6a4a048e6f3c047edac851d1f66eca4a4f0a823faa1d9395892378fcb700b1.png",
    ),

    "channel"      : "finish-work",
    "channel_id"   : "608504710906904576",
    "channel_nsfw" : False,
    "channel_topic": None,
    "channel_type" : 0,
    "server"       : "ABFMMD NSFW Server",
    "server_id"    : "488668827274444803",
},

{
    "#url"     : "https://kemono.cr/discord/server/488668827274444803#608504710906904576",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#count"   : 4,

    "channel"      : "finish-work",
    "channel_id"   : "608504710906904576",
    "channel_nsfw" : False,
    "channel_topic": None,
    "channel_type" : 0,
    "server"       : "ABFMMD NSFW Server",
    "server_id"    : "488668827274444803",
},

{
    "#url"     : "https://kemono.cr/discord/server/488668827274444803/channel/608504710906904576#finish-work",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#count"   : 4,

    "channel"      : "finish-work",
    "channel_id"   : "608504710906904576",
    "channel_nsfw" : False,
    "channel_topic": None,
    "channel_type" : 0,
    "server"       : "ABFMMD NSFW Server",
    "server_id"    : "488668827274444803",
    "date"         : "type:datetime",
},

{
    "#url"     : "https://kemono.cr/discord/server/818188637329031199/818343747275456522",
    "#comment" : "pagination",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#range"   : "1-250",
    "#count"   : 250,

    "channel"      : "wraith-sfw-gallery",
    "channel_id"   : "818343747275456522",
    "channel_nsfw" : False,
    "channel_type" : 0,
    "channel_topic": None,
    "server"       : "The Ghost Zone",
    "server_id"    : "818188637329031199",
},

{
    "#url"     : "https://kemono.cr/discord/server/256559665620451329/channel/462437519519383555#",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#pattern" : r"https://kemono\.cr/data/(e3/77/e377e3525164559484ace2e64425b0cec1db08.*\.png|51/45/51453640a5e0a4d23fbf57fb85390f9c5ec154.*\.gif)",
    "#count"   : ">= 2",

    "hash": {
        "51453640a5e0a4d23fbf57fb85390f9c5ec15459af0bb5ba65a83781056b68e2",
        "e377e3525164559484ace2e64425b0cec1db0863b9398682b90a9af006d87758",
    },
},

{
    "#url"     : "https://kemono.cr/discord/server/315262215055736843/channel/315262215055736843#general",
    "#comment" : "'inline' files",
    "#category": ("", "kemono", "discord"),
    "#class"   : kemono.KemonoDiscordExtractor,
    "#options" : {"image-filter": "type == 'inline'"},
    "#pattern" : r"https://cdn\.discordapp\.com/attachments/\d+/\d+/.+$",
    "#range"   : "1-5",

    "hash": "",
},

{
    "#url"     : "https://kemono.cr/discord/server/488668827274444803",
    "#category": ("", "kemono", "discord-server"),
    "#class"   : kemono.KemonoDiscordServerExtractor,
    "#pattern" : kemono.KemonoDiscordExtractor.pattern,
    "#count"   : 26,
},

{
    "#url"     : "https://kemono.cr/posts?q=foobar",
    "#category": ("", "kemono", "posts"),
    "#class"   : kemono.KemonoPostsExtractor,
    "#count"   : range(60, 100),
},

{
    "#url"     : "https://kemono.cr/favorites",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
    "#pattern" : kemono.KemonoUserExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://kemono.cr/patreon/user/881792",
        "https://kemono.cr/fanbox/user/6993449",
        "https://kemono.cr/subscribestar/user/alcorart",
        "https://kemono.cr/gumroad/user/shengtian",
    ),
},

{
    "#url"     : "https://kemono.cr/favorites?type=artist&sort=faved_seq&order=asc",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
    "#pattern" : kemono.KemonoUserExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://kemono.cr/fanbox/user/6993449",
        "https://kemono.cr/patreon/user/881792",
        "https://kemono.cr/subscribestar/user/alcorart",
        "https://kemono.cr/gumroad/user/shengtian",
    ),
},

{
    "#url"     : "https://kemono.cr/favorites?type=post",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
    "#pattern" : kemono.KemonoPostExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://kemono.cr/subscribestar/user/alcorart/post/184329",
        "https://kemono.cr/fanbox/user/6993449/post/23913",
        "https://kemono.cr/patreon/user/881792/post/4769638",
    ),
},

{
    "#url"     : "https://kemono.cr/favorites?type=post&sort=published&order=asc",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
    "#pattern" : kemono.KemonoPostExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://kemono.cr/patreon/user/881792/post/4769638",
        "https://kemono.cr/fanbox/user/6993449/post/23913",
        "https://kemono.cr/subscribestar/user/alcorart/post/184329",
    ),
},

{
    "#url"     : "https://kemono.cr/account/favorites/artists",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
},

{
    "#url"     : "https://kemono.cr/account/favorites/posts?sort_by=published&order=asc",
    "#category": ("", "kemono", "favorite"),
    "#class"   : kemono.KemonoFavoriteExtractor,
},

{
    "#url"     : "https://kemono.cr/artists?q=aMSa",
    "#category": ("", "kemono", "artists"),
    "#class"   : kemono.KemonoArtistsExtractor,
    "#pattern" : kemono.KemonoUserExtractor.pattern,
    "#results" : (
        "https://kemono.cr/patreon/user/91205314",
        "https://kemono.cr/patreon/user/51528107",
        "https://kemono.cr/fanbox/user/12812028",
        "https://kemono.cr/patreon/user/35237747",
        "https://kemono.cr/patreon/user/8296916",
        "https://kemono.cr/patreon/user/155095324",
        "https://kemono.cr/patreon/user/75988930",
        "https://kemono.cr/patreon/user/93703989",
        "https://kemono.cr/patreon/user/100292687",
        "https://kemono.cr/patreon/user/138609443",
        "https://kemono.cr/patreon/user/61646879",
        "https://kemono.cr/patreon/user/110669843",
        "https://kemono.cr/patreon/user/44343773",
        "https://kemono.cr/patreon/user/77920059",
        "https://kemono.cr/patreon/user/102386631",
    ),

    "favorited": int,
    "id"       : str,
    "indexed"  : int,
    "name"     : str,
    "service"  : {"patreon", "fanbox"},
    "updated"  : int,
},

{
    "#url"     : "https://kemono.cr/artists?q=Axe&service=discord&sort_by=name&order=asc",
    "#category": ("", "kemono", "artists"),
    "#class"   : kemono.KemonoArtistsExtractor,
    "#pattern" : kemono.KemonoDiscordServerExtractor.pattern,
    "#results" : "https://kemono.cr/discord/server/1168450323023663164",

    "favorited": range(40, 80),
    "id"       : "1168450323023663164",
    "indexed"  : 1710201675,
    "name"     : "Axel Colored Workshop",
    "service"  : "discord",
    "updated"  : range(1740000000, 2000000000),
},

)
