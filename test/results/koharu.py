# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import koharu


__tests__ = (
{
    "#url"     : "https://niyaniya.moe/g/14216/6c67076fdd45",
    "#category": ("", "koharu", "gallery"),
    "#class"   : koharu.KoharuGalleryExtractor,
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
    "#category": ("", "koharu", "gallery"),
    "#class"   : koharu.KoharuGalleryExtractor,
    "#options" : {"cbz": False, "format": "780"},
    "#pattern" : r"https://koharusexo.xyz/data/59905/2df9110af7f1/a7cbeca3fb9c83aa87582a8a74cc8f8ce1b9e9b434dc1af293628871642f42df/[0-9a-f]+/.+",
    "#count"   : 22,
},

{
    "#url"     : "https://niyaniya.moe/g/14216/6c67076fdd45",
    "#category": ("", "koharu", "gallery"),
    "#class"   : koharu.KoharuGalleryExtractor,
    "#options" : {"cbz": False, "format": "780"},
    "#range"   : "1",
    "#sha1_content": "08954e0ae18a900ee7ca144d1661c664468c2525",
},

{
    "#url"  : "https://koharu.to/g/14216/6c67076fdd45",
    "#class": koharu.KoharuGalleryExtractor,
},
{
    "#url"  : "https://anchira.to/g/14216/6c67076fdd45",
    "#class": koharu.KoharuGalleryExtractor,
},
{
    "#url"  : "https://seia.to/g/14216/6c67076fdd45",
    "#class": koharu.KoharuGalleryExtractor,
},
{
    "#url"  : "https://shupogaki.moe/g/14216/6c67076fdd45",
    "#class": koharu.KoharuGalleryExtractor,
},
{
    "#url"  : "https://hoshino.one/g/14216/6c67076fdd45",
    "#class": koharu.KoharuGalleryExtractor,
},

{
    "#url"     : "https://niyaniya.moe/reader/14216/6c67076fdd45",
    "#category": ("", "koharu", "gallery"),
    "#class"   : koharu.KoharuGalleryExtractor,
},

{
    "#url"     : "https://niyaniya.moe/?s=tag:^beach$",
    "#category": ("", "koharu", "search"),
    "#class"   : koharu.KoharuSearchExtractor,
    "#pattern" : koharu.KoharuGalleryExtractor.pattern,
    "#count"   : ">= 50",
},

{
    "#url"     : "https://niyaniya.moe/favorites",
    "#category": ("", "koharu", "favorite"),
    "#class"   : koharu.KoharuFavoriteExtractor,
    "#pattern" : koharu.KoharuGalleryExtractor.pattern,
    "#auth"    : True,
    "#urls"    : [
        "https://niyaniya.moe/g/14216/6c67076fdd45",
    ],
},

{
    "#url"     : "https://niyaniya.moe/favorites?cat=6&sort=4",
    "#category": ("", "koharu", "favorite"),
    "#class"   : koharu.KoharuFavoriteExtractor,
    "#pattern" : koharu.KoharuGalleryExtractor.pattern,
    "#auth"    : True,
    "#urls"    : [
        "https://niyaniya.moe/g/14216/6c67076fdd45",
    ],
},

)
