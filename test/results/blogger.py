# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import blogger


__tests__ = (
{
    "#url"     : "https://julianbphotography.blogspot.com/2010/12/moon-rise.html",
    "#category": ("", "blogger", "post"),
    "#class"   : blogger.BloggerPostExtractor,
    "#pattern" : "https://3.bp.blogspot.com/.*/s0/Icy-Moonrise-.*.jpg",
    "#sha1_url": "9928429fb62f712eb4de80f53625eccecc614aae",

    "blog": {
        "date"       : "dt:2010-11-21 18:19:42",
        "description": "",
        "id"         : "5623928067739466034",
        "kind"       : "blogger#blog",
        "locale"     : dict,
        "name"       : "Julian Bunker Photography",
        "pages"      : int,
        "posts"      : int,
        "published"  : "2010-11-21T10:19:42-08:00",
        "updated"    : str,
        "url"        : "http://julianbphotography.blogspot.com/",
    },
    "post": {
        "author"   : "Julian Bunker",
        "content"  : str,
        "date"     : "dt:2010-12-26 01:08:00",
        "etag"     : str,
        "id"       : "6955139236418998998",
        "kind"     : "blogger#post",
        "published": "2010-12-25T17:08:00-08:00",
        "replies"  : "0",
        "title"    : "Moon Rise",
        "updated"  : "2011-12-06T05:21:24-08:00",
        "url"      : r"re:.+/2010/12/moon-rise.html$",
    },
    "num" : int,
    "url" : str,
},

{
    "#url"     : "blogger:http://www.julianbunker.com/2010/12/moon-rise.html",
    "#category": ("", "blogger", "post"),
    "#class"   : blogger.BloggerPostExtractor,
},

{
    "#url"     : "http://cfnmscenesinmovies.blogspot.com/2011/11/cfnm-scene-jenna-fischer-in-office.html",
    "#comment" : "video (#587)",
    "#category": ("", "blogger", "post"),
    "#class"   : blogger.BloggerPostExtractor,
    "#pattern" : r"https://.+\.googlevideo\.com/videoplayback",
},

{
    "#url"     : "https://randomthingsthroughmyletterbox.blogspot.com/2022/01/bitter-flowers-by-gunnar-staalesen-blog.html",
    "#comment" : "new image domain (#2204)",
    "#category": ("", "blogger", "post"),
    "#class"   : blogger.BloggerPostExtractor,
    "#pattern" : "https://blogger.googleusercontent.com/img/a/.+=s0$",
    "#count"   : 8,
},

{
    "#url"     : "https://julianbphotography.blogspot.com/",
    "#category": ("", "blogger", "blog"),
    "#class"   : blogger.BloggerBlogExtractor,
    "#pattern" : r"https://\d\.bp\.blogspot\.com/.*/s0/[^.]+\.jpg",
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "blogger:https://www.kefblog.com.ng/",
    "#category": ("", "blogger", "blog"),
    "#class"   : blogger.BloggerBlogExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://julianbphotography.blogspot.com/search?q=400mm",
    "#category": ("", "blogger", "search"),
    "#class"   : blogger.BloggerSearchExtractor,
    "#count"   : "< 10",

    "query": "400mm",
},

{
    "#url"     : "https://dmmagazine.blogspot.com/search/label/D%26D",
    "#category": ("", "blogger", "label"),
    "#class"   : blogger.BloggerLabelExtractor,
    "#range"   : "1-25",
    "#count"   : 25,

    "label": "D&D",
},

)
