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
    "#pattern" : r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_imgs/[^/?#]+\.(jpg|png|gif)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/images/100471",
    "#category": ("", "itaku", "image"),
    "#class"   : itaku.ItakuImageExtractor,
    "#pattern" : r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_imgs/220504_oUNIAFT\.png",
    "#count"   : 1,

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
    "image"           : "https://d1wmr8tlk3viaj.cloudfront.net/gallery_imgs/220504_oUNIAFT.png",
    "image_xl"        : "https://d1wmr8tlk3viaj.cloudfront.net/gallery_imgs/220504_oUNIAFT/lg.jpg",
    "liked_by_you"    : False,
    "maturity_rating" : "SFW",
    "num_comments"    : int,
    "num_likes"       : int,
    "num_reshares"    : int,
    "obj_tags"        : 136446,
    "owner"           : 16775,
    "owner_avatar"    : "https://d1wmr8tlk3viaj.cloudfront.net/profile_pics/av2022r_vKYVywc/md.jpg",
    "owner_displayname": "Piku",
    "owner_username"  : "piku",
    "reshared_by_you" : False,
    "sections"        : ["Fanart/Miku"],
    "tags"            : list,
    "tags_character"  : ["hatsune_miku"],
    "tags_copyright"  : ["vocaloid"],
    "tags_general"    : [
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
    "#pattern" : r"https://d1wmr8tlk3viaj\.cloudfront\.net/gallery_vids/sleepy_af_OY5GHWw\.mp4",
},

)
