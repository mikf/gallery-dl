# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tumblrgallery


__tests__ = (
{
    "#url"     : "https://tumblrgallery.xyz/tumblrblog/gallery/103975.html",
    "#category": ("", "tumblrgallery", "tumblrblog"),
    "#class"   : tumblrgallery.TumblrgalleryTumblrblogExtractor,
},

{
    "#url"     : "https://tumblrgallery.xyz/post/405674.html",
    "#category": ("", "tumblrgallery", "post"),
    "#class"   : tumblrgallery.TumblrgalleryPostExtractor,
    "#pattern" : r"https://78\.media\.tumblr\.com/bec67072219c1f3bc04fd9711dec42ef/tumblr_p51qq1XCHS1txhgk3o1_1280\.jpg",
    "#count"   : 3,
},

{
    "#url"     : "https://tumblrgallery.xyz/s.php?q=everyday-life",
    "#category": ("", "tumblrgallery", "search"),
    "#class"   : tumblrgallery.TumblrgallerySearchExtractor,
    "#pattern" : r"https://\d+\.media\.tumblr\.com/.+",
    "#count"   : "< 1000",
},

)
