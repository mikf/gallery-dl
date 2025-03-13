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
    "#sha1_metadata": "2cadd32796492baca25f5060dc95e9f4e24a0ff2",
    "#sha1_content" : "742c6d256c813b29f246e1d765bba949fc3ac453",
},

{
    "#url"     : "https://boards.4channel.org/tg/thread/15396072/",
    "#category": ("", "4chan", "thread"),
    "#class"   : _4chan._4chanThreadExtractor,
    "#sha1_url"     : "39082ad166161966d7ba8e37f2173a824eb540f0",
    "#sha1_metadata": "2cadd32796492baca25f5060dc95e9f4e24a0ff2",
},

{
    "#url"     : "https://boards.4channel.org/po/",
    "#category": ("", "4chan", "board"),
    "#class"   : _4chan._4chanBoardExtractor,
    "#pattern" : _4chan._4chanThreadExtractor.pattern,
    "#count"   : ">= 100",
},

)
