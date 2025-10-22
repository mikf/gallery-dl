# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.pidgi.net/wiki/File:Key_art_-_Fight_Knight.png",
    "#category": ("wikimedia", "pidgiwiki", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#results" : "https://cdn.pidgi.net/images/0/0c/Key_art_-_Fight_Knight.png?format=original",
},

{
    "#url"     : "https://pidgi.net/wiki/File:Key_art_-_Fight_Knight.png",
    "#category": ("wikimedia", "pidgiwiki", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
