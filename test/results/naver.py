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

)
