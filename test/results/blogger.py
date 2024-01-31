# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import blogger


__tests__ = (
{
    "#url"     : "blogger:http://www.julianbunker.com/2010/12/moon-rise.html",
    "#category": ("blogger", "www.julianbunker.com", "post"),
    "#class"   : blogger.BloggerPostExtractor,
},

{
    "#url"     : "blogger:https://www.kefblog.com.ng/",
    "#category": ("blogger", "www.kefblog.com.ng", "blog"),
    "#class"   : blogger.BloggerBlogExtractor,
    "#range"   : "1-25",
    "#count"   : 25,
},

{
    "#url"     : "blogger:http://www.julianbunker.com/search?q=400mm",
    "#category": ("blogger", "www.julianbunker.com", "search"),
    "#class"   : blogger.BloggerSearchExtractor,
},

{
    "#url"     : "blogger:http://www.julianbunker.com/search/label/D%26D",
    "#category": ("blogger", "www.julianbunker.com", "label"),
    "#class"   : blogger.BloggerLabelExtractor,
},

)
