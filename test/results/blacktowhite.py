# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import xenforo


__tests__ = (
{
    "#url"     : "https://www.blacktowhite.net/threads/rules-for-posting-photos-gifs-and-videos.337383/post-6545937",
    "#category": ("xenforo", "blacktowhite", "post"),
    "#class"   : xenforo.XenforoPostExtractor,
    "#results" : "https://www.blacktowhite.net/proxy.php?image=https%3A%2F%2Fwww.dailycartoonist.com%2Fwp-content%2Fuploads%2F2020%2F01%2Fdemdonk-jacksonface.jpg&amp;hash=ee3cee17bf3f9b2dcdd41dbe7c1ea35e",

    "count"       : 1,
    "extension"   : "jpg",
    "filename"    : "demdonk-jacksonface",
    "post"        : {
        "author"     : "Truthman",
        "author_id"  : "40508",
        "author_slug": "truthman",
        "date"       : "dt:2025-08-29 20:45:50",
        "id"         : "6545937",
    },
},

{
    "#url"     : "https://www.blacktowhite.net/threads/rules-for-posting-photos-gifs-and-videos.337383/",
    "#category": ("xenforo", "blacktowhite", "thread"),
    "#class"   : xenforo.XenforoThreadExtractor,
    "#results" : (
        "https://twitter.com/x/status/1986133525955743868",
        "https://www.blacktowhite.net/attachments/bbc-worship-very-attractive-woman-jpg.8426431/",
        "https://www.blacktowhite.net/proxy.php?image=https%3A%2F%2Fwww.dailycartoonist.com%2Fwp-content%2Fuploads%2F2020%2F01%2Fdemdonk-jacksonface.jpg&amp;hash=ee3cee17bf3f9b2dcdd41dbe7c1ea35e",
    ),

    "thread"      : {
        "author"     : "MacNfries",
        "author_id"  : "1129",
        "author_slug": "macnfries",
        "author_url" : "https://www.blacktowhite.net/members/macnfries.1129/",
        "date"       : "dt:2025-07-13 04:15:28",
        "id"         : "337383",
        "section"    : "Off-Topic Discussion",
        "tags"       : (),
        "title"      : "RULES For POSTING PHOTOS, GIFS, and VIDEOS",
        "url"        : "https://www.blacktowhite.net/threads/rules-for-posting-photos-gifs-and-videos.337383/",
    },
},

{
    "#url"     : "https://www.blacktowhite.net/media/baby-goddess-energy.845601",
    "#comment" : "video",
    "#category": ("xenforo", "blacktowhite", "media-item"),
    "#class"   : xenforo.XenforoMediaItemExtractor,
    "#auth"    : False,
    "#results" : "https://www.blacktowhite.net/media/baby-goddess-energy.845601/full",
},

{
    "#url"     : "https://www.blacktowhite.net/media/baby-goddess-energy.845601",
    "#comment" : "video",
    "#category": ("xenforo", "blacktowhite", "media-item"),
    "#class"   : xenforo.XenforoMediaItemExtractor,
    "#auth"    : False,
    "#options" : {"metadata": True},
    "#results" : "https://www.blacktowhite.net/data/xfmg/video/8173/8173378-a16bd8e0c10523da2f99e8a9af17c03a.mov",
},

{
    "#url"     : "https://www.blacktowhite.net/media/img_5727-jpeg.840519",
    "#comment" : "image",
    "#category": ("xenforo", "blacktowhite", "media-item"),
    "#class"   : xenforo.XenforoMediaItemExtractor,
    "#results" : "https://www.blacktowhite.net/media/img_5727-jpeg.840519/full",
    "#sha1_content": "d8cfca63c71bc7330fdfa7d17d6247392cbb4472",
},

{
    "#url"     : "https://www.blacktowhite.net/media/albums/my-slutty-hotwife-gf-on-holidays-without-hubby-more-of-7000kms-december-2k25.47700",
    "#category": ("xenforo", "blacktowhite", "media-album"),
    "#class"   : xenforo.XenforoMediaAlbumExtractor,
    "#auth"    : False,
    "#results" : (
        "https://www.blacktowhite.net/media/on-the-cave.947141/full",
        "https://www.blacktowhite.net/media/she-likes-to-blow-black-cocks.947140/full",
        "https://www.blacktowhite.net/media/teasing-kings-around.947139/full",
        "https://www.blacktowhite.net/media/waiting-a-caribbean-black-cock.947138/full",
    ),
    "#log": "username & password or authenticated cookies needed",

    "album"    : {
        "author"     : "westindiandick",
        "author_id"  : "128528",
        "author_slug": "westindiandick",
        "author_url" : "https://www.blacktowhite.net/members/westindiandick.128528/",
        "count"      : 5,
        "date"       : "dt:2026-03-06 05:17:08",
        "description": "",
        "id"         : "47700",
        "slug"       : "my-slutty-hotwife-gf-on-holidays-without-hubby-more-of-7000kms-december-2k25",
        "title"      : "My Slutty Hotwife Gf on holidays without hubby...More of 7000Kms... December 2K25",
        "url"        : "https://www.blacktowhite.net/media/albums/my-slutty-hotwife-gf-on-holidays-without-hubby-more-of-7000kms-december-2k25.47700/",
    },
},

{
    "#url"     : "https://www.blacktowhite.net/media/users/elodies_secret.1115361/",
    "#category": ("xenforo", "blacktowhite", "media-user"),
    "#class"   : xenforo.XenforoMediaUserExtractor,
    "#archive" : False,
    "#count"   : 14,

    "author_id"  : "1115361",
    "author_slug": "elodies_secret",
},

)
