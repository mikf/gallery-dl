# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import idolcomplex
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.idolcomplex.com/en/posts?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
    "#pattern" : r"https://i[sv]\.sankakucomplex\.com/data/[^/]{2}/[^/]{2}/[^/]{32}\.\w+\?e=\d+&.+",
    "#range"   : "18-22",
    "#count"   : 5,
},

{
    "#url"     : "https://www.idolcomplex.com/zh-CN/posts?tags=lyumos",
    "#comment" : "locale code (ISO 639-1 + ISO 3166-1) (#8667)",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idolcomplex.com/posts?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/posts/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/?tags=lyumos+wreath&page=3&next=694215",
    "#category": ("booru", "idolcomplex", "tag"),
    "#class"   : idolcomplex.IdolcomplexTagExtractor,
},

{
    "#url"     : "https://www.idolcomplex.com/en/pools/e9PMwnwRBK3",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
    "#auth"    : True,
    "#pattern" : (
        r"https://iv.sankakucomplex.com/data/50/9e/509eccbba54a43cea6b275a65b93c51d\.jpg\?e=\d+&expires=\d+&m=.+",
        r"https://iv.sankakucomplex.com/data/cf/ae/cfae655b594634126bddc10ba7965485\.jpg\?e=\d+&expires=\d+&m=.+",
        r"https://iv.sankakucomplex.com/data/53/b3/53b3d915a79ac72747455f4d0e843fc0\.jpg\?e=\d+&expires=\d+&m=.+",
    ),
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/pools/e9PMwnwRBK3",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/pools/show/145",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/pool/show/145",
    "#category": ("booru", "idolcomplex", "pool"),
    "#class"   : idolcomplex.IdolcomplexPoolExtractor,
},

{
    "#url"     : "https://www.idolcomplex.com/en/posts/vkr36qdOaZ4",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
    "#auth"    : True,
    "#sha1_content": "694ec2491240787d75bf5d0c75d0082b53a85afd",

    "audios"          : [],
    "author"          : {
        "avatar"       : str,
        "avatar_rating": "q",
        "display_name" : "kekal",
        "id"           : "8YEa7e8RmD0",
        "level"        : 20,
        "name"         : "kekal",
    },
    "category"        : "idolcomplex",
    "change"          : 2121180,
    "comment_count"   : None,
    "created_at"      : 1511560888,
    "date"            : "dt:2017-11-24 22:01:28",
    "extension"       : "jpg",
    "fav_count"       : range(90, 120),
    "file_ext"        : "jpg",
    "file_size"       : 97521,
    "file_type"       : "image/jpeg",
    "file_url"        : r"re:https?://iv.sankakucomplex.com/data/50/9e/509eccbba54a43cea6b275a65b93c51d.jpg\?e=\d+&.+",
    "filename"        : "509eccbba54a43cea6b275a65b93c51d",
    "generation_directives": None,
    "gif_preview_url" : None,
    "has_children"    : False,
    "has_comments"    : False,
    "has_notes"       : False,
    "height"          : 683,
    "id"              : "vkr36qdOaZ4",
    "in_visible_pool" : True,
    "is_anonymous"    : False,
    "is_favorited"    : False,
    "is_note_locked"  : False,
    "is_premium"      : False,
    "is_rating_locked": False,
    "is_restricted_anonymous_upload": False,
    "is_status_locked": False,
    "md5"             : "509eccbba54a43cea6b275a65b93c51d",
    "parent_id"       : None,
    "preview_height"  : 400,
    "preview_url"     : r"re:https?://iv.sankakucomplex.com/data/preview/50/9e/509eccbba54a43cea6b275a65b93c51d.avif\?e=\d+&.+",
    "preview_width"   : 600,
    "rating"          : "s",
    "reactions"       : [],
    "redirect_to_signup": False,
    "sample_height"   : 683,
    "sample_url"      : r"re:https?://iv.sankakucomplex.com/data/50/9e/509eccbba54a43cea6b275a65b93c51d.jpg\?e=\d+&.+",
    "sample_width"    : 1024,
    "sequence"        : None,
    "source"          : "removed",
    "status"          : "active",
    "subtitles"       : [],
    "tag_string"      : "lyumos the_witcher shani_(the_witcher) cosplay waistcoat wreath female green_eyes non-asian red_hair 1girl 3:2_aspect_ratio tagme",
    "tags"            : [
        "lyumos",
        "the_witcher",
        "shani_(the_witcher)",
        "cosplay",
        "waistcoat",
        "wreath",
        "female",
        "green_eyes",
        "non-asian",
        "red_hair",
        "1girl",
        "3:2_aspect_ratio",
        "tagme",
    ],
    "total_score"     : range(120, 150),
    "total_tags"      : 13,
    "user_vote"       : None,
    "video_duration"  : None,
    "vote_count"      : range(25, 50),
    "width"           : 1024,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/vkr36qdOaZ4",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/en/posts/show/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/posts/509eccbba54a43cea6b275a65b93c51d",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
},

{
    "#url"     : "https://idol.sankakucomplex.com/post/show/694215",
    "#category": ("booru", "idolcomplex", "post"),
    "#class"   : idolcomplex.IdolcomplexPostExtractor,
    "#exception": exception.AbortExtraction,
    "#sha1_content": "694ec2491240787d75bf5d0c75d0082b53a85afd",

    "id"            : "vkr36qdOaZ4",  # legacy ID: 694215
    "tags_character": "shani_(the_witcher)",
    "tags_copyright": "the_witcher",
    "tags_idol"     : str,
    "tags_medium"   : str,
    "tags_general"  : str,
},

)
