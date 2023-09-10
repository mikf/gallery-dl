# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import keenspot


__tests__ = (
{
    "#url"     : "http://marksmen.keenspot.com/",
    "#comment" : "link",
    "#category": ("", "keenspot", "comic"),
    "#class"   : keenspot.KeenspotComicExtractor,
    "#range"   : "1-3",
    "#sha1_url": "83bcf029103bf8bc865a1988afa4aaeb23709ba6",
},

{
    "#url"     : "http://barkercomic.keenspot.com/",
    "#comment" : "id",
    "#category": ("", "keenspot", "comic"),
    "#class"   : keenspot.KeenspotComicExtractor,
    "#range"   : "1-3",
    "#sha1_url": "c4080926db18d00bac641fdd708393b7d61379e6",
},

{
    "#url"     : "http://crowscare.keenspot.com/",
    "#comment" : "id v2",
    "#category": ("", "keenspot", "comic"),
    "#class"   : keenspot.KeenspotComicExtractor,
    "#range"   : "1-3",
    "#sha1_url": "a00e66a133dd39005777317da90cef921466fcaa",
},

{
    "#url"     : "http://supernovas.keenspot.com/",
    "#comment" : "ks",
    "#category": ("", "keenspot", "comic"),
    "#class"   : keenspot.KeenspotComicExtractor,
    "#range"   : "1-3",
    "#sha1_url": "de21b12887ef31ff82edccbc09d112e3885c3aab",
},

{
    "#url"     : "http://twokinds.keenspot.com/comic/1066/",
    "#category": ("", "keenspot", "comic"),
    "#class"   : keenspot.KeenspotComicExtractor,
    "#range"   : "1-3",
    "#sha1_url": "6a784e11370abfb343dcad9adbb7718f9b7be350",
},

)
