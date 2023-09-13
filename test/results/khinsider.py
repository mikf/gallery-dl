# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import khinsider


__tests__ = (
{
    "#url"     : "https://downloads.khinsider.com/game-soundtracks/album/horizon-riders-wii",
    "#category": ("", "khinsider", "soundtrack"),
    "#class"   : khinsider.KhinsiderSoundtrackExtractor,
    "#pattern" : r"https?://vgm(site|downloads)\.com/soundtracks/horizon-riders-wii/[^/]+/Horizon%20Riders%20Wii%20-%20Full%20Soundtrack\.mp3",
    "#count"   : 1,

    "album"    : {
        "count"   : 1,
        "date"    : "Sep 18th, 2016",
        "name"    : "Horizon Riders",
        "platform": "Wii",
        "size"    : 26214400,
        "type"    : "Gamerip",
    },
    "extension": "mp3",
    "filename" : "Horizon Riders Wii - Full Soundtrack",
},

)
