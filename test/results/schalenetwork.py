# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import schalenetwork


__tests__ = (
{
    "#url"     : "https://niyaniya.moe/g/14216/6c67076fdd45",
    "#class"   : schalenetwork.SchalenetworkGalleryExtractor,
    "#options" : {"tags": True},
    "#pattern" : r"https://kisakisexo.xyz/download/59896/a4fbd1828229/f47639c6abaf1903dd69c36a3d961da84741a1831aa07a2906ce9c74156a5d75\?v=1721626410802&w=0",
    "#count"   : 1,

    "count"     : 22,
    "created_at": 1721626410802,
    "date"      : "dt:2024-07-22 05:33:30",
    "extension" : "cbz",
    "filename"  : "f47639c6abaf1903dd69c36a3d961da84741a1831aa07a2906ce9c74156a5d75",
    "id"        : 14216,
    "num"       : 1,
    "public_key": "6c67076fdd45",
    "tags": [
        "general:beach",
        "general:booty",
        "general:dark skin",
        "general:fingering",
        "general:handjob",
        "general:light hair",
        "general:nakadashi",
        "general:outdoors",
        "general:ponytail",
        "general:swimsuit",
        "general:x-ray",
        "artist:ouchi kaeru",
        "magazine:comic kairakuten 2024-08",
        "female:busty",
        "language:english",
        "language:translated",
        "other:uncensored",
        "other:vanilla",
    ],
    "tags_artist": [
        "ouchi kaeru",
    ],
    "tags_female": [
        "busty",
    ],
    "tags_general": [
        "beach",
        "booty",
        "dark skin",
        "fingering",
        "handjob",
        "light hair",
        "nakadashi",
        "outdoors",
        "ponytail",
        "swimsuit",
        "x-ray",
    ],
    "tags_language": [
        "english",
        "translated",
    ],
    "tags_magazine": [
        "comic kairakuten 2024-08",
    ],
    "tags_other": [
        "uncensored",
        "vanilla",
    ],
    "title"     : "[Ouchi Kaeru] Summer Business (Comic Kairakuten 2024-08)",
    "updated_at": 1721626410802,
},

{
    "#url"     : "https://niyaniya.moe/g/14216/6c67076fdd45",
    "#class"   : schalenetwork.SchalenetworkGalleryExtractor,
    "#options" : {"cbz": False, "format": "780"},
    "#pattern" : r"https://koharusexo.xyz/data/59905/2df9110af7f1/a7cbeca3fb9c83aa87582a8a74cc8f8ce1b9e9b434dc1af293628871642f42df/[0-9a-f]+/.+",
    "#count"   : 22,
},

{
    "#url"     : "https://niyaniya.moe/g/14216/6c67076fdd45",
    "#class"   : schalenetwork.SchalenetworkGalleryExtractor,
    "#options" : {"cbz": False, "format": "780"},
    "#range"   : "1",
    "#sha1_content": "08954e0ae18a900ee7ca144d1661c664468c2525",
},

{
    "#url"  : "https://koharu.to/g/14216/6c67076fdd45",
    "#class": schalenetwork.SchalenetworkGalleryExtractor,
},
{
    "#url"  : "https://anchira.to/g/14216/6c67076fdd45",
    "#class": schalenetwork.SchalenetworkGalleryExtractor,
},
{
    "#url"  : "https://seia.to/g/14216/6c67076fdd45",
    "#class": schalenetwork.SchalenetworkGalleryExtractor,
},
{
    "#url"  : "https://shupogaki.moe/g/14216/6c67076fdd45",
    "#class": schalenetwork.SchalenetworkGalleryExtractor,
},
{
    "#url"  : "https://hoshino.one/g/14216/6c67076fdd45",
    "#class": schalenetwork.SchalenetworkGalleryExtractor,
},

{
    "#url"     : "https://niyaniya.moe/reader/14216/6c67076fdd45",
    "#class"   : schalenetwork.SchalenetworkGalleryExtractor,
},

{
    "#url"     : "https://niyaniya.moe/?s=tag:^beach$",
    "#class"   : schalenetwork.SchalenetworkSearchExtractor,
    "#pattern" : schalenetwork.SchalenetworkGalleryExtractor.pattern,
    "#count"   : ">= 50",
},

{
    "#url"     : "https://niyaniya.moe/browse?s=beach",
    "#class"   : schalenetwork.SchalenetworkSearchExtractor,
},

{
    "#url"     : "https://niyaniya.moe/tag/tag:beach",
    "#class"   : schalenetwork.SchalenetworkSearchExtractor,
},

{
    "#url"     : "https://niyaniya.moe/tag/circle:tentou+mushi+no+sanba",
    "#class"   : schalenetwork.SchalenetworkSearchExtractor,
    "#results" : (
        "https://niyaniya.moe/g/26044/9b7ecf9bcf00",
        "https://niyaniya.moe/g/24342/c723a7fe9191",
        "https://niyaniya.moe/g/23787/7a51f4258481",
        "https://niyaniya.moe/g/23784/d81779e07505",
        "https://niyaniya.moe/g/23764/cb867963cfcb",
        "https://niyaniya.moe/g/23760/a667d4a7f447",
        "https://niyaniya.moe/g/23669/9ec3ff4c6737",
    ),
},

{
    "#url"     : "https://niyaniya.moe/favorites",
    "#class"   : schalenetwork.SchalenetworkFavoriteExtractor,
    "#pattern" : schalenetwork.SchalenetworkGalleryExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://niyaniya.moe/g/14216/6c67076fdd45",
    ),
},

{
    "#url"     : "https://niyaniya.moe/favorites?cat=6&sort=4",
    "#class"   : schalenetwork.SchalenetworkFavoriteExtractor,
    "#pattern" : schalenetwork.SchalenetworkGalleryExtractor.pattern,
    "#auth"    : True,
    "#results" : (
        "https://niyaniya.moe/g/14216/6c67076fdd45",
    ),
},

)
