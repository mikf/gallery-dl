# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import kemonoparty
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://kemono.su/fanbox/user/6993449",
    "#category": ("", "kemonoparty", "fanbox"),
    "#class"   : kemonoparty.KemonopartyUserExtractor,
    "#range"   : "1-500",
    "#count"   : 500,
},

{
    "#url"     : "https://kemono.su/patreon/user/881792?o=150",
    "#comment" : "'max-posts' option, 'o' query parameter (#1674)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyUserExtractor,
    "#options" : {"max-posts": 100},
    "#count"   : range(200, 400),
},

{
    "#url"     : "https://kemono.su/fanbox/user/6993449?q=お蔵入りになった",
    "#comment" : "search / 'q' query parameter (#3385, #4057)",
    "#category": ("", "kemonoparty", "fanbox"),
    "#class"   : kemonoparty.KemonopartyUserExtractor,
    "#urls"    : (
        "https://kemono.su/data/ef/7b/ef7b4398a2f4ada597421fd3c116cff86e85695911f7cd2a459b0e566b864e46.png",
        "https://kemono.su/data/73/e6/73e615f6645b9d1af6329448601673c9275f07fd11eb37670c97e307e29a9ee9.png",
    ),

    "id": "8779",
},

{
    "#url"     : "https://kemono.su/subscribestar/user/alcorart",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyUserExtractor,
},

{
    "#url"     : "https://kemono.su/subscribestar/user/alcorart",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyUserExtractor,
},

