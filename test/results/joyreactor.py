# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import reactor


__tests__ = (
{
    "#url"     : "http://joyreactor.cc/tag/Advent+Cirno",
    "#category": ("reactor", "joyreactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
    "#count"   : ">= 15",
},

{
    "#url"     : "http://joyreactor.com/tag/Cirno",
    "#category": ("reactor", "joyreactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
    "#sha1_url": "aa59090590b26f4654881301fe8fe748a51625a8",
},

{
    "#url"     : "http://joyreactor.com/tag/Dark+Souls+2/best",
    "#comment" : "'best' rating (#3073)",
    "#category": ("reactor", "joyreactor", "tag"),
    "#class"   : reactor.ReactorTagExtractor,
    "#count"   : 4,
},

{
    "#url"     : "http://joyreactor.cc/search/Nature",
    "#category": ("reactor", "joyreactor", "search"),
    "#class"   : reactor.ReactorSearchExtractor,
    "#range"   : "1-25",
    "#count"   : ">= 20",
},

{
    "#url"     : "http://joyreactor.com/search?q=Nature",
    "#category": ("reactor", "joyreactor", "search"),
    "#class"   : reactor.ReactorSearchExtractor,
    "#range"   : "1-25",
    "#count"   : ">= 20",
},

{
    "#url"     : "http://joyreactor.cc/user/hemantic",
    "#category": ("reactor", "joyreactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
},

{
    "#url"     : "http://joyreactor.com/user/Tacoman123",
    "#category": ("reactor", "joyreactor", "user"),
    "#class"   : reactor.ReactorUserExtractor,
    "#sha1_url": "60ce9a3e3db791a0899f7fb7643b5b87d09ae3b5",
},

{
    "#url"     : "http://joyreactor.com/post/3721876",
    "#comment" : "single image",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#pattern"      : r"http://img\d\.joyreactor\.com/pics/post/full/cartoon-painting-monster-lake-4841316.jpeg",
    "#count"        : 1,
    "#sha1_metadata": "2207a7dfed55def2042b6c2554894c8d7fda386e",
},

{
    "#url"     : "http://joyreactor.com/post/3713804",
    "#comment" : "4 images",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#pattern"      : r"http://img\d\.joyreactor\.com/pics/post/full/movie-tv-godzilla-monsters-\d+\.jpeg",
    "#count"        : 4,
    "#sha1_metadata": "d7da9ba7809004c809eedcf6f1c06ad0fbb3df21",
},

{
    "#url"     : "http://joyreactor.com/post/3726210",
    "#comment" : "gif / video",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url"     : "60f3b9a0a3918b269bea9b4f8f1a5ab3c2c550f8",
    "#sha1_metadata": "8949d9d5fc469dab264752432efbaa499561664a",
},

{
    "#url"     : "http://joyreactor.com/post/3668724",
    "#comment" : "youtube embed",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url"     : "bf1666eddcff10c9b58f6be63fa94e4e13074214",
    "#sha1_metadata": "e18b1ffbd79d76f9a0e90b6d474cc2499e343f0b",
},

{
    "#url"     : "http://joyreactor.cc/post/1299",
    "#comment" : "'malformed' JSON",
    "#category": ("reactor", "joyreactor", "post"),
    "#class"   : reactor.ReactorPostExtractor,
    "#sha1_url": "ab02c6eb7b4035ad961b29ee0770ee41be2fcc39",
},

)
