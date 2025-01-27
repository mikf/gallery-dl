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
    "type"     : "track",
    "url"      : str,
},

{
    "#url"  : "https://downloads.khinsider.com/game-soundtracks/album/super-mario-64-soundtrack",
    "#class": khinsider.KhinsiderSoundtrackExtractor,
    "#options": {"covers": True},
    "#range"  : "1-10",
    "#urls"   : (
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/00%20Front.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/01%20Back.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/02%20Booklet%20Front%20and%20Back.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/03%20Booklet%20p%2001-02.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/04%20Booklet%20p%2003-04.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/05%20Booklet%20p%2005-06.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/06%20Disc.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/07%20Front%20digital.png",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/08%20Obi.jpg",
        "https://vgmsite.com/soundtracks/super-mario-64-soundtrack/09%20Tray.jpg",
    ),

    "extension": {"jpg", "png"},
    "type"     : "cover",
    "album"    : {
        "catalog"  : "PCCG-00357",
        "count"    : 36,
        "date"     : "Jul 1st, 2024",
        "developer": "",
        "name"     : "Super Mario 64 Original Soundtrack",
        "platform" : ["N64"],
        "publisher": "Nintendo",
        "size"     : 102760448,
        "type"     : "Soundtrack",
        "uploader" : "HeroArts",
        "year"     : "1996",
    },
},

)
