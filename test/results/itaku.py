# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import itaku


__tests__ = (
{
    "#url"     : "https://itaku.ee/profile/piku/gallery",
    "#category": ("", "itaku", "gallery"),
    "#class"   : itaku.ItakuGalleryExtractor,
    "#pattern" : r"https://itaku\.ee/api/media/gallery_imgs/[^/?#]+\.(jpg|png|gif)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/images/100471",
    "#category": ("", "itaku", "image"),
    "#class"   : itaku.ItakuImageExtractor,
    "#urls"    : "https://itaku.ee/api/media/gallery_imgs/220504_oUNIAFT.png",

    "already_pinned"  : None,
    "blacklisted"     : {
        "blacklisted_tags": [],
        "is_blacklisted"  : False,
    },
    "can_reshare"     : True,
    "date"            : "dt:2022-05-05 19:21:17",
    "date_added"      : "2022-05-05T19:21:17.674148Z",
    "date_edited"     : "2022-05-25T14:37:46.220612Z",
    "description"     : "sketch from drawpile",
    "extension"       : "png",
    "filename"        : "220504_oUNIAFT",
    "hotness_score"   : float,
    "id"              : 100471,
    "image"           : "https://itaku.ee/api/media/gallery_imgs/220504_oUNIAFT.png",
    "image_xl"        : "https://itaku.ee/api/media/gallery_imgs/220504_oUNIAFT/lg.jpg",
    "liked_by_you"    : False,
    "maturity_rating" : "SFW",
    "num_comments"    : int,
    "num_likes"       : int,
    "num_reshares"    : int,
    "obj_tags"        : 136446,
    "owner"           : 16775,
    "owner_avatar"    : "https://itaku.ee/api/media/profile_pics/av2022r_vKYVywc/md.jpg",
    "owner_displayname": "Piku",
    "owner_username"  : "piku",
    "reshared_by_you" : False,
    "sections"        : ["Fanart/Miku"],
    "tags"            : list,
    "tags_character"  : ["hatsune_miku"],
    "tags_copyright"  : ["vocaloid"],
    "tags_general": [
        "twintails",
        "green_hair",
        "flag",
        "gloves",
        "green_eyes",
        "female",
        "racing_miku",
    ],
    "title"           : "Racing Miku 2022 Ver.",
    "too_mature"      : False,
    "uncompressed_filesize": "0.62",
    "video"           : None,
    "visibility"      : "PUBLIC",
},

{
    "#url"     : "https://itaku.ee/images/19465",
    "#comment" : "video",
    "#category": ("", "itaku", "image"),
    "#class"   : itaku.ItakuImageExtractor,
    "#urls"    : "https://itaku.ee/api/media/gallery_vids/sleepy_af_OY5GHWw.mp4",
},

{
    "#url"     : "https://itaku.ee/home/images?tags=cute",
    "#comment" : "simple search",
    "#category": ("", "itaku", "search"),
    "#class"   : itaku.ItakuSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/home/images?maturity_rating=SFW&date_range=&ordering=-date_added&text=hello&is_video=true",
    "#comment" : "search for videos",
    "#category": ("", "itaku", "search"),
    "#class"   : itaku.ItakuSearchExtractor,
    "#count"   : range(5, 50),
},

{
    "#url"     : "https://itaku.ee/home/images?tags=%2Bcute&tags=-cute&tags=~cute&maturity_rating=SFW&date_range=&ordering=-date_added",
    "#comment" : "search with postive, negative, and optional tags",
    "#category": ("", "itaku", "search"),
    "#class"   : itaku.ItakuSearchExtractor,
    "#count"   : 0,
},
)
