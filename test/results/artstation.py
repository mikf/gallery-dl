# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import artstation
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.artstation.com/sungchoi/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/(4k|large|medium|small)/[^/]+",
    "#range"   : "1-10",
    "#count"   : ">= 10",
},

{
    "#url"     : "https://www.artstation.com/sungchoi/albums/all/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/",
    "#category": ("", "artstation", "user"),
    "#class"   : artstation.ArtstationUserExtractor,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770899",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://www.artstation.com/huimeiye/albums/770898",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://huimeiye.artstation.com/albums/770899",
    "#category": ("", "artstation", "album"),
    "#class"   : artstation.ArtstationAlbumExtractor,
},

{
    "#url"     : "https://www.artstation.com/mikf/likes",
    "#category": ("", "artstation", "likes"),
    "#class"   : artstation.ArtstationLikesExtractor,
    "#pattern" : r"https://\w+\.artstation\.com/p/assets/images/images/\d+/\d+/\d+/(4k|large|medium|small)/[^/]+",
    "#count"   : 6,
},

{
    "#url"     : "https://www.artstation.com/sungchoi/likes",
    "#comment" : "no likes",
    "#category": ("", "artstation", "likes"),
    "#class"   : artstation.ArtstationLikesExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.artstation.com/contests/thu-2017/challenges/20",
    "#category": ("", "artstation", "challenge"),
    "#class"   : artstation.ArtstationChallengeExtractor,
},

{
    "#url"     : "https://www.artstation.com/contests/beyond-human/challenges/23?sorting=winners",
    "#category": ("", "artstation", "challenge"),
    "#class"   : artstation.ArtstationChallengeExtractor,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://www.artstation.com/search?query=ancient&sort_by=rank",
    "#category": ("", "artstation", "search"),
    "#class"   : artstation.ArtstationSearchExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork?sorting=latest",
    "#category": ("", "artstation", "artwork"),
    "#class"   : artstation.ArtstationArtworkExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://www.artstation.com/artwork/LQVJr",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#pattern"     : r"https?://\w+\.artstation\.com/p/assets/images/images/008/760/279/4k/.+",
    "#sha1_content": "7b113871465fdc09d127adfdc2767d51cf45a7e9",
},

{
    "#url"     : "https://www.artstation.com/artwork/Db3dy",
    "#comment" : "multiple images per project",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://www.artstation.com/artwork/g4WPK",
    "#comment" : "embedded youtube video",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#options" : {"external": True},
    "#pattern" : "ytdl:https://www.youtube.com/embed/JNFfJtwwrU0",
    "#range"   : "2",
},

{
    "#url"     : "https://www.artstation.com/artwork/3q3mXB",
    "#comment" : "404 (#3016)",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://sungchoi.artstation.com/projects/LQVJr",
    "#comment" : "alternate URL patterns",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://artstn.co/p/LQVJr",
    "#category": ("", "artstation", "image"),
    "#class"   : artstation.ArtstationImageExtractor,
},

{
    "#url"     : "https://www.artstation.com/sungchoi/following",
    "#category": ("", "artstation", "following"),
    "#class"   : artstation.ArtstationFollowingExtractor,
    "#pattern" : artstation.ArtstationUserExtractor.pattern,
    "#count"   : ">= 50",
},

)
