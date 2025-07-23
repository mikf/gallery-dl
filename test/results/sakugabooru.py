# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import moebooru


__tests__ = (
{
    "#url"     : "https://www.sakugabooru.com/post/show/125570",
    "#category": ("moebooru", "sakugabooru", "post"),
    "#class"   : moebooru.MoebooruPostExtractor,
    "#options" : {"tags": True},
    "#results" : "https://www.sakugabooru.com/data/31db5edb23f7b5db590d182ea84a00b2.mp4",

    "actual_preview_height": 169,
    "actual_preview_width": 300,
    "approver_id": 508,
    "author": "chii",
    "change": 595064,
    "created_at": 1592745120,
    "creator_id": 5287,
    "date"      : "dt:2020-06-21 13:12:00",
    "extension": "mp4",
    "file_ext": "mp4",
    "file_size": 3472647,
    "file_url": "https://www.sakugabooru.com/data/31db5edb23f7b5db590d182ea84a00b2.mp4",
    "filename": "31db5edb23f7b5db590d182ea84a00b2",
    "frames": [],
    "frames_pending": [],
    "frames_pending_string": "",
    "frames_string": "",
    "has_children": False,
    "height": 480,
    "id": 125570,
    "is_held": False,
    "is_note_locked": False,
    "is_pending": False,
    "is_rating_locked": False,
    "is_shown_in_index": True,
    "jpeg_file_size": 0,
    "jpeg_height": 480,
    "jpeg_url": "https://www.sakugabooru.com/data/31db5edb23f7b5db590d182ea84a00b2.mp4",
    "jpeg_width": 854,
    "last_commented_at": 0,
    "last_noted_at": 0,
    "md5": "31db5edb23f7b5db590d182ea84a00b2",
    "parent_id": None,
    "preview_height": 84,
    "preview_url": "https://www.sakugabooru.com/data/preview/31db5edb23f7b5db590d182ea84a00b2.jpg",
    "preview_width": 150,
    "rating": "s",
    "sample_file_size": 0,
    "sample_height": 480,
    "sample_url": "https://www.sakugabooru.com/data/31db5edb23f7b5db590d182ea84a00b2.mp4",
    "sample_width": 854,
    "score": range(20, 50),
    "source": "#14",
    "status": "active",
    "tags": "animals animated artist_unknown character_acting creatures nichijou smears",
    "tags_artist": "artist_unknown",
    "tags_copyright": "nichijou",
    "tags_general": "animals animated character_acting creatures smears",
    "updated_at": 1592819293,
    "width": 854,
},

{
    "#url"     : "https://www.sakugabooru.com/post?tags=nichijou",
    "#category": ("moebooru", "sakugabooru", "tag"),
    "#class"   : moebooru.MoebooruTagExtractor,
},

{
    "#url"     : "https://www.sakugabooru.com/pool/show/1",
    "#category": ("moebooru", "sakugabooru", "pool"),
    "#class"   : moebooru.MoebooruPoolExtractor,
    "#options" : {"metadata": True},
    "#results" : (
        "https://www.sakugabooru.com/data/cd1fe3601ddbb8b13db794a1f51acf36.gif",
        "https://www.sakugabooru.com/data/c6dedf058957f89126bcbdfd209bfc69.gif",
        "https://www.sakugabooru.com/data/3a8d6b7ec40fb66447d160d53759ec71.gif",
        "https://www.sakugabooru.com/data/09f50c0cc6b3d922cd6b34a99103cc51.gif",
        "https://www.sakugabooru.com/data/9d219fd70727eb9fe5a7fb04b7cc7c47.gif",
        "https://www.sakugabooru.com/data/5a2d035974f26221ce3d8914e74695c6.gif",
    ),

    "pool": {
        "created_at" : "2013-08-18T15:48:19.938Z",
        "description": "",
        "id"         : 1,
        "is_public"  : True,
        "name"       : "Yutapon Stranger Genga Comparisons",
        "post_count" : 6,
        "updated_at" : "2013-08-18T15:58:19.037Z",
        "user_id"    : 4,
    },
},

{
    "#url"     : "https://www.sakugabooru.com/post/popular_recent",
    "#category": ("moebooru", "sakugabooru", "popular"),
    "#class"   : moebooru.MoebooruPopularExtractor,
},

)
