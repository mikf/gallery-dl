# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pillowfort
import datetime


__tests__ = (
{
    "#url"     : "https://www.pillowfort.social/posts/27510",
    "#category": ("", "pillowfort", "post"),
    "#class"   : pillowfort.PillowfortPostExtractor,
    "#pattern" : r"https://img\d+\.pillowfort\.social/posts/\w+_out\d+\.png",
    "#count"   : 4,

    "avatar_url"      : str,
    "col"             : 0,
    "commentable"     : True,
    "comments_count"  : int,
    "community_id"    : None,
    "content"         : str,
    "created_at"      : str,
    "date"            : datetime.datetime,
    "deleted"         : None,
    "deleted_at"      : None,
    "deleted_by_mod"  : None,
    "deleted_for_flag_id": None,
    "embed_code"      : None,
    "id"              : int,
    "last_activity"   : str,
    "last_activity_elapsed": str,
    "last_edited_at"  : str,
    "likes_count"     : int,
    "media_type"      : "picture",
    "nsfw"            : False,
    "num"             : int,
    "original_post_id": None,
    "original_post_user_id": None,
    "picture_content_type": None,
    "picture_file_name": None,
    "picture_file_size": None,
    "picture_updated_at": None,
    "post_id"         : 27510,
    "post_type"       : "picture",
    "privacy"         : "public",
    "reblog_copy_info": list,
    "rebloggable"     : True,
    "reblogged_from_post_id": None,
    "reblogged_from_user_id": None,
    "reblogs_count"   : int,
    "row"             : int,
    "small_image_url" : None,
    "tags"            : list,
    "time_elapsed"    : str,
    "timestamp"       : str,
    "title"           : "What is Pillowfort.social?",
    "updated_at"      : str,
    "url"             : r"re:https://img3.pillowfort.social/posts/.*\.png",
    "user_id"         : 5,
    "username"        : "Staff",
},

{
    "#url"     : "https://www.pillowfort.social/posts/1557500",
    "#category": ("", "pillowfort", "post"),
    "#class"   : pillowfort.PillowfortPostExtractor,
    "#options" : {
        "external": True,
        "inline"  : False,
    },
    "#pattern" : r"https://twitter\.com/Aliciawitdaart/status/1282862493841457152",
},

{
    "#url"     : "https://www.pillowfort.social/posts/1672518",
    "#category": ("", "pillowfort", "post"),
    "#class"   : pillowfort.PillowfortPostExtractor,
    "#options" : {"inline": True},
    "#count"   : 3,
},

{
    "#url"     : "https://www.pillowfort.social/Pome",
    "#category": ("", "pillowfort", "user"),
    "#class"   : pillowfort.PillowfortUserExtractor,
    "#pattern" : r"https://img\d+\.pillowfort\.social/posts/",
    "#range"   : "1-15",
    "#count"   : 15,
},

)
