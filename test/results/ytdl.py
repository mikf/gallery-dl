# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import ytdl


__tests__ = (
{
    "#url"     : "ytdl:https://www.youtube.com/watch?v=BaW_jenozKc&t=1s&end=9",
    "#category": ("", "ytdl", "Youtube"),
    "#class"   : ytdl.YoutubeDLExtractor,
},

{
    "#url"     : "ytdl:http://media.w3.org/2010/05/sintel/trailer.mp4",
    "#category": ("", "ytdl-generic", "media.w3.org"),
    "#class"   : ytdl.YoutubeDLExtractor,
},

)
