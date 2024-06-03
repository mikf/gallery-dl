# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentainexus


__tests__ = (
{
    "#url"     : "https://hentainexus.com/view/5688",
    "#category": ("", "hentainexus", "gallery"),
    "#class"   : hentainexus.HentainexusGalleryExtractor,

    "artist"     : "Tsukiriran",
    "book"       : "",
    "circle"     : "",
    "count"      : 4,
    "cover"      : str,
    "description": "The cherry blossom blooms for one final graduation memory. ❤",
    "event"      : "",
    "extension"  : "png",
    "filename"   : str,
    "gallery_id" : 5688,
    "image"      : str,
    "label"      : str,
    "lang"       : "en",
    "language"   : "English",
    "magazine"   : "Comic Bavel 2018-08",
    "num"        : range(1, 4),
    "parody"     : "Original Work",
    "publisher"  : "FAKKU",
    "tags"       : [
        "busty",
        "color",
        "creampie",
        "exhibitionism",
        "hentai",
        "kimono",
        "pubic hair",
        "uncensored",
        "vanilla",
    ],
    "title"      : "Graduation!",
    "title_conventional": "[Tsukiriran] Graduation! (Comic Bavel 2018-08)",
    "type"       : "image",
    "url_label"  : str,
},

{
    "#url"     : "https://hentainexus.com/read/5688",
    "#category": ("", "hentainexus", "gallery"),
    "#class"   : hentainexus.HentainexusGalleryExtractor,
},

{
    "#url"     : "https://hentainexus.com/?q=tag:%22heart+pupils%22%20tag:group",
    "#category": ("", "hentainexus", "search"),
    "#class"   : hentainexus.HentainexusSearchExtractor,
    "#pattern" : hentainexus.HentainexusGalleryExtractor.pattern,
    "#range"   : "1-30",
    "#count"   : 30,
},

{
    "#url"     : "https://hentainexus.com/page/3?q=tag:%22heart+pupils%22",
    "#category": ("", "hentainexus", "search"),
    "#class"   : hentainexus.HentainexusSearchExtractor,
},

)
