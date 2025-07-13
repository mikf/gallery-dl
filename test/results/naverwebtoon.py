# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import naverwebtoon


__tests__ = (
{
    "#url"     : "https://comic.naver.com/webtoon/detail?titleId=26458&no=1&weekday=tue",
    "#class"   : naverwebtoon.NaverWebtoonEpisodeExtractor,
    "#count"       : 14,
    "#sha1_url"    : "47a956ba8c7a837213d5985f50c569fcff986f75",
    "#sha1_content": "3806b6e8befbb1920048de9888dfce6220f69a60",

    "author"   : ["김규삼"],
    "artist"   : ["김규삼"],
    "comic"    : "N의등대-눈의등대",
    "count"    : 14,
    "episode"  : "1",
    "extension": "jpg",
    "num"      : int,
    "tags"     : [
        "스릴러",
        "완결무료",
        "완결스릴러",
    ],
    "title"    : "n의 등대 - 눈의 등대 1화",
    "title_id" : "26458",
},

{
    "#url"     : "https://comic.naver.com/challenge/detail?titleId=765124&no=1",
    "#class"   : naverwebtoon.NaverWebtoonEpisodeExtractor,
    "#pattern" : r"https://image-comic\.pstatic\.net/user_contents_data/challenge_comic/2021/01/19/342586/upload_7149856273586337846\.jpeg",
    "#count"   : 1,

    "author"   : ["kemi****"],
    "artist"   : [],
    "comic"    : "우니 모두의 이야기",
    "count"    : 1,
    "episode"  : "1",
    "extension": "jpeg",
    "filename" : "upload_7149856273586337846",
    "num"      : 1,
    "tags"     : [
        "일상툰",
        "우니모두의이야기",
        "퇴사",
        "입사",
        "신입사원",
        "사회초년생",
        "회사원",
        "20대",
    ],
    "title"    : "퇴사하다",
    "title_id" : "765124",
},

{
    "#url"     : "https://comic.naver.com/bestChallenge/detail?titleId=620732&no=334",
    "#comment" : "empty tags (#5120)",
    "#class"   : naverwebtoon.NaverWebtoonEpisodeExtractor,
    "#count"   : 9,

    "artist"  : [],
    "author"  : ["안트로anthrokim"],
    "comic"   : "백일몽화원",
    "count"   : 9,
    "episode" : "334",
    "num"     : range(1, 9),
    "tags"    : [],
    "title"   : "321화... 성(省)",
    "title_id": "620732",
},

{
    "#url"     : "https://comic.naver.com/bestChallenge/detail.nhn?titleId=771467&no=3",
    "#class"   : naverwebtoon.NaverWebtoonEpisodeExtractor,
    "#pattern" : r"https://image-comic\.pstatic\.net/user_contents_data/challenge_comic/2021/04/28/345534/upload_3617293622396203109\.jpeg",
    "#count"   : 1,
},

{
    "#url"     : "https://comic.naver.com/webtoon/list?titleId=22073",
    "#class"   : naverwebtoon.NaverWebtoonComicExtractor,
    "#pattern" : naverwebtoon.NaverWebtoonEpisodeExtractor.pattern,
    "#count"   : 32,
},

{
    "#url"     : "https://comic.naver.com/webtoon/list?titleId=765124",
    "#comment" : "/webtoon/ path for 'challenge' comic (#5123)",
    "#class"   : naverwebtoon.NaverWebtoonComicExtractor,
    "#range"   : "1",
    "#results" : "https://comic.naver.com/challenge/detail?titleId=765124&no=1",
},

{
    "#url"     : "https://comic.naver.com/challenge/list?titleId=765124",
    "#class"   : naverwebtoon.NaverWebtoonComicExtractor,
    "#pattern" : naverwebtoon.NaverWebtoonEpisodeExtractor.pattern,
    "#count"   : 24,
},

{
    "#url"     : "https://comic.naver.com/bestChallenge/list.nhn?titleId=789786",
    "#class"   : naverwebtoon.NaverWebtoonComicExtractor,
    "#pattern" : naverwebtoon.NaverWebtoonEpisodeExtractor.pattern,
    "#count"   : 1,
},

)
