# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wallpapercave


__tests__ = (
{
    "#url"     : "https://wallpapercave.com/w/wp10270355",
    "#category": ("", "wallpapercave", "image"),
    "#class"   : wallpapercave.WallpapercaveImageExtractor,
    "#urls"        : "https://wallpapercave.com/download/sekai-saikou-no-ansatsusha-isekai-kizoku-ni-tensei-suru-wallpapers-wp10270355",
    "#sha1_content": "58b088aaa1cf1a60e347015019eb0c5a22b263a6",
},

{
    "#url"     : "https://wallpapercave.com/apple-wwdc-2024-wallpapers",
    "#comment" : "album listing",
    "#category": ("", "wallpapercave", "image"),
    "#class"   : wallpapercave.WallpapercaveImageExtractor,
    "#archive" : False,
    "#urls"    : [
        "https://wallpapercave.com/wp/wp13775438.jpg",
        "https://wallpapercave.com/wp/wp13775439.jpg",
        "https://wallpapercave.com/wp/wp13775440.jpg",
        "https://wallpapercave.com/wp/wp13775441.jpg",
    ],
},

)
