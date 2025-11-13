# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import itaku


__tests__ = (
{
    "#url"     : "https://itaku.ee/profile/piku",
    "#class"   : itaku.ItakuUserExtractor,
    "#results" : (
        "https://itaku.ee/profile/piku/gallery",
    ),
},

{
    "#url"     : "https://itaku.ee/profile/piku",
    "#class"   : itaku.ItakuUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://itaku.ee/profile/piku/gallery",
        "https://itaku.ee/profile/piku/posts",
        "https://itaku.ee/profile/piku/followers",
        "https://itaku.ee/profile/piku/following",
        "https://itaku.ee/profile/piku/stars",
    ),
},

{
    "#url"     : "https://itaku.ee/profile/piku/gallery",
    "#class"   : itaku.ItakuGalleryExtractor,
    "#pattern" : r"https://itaku\.ee/api/media/gallery_imgs/[^/?#]+\.(jpg|png|gif)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/profile/piku/gallery/7391",
    "#comment" : "gallery section (#6951)",
    "#class"   : itaku.ItakuGalleryExtractor,
    "#results" : (
        "https://itaku.ee/api/media/gallery_imgs/misty-psyduck_IWbYdwT.png",
        "https://itaku.ee/api/media/gallery_imgs/bea_alpha_N0YGfeT.png",
    ),

    "sections" : ["Fanart/Pokemon"],
},

{
    "#url"     : "https://itaku.ee/profile/piku/gallery/7391",
    "#comment" : "'order' option",
    "#class"   : itaku.ItakuGalleryExtractor,
    "#options" : {"order": "reverse"},
    "#results" : (
        "https://itaku.ee/api/media/gallery_imgs/bea_alpha_N0YGfeT.png",
        "https://itaku.ee/api/media/gallery_imgs/misty-psyduck_IWbYdwT.png",
    ),

    "sections" : ["Fanart/Pokemon"],
},

{
    "#url"     : "https://itaku.ee/profile/piku/posts",
    "#class"   : itaku.ItakuPostsExtractor,
    "#results" : (
        "https://itaku.ee/api/media/gallery_imgs/220415_xEFUVR6.png",
        "https://itaku.ee/api/media/gallery_imgs/220308_J0mgJ24.png",
        "https://itaku.ee/api/media/gallery_imgs/220511_rdGpatf.png",
        "https://itaku.ee/api/media/gallery_imgs/220420b_4Lrk6gB.png",
    ),

    "id"   : {23762, 16422},
    "count": {3, 1},
    "num"  : range(1, 3),
    "date" : "type:datetime",
    "title": {"Maids", ""},
},

{
    "#url"     : "https://itaku.ee/profile/starluxioad/posts/2008",
    "#comment" : "posts folder",
    "#class"   : itaku.ItakuPostsExtractor,
    "#count"   : 12,

    "id"   : {160779, 160163, 151859, 151851, 150443},
    "count": {2, 3},
    "num"  : range(1, 3),
    "date" : "type:datetime",
    "title": str,
},

{
    "#url"     : "https://itaku.ee/profile/piku/stars",
    "#class"   : itaku.ItakuStarsExtractor,
    "#pattern" : r"https://itaku\.ee/api/media/gallery_imgs/[^/?#]+\.(jpg|png|gif)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/profile/piku/followers",
    "#class"   : itaku.ItakuFollowersExtractor,
    "#pattern" : itaku.ItakuUserExtractor.pattern,
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://itaku.ee/profile/piku/following",
    "#class"   : itaku.ItakuFollowingExtractor,
    "#pattern" : itaku.ItakuUserExtractor.pattern,
    "#range"   : "1-60",
    "#count"   : 60,
},

{
    "#url"     : "https://itaku.ee/profile/USER/bookmarks/image/13712",
    "#class"   : itaku.ItakuBookmarksExtractor,
    "#results" : (
        "https://itaku.ee/api/media/gallery_imgs/220511_rdGpatf.png",
        "https://itaku.ee/api/media/gallery_imgs/220504_oUNIAFT.png",
        "https://itaku.ee/api/media/gallery_vids/sleepy_af_OY5GHWw.mp4",
    ),
},

