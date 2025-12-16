# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import aryion


__tests__ = (
{
    "#url"     : "https://aryion.com/g4/gallery/jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
    "#options" : {"recursive": False},
    "#pattern" : r"https://aryion\.com/g4/data\.php\?id=\d+$",
    "#range"   : "48-52",
    "#count"   : 5,
},

{
    "#url"     : "https://aryion.com/g4/user/jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
},

{
    "#url"     : "https://aryion.com/g4/latest.php?name=jameshoward",
    "#category": ("", "aryion", "gallery"),
    "#class"   : aryion.AryionGalleryExtractor,
},

{
    "#url"     : "https://aryion.com/g4/favorites/jameshoward",
    "#category": ("", "aryion", "favorite"),
    "#class"   : aryion.AryionFavoriteExtractor,
    "#range"   : "1-10",
    "#count"   : 10,

    "user"     : "jameshoward",
    "artist"   : "re:^((?!jameshoward).)*$",
},

{
    "#url"     : "https://aryion.com/g4/favorites/CultOfTheShyCorpus",
    "#class"   : aryion.AryionFavoriteExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://aryion.com/g4/data.php?id=373076",
        "https://aryion.com/g4/data.php?id=373075",
        "https://aryion.com/g4/data.php?id=373074",
    ),

    "user"  : "CultOfTheShyCorpus",
    "folder": "Camilla Swallows Corrin",
    "path"  : [
        "Older Art!",
        "Older Fanart!",
    ],
},

{
    "#url"     : "https://aryion.com/g4/favorites/CultOfTheShyCorpus/Elf%27s%20Revenge",
    "#comment" : "'category' URL (#8705)",
    "#class"   : aryion.AryionFavoriteExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://aryion.com/g4/data.php?id=531328",
        "https://aryion.com/g4/data.php?id=403354",
        "https://aryion.com/g4/data.php?id=361515",
    ),

    "folder"     : "Elf's Revenge",
    "path"       : [],
},

{
    "#url"     : "https://aryion.com/g4/tags.php?tag=star+wars&p=28",
    "#category": ("", "aryion", "tag"),
    "#class"   : aryion.AryionTagExtractor,
    "#count"   : ">= 5",
},

{
    "#url"     : "https://aryion.com/g4/view/510079",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#sha1_url": "f233286fa5558c07ae500f7f2d5cb0799881450e",

    "artist"     : "jameshoward",
    "user"       : "jameshoward",
    "filename"   : "jameshoward-510079-subscribestar_150",
    "extension"  : "jpg",
    "id"         : 510079,
    "width"      : 1665,
    "height"     : 1619,
    "size"       : 784239,
    "title"      : "I'm on subscribestar now too!",
    "description": r"re:Doesn't hurt to have a backup, right\?",
    "tags"       : [
        "Non-Vore",
        "subscribestar",
    ],
    "date"       : "dt:2019-02-16 19:30:34",
    "path"       : [],
    "views"      : int,
    "favorites"  : int,
    "comments"   : int,
    "_http_lastmodified": "Sat, 16 Feb 2019 19:30:34 GMT",
},

{
    "#url"     : "https://aryion.com/g4/view/588928",
    "#comment" : "x-folder (#694)",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#pattern" : aryion.AryionPostExtractor.pattern,
    "#count"   : ">= 8",
},

{
    "#url"     : "https://aryion.com/g4/view/537379",
    "#comment" : "x-comic-folder (#945)",
    "#category": ("", "aryion", "post"),
    "#class"   : aryion.AryionPostExtractor,
    "#pattern" : aryion.AryionPostExtractor.pattern,
    "#count"   : 2,
},

{
    "#url"     : "https://aryion.com/g4/search.php?q=forest1",
    "#class"   : aryion.AryionSearchExtractor,
    "#results" : (
        "https://aryion.com/g4/data.php?id=165068",
        "https://aryion.com/g4/data.php?id=165069",
        "https://aryion.com/g4/data.php?id=165070",
        "https://aryion.com/g4/data.php?id=165071",
        "https://aryion.com/g4/data.php?id=165064",
    ),

    "search"     : {
        "prefix": "",
        "q"     : "forest1",
    },
},

{
    "#url"     : "https://aryion.com/g4/search.php?q=&tags=water%2C+&type_search=&user=&from_date=04%2F01%2F2025&to_date=07%2F01%2F2025&sort=view_count&p=2",
    "#class"   : aryion.AryionSearchExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://aryion.com/g4/data.php?id=1134439",
        "https://aryion.com/g4/data.php?id=1124899",
        "https://aryion.com/g4/data.php?id=1133691",
    ),

    "search"     : {
        "from_date"  : "04/01/2025",
        "p"          : "2",
        "prefix"     : "t_",
        "q"          : "",
        "sort"       : "view_count",
        "tags"       : "water, ",
        "to_date"    : "07/01/2025",
        "type_search": "",
        "user"       : "",
    },
},

{
    "#url"     : "https://aryion.com/g4/messagepage.php",
    "#class"   : aryion.AryionWatchExtractor,
},

)
