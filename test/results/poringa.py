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
    "#count"   : 26,

    "count"    : 26,
    "num"      : range(1, 26),
    "post_id"  : "3051081",
    "title"    : "turrita alto ojete...",
    "user"     : "vipower1top",
},

{
    "#url"     : "http://www.poringa.net/posts/imagenes/3095554/Otra-culona-de-instagram.html",
    "#category": ("", "poringa", "post"),
    "#class"   : poringa.PoringaPostExtractor,
    "#count"   : 15,

    "count"    : 15,
    "num"      : range(1, 15),
    "post_id"  : "3095554",
    "title"    : "Otra culona de instagram",
    "user"     : "Expectro007",
},

{
    "#url"     : "http://www.poringa.net/Expectro007",
    "#category": ("", "poringa", "user"),
    "#class"   : poringa.PoringaUserExtractor,
    "#pattern" : r"https?://img-\d+\.poringa\.net/poringa/img/././././././Expectro007/\w{3}\.(jpg|png|gif)",
    "#count"   : range(500, 600),
},

{
    "#url"     : "http://www.poringa.net/buscar/?&q=yuslopez",
    "#category": ("", "poringa", "search"),
    "#class"   : poringa.PoringaSearchExtractor,
    "#pattern" : r"https?://img-\d+\.poringa\.net/poringa/img/././././././\w+/\w{3}\.(jpg|png|gif)",
    "#range"   : "1-50",
    "#count"   : 50,
},

)
