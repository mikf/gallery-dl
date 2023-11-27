# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.4chan")
_4chan = getattr(gallery_dl.extractor, "4chan")


__tests__ = (
{
    "#url"     : "https://boards.4chan.org/tg/thread/15396072/",
    "#category": ("", "4chan", "thread"),
    "#class"   : _4chan._4chanThreadExtractor,
    "#sha1_url"     : "39082ad166161966d7ba8e37f2173a824eb540f0",
    "#sha1_metadata": "7ae2f4049adf0d2f835eb91b6b26b7f4ec882e0a",
    "#sha1_content" : "551e432d52700ff3711f14752124e9af86ecbbdf",
},

{
    "#url"     : "https://boards.4channel.org/tg/thread/15396072/",
    "#category": ("", "4chan", "thread"),
    "#class"   : _4chan._4chanThreadExtractor,
    "#sha1_url"     : "39082ad166161966d7ba8e37f2173a824eb540f0",
    "#sha1_metadata": "7ae2f4049adf0d2f835eb91b6b26b7f4ec882e0a",
},

{
    "#url"     : "https://boards.4channel.org/po/",
    "#category": ("", "4chan", "board"),
    "#class"   : _4chan._4chanBoardExtractor,
    "#pattern" : _4chan._4chanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

)
