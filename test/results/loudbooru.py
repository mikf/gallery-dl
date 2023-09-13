# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import shimmie2


__tests__ = (
{
    "#url"     : "https://loudbooru.com/post/list/original_character/1",
    "#category": ("shimmie2", "loudbooru", "tag"),
    "#class"   : shimmie2.Shimmie2TagExtractor,
    "#pattern" : r"https://loudbooru\.com/_images/[0-9a-f]{32}/\d+",
    "#range"   : "1-100",
    "#count"   : 100,
},

{
    "#url"     : "https://loudbooru.com/post/view/33828",
    "#category": ("shimmie2", "loudbooru", "post"),
    "#class"   : shimmie2.Shimmie2PostExtractor,
    "#pattern"     : r"https://loudbooru\.com/_images/.+\.png",
    "#sha1_content": "a4755f787ba23ae2aa297a46810f802ca9032739",

    "extension": "png",
    "file_url" : "https://loudbooru.com/_images/ca2638d903c86e8337fe9aeb4974be88/33828%20-%202020%20artist%3Astikyfinkaz%20character%3Alisa_loud%20cover%20fanfiction%3Aplatz_eins%20frowning%20half-closed_eyes%20solo%20text%20title_card.png",
    "filename" : "33828 - 2020 artist:stikyfinkaz character:lisa_loud cover fanfiction:platz_eins frowning half-closed_eyes solo text title_card",
    "height"   : 1920,
    "id"       : 33828,
    "md5"      : "ca2638d903c86e8337fe9aeb4974be88",
    "tags"     : "2020 artist:stikyfinkaz character:lisa_loud cover fanfiction:platz_eins frowning half-closed_eyes solo text title_card",
    "width"    : 1078,
},

)
