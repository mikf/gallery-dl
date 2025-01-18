# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import khinsider


__tests__ = (
{
    "#url"     : "https://downloads.khinsider.com/game-soundtracks/album/horizon-riders-wii",
    "#class"   : khinsider.KhinsiderSoundtrackExtractor,
    "#pattern" : r"https?://(dl\.|kappa\.)?vgm(site|downloads)\.com/soundtracks/horizon-riders-wii/[^/]+/Horizon%20Riders%20Wii%20-%20Full%20Soundtrack\.mp3",
    "#count"   : 1,

    "album"    : {
        "catalog"  : "",
        "count"    : 1,
        "date"     : "Sep 18th, 2016",
        "developer": "Sabarasa",
        "publisher": "Sabarasa",
        "name"     : "Horizon Riders (WiiWare)",
        "platform" : ["Wii"],
        "size"     : 26214400,
        "type"     : "Gamerip",
        "uploader" : "",
        "year"     : "2011",

    },
    "extension": "mp3",
    "filename" : "Horizon Riders Wii - Full Soundtrack",
},

{
    "#url"  : "https://downloads.khinsider.com/game-soundtracks/album/last-kingdom-goddess-of-victory-nikke-original-soundtrack-2024",
    "#class": khinsider.KhinsiderSoundtrackExtractor,
    "#range": "1",

    "album": {
        "catalog"  : "N/A",
        "count"    : 18,
        "date"     : "Dec 23rd, 2024",
        "developer": "",
        "name"     : "Last Kingdom (Goddess of Victory: NIKKE Original Soundtrack)",
        "platform" : ["Android", "iOS", "Windows"],
        "publisher": "LEVEL NINE",
        "size"     : 138412032,
        "type"     : "Soundtrack",
        "uploader" : "ルナブレイズ",
        "year"     : "2024"
    },
    "extension": "mp3",
    "filename" : str,
    "num"      : int,
    "url"      : str,
},

)
