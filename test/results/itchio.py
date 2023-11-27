# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import itchio


__tests__ = (
{
    "#url"     : "https://sirtartarus.itch.io/a-craft-of-mine",
    "#category": ("", "itchio", "game"),
    "#class"   : itchio.ItchioGameExtractor,
    "#pattern" : r"https://(dl.itch.zone|itchio-mirror.\w+.r2.cloudflarestorage.com)/upload2/game/1983311/\d+\?",
    "#count"   : 3,

    "extension": "",
    "filename" : r"re:\d+",
    "game"     : {
        "id"   : 1983311,
        "noun" : "game",
        "title": "A Craft Of Mine",
        "url"  : "https://sirtartarus.itch.io/a-craft-of-mine",
    },
    "user"     : {
        "id"  : 4060052,
        "name": "SirTartarus",
        "url" : "https://sirtartarus.itch.io",
    },
},

)
