# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import poringa


__tests__ = (
{
    "#url"     : "http://www.poringa.net/posts/imagenes/3051081/Turrita-alto-ojete.html",
    "#category": ("", "poringa", "post"),
    "#class"   : poringa.PoringaPostExtractor,
    "#pattern" : r"http:\/\/www\.poringa\.net\/posts\/imagenes\/3051081\/[a-zA-Z0-9_-]+\.html",

    "post_id": "3051081",
    "title"   : "turrita alto ojete...",
    "user"    : "vipower1top",
},

{
    "#url"     : "http://www.poringa.net/posts/imagenes/3095554/Otra-culona-de-instagram.html",
    "#category": ("", "poringa", "post"),
    "#class"   : poringa.PoringaPostExtractor,
    "#pattern" : r"http:\/\/www\.poringa\.net\/posts\/imagenes\/3095554\/[a-zA-Z0-9_-]+\.html",

    "album_id": "3095554",
    "title"   : "Otra culona de instagram",
    "user"    : "Expectro007",
},

{
    "#url"     : "http://www.poringa.net/Expectro007",
    "#category": ("", "poringa", "user"),
    "#class"   : poringa.PoringaUserExtractor,
    "#range"   : "1-25",
},

{
    "#url"     : "http://www.poringa.net/buscar/?&q=yuslopez",
    "#category": ("", "poringa", "search"),
    "#class"   : poringa.PoringaSearchExtractor,
    "#range"   : "1-25",
},

)
