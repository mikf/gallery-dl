# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import weverse


IMAGE_URL_PATTERN = r"https://phinf\.wevpstatic\.net/.+\.(?:gif|jpe?g|png|webp)$"
VIDEO_URL_PATTERN = r"https://weverse-rmcnmv\.akamaized\.net/.+\.(?:mp4|webm)(?:\?.+)?$"
COMBINED_URL_PATTERN = "(?i)" + IMAGE_URL_PATTERN + "|" + VIDEO_URL_PATTERN


__tests__ = (
{
    "#url": "https://weverse.io/lesserafim/artist/4-147791342",
    "#comment": "post containing both a video and image",
    "#category": ("", "weverse", "post"),
    "#class": weverse.WeversePostExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 2,

    "date": "dt:2024-01-18 06:08:35",
    "post_url": "https://weverse.io/lesserafim/artist/4-147791342",
    "post_id": "4-147791342",
    "post_type": "NORMAL",
    "section_type": "ARTIST",
    "author": {
        "id": "b60d95bc3b71f4d97b28ac1b971cc641",
        "name": "KAZUHA",
        "profile_type": "ARTIST",
    },
    "community": {
        "id": 47,
        "name": "LE SSERAFIM",
        "artist_code": "LESSERAFIM",
    },
},

{
    "#url": "https://weverse.io/lesserafim/artist/4-150863209",
    "#comment": "text only",
    "#category": ("", "weverse", "post"),
    "#class": weverse.WeversePostExtractor,
    "#count": 0,
},

{
    "#url": "https://weverse.io/dreamcatcher/artist/3-138146100",
    "#comment": ("the order of the files returned by the api does not always match the order on the site"
                 "the id of the second file returned by the api is `2-274423384`"
                 "the id of the second file displayed on the site is `3-274413871`"),
    "#category": ("", "weverse", "post"),
    "#class": weverse.WeversePostExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#range": "2",
    "#count": 1,

    "id": "3-274413871",
    "num": 2,
},

{
    "#url": "https://weverse.io/dreamcatcher/fanpost/2-135105553",
    "#comment": "fan post",
    "#category": ("", "weverse", "post"),
    "#class": weverse.WeversePostExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 1,

    "section_type": "FEED",
    "author": {
        "profile_type": "FAN",
    },
},

{
    "#url": "https://weverse.io/dreamcatcher/profile/e89820ec1a72d7255120284ca3aeafa5",
    "#category": ("", "weverse", "member"),
    "#class": weverse.WeverseMemberExtractor,
    "#pattern": weverse.WeversePostExtractor.pattern,
    "#auth": True,
},

{
    "#url": "https://weverse.io/dreamcatcher/feed",
    "#comment": "feed tab (fan posts)"
    "each pagination call returns up to 20 items",
    "#category": ("", "weverse", "feed"),
    "#class": weverse.WeverseFeedExtractor,
    "#pattern": weverse.WeversePostExtractor.pattern,
    "#auth": True,
    "#range": "21",
},

{
    "#url": "https://weverse.io/dreamcatcher/artist",
    "#comment": "artist tab (artist posts)"
    "each pagination call returns up to 20 items",
    "#category": ("", "weverse", "feed"),
    "#class": weverse.WeverseFeedExtractor,
    "#pattern": weverse.WeversePostExtractor.pattern,
    "#auth": True,
    "#range": "21",
},

{
    "#url": "https://weverse.io/dreamcatcher/moment/e89820ec1a72d7255120284ca3aeafa5/post/2-111675163",
    "#comment": "moment",
    "#category": ("", "weverse", "moment"),
    "#class": weverse.WeverseMomentExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 1,

    "width": 1080,
    "height": 1920,
    "date": "dt:2023-01-09 06:25:41",
    "expire_at": "dt:2023-01-10 06:25:41",
},

{
    "#url": "https://weverse.io/dreamcatcher/moment/785506b50e7890c3b81491f20728ee82/post/2-101327656",
    "#comment": "momentW1",
    "#category": ("", "weverse", "moment"),
    "#class": weverse.WeverseMomentExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 1,

    "width": 1128,
    "height": 1504,
    "date": "dt:2022-07-17 00:24:48",
    "expire_at": "dt:2022-07-18 00:24:48",
},

{
    "#url": "https://weverse.io/dreamcatcher/moment/e89820ec1a72d7255120284ca3aeafa5",
    "#comment": "each pagination call returns 1 item",
    "#category": ("", "weverse", "moments"),
    "#class": weverse.WeverseMomentsExtractor,
    "#pattern": weverse.WeverseMomentExtractor.pattern,
    "#auth": True,
    "#range": "2",
},

{
    "#url": "https://weverse.io/lesserafim/media/0-128617470",
    "#comment": "image",
    "#category": ("", "weverse", "media"),
    "#class": weverse.WeverseMediaExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 5,

    "media_type": "IMAGE",
    "categories": [
        {
            "id": 1091,
            "type": "MEDIA",
            "title": "PHOTOBOOK",
        },
    ],
    "community": {
        "name": "LE SSERAFIM",
    },
},

{
    "#url": "https://weverse.io/lesserafim/media/1-128435266",
    "#comment": "video",
    "#category": ("", "weverse", "media"),
    "#class": weverse.WeverseMediaExtractor,
    "#pattern": COMBINED_URL_PATTERN,
    "#count": 1,

    "width": 1080,
    "height": 1920,
    "media_type": "VOD",
    "categories": [
        {
            "id": 1532,
            "type": "MEDIA",
            "title": "Perfect Night",
        }
    ],
},

{
    "#url": "https://weverse.io/dreamcatcher/media/1-128875973",
    "#comment": "embed",
    "#category": ("", "weverse", "media"),
    "#class": weverse.WeverseMediaExtractor,

    "post_type": "YOUTUBE",
},

{
    "#url": "https://weverse.io/dreamcatcher/media",
    "#comment": "each pagination call returns up to 10 items",
    "#category": ("", "weverse", "media-tab"),
    "#class": weverse.WeverseMediaTabExtractor,
    "#pattern": weverse.WeverseMediaExtractor.pattern,
    "#auth": True,
    "#range": "11",
},

{
    "#url": "https://weverse.io/lesserafim/media/category/494",
    "#comment": "each pagination call returns up to 10 items",
    "#category": ("", "weverse", "media-category"),
    "#class": weverse.WeverseMediaCategoryExtractor,
    "#pattern": weverse.WeverseMediaExtractor.pattern,
    "#auth": True,
    "#range": "11",
},

)
