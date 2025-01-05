# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import danbooru


__tests__ = (
{
    "#url"     : "https://danbooru.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#sha1_content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
},

{
    "#url"     : "https://danbooru.donmai.us/posts?tags=mushishi",
    "#comment" : "test page transitions",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#count"   : ">= 300",
},

{
    "#url"     : "https://danbooru.donmai.us/posts?tags=pixiv_id%3A1476533",
    "#comment" : "'external' option (#1747)",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
    "#options" : {"external": True},
    "#pattern" : r"https://i\.pximg\.net/img-original/img/2008/08/28/02/35/48/1476533_p0\.jpg",
},

{
    "#url"     : "https://hijiribe.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://sonohara.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://safebooru.donmai.us/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://donmai.moe/posts?tags=bonocho",
    "#category": ("Danbooru", "danbooru", "tag"),
    "#class"   : danbooru.DanbooruTagExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/pools/7659",
    "#category": ("Danbooru", "danbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
    "#sha1_content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
},

{
    "#url"     : "https://danbooru.donmai.us/pool/show/7659",
    "#category": ("Danbooru", "danbooru", "pool"),
    "#class"   : danbooru.DanbooruPoolExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/posts/294929",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#sha1_content": "5e255713cbf0a8e0801dc423563c34d896bb9229",

    "approver_id": None,
    "bit_flags": 0,
    "created_at": "2008-08-12T00:46:05.385-04:00",
    "date": "dt:2008-08-12 04:46:05",
    "down_score": 0,
    "extension": "jpg",
    "fav_count": 9,
    "file_ext": "jpg",
    "file_size": 358232,
    "file_url": "https://cdn.donmai.us/original/ac/8e/ac8e3b92ea328ce9cf7211e69c905bf9.jpg",
    "filename": "ac8e3b92ea328ce9cf7211e69c905bf9",
    "has_active_children": False,
    "has_children": False,
    "has_large": True,
    "has_visible_children": False,
    "id": 294929,
    "image_height": 687,
    "image_width": 895,
    "is_banned": False,
    "is_deleted": False,
    "is_flagged": False,
    "is_pending": False,
    "large_file_url": "https://cdn.donmai.us/sample/ac/8e/sample-ac8e3b92ea328ce9cf7211e69c905bf9.jpg",
    "last_comment_bumped_at": None,
    "last_commented_at": None,
    "last_noted_at": None,
    "md5": "ac8e3b92ea328ce9cf7211e69c905bf9",
    "media_asset": dict,
    "parent_id": None,
    "pixiv_id": 1129835,
    "preview_file_url": "https://cdn.donmai.us/180x180/ac/8e/ac8e3b92ea328ce9cf7211e69c905bf9.jpg",
    "rating": "s",
    "score": 1,
    "source": "https://i.pximg.net/img-original/img/2008/07/09/16/10/23/1129835_p0.jpg",
    "subcategory": "post",
    "tag_count": 32,
    "tag_count_artist": 1,
    "tag_count_character": 3,
    "tag_count_copyright": 3,
    "tag_count_general": 23,
    "tag_count_meta": 2,
    "tag_string": "2boys bat_(animal) batman batman_(series) black_bodysuit bodysuit bonocho brown_eyes closed_mouth collared_shirt commentary_request copyright_name dc_comics expressionless facepaint glasgow_smile heath_ledger joker_(dc) male_focus multiple_boys outline outstretched_arm parted_lips photoshop_(medium) pink_shirt shirt sketch smile the_dark_knight upper_body white_outline wing_collar",
    "tag_string_artist": "bonocho",
    "tag_string_character": "batman heath_ledger joker_(dc)",
    "tag_string_copyright": "batman_(series) dc_comics the_dark_knight",
    "tag_string_general": "2boys bat_(animal) black_bodysuit bodysuit brown_eyes closed_mouth collared_shirt copyright_name expressionless facepaint glasgow_smile male_focus multiple_boys outline outstretched_arm parted_lips pink_shirt shirt sketch smile upper_body white_outline wing_collar",
    "tag_string_meta": "commentary_request photoshop_(medium)",
    "tags": [
        "2boys",
        "bat_(animal)",
        "batman",
        "batman_(series)",
        "black_bodysuit",
        "bodysuit",
        "bonocho",
        "brown_eyes",
        "closed_mouth",
        "collared_shirt",
        "commentary_request",
        "copyright_name",
        "dc_comics",
        "expressionless",
        "facepaint",
        "glasgow_smile",
        "heath_ledger",
        "joker_(dc)",
        "male_focus",
        "multiple_boys",
        "outline",
        "outstretched_arm",
        "parted_lips",
        "photoshop_(medium)",
        "pink_shirt",
        "shirt",
        "sketch",
        "smile",
        "the_dark_knight",
        "upper_body",
        "white_outline",
        "wing_collar",
    ],
    "tags_artist": [
        "bonocho",
    ],
    "tags_character": [
        "batman",
        "heath_ledger",
        "joker_(dc)",
    ],
    "tags_copyright": [
        "batman_(series)",
        "dc_comics",
        "the_dark_knight",
    ],
    "tags_general": [
        "2boys",
        "bat_(animal)",
        "black_bodysuit",
        "bodysuit",
        "brown_eyes",
        "closed_mouth",
        "collared_shirt",
        "copyright_name",
        "expressionless",
        "facepaint",
        "glasgow_smile",
        "male_focus",
        "multiple_boys",
        "outline",
        "outstretched_arm",
        "parted_lips",
        "pink_shirt",
        "shirt",
        "sketch",
        "smile",
        "upper_body",
        "white_outline",
        "wing_collar",
    ],
    "tags_meta": [
        "commentary_request",
        "photoshop_(medium)",
    ],
    "up_score": range(1, 5),
    "updated_at": "2022-07-11T23:42:31.881-04:00",
    "uploader_id": 67005,
},

{
    "#url"     : "https://danbooru.donmai.us/posts/3613024",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
    "#options" : {"ugoira": True},
    "#pattern" : r"https?://.+\.zip$",
},

{
    "#url"     : "https://danbooru.donmai.us/post/show/294929",
    "#category": ("Danbooru", "danbooru", "post"),
    "#class"   : danbooru.DanbooruPostExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/explore/posts/popular",
    "#category": ("Danbooru", "danbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
},

{
    "#url"     : "https://danbooru.donmai.us/explore/posts/popular?date=2013-06-06&scale=week",
    "#category": ("Danbooru", "danbooru", "popular"),
    "#class"   : danbooru.DanbooruPopularExtractor,
    "#range"   : "1-120",
    "#count"   : 120,
},

{
    "#url"     : "https://danbooru.donmai.us/artists/288683",
    "#category": ("Danbooru", "danbooru", "artist"),
    "#class"   : danbooru.DanbooruArtistExtractor,
    "#urls"    : "https://danbooru.donmai.us/posts?tags=kaori_%28vuoian_appxv%29",

    "created_at" : "2022-05-12T16:00:40.852-04:00",
    "updated_at" : "2022-05-12T22:10:51.917-04:00",
    "group_name" : "",
    "id"         : 288683,
    "is_banned"  : False,
    "is_deleted" : False,
    "name"       : "kaori_(vuoian_appxv)",
    "other_names": [
        "香",
        "vuoian_appxv",
    ],
},

{
    "#url"     : "https://danbooru.donmai.us/artists?commit=Search&search%5Bany_name_matches%5D=yu&search%5Border%5D=created_at",
    "#category": ("Danbooru", "danbooru", "artist-search"),
    "#class"   : danbooru.DanbooruArtistSearchExtractor,
    "#pattern" : danbooru.DanbooruTagExtractor.pattern,
    "#count"   : "> 50",

    "created_at" : str,
    "updated_at" : str,
    "group_name" : str,
    "id"         : int,
    "is_banned"  : bool,
    "is_deleted" : bool,
    "name"       : str,
    "other_names": list,
},

)