{
    "#url"     : "https://itaku.ee/profile/USER/bookmarks/user/11069",
    "#class"   : itaku.ItakuBookmarksExtractor,
    "#results" : (
        "https://itaku.ee/profile/deliciousorange",
        "https://itaku.ee/profile/piku",
    ),
},

{
    "#url"     : "https://itaku.ee/images/100471",
    "#class"   : itaku.ItakuImageExtractor,
    "#results" : "https://itaku.ee/api/media/gallery_imgs/220504_oUNIAFT.png",

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
    "tags_general"    : [
        "female",
        "green_eyes",
        "twintails",
        "green_hair",
        "gloves",
        "flag",
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
    "#class"   : itaku.ItakuImageExtractor,
    "#results" : "https://itaku.ee/api/media/gallery_vids/sleepy_af_OY5GHWw.mp4",
},

{
    "#url"     : "https://itaku.ee/posts/16422",
    "#class"   : itaku.ItakuPostExtractor,
    "#results" : "https://itaku.ee/api/media/gallery_imgs/220420b_4Lrk6gB.png",

    "already_pinned" : None,
    "can_reshare"    : True,
    "category"       : "itaku",
    "content"        : "",
    "content_warning": "",
    "count"          : 1,
    "created_by_images": True,
    "date"           : "dt:2022-04-26 16:06:30",
    "date_added"     : "2022-04-26T16:06:30.352389Z",
    "date_edited"    : "2022-05-10T21:32:44.017311Z",
    "extension"      : "png",
    "file"           : {
        "already_pinned" : None,
        "animated"       : False,
        "blacklisted"    : {
            "blacklisted_tags": [],
            "is_blacklisted"  : False,
        },
        "bookmarked_by_you": False,
        "content_warning": "",
        "date"           : "dt:2022-04-26 16:06:28",
        "date_added"     : "2022-04-26T16:06:28.272442Z",
        "date_edited"    : "2022-06-30T09:43:58.816192Z",
        "id"             : 77775,
        "image"          : "https://itaku.ee/api/media/gallery_imgs/220420b_4Lrk6gB.png",
        "image_lg"       : "https://itaku.ee/api/media/gallery_imgs/220420b_4Lrk6gB/lg.jpg",
        "image_xl"       : "https://itaku.ee/api/media/gallery_imgs/220420b_4Lrk6gB/lg.jpg",
        "is_thumbnail_for_video": False,
        "liked_by_you"   : False,
        "maturity_rating": "SFW",
        "num_comments"   : 0,
        "num_likes"      : range(60, 90),
        "num_reshares"   : 0,
        "owner"          : 16775,
        "owner_displayname": "Piku",
        "show_content_warning": False,
        "title"          : "Felicia",
        "too_mature"     : False,
        "visibility"     : "PUBLIC",
    },
    "filename"       : "220420b_4Lrk6gB",
    "folders"        : [],
    "id"             : 16422,
    "liked_by_you"   : False,
    "maturity_rating": "SFW",
    "num"            : 1,
    "num_comments"   : 0,
    "num_images"     : 1,
    "num_likes"      : range(40, 70),
    "num_reshares"   : 0,
    "obj_tags"       : 99052,
    "owner"          : 16775,
    "owner_avatar"   : "https://itaku.ee/api/media/profile_pics/av2022r_vKYVywc/md.jpg",
    "owner_displayname": "Piku",
    "owner_username" : "piku",
    "poll"           : None,
    "reshared_by_you": False,
    "subcategory"    : "post",
    "tags"           : [],
    "title"          : "",
    "too_mature"     : False,
    "visibility"     : "PUBLIC",
},

{
    "#url"     : "https://itaku.ee/home/images?tags=cute",
    "#comment" : "simple search",
    "#class"   : itaku.ItakuSearchExtractor,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://itaku.ee/home/images?maturity_rating=SFW&date_range=&ordering=-date_added&text=hello&is_video=true",
    "#comment" : "search for videos",
    "#class"   : itaku.ItakuSearchExtractor,
    "#count"   : range(5, 50),
},

{
    "#url"     : "https://itaku.ee/home/images?tags=cute&tags=-cute&tags=~cute&maturity_rating=SFW&date_range=&ordering=-date_added",
    "#comment" : "search with postive, negative, and optional tags",
    "#class"   : itaku.ItakuSearchExtractor,
    "#count"   : 0,
},
)
