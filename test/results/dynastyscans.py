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
    "#sha1_url"     : "dce64e8c504118f1ab4135c00245ea12413896cb",
    "#sha1_metadata": "b67599703c27316a2fe4f11c3232130a1904e032",
},

{
    "#url"     : "http://dynasty-scans.com/chapters/new_game_the_spinoff_special_13",
    "#category": ("", "dynastyscans", "chapter"),
    "#class"   : dynastyscans.DynastyscansChapterExtractor,
    "#sha1_url"     : "dbe5bbb74da2edcfb1832895a484e2a40bc8b538",
    "#sha1_metadata": "6b674eb3a274999153f6be044973b195008ced2f",
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
    "#sha1_url"     : "22cf0fb64e12b29e79b0a3d26666086a48f9916a",
    "#sha1_metadata": "11cbc555a15528d25567977b8808e10369c4c3ee",
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
    "#sha1_url"     : "15e54bd94148a07ed037f387d046c27befa043b2",
    "#sha1_metadata": "0d8976c2d6fbc9ed6aa712642631b96e456dc37f",
},

)
