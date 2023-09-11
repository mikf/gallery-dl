# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import generic


__tests__ = (
{
    "#url"     : "generic:https://www.nongnu.org/lzip/",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
    "#count"       : 1,
    "#sha1_content": "40be5c77773d3e91db6e1c5df720ee30afb62368",

    "description": "Lossless data compressor",
    "imageurl"   : "https://www.nongnu.org/lzip/lzip.png",
    "keywords"   : "lzip, clzip, plzip, lzlib, LZMA, bzip2, gzip, data compression, GNU, free software",
    "pageurl"    : "https://www.nongnu.org/lzip/",
},

{
    "#url"     : "generic:https://räksmörgås.josefsson.org/",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
    "#pattern" : "^https://räksmörgås.josefsson.org/",
    "#count"   : 2,
},

{
    "#url"     : "generic:https://en.wikipedia.org/Main_Page",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

{
    "#url"     : "generic:https://example.org/path/to/file?que=1?&ry=2/#fragment",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

{
    "#url"     : "generic:https://example.org/%27%3C%23/%23%3E%27.htm?key=%3C%26%3E",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

{
    "#url"     : "generic:https://en.wikipedia.org/Main_Page",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

{
    "#url"     : "generic:https://example.org/path/to/file?que=1?&ry=2/#fragment",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

{
    "#url"     : "generic:https://example.org/%27%3C%23/%23%3E%27.htm?key=%3C%26%3E",
    "#category": ("", "generic", ""),
    "#class"   : generic.GenericExtractor,
},

)
