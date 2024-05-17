# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import naver


__tests__ = (
{
    "#url"     : "https://blog.naver.com/rlfqjxm0/221430673006",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
    "#sha1_url"     : "6c694f3aced075ed5e9511f1e796d14cb26619cc",
    "#sha1_metadata": "a6e23d19afbee86b37d6e7ad934650c379d2cb1e",
},

{
    "#url"     : "https://blog.naver.com/PostView.nhn?blogId=rlfqjxm0&logNo=221430673006",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
    "#sha1_url"     : "6c694f3aced075ed5e9511f1e796d14cb26619cc",
    "#sha1_metadata": "a6e23d19afbee86b37d6e7ad934650c379d2cb1e",
},

{
    "#url"     : "https://blog.naver.com/PostView.nhn?blogId=rlfqjxm0&logNo=70161391809",
    "#comment" : "filenames in EUC-KR encoding (#5126)",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
    "#urls": (
        "https://blogfiles.pstatic.net/20130305_23/ping9303_1362411028002Dpz9z_PNG/1_사본.png",
        "https://blogfiles.pstatic.net/20130305_46/rlfqjxm0_1362473322580x33zi_PNG/오마갓합작.png",
    ),

    "blog": {
        "id"  : "rlfqjxm0",
        "num" : 43030507,
        "user": "에나",
    },
    "post": {
        "date"       : "dt:2013-03-05 17:48:00",
        "description": " ◈     PROMOTER ：핑수 ˚ 아담 EDITOR：핑수   넵：이크：핑수...",
        "num"        : 70161391809,
        "title"      : "[공유] { 합작}  OH, MY GOD! ~ 아 또 무슨 종말을 한다 그래~",
    },
    "count"    : 2,
    "num"      : range(1, 2),
    "filename" : r"re:1_사본|오마갓합작",
    "extension": "png",
},

{
    "#url"     : "https://blog.naver.com/PostView.naver?blogId=rlfqjxm0&logNo=221430673006",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
},

{
    "#url"     : "https://blog.naver.com/gukjung",
    "#category": ("", "naver", "blog"),
    "#class"   : naver.NaverBlogExtractor,
    "#pattern" : naver.NaverPostExtractor.pattern,
    "#range"   : "1-12",
    "#count"   : 12,
},

{
    "#url"     : "https://blog.naver.com/PostList.nhn?blogId=gukjung",
    "#category": ("", "naver", "blog"),
    "#class"   : naver.NaverBlogExtractor,
    "#pattern" : naver.NaverPostExtractor.pattern,
    "#range"   : "1-12",
    "#count"   : 12,
},

{
    "#url"     : "https://blog.naver.com/PostList.naver?blogId=gukjung",
    "#category": ("", "naver", "blog"),
    "#class"   : naver.NaverBlogExtractor,
},

)
