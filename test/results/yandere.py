# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import moebooru


__tests__ = (
{
    "#url"     : "https://yande.re/post/show/51824",
    "#category": ("moebooru", "yandere", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
    "#options"     : {"tags": True},
    "#sha1_content": "59201811c728096b2d95ce6896fd0009235fe683",

    "tags_artist"   : "sasaki_tamaru",
    "tags_circle"   : "softhouse_chara",
    "tags_copyright": "ouzoku",
    "tags_general"  : str,
},

{
    "#url"     : "https://yande.re/post/show/993156",
    "#category": ("moebooru", "yandere", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
    "#options"     : {"notes": True},
    "#sha1_content": "fed722bd90f48de41ec163692befc701056e2b1e",

    "notes": [
        {
            "id"    : 7096,
            "x"     : 90,
            "y"     : 626,
            "width" : 283,
            "height": 529,
            "body"  : "Please keep this as a secret for me!!",
        },
        {
            "id"    : 7095,
            "x"     : 900,
            "y"     : 438,
            "width" : 314,
            "height": 588,
            "body"  : "The facts that I love playing games",
        },
    ],
},

{
    "#url"     : "https://yande.re/post?tags=ouzoku+armor",
    "#category": ("moebooru", "yandere", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
    "#sha1_content": "59201811c728096b2d95ce6896fd0009235fe683",
},

{
    "#url"     : "https://yande.re/pool/show/318",
    "#category": ("moebooru", "yandere", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
    "#sha1_content": "2a35b9d6edecce11cc2918c6dce4de2198342b68",
    "#results"     : (
        "https://files.yande.re/image/62558ad1d68ffb47e903694d2c5f9e53/yande.re%2051824%20armor%20ouzoku%20pantsu%20sasaki_tamaru%20softhouse_chara%20sword%20thighhighs.jpg",
        "https://files.yande.re/image/c57fcd886f643297f1283242e572b81d/yande.re%2036975%20ashita_no_kimi_to_au_tame_ni%20cleavage%20kurashima_tomoyasu%20pantsu%20wakamiya_asuka.jpg",
        "https://files.yande.re/image/c877ec0dc18dd79d69217011adfa5af3/yande.re%2051832%20aburidashi_zakuro%20animal_ears%20erect_nipples%20pantsu%20tail.jpg",
    ),
},

{
    "#url"     : "https://yande.re/pool/show/318",
    "#comment" : "'metadata' option (#4646)",
    "#category": ("moebooru", "yandere", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
    "#options" : {"metadata": True},
    "#count"   : 3,

    "pool": {
        "created_at" : "2008-12-13T15:56:10.728Z",
        "description": "Dengeki Hime's posts are in pool #97.",
        "id"         : 318,
        "is_public"  : True,
        "name"       : "Galgame Mag 08",
        "post_count" : 3,
        "updated_at" : "2012-03-11T14:31:00.935Z",
        "user_id"    : 1305,
    },

},

{
    "#url"     : "https://yande.re/post/popular_by_month?month=6&year=2014",
    "#category": ("moebooru", "yandere", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
    "#count"   : 40,
},

{
    "#url"     : "https://yande.re/post/popular_recent",
    "#category": ("moebooru", "yandere", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

)
