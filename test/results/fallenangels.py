# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import fallenangels


__tests__ = (
{
    "#url"     : "https://manga.fascans.com/manga/chronos-ruler/20/1",
    "#category": ("", "fallenangels", "chapter"),
    "#class"   : fallenangels.FallenangelsChapterExtractor,
    "#sha1_url"     : "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
    "#sha1_metadata": "2dfcc50020e32cd207be88e2a8fac0933e36bdfb",
},

{
    "#url"     : "http://truyen.fascans.com/manga/hungry-marie/8",
    "#category": ("", "fallenangels", "chapter"),
    "#class"   : fallenangels.FallenangelsChapterExtractor,
    "#sha1_url"     : "1f923d9cb337d5e7bbf4323719881794a951c6ae",
    "#sha1_metadata": "2bdb7334c0e3eceb9946ffd3132df679b4a94f6a",
},

{
    "#url"     : "http://manga.fascans.com/manga/rakudai-kishi-no-eiyuutan/19.5",
    "#category": ("", "fallenangels", "chapter"),
    "#class"   : fallenangels.FallenangelsChapterExtractor,
    "#sha1_url"     : "273f6863966c83ea79ad5846a2866e08067d3f0e",
    "#sha1_metadata": "d1065685bfe0054c4ff2a0f20acb089de4cec253",
},

{
    "#url"     : "https://manga.fascans.com/manga/chronos-ruler",
    "#category": ("", "fallenangels", "manga"),
    "#class"   : fallenangels.FallenangelsMangaExtractor,
    "#sha1_url"     : "eea07dd50f5bc4903aa09e2cc3e45c7241c9a9c2",
    "#sha1_metadata": "c414249525d4c74ad83498b3c59a813557e59d7e",
},

{
    "#url"     : "https://truyen.fascans.com/manga/rakudai-kishi-no-eiyuutan",
    "#category": ("", "fallenangels", "manga"),
    "#class"   : fallenangels.FallenangelsMangaExtractor,
    "#sha1_url"     : "51a731a6b82d5eb7a335fbae6b02d06aeb2ab07b",
    "#sha1_metadata": "2d2a2a5d9ea5925eb9a47bb13d848967f3af086c",
},

)
