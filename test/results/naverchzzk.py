# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import naverchzzk


__tests__ = (

{
    "#url"    : "https://chzzk.naver.com/f30b95fc9af53a75b781d7d3dd933892/community/detail/13393754",
    "#class"  : naverchzzk.NaverChzzkCommentExtractor,
    "#results": (
        "https://nng-phinf.pstatic.net/MjAyNDA3MDlfNDgg/MDAxNzIwNTMzNzg2MDUx.0K9XrEW9CCSd2b7VdQHf8RGWkHAUsqEhNnLlleA11SUg.ZLx2V3gJPZR-kzrMY3E17wbu1ZmzYjitrEKmM_ykeWkg.PNG/tftyt.png",
    ),
    "#count"  : 1,

    "id"      : 13393754,
    "uid"     : "f30b95fc9af53a75b781d7d3dd933892",
    "date"    : "dt:2024-07-09 23:03:07",
    "num"     : int,
    "user"    : {
        "userNickname": "memoji",
        "userRoleCode": "streamer",
    },
    "file"     : {
        "attachType": "PHOTO",
        "date" : "dt:2024-07-09 14:03:07",
        "order": int,
        "date_updated": "dt:2024-07-09 14:03:07",
    },
},

{
    "#url"    : "https://chzzk.naver.com/f30b95fc9af53a75b781d7d3dd933892/community/detail/20273040",
    "#class"  : naverchzzk.NaverChzzkCommentExtractor,
    "#results": (
        "https://nng-phinf.pstatic.net/MjAyNTA2MTNfMTUw/MDAxNzQ5ODI1NjkyMzgx.8bsZ9moAfpuK3dqhHBxdd_CQdSuP5-MRrFgyJGDfdtEg.cs9HcI9BxBVXGUqJQhsUSGyOYvB3vj2itDB-arpvmokg.GIF/%EB%AC%BC%EC%9E%90%EB%AF%B8%EB%84%A4a.gif",
        "https://nng-phinf.pstatic.net/MjAyNTA2MTNfMTAg/MDAxNzQ5ODI1NzA2NDk4.8PHxVU-4N8UE6mnDoDRhTMYoao9p0niz08DPQEqm2pog.C4KZL_RiK-jGlfKgoXJS5LdO3BDZUuPDCSsaqttE6Jwg.GIF/%EB%AC%BC%EC%9E%90%EB%AF%B8%EB%84%A4ab.gif",
        "https://nng-phinf.pstatic.net/MjAyNTA2MTNfMjUz/MDAxNzQ5ODI1NzAzNTIw.ZODg1ok9tj0e9jQYgdAouwb_4MPX938QPWwNyhPdGs8g.wB3uMXpHObpljfoBcUTuemJfiYHTYuUT629BDIL18cog.GIF/%EB%AC%BC%EC%9E%90%EB%AF%B8%EB%84%A4b.gif",
    ),
    "#count"  : 3,

    "id"      : 20273040,
    "uid"     : "f30b95fc9af53a75b781d7d3dd933892",
    "date"    : "dt:2025-06-13 23:42:18",
    "content" : "https://mega.nz/file/DfoFgBAC#r5F_lbI4DUc2l5uuSlTMctMpk1I-qHC575ifLhYOWLI\nhttps://mega.nz/file/LWAmkCwR#BML88rd6vRu2rKg3UwKIJzdreU86w0StAmw_7h0Nueo\n\n",
    "num"     : int,
    "user"    : {
        "userNickname": "memoji",
        "userRoleCode": "streamer",
    },
    "file"      : {
        "attachType": "PHOTO",
        "date"  : "dt:2025-06-13 14:42:18",
        "width" : int,
        "order" : int,
        "height": int,
        "extraJson": "{\"width\":900,\"height\":800}",
        "date_updated": "dt:2025-06-13 14:42:18",
    },
},

{
    "#url"  : "https://chzzk.naver.com/f30b95fc9af53a75b781d7d3dd933892/community",
    "#class": naverchzzk.NaverChzzkCommunityExtractor,
    "#range": "1-50",
    "#count": 50,
},

{
    "#url"    : "https://chzzk.naver.com/f30b95fc9af53a75b781d7d3dd933892/community",
    "#class"  : naverchzzk.NaverChzzkCommunityExtractor,
    "#options": {"offset": 50},
    "#range"  : "1-50",
    "#count"  : 50,
},

)
