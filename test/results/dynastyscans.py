# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import dynastyscans


__tests__ = (
{
    "#url"     : "http://dynasty-scans.com/chapters/hitoribocchi_no_oo_seikatsu_ch33",
    "#category": ("", "dynastyscans", "chapter"),
    "#class"   : dynastyscans.DynastyscansChapterExtractor,
    "#sha1_url"     : "3cafa527fecec27a66f35e038c0c53e35d5e4317",
    "#sha1_metadata": "7b134f2093813d45774cc68a3cd199ffce3e6fd3",
},

{
    "#url"     : "http://dynasty-scans.com/chapters/new_game_the_spinoff_special_13",
    "#category": ("", "dynastyscans", "chapter"),
    "#class"   : dynastyscans.DynastyscansChapterExtractor,
    "#sha1_url"     : "047fa6d58f90272883157a80fbf1e6f03ea5bbab",
    "#sha1_metadata": "62dc42e9025c79bdd3e26e026a690f4c28548fd4",
},

{
    "#url"     : "https://dynasty-scans.com/series/hitoribocchi_no_oo_seikatsu",
    "#category": ("", "dynastyscans", "manga"),
    "#class"   : dynastyscans.DynastyscansMangaExtractor,
    "#pattern" : dynastyscans.DynastyscansChapterExtractor.pattern,
    "#count"   : ">= 100",
},

{
    "#url"     : "https://dynasty-scans.com/images?with[]=4930&with[]=5211",
    "#category": ("", "dynastyscans", "search"),
    "#class"   : dynastyscans.DynastyscansSearchExtractor,
    "#sha1_url"     : "d2422163db7b1db94bf343f8cd50ba9cc08ae6b5",
    "#sha1_metadata": "65f9948e7f29a1db2b3e6abb697f7476d2196708",
},

{
    "#url"     : "https://dynasty-scans.com/images",
    "#category": ("", "dynastyscans", "search"),
    "#class"   : dynastyscans.DynastyscansSearchExtractor,
    "#range"   : "1",
    "#count"   : 1,
},

{
    "#url"     : "https://dynasty-scans.com/images/1245",
    "#category": ("", "dynastyscans", "image"),
    "#class"   : dynastyscans.DynastyscansImageExtractor,
    "#sha1_url"     : "877054defac8ea2bbaeb632db176037668c73eea",
    "#sha1_metadata": "9f6fd139c372203dcf7237e662a80963ab070cb0",
},

)
