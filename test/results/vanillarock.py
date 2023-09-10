# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vanillarock


__tests__ = (
{
    "#url"     : "https://vanilla-rock.com/mizuhashi_parsee-5",
    "#category": ("", "vanillarock", "post"),
    "#class"   : vanillarock.VanillarockPostExtractor,
    "#sha1_url"     : "7fb9a4d18d9fa22d7295fee8d94ab5a7a52265dd",
    "#sha1_metadata": "b91df99b714e1958d9636748b1c81a07c3ef52c9",
},

{
    "#url"     : "https://vanilla-rock.com/tag/%e5%b0%84%e5%91%bd%e4%b8%b8%e6%96%87",
    "#category": ("", "vanillarock", "tag"),
    "#class"   : vanillarock.VanillarockTagExtractor,
    "#pattern" : vanillarock.VanillarockPostExtractor.pattern,
    "#count"   : ">= 12",
},

{
    "#url"     : "https://vanilla-rock.com/category/%e4%ba%8c%e6%ac%a1%e3%82%a8%e3%83%ad%e7%94%bb%e5%83%8f/%e8%90%8c%e3%81%88%e3%83%bb%e3%82%bd%e3%83%95%e3%83%88%e3%82%a8%e3%83%ad",
    "#category": ("", "vanillarock", "tag"),
    "#class"   : vanillarock.VanillarockTagExtractor,
    "#pattern" : vanillarock.VanillarockPostExtractor.pattern,
    "#count"   : ">= 5",
},

)