{
    "#url"     : "https://kemono.su/fanbox/user/6993449/post/506575",
    "#category": ("", "kemonoparty", "fanbox"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#pattern"     : r"https://kemono.su/data/21/0f/210f35388e28bbcf756db18dd516e2d82ce75[0-9a-f]+\.jpg",
    "#sha1_content": "900949cefc97ab8dc1979cc3664785aac5ba70dd",

    "added"      : "2020-05-06T20:28:02.302000",
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
    "#url"     : "https://kemono.su/fanbox/user/7356311/post/802343",
    "#comment" : "inline image (#1286)",
    "#category": ("", "kemonoparty", "fanbox"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#pattern" : r"https://kemono\.su/data/47/b5/47b5c014ecdcfabdf2c85eec53f1133a76336997ae8596f332e97d956a460ad2\.jpg",

    "hash": "47b5c014ecdcfabdf2c85eec53f1133a76336997ae8596f332e97d956a460ad2",
},

{
    "#url"     : "https://kemono.su/gumroad/user/3101696181060/post/tOWyf",
    "#category": ("", "kemonoparty", "gumroad"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#count"   : 12,
},

{
    "#url"     : "https://kemono.party/gumroad/user/3252870377455/post/aJnAH",
    "#comment" : "username (#1548, #1652)",
    "#category": ("", "kemonoparty", "gumroad"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#options" : {"metadata": True},

    "username": "Kudalyn's Creations",
},

{
    "#url"     : "https://kemono.su/patreon/user/4158582/post/32099982",
    "#comment" : "allow duplicates (#2440)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://kemono.su/patreon/user/4158582/post/32099982",
    "#comment" : "allow duplicates (#2440)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#options" : {"duplicates": True},
    "#count"   : 3,
},

{
    "#url"     : "https://kemono.su/patreon/user/3161935/post/23445732",
    "#comment" : "comments (#2008)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#options" : {"comments": True},

    "comments": "len:12",
},

{
    "#url"     : "https://kemono.su/patreon/user/34134344/post/38129255",
    "#comment" : "DMs (#2008); no comments",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#options" : {"dms": True, "comments": True},

    "comments": (),
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
    "#url"     : "https://kemono.su/patreon/user/3161935/post/68231671",
    "#comment" : "announcements",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
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
    "#url"     : "https://kemono.su/patreon/user/19623797/post/29035449",
    "#comment" : "invalid file (#3510)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#pattern"     : r"907ba78b4545338d3539683e63ecb51cf51c10adc9dabd86e92bd52339f298b9\.txt",
    "#sha1_content": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
},

{
    "#url"     : "https://kemono.su/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
},

{
    "#url"     : "https://kemono.su/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
},

{
    "#url"     : "https://www.kemono.su/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
},

{
    "#url"     : "https://beta.kemono.su/subscribestar/user/alcorart/post/184330",
    "#category": ("", "kemonoparty", "subscribestar"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
},

{
    "#url"     : "https://kemono.su/patreon/user/3161935/post/68231671/revision/142470",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#urls"    : "https://kemono.su/data/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86.jpg",

    "file"          : {
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
    "revision_count": 10,
    "revision_hash" : "e0e93281495e151b11636c156e52bfe9234c2a40",
},

{
    "#url"     : "https://kemono.su/patreon/user/3161935/post/68231671",
    "#comment" : "unique revisions (#5013)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#options" : {"revisions": "unique"},
    "#urls"    : "https://kemono.su/data/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86.jpg",
    "#archive" : False,

    "filename"      : "wip update",
    "hash"          : "88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86",
    "revision_id"   : {9277608, 0},
    "revision_index": {1, 2},
    "revision_count": 2,
    "revision_hash" : {"e0e93281495e151b11636c156e52bfe9234c2a40",
                       "79d5967719583a6fa52b2fc143e6a80fcdf75fb8"},
},

{
    "#url"     : "https://kemono.su/patreon/user/3161935/post/68231671/revisions",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#pattern" : r"https://kemono\.su/data/88/52/88521f71822dfa2f42df3beba319ea4fceda2a2d6dc59da0276a75238f743f86\.jpg",
    "#count"   : 10,
    "#archive" : False,

    "revision_id": range(134996, 9277608),
    "revision_index": range(1, 10),
    "revision_count": 10,
    "revision_hash": "e0e93281495e151b11636c156e52bfe9234c2a40",
},


{
    "#url"     : "https://kemono.su/patreon/user/3161935/post/68231671/revision/12345",
    "#comment" : "revisions (#4498)",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://kemono.su/patreon/user/6298789/post/69764693",
    "#comment" : "'published' metadata with extra microsecond data",
    "#category": ("", "kemonoparty", "patreon"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,

    "date"     : "dt:2022-07-29 21:12:11",
    "published": "2022-07-29T21:12:11.483000",
},

{
    "#url"     : "https://kemono.su/gumroad/user/3267960360326/post/jwwag",
    "#comment" : "empty 'file' with no 'path' (#5368)",
    "#category": ("", "kemonoparty", "gumroad"),
    "#class"   : kemonoparty.KemonopartyPostExtractor,
    "#count"   : 8,

    "type"     : "attachment",
},

{
    "#url"     : "https://kemono.su/discord/server/488668827274444803/608504710906904576",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#count"   : 4,

    "channel"     : "608504710906904576",
    "channel_name": "",
},

{
    "#url"     : "https://kemono.su/discord/server/488668827274444803#608504710906904576",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#count"   : 4,

    "channel"     : "608504710906904576",
    "channel_name": "finish-work",
},

{
    "#url"     : "https://kemono.su/discord/server/488668827274444803#finish-work",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#count"   : 4,

    "channel"     : "608504710906904576",
    "channel_name": "finish-work",
},

{
    "#url"     : "https://kemono.su/discord/server/488668827274444803/channel/608504710906904576#finish-work",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#count"   : 4,

    "channel"     : "608504710906904576",
    "channel_name": "finish-work",
    "date"        : "type:datetime",
},

{
    "#url"     : "https://kemono.su/discord/server/818188637329031199#818343747275456522",
    "#comment" : "pagination",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#range"   : "1-250",
    "#count"   : 250,

    "channel"     : "818343747275456522",
    "channel_name": "wraith-sfw-gallery",
},

{
    "#url"     : "https://kemono.su/discord/server/256559665620451329/channel/462437519519383555#",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#pattern" : r"https://kemono\.su/data/(e3/77/e377e3525164559484ace2e64425b0cec1db08.*\.png|51/45/51453640a5e0a4d23fbf57fb85390f9c5ec154.*\.gif)",
    "#count"   : ">= 2",

    "hash": r"re:e377e3525164559484ace2e64425b0cec1db08|51453640a5e0a4d23fbf57fb85390f9c5ec154",
},

{
    "#url"     : "https://kemono.su/discord/server/315262215055736843/channel/315262215055736843#general",
    "#comment" : "'inline' files",
    "#category": ("", "kemonoparty", "discord"),
    "#class"   : kemonoparty.KemonopartyDiscordExtractor,
    "#options" : {"image-filter": "type == 'inline'"},
    "#pattern" : r"https://cdn\.discordapp\.com/attachments/\d+/\d+/.+$",
    "#range"   : "1-5",

    "hash": "",
},

{
    "#url"     : "https://kemono.su/discord/server/488668827274444803",
    "#category": ("", "kemonoparty", "discord-server"),
    "#class"   : kemonoparty.KemonopartyDiscordServerExtractor,
    "#pattern" : kemonoparty.KemonopartyDiscordExtractor.pattern,
    "#count"   : 15,
},

{
    "#url"     : "https://kemono.su/posts?q=foobar",
    "#category": ("", "kemonoparty", "posts"),
    "#class"   : kemonoparty.KemonopartyPostsExtractor,
    "#count"   : range(60, 100),
},

{
    "#url"     : "https://kemono.su/favorites",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
    "#pattern" : kemonoparty.KemonopartyUserExtractor.pattern,
    "#auth"    : True,
    "#urls"    : (
        "https://kemono.su/patreon/user/881792",
        "https://kemono.su/fanbox/user/6993449",
        "https://kemono.su/subscribestar/user/alcorart",
        "https://kemono.su/gumroad/user/shengtian",
    ),
},

{
    "#url"     : "https://kemono.su/favorites?type=artist&sort=faved_seq&order=asc",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
    "#pattern" : kemonoparty.KemonopartyUserExtractor.pattern,
    "#auth"    : True,
    "#urls"    : (
        "https://kemono.su/fanbox/user/6993449",
        "https://kemono.su/patreon/user/881792",
        "https://kemono.su/subscribestar/user/alcorart",
        "https://kemono.su/gumroad/user/shengtian",
    ),
},

{
    "#url"     : "https://kemono.su/favorites?type=post",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
    "#pattern" : kemonoparty.KemonopartyPostExtractor.pattern,
    "#auth"    : True,
    "#urls"    : (
        "https://kemono.su/subscribestar/user/alcorart/post/184329",
        "https://kemono.su/fanbox/user/6993449/post/23913",
        "https://kemono.su/patreon/user/881792/post/4769638",
    ),
},

{
    "#url"     : "https://kemono.su/favorites?type=post&sort=published&order=asc",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
    "#pattern" : kemonoparty.KemonopartyPostExtractor.pattern,
    "#auth"    : True,
    "#urls"    : (
        "https://kemono.su/patreon/user/881792/post/4769638",
        "https://kemono.su/fanbox/user/6993449/post/23913",
        "https://kemono.su/subscribestar/user/alcorart/post/184329",
    ),
},

{
    "#url"     : "https://kemono.su/account/favorites/artists",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
},

{
    "#url"     : "https://kemono.su/account/favorites/posts?sort_by=published&order=asc",
    "#category": ("", "kemonoparty", "favorite"),
    "#class"   : kemonoparty.KemonopartyFavoriteExtractor,
},

)
