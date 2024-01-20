# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import blogger


__tests__ = (
{
    "#url"     : "https://www.micmicidol.club/2023/11/weekly-taishu-20231113-cover.html",
    "#category": ("blogger", "micmicidol", "post"),
    "#class"   : blogger.BloggerPostExtractor,
    "#urls"    : "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhgtpSSdrol9aKP_ztcc_mp9TUUS0U_t2DYJuGX3XCs6X5CkxIb-pM98QlxbkgJFvQj-0e6RbXNBf047qyMDZLcPJsm9dTqAn2XkTVfLhWRaxxVvIYnHYu0R0d7WsAUSFs0MDe4Sotpuqp5DQnjr45T17CXKbWtq9cR3op9dDQh3yiw2a6_HInIjLRm5io/s0/000-micmicidol.jpg",

    "blog": {
        "date"       : "dt:2023-12-13 08:31:54",
        "description": "",
        "id"         : "4995780788834875038",
        "kind"       : "blogger#blog",
        "locale"     : {
            "country" : "",
            "language": "en",
            "variant" : "",
        },
        "name"       : "MIC MIC IDOL",
        "pages"      : int,
        "posts"      : int,
        "published"  : "2023-12-13T16:31:54+08:00",
        "updated"    : str,
        "url"        : "http://www.micmicidol.club/"
    },
    "post": {
        "author"   : "MIC MIC IDOL",
        "content"  : "&nbsp;",
        "date"     : "dt:2023-11-18 08:01:00",
        "etag"     : str,
        "id"       : "2417999400144347191",
        "kind"     : "blogger#post",
        "labels"   : [
            "- Cover",
            "Weekly Taishu",
            "Weekly Taishu Cover",
        ],
        "published": "2023-11-18T16:01:00+08:00",
        "replies"  : "0",
        "title"    : "Weekly Taishu 週刊大衆 2023.11.13 Cover",
        "updated"  : "2023-12-13T16:41:54+08:00",
        "url"      : "http://www.micmicidol.club/2023/11/weekly-taishu-20231113-cover.html"
    },
    "num" : 1,
    "url" : "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhgtpSSdrol9aKP_ztcc_mp9TUUS0U_t2DYJuGX3XCs6X5CkxIb-pM98QlxbkgJFvQj-0e6RbXNBf047qyMDZLcPJsm9dTqAn2XkTVfLhWRaxxVvIYnHYu0R0d7WsAUSFs0MDe4Sotpuqp5DQnjr45T17CXKbWtq9cR3op9dDQh3yiw2a6_HInIjLRm5io/s0/000-micmicidol.jpg",
},

{
    "#url"     : "https://www.micmicidol.club/",
    "#category": ("blogger", "micmicidol", "blog"),
    "#class"   : blogger.BloggerBlogExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "https://www.micmicidol.club/search?q=cover",
    "#category": ("blogger", "micmicidol", "search"),
    "#class"   : blogger.BloggerSearchExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
    "#archive" : False,

    "query"    : "cover",
},

{
    "#url"     : "https://www.micmicidol.club/search/label/Weekly%20Taishu%20Cover",
    "#category": ("blogger", "micmicidol", "label"),
    "#class"   : blogger.BloggerLabelExtractor,
    "#range"   : "1-25",
    "#count"   : 25,

    "label"    : "Weekly Taishu Cover",
},

)
