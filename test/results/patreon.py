# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import patreon
import datetime
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.patreon.com/koveliana",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#range"   : "1-15",
    "#count"   : 15,

    "attachments"  : list,
    "campaign"     : dict,
    "comment_count": int,
    "content"      : str,
    "creator"      : dict,
    "date"         : datetime.datetime,
    "id"           : int,
    "images"       : list,
    "like_count"   : int,
    "post_type"    : str,
    "published_at" : str,
    "title"        : str,
},

{
    "#url"     : "https://www.patreon.com/koveliana/posts?filters[month]=2020-3",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#count"   : 1,

    "date": "dt:2020-03-30 21:21:44",
},

{
    "#url"     : "https://www.patreon.com/kovelianot",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/c/koveliana",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user/posts/?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?c=369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/profile/creators?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/profile/creators?c=369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/id:369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/home",
    "#class"   : patreon.PatreonUserExtractor,
},

{
    "#url"     : "https://www.patreon.com/posts/precious-metal-23563293",
    "#comment" : "postfile + attachments",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.patreon.com/posts/free-mari-8s-113049301",
    "#comment" : "'This page has been removed' - postfile + attachments_media (#6241)",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.patreon.com/posts/56127163",
    "#comment" : "account suspended",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "tags (#1539)",
    "#class"   : patreon.PatreonPostExtractor,
    "#pattern" : r"https://c10.patreonusercontent.com/4/patreon-media/p/post/12497641/3d99f5f5b635428ca237fedf0f223f1a/eyJhIjoxLCJwIjoxfQ%3D%3D/1\.JPG\?.+",

    "tags": ["AWMedia"],
    "campaign": {
        "avatar_photo_image_urls": dict,
        "avatar_photo_url": "https://c10.patreonusercontent.com/4/patreon-media/p/campaign/350434/cadc16f03fa1460f9185505b0a858c1b/eyJ3IjoyMDB9/1.png?token-time=2145916800&token-hash=yBXVH1-UXYOUow9qRey-I6eJe8PcuRQDDKhw730g5jc%3D",
        "creation_name": "creating Art Photography/Videography",
        "currency": "USD",
        "current_user_can_be_free_member": True,
        "current_user_is_free_member": False,
        "is_free_membership_paused": False,
        "is_monthly": True,
        "name": "ReedandWeep",
        "offers_free_membership": True,
        "offers_paid_membership": True,
        "pay_per_name": "month",
        "pledge_url": "/checkout/Reedandweep",
        "primary_theme_color": None,
        "show_audio_post_download_links": True,
        "show_free_membership_cta": False,
        "url": "https://www.patreon.com/Reedandweep",
    },

},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "custom image format (#6569)",
    "#class"   : patreon.PatreonPostExtractor,
    "#options" : {"format-images": "thumbnail"},
    "#pattern"     : r"https://c10.patreonusercontent.com/4/patreon-media/p/post/12497641/3d99f5f5b635428ca237fedf0f223f1a/eyJoIjozNjAsInciOjM2MH0%3D/1\.JPG\?.+",
    "#sha1_content": "190e249295eeca1a8ffbcf1aece788b4f69bbb64",
},

{
    "#url"     : "https://www.patreon.com/posts/m3u8-94714289",
    "#class"   : patreon.PatreonPostExtractor,
    "#pattern" : [
        r"https://c10\.patreonusercontent\.com/4/patreon-media/p/post/94714289/be3d8eb994ae44eca4baffcdc6dd25fc/eyJhIjoxLCJwIjoxfQ%3D%3D/1\.png",
        r"ytdl:https://stream\.mux\.com/NLrxTLdxyGStpOgapJAtB8uPGAaokEcj8YovML00y2DY\.m3u8\?token=ey",
    ]
},

{
    "#url"     : "https://www.patreon.com/posts/not-found-123",
    "#class"   : patreon.PatreonPostExtractor,
    "#exception": exception.NotFoundError,
},

)
