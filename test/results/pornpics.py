# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pornpics


__tests__ = (
{
    "#url"     : "https://www.pornpics.com/galleries/british-beauty-danielle-flashes-hot-breasts-ass-and-snatch-in-the-forest-62610699/",
    "#category": ("", "pornpics", "gallery"),
    "#class"   : pornpics.PornpicsGalleryExtractor,
    "#pattern" : r"https://cdni\.pornpics\.com/1280/7/160/62610699/62610699_\d+_[0-9a-f]{4}\.jpg",

    "categories": [
        "MILF",
        "Amateur",
        "Sexy",
        "Outdoor",
    ],
    "channel"   : "FTV MILFs",
    "count"     : 17,
    "gallery_id": 62610699,
    "models"    : ["Danielle"],
    "num"       : int,
    "slug"      : "british-beauty-danielle-flashes-hot-breasts-ass-and-snatch-in-the-forest",
    "tags"      : [
        "Amateur MILF",
        "Sexy MILF",
    ],
    "title"     : "British beauty Danielle flashes hot breasts, ass and snatch in the forest",
    "views"     : int,
},

{
    "#url"     : "https://pornpics.com/es/galleries/62610699",
    "#category": ("", "pornpics", "gallery"),
    "#class"   : pornpics.PornpicsGalleryExtractor,

    "slug": "british-beauty-danielle-flashes-hot-breasts-ass-and-snatch-in-the-forest",
},

{
    "#url"     : "https://www.pornpics.com/tags/summer-dress/",
    "#category": ("", "pornpics", "tag"),
    "#class"   : pornpics.PornpicsTagExtractor,
    "#pattern" : pornpics.PornpicsGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://pornpics.com/fr/tags/summer-dress",
    "#category": ("", "pornpics", "tag"),
    "#class"   : pornpics.PornpicsTagExtractor,
},

{
    "#url"     : "https://www.pornpics.com/?q=nature",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
    "#pattern" : pornpics.PornpicsGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://www.pornpics.com/channels/femjoy/",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
    "#pattern" : pornpics.PornpicsGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://www.pornpics.com/pornstars/emma-brown/",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
    "#pattern" : pornpics.PornpicsGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : 50,
},

{
    "#url"     : "https://pornpics.com/jp/?q=nature",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
},

{
    "#url"     : "https://pornpics.com/it/channels/femjoy",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
},

{
    "#url"     : "https://pornpics.com/pt/pornstars/emma-brown",
    "#category": ("", "pornpics", "search"),
    "#class"   : pornpics.PornpicsSearchExtractor,
},

)
