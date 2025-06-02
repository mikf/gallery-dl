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
    "#url"     : "https://blog.naver.com/jws790103/223239681955",
    "#comment" : "videos",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
    "#pattern" : (
        r"https://blogfiles.pstatic.net/MjAyMzA5MjVfMTMy/MDAxNjk1NjQ0MzI4OTE3.UxgvxTesk7Y88OWGvPMwQhbmCPp6mPA_C-5l5lJggyEg.B0DbxNEzz3DxRJtShiiBHDLzLQSCFDo_Bp6c-bcMDiog.JPEG.jws790103/20230925%EF%BC%BF080218.jpg",
        r"https://blogfiles.pstatic.net/MjAyMzA5MjVfMjAz/MDAxNjk1NjQ0MzI4OTA5.Kd4VzqHhhrgby7rCA1iPdBX6f_k2DPEBnlRdOWD-kPgg.U0C1lmlKVMZMA4hhhs69nolZwCZ4Plme4KVbNfhezhkg.JPEG.jws790103/20230925%EF%BC%BF081103.jpg",
        r"https://blogfiles.pstatic.net/MjAyMzA5MjVfMTg3/MDAxNjk1NjQ0MzI4OTk2.faiqny7Fl82Nnc3cJj85xa_MSBjYR3BStKeHw2bjYTwg.7Z8w0lDO9Uhjr8QTGwA0az_UZhN9haHocbYWgEyBO9gg.JPEG.jws790103/20230925%EF%BC%BF081141.jpg",
        r"https://blogfiles.pstatic.net/MjAyMzA5MjVfMTIz/MDAxNjk1NjQ0MzI4OTIz.xkrCwJuYVtQID9td3XdEz8JHHrdN5UZzfOJ6nb1rW4Mg.d1FfbB8GONEej23X9Uc9uAP_oBwWnTbb9aFaBCrkfQEg.JPEG.jws790103/20230925%EF%BC%BF100506.jpg",
        r"https://blogfiles.pstatic.net/MjAyMzA5MjVfMjI4/MDAxNjk1NjQ0MzI5Njg4.BHqs4eTTqOFfvYx7oZBCdeYXkQOkTFiTb8kWdC4JLeYg.8ytEDpmgyn79au0g1vGJhVxRPRVlKLF0gwQe4L0egFIg.JPEG.jws790103/20230925%EF%BC%BF100548.jpg",
        r"https://a01-g-naver-vod.akamaized.net/blog/a/read/v2/VOD_ALPHA/blog_2023_10_18_2486/base_pathfinder_pf3448100_81cd756f-6cff-11ee-b67f-80615f0c46d6.mp4\?__gda__=\d+_\w+&in_out_flag=1",
        r"https://a01-g-naver-vod.akamaized.net/blog/a/read/v2/VOD_ALPHA/blog_2023_10_18_162/base_pathfinder_pf3448100_810b0fc9-6cff-11ee-8895-a0369ffde1ec.mp4\?__gda__=\d+_\w+&in_out_flag=1",
    ),

    "blog": {
        "id"  : "jws790103",
        "num" : 25591202,
        "user": "fm컴퍼니 짱",
    },
    "post": {
        "date"       : "dt:2023-10-18 06:50:00",
        "description": "체육행사 기획행사는 fm컴퍼니에서 함께 하겠습니다. 어린이집 연합회 마라톤 대회에 무대렌탈 장비를 대여...",
        "num"        : 223239681955,
        "title"      : "마라톤대회 무대설치 기획행사 무대설치 체육행사 무대설치완료 fm컴퍼니에서 함께 하였습니다.",
    },
    "extension": {"jpg", "mp4"},
    "count"    : 7,
    "num"      : range(1, 7),
},

{
    "#url"     : "https://blog.naver.com/jws790103/223239681955",
    "#comment" : "'videos' option",
    "#category": ("", "naver", "post"),
    "#class"   : naver.NaverPostExtractor,
    "#options" : {"videos": False},
    "#urls": (
        "https://blogfiles.pstatic.net/MjAyMzA5MjVfMTMy/MDAxNjk1NjQ0MzI4OTE3.UxgvxTesk7Y88OWGvPMwQhbmCPp6mPA_C-5l5lJggyEg.B0DbxNEzz3DxRJtShiiBHDLzLQSCFDo_Bp6c-bcMDiog.JPEG.jws790103/20230925%EF%BC%BF080218.jpg",
        "https://blogfiles.pstatic.net/MjAyMzA5MjVfMjAz/MDAxNjk1NjQ0MzI4OTA5.Kd4VzqHhhrgby7rCA1iPdBX6f_k2DPEBnlRdOWD-kPgg.U0C1lmlKVMZMA4hhhs69nolZwCZ4Plme4KVbNfhezhkg.JPEG.jws790103/20230925%EF%BC%BF081103.jpg",
        "https://blogfiles.pstatic.net/MjAyMzA5MjVfMTg3/MDAxNjk1NjQ0MzI4OTk2.faiqny7Fl82Nnc3cJj85xa_MSBjYR3BStKeHw2bjYTwg.7Z8w0lDO9Uhjr8QTGwA0az_UZhN9haHocbYWgEyBO9gg.JPEG.jws790103/20230925%EF%BC%BF081141.jpg",
        "https://blogfiles.pstatic.net/MjAyMzA5MjVfMTIz/MDAxNjk1NjQ0MzI4OTIz.xkrCwJuYVtQID9td3XdEz8JHHrdN5UZzfOJ6nb1rW4Mg.d1FfbB8GONEej23X9Uc9uAP_oBwWnTbb9aFaBCrkfQEg.JPEG.jws790103/20230925%EF%BC%BF100506.jpg",
        "https://blogfiles.pstatic.net/MjAyMzA5MjVfMjI4/MDAxNjk1NjQ0MzI5Njg4.BHqs4eTTqOFfvYx7oZBCdeYXkQOkTFiTb8kWdC4JLeYg.8ytEDpmgyn79au0g1vGJhVxRPRVlKLF0gwQe4L0egFIg.JPEG.jws790103/20230925%EF%BC%BF100548.jpg",
    ),

    "extension": "jpg",
    "count"    : 5,
    "num"      : range(1, 5),
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
