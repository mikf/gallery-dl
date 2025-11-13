# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imgpile


__tests__ = (
{
    "#url"     : "https://imgpile.com/p/bbjiXrl",
    "#class"   : imgpile.ImgpilePostExtractor,
    "#results" : (
        "https://cdn.imgpile.com/f/BobTUou.jpg",
        "https://cdn.imgpile.com/f/Wr9cQFK.jpg",
        "https://cdn.imgpile.com/f/VevZbjw.png",
    ),

    "id"       : {3518940, 3518941, 3518942},
    "id_slug"  : {"BobTUou", "Wr9cQFK", "VevZbjw"},
    "count"    : 3,
    "num"      : range(1, 3),
    "filename" : str,
    "extension": {"jpg", "png"},
    "url"      : r"re:https://cdn.imgpile.com/f/\w+\.(jpg|png)",
    "post"     : {
        "author" : "zilla_64",
        "count"  : 3,
        "id"     : 105411,
        "id_slug": "bbjiXrl",
        "score"  : range(-5, 5),
        "title"  : "Mecha-King Ghidorah scans",
        "views"  : range(8_300, 12_000),
        "tags"   : [
            "text",
            "description",
            "Godzilla",
            "battle",
            "story",
            "article",
            "monsters",
            "characters",
            "device",
            "time",
            "space",
            "mecha",
        ],
    },
},

{
    "#url"     : "https://imgpile.com/u/zilla_64",
    "#class"   : imgpile.ImgpileUserExtractor,
    "#pattern" : imgpile.ImgpilePostExtractor.pattern,
    "#count"   : 16,
},

)
