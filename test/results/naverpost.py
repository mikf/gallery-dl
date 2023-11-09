# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import naverpost

IMAGE_URL_PATTERN = r"(?i)https://post-phinf\.pstatic\.net/.*\.(?:gif|jpe?g|png|webp)"


__tests__ = (
{
    "#url": "https://m.post.naver.com/viewer/postView.nhn?volumeNo=15861102&memberNo=16220685",
    "#comment": ".nhn page extension",
    "#category": ("", "naverpost", "post"),
    "#class": naverpost.NaverpostPostExtractor,
    "#pattern": IMAGE_URL_PATTERN,
    "#count": 34,

    "title": "[쇼! 음악중심] 180526 방탄소년단 FAKE LOVE 현장 포토",
    "description": "[BY MBC예능연구소] [쇼! 음악중심] 589회, 20180526 ※본 콘텐츠는 상업적 용도의 사용을 금합니다.",
    "author": "MBC예능연구소",
    "date": "dt:2018-05-29 12:09:34",
    "views": int,
},

{
    "#url": "https://post.naver.com/viewer/postView.naver?volumeNo=31389956&memberNo=29156514",
    "#comment": ".naver page extension",
    "#category": ("", "naverpost", "post"),
    "#class": naverpost.NaverpostPostExtractor,
    "#pattern": IMAGE_URL_PATTERN,
    "#count": 48,

    "title": "매일 밤 꿈꿔 왔던 드림캐쳐 '바람아' 활동 비하인드 현장",
    "description": "[BY 드림캐쳐컴퍼니] 안녕하세요.드림캐쳐 포스트 지기입니다!(*･▽･*)'Odd Eye' 활동이 끝나고 아쉬웠을...",
    "author": "드림캐쳐컴퍼니",
    "date": "dt:2021-05-03 06:00:09",
    "views": int,
},

{
    "#url": "https://post.naver.com/my.naver?memberNo=29156514",
    "#comment": "up to 20 posts are returned per request",
    "#category": ("", "naverpost", "user"),
    "#class": naverpost.NaverpostUserExtractor,
    "#pattern": naverpost.NaverpostPostExtractor.pattern,
    "#range": "1-21",
    "#count": 21,
},

)
