# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import instagram


__tests__ = (
{
    "#url"     : "https://www.instagram.com/instagram/",
    "#category": ("", "instagram", "user"),
    "#class"   : instagram.InstagramUserExtractor,
    "#auth"    : False,
    "#options" : {"include": "all"},
    "#results" : (
        "https://www.instagram.com/instagram/info/",
        "https://www.instagram.com/instagram/avatar/",
        "https://www.instagram.com/stories/instagram/",
        "https://www.instagram.com/instagram/highlights/",
        "https://www.instagram.com/instagram/posts/",
        "https://www.instagram.com/instagram/reels/",
        "https://www.instagram.com/instagram/tagged/",
    ),
},

{
    "#url"     : "https://www.instagram.com/instagram/?hl=en",
    "#category": ("", "instagram", "user"),
    "#class"   : instagram.InstagramUserExtractor,
},

{
    "#url"     : "https://www.instagram.com/id:25025320/",
    "#category": ("", "instagram", "user"),
    "#class"   : instagram.InstagramUserExtractor,
},

{
    "#url"     : "https://www.instagram.com/instagram/posts/",
    "#category": ("", "instagram", "posts"),
    "#class"   : instagram.InstagramPostsExtractor,
    "#range"   : "1-16",
    "#count"   : ">= 16",
},

{
    "#url"     : "https://www.instagram.com/instagram/reels/",
    "#category": ("", "instagram", "reels"),
    "#class"   : instagram.InstagramReelsExtractor,
    "#range"   : "40-60",
    "#count"   : ">= 20",
},

{
    "#url"     : "https://www.instagram.com/instagram/tagged/",
    "#category": ("", "instagram", "tagged"),
    "#class"   : instagram.InstagramTaggedExtractor,
    "#range"   : "1-16",
    "#count"   : ">= 16",

    "tagged_owner_id" : "25025320",
    "tagged_username" : "instagram",
    "tagged_full_name": "Instagram",
},

{
    "#url"     : "https://www.instagram.com/kadakaofficial/guide/knit-i-need-collection/18131821684305217/",
    "#category": ("", "instagram", "guide"),
    "#class"   : instagram.InstagramGuideExtractor,
    "#range"   : "1-16",
    "#count"   : ">= 16",
},

{
    "#url"     : "https://www.instagram.com/instagram/saved/",
    "#category": ("", "instagram", "saved"),
    "#class"   : instagram.InstagramSavedExtractor,
},

{
    "#url"     : "https://www.instagram.com/instagram/saved/all-posts/",
    "#category": ("", "instagram", "saved"),
    "#class"   : instagram.InstagramSavedExtractor,
},

{
    "#url"     : "https://www.instagram.com/instagram/saved/collection_name/123456789/",
    "#category": ("", "instagram", "collection"),
    "#class"   : instagram.InstagramCollectionExtractor,
},

{
    "#url"     : "https://www.instagram.com/stories/instagram/",
    "#category": ("", "instagram", "stories"),
    "#class"   : instagram.InstagramStoriesExtractor,
},

{
    "#url"     : "https://www.instagram.com/stories/highlights/18042509488170095/",
    "#category": ("", "instagram", "highlights"),
    "#class"   : instagram.InstagramStoriesExtractor,
},

{
    "#url"     : "https://instagram.com/stories/geekmig/2724343156064789461",
    "#category": ("", "instagram", "stories"),
    "#class"   : instagram.InstagramStoriesExtractor,
},

{
    "#url"     : "https://www.instagram.com/stories/me/",
    "#class"   : instagram.InstagramStoriesTrayExtractor,
},

{
    "#url"     : "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDQyNTA5NDg4MTcwMDk1",
    "#category": ("", "instagram", "highlights"),
    "#class"   : instagram.InstagramStoriesExtractor,
},

{
    "#url"     : "https://www.instagram.com/s/aGlnaGxpZ2h0OjE4MDQyNTA5NDg4MTcwMDk1?story_media_id=2724343156064789461",
    "#category": ("", "instagram", "highlights"),
    "#class"   : instagram.InstagramStoriesExtractor,
},

{
    "#url"     : "https://www.instagram.com/instagram/highlights",
    "#category": ("", "instagram", "highlights"),
    "#class"   : instagram.InstagramHighlightsExtractor,
},

{
    "#url"     : "https://www.instagram.com/instagram/following",
    "#category": ("", "instagram", "following"),
    "#class"   : instagram.InstagramFollowingExtractor,
    "#range"   : "1-16",
    "#count"   : ">= 16",
},

{
    "#url"     : "https://www.instagram.com/explore/tags/instagram/",
    "#category": ("", "instagram", "tag"),
    "#class"   : instagram.InstagramTagExtractor,
    "#range"   : "1-16",
    "#count"   : ">= 16",
},

{
    "#url"     : "https://www.instagram.com/instagram/info",
    "#category": ("", "instagram", "info"),
    "#class"   : instagram.InstagramInfoExtractor,
    "#auth"    : False,
},

{
    "#url"     : "https://www.instagram.com/instagram/avatar",
    "#category": ("", "instagram", "avatar"),
    "#class"   : instagram.InstagramAvatarExtractor,
    "#pattern" : r"https://instagram\.[\w.-]+\.fbcdn\.net/v/t51\.2885-19/281440578_1088265838702675_6233856337905829714_n\.jpg",
},

{
    "#url"     : "https://www.instagram.com/p/BqvsDleB3lV/",
    "#comment" : "GraphImage",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "#pattern" : r"https://[^/]+\.(cdninstagram\.com|fbcdn\.net)/v(p/[0-9a-f]+/[0-9A-F]+)?/t51.2885-15/e35/44877605_725955034447492_3123079845831750529_n.jpg",

    "date"          : "dt:2018-11-29 01:04:04",
    "description"   : str,
    "height"        : int,
    "likes"         : int,
    "location_id"   : "214424288",
    "location_slug" : "hong-kong",
    "location_url"  : r"re:/explore/locations/214424288/hong-kong/",
    "media_id"      : "1922949326347663701",
    "shortcode"     : "BqvsDleB3lV",
    "post_id"       : "1922949326347663701",
    "post_shortcode": "BqvsDleB3lV",
    "post_url"      : "https://www.instagram.com/p/BqvsDleB3lV/",
    "tags"          : ["#WHPsquares"],
    "typename"      : "GraphImage",
    "username"      : "instagram",
    "width"         : int,
},

{
    "#url"     : "https://www.instagram.com/p/BoHk1haB5tM/",
    "#comment" : "GraphSidecar",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "#count"   : 5,

    "sidecar_media_id": "1875629777499953996",
    "sidecar_shortcode": "BoHk1haB5tM",
    "post_id"         : "1875629777499953996",
    "post_shortcode"  : "BoHk1haB5tM",
    "post_url"        : "https://www.instagram.com/p/BoHk1haB5tM/",
    "num"             : int,
    "likes"           : int,
    "username"        : "instagram",
},

{
    "#url"     : "https://www.instagram.com/p/Bqxp0VSBgJg/",
    "#comment" : "GraphVideo",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "#pattern" : r"/46840863_726311431074534_7805566102611403091_n\.mp4",

    "date"       : "dt:2018-11-29 19:23:58",
    "description": str,
    "height"     : int,
    "likes"      : int,
    "media_id"   : "1923502432034620000",
    "post_url"   : "https://www.instagram.com/p/Bqxp0VSBgJg/",
    "shortcode"  : "Bqxp0VSBgJg",
    "tags"       : ["#ASMR"],
    "typename"   : "GraphVideo",
    "username"   : "instagram",
    "width"      : int,
},

{
    "#url"     : "https://www.instagram.com/tv/BkQjCfsBIzi/",
    "#comment" : "GraphVideo (IGTV)",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "#pattern" : r"/10000000_597132547321814_702169244961988209_n\.mp4",

    "date"       : "dt:2018-06-20 19:51:32",
    "description": str,
    "height"     : int,
    "likes"      : int,
    "media_id"   : "1806097553666903266",
    "post_url"   : "https://www.instagram.com/p/BkQjCfsBIzi/",
    "shortcode"  : "BkQjCfsBIzi",
    "typename"   : "GraphVideo",
    "username"   : "instagram",
    "width"      : int,
},

{
    "#url"     : "https://www.instagram.com/p/BtOvDOfhvRr/",
    "#comment" : "GraphSidecar with 2 embedded GraphVideo objects",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "#count"   : 2,

    "post_url"        : "https://www.instagram.com/p/BtOvDOfhvRr/",
    "sidecar_media_id": "1967717017113261163",
    "sidecar_shortcode": "BtOvDOfhvRr",
    "video_url"       : str,
},

{
    "#url"     : "https://www.instagram.com/p/B_2lf3qAd3y/",
    "#comment" : "GraphImage with tagged user",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,

    "tagged_users": [{
    "id"       : "1246468638",
    "username" : "kaaymbl",
    "full_name": "Call Me Kay",
}],
},

{
    "#url"     : "https://www.instagram.com/dm/p/CW042g7B9CY/",
    "#comment" : "URL with username (#2085)",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
},

{
    "#url"     : "https://www.instagram.com/reel/CDg_6Y1pxWu/",
    "#category": ("", "instagram", "reel"),
    "#class"   : instagram.InstagramPostExtractor,
},

{
    "#url"     : "https://www.instagram.com/reels/CDg_6Y1pxWu/",
    "#category": ("", "instagram", "reel"),
    "#class"   : instagram.InstagramPostExtractor,
},

{
    "#url"     : "https://www.instagram.com/share/BACiUUUYQV",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "shortcode"  : "C6q-XdvsU5v",
},

{
    "#url"     : "https://www.instagram.com/share/p/BACiUUUYQV",
    "#category": ("", "instagram", "post"),
    "#class"   : instagram.InstagramPostExtractor,
    "shortcode"  : "C6q-XdvsU5v",
},

{
    "#url"     : "https://www.instagram.com/share/reel/BARSSL4rTu",
    "#category": ("", "instagram", "reel"),
    "#class"   : instagram.InstagramPostExtractor,
    "shortcode"  : "DHbVbT4Jx0c",
}

)
