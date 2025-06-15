# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://rule34hentai.net/post/list/mizuki_kotora/1",
    "#category": ("shimmie2", "rule34hentai", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#results" : (
        "https://rule34hentai.net/_images/7f3a411263d0f6de936e47ae8f9d35fb/332%20-%20Darkstalkers%20Felicia%20mizuki_kotora.jpeg",
        "https://rule34hentai.net/_images/1a8eca7c04f8bf325bc993c5751a91c4/264%20-%20Darkstalkers%20Felicia%20mizuki_kotora.jpeg",
        "https://rule34hentai.net/_images/09511511c4c9e9e1f9b795e059a60832/259%20-%20Darkstalkers%20Felicia%20mizuki_kotora.jpeg",
    ),

    "extension"  : "jpeg",
    "file_url"   : r"re:https://rule34hentai.net/_images/.+\.jpeg",
    "filename"   : r"re:\d+ - \w+",
    "height"     : range(496, 875),
    "id"         : range(259, 332),
    "md5"        : r"re:^[0-9a-f]{32}$",
    "search_tags": "mizuki_kotora",
    "size"       : int,
    "tags"       : str,
    "width"      : range(500, 850),
},

{
    "#url"     : "https://rule34hentai.net/post/view/264",
    "#category": ("shimmie2", "rule34hentai", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#results"     : "https://rule34hentai.net/_images/1a8eca7c04f8bf325bc993c5751a91c4/264%20-%20Darkstalkers%20Felicia%20mizuki_kotora.jpg",
    "#sha1_content": "6c23780bb78673cbff1bca9accb77ea11ec734f3",

    "extension": "jpg",
    "file_url" : "https://rule34hentai.net/_images/1a8eca7c04f8bf325bc993c5751a91c4/264%20-%20Darkstalkers%20Felicia%20mizuki_kotora.jpg",
    "filename" : "264 - Darkstalkers Felicia mizuki_kotora",
    "height"   : 875,
    "id"       : 264,
    "md5"      : "1a8eca7c04f8bf325bc993c5751a91c4",
    "size"     : 0,
    "tags"     : "Darkstalkers Felicia mizuki_kotora",
    "width"    : 657,
},

)
