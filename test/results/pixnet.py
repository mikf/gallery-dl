# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixnet


__tests__ = (
{
    "#url"     : "https://albertayu773.pixnet.net/album/photo/159443828",
    "#category": ("", "pixnet", "image"),
    "#class"   : pixnet.PixnetImageExtractor,
    "#sha1_url"     : "156564c422138914c9fa5b42191677b45c414af4",
    "#sha1_metadata": "19971bcd056dfef5593f4328a723a9602be0f087",
    "#sha1_content" : "0e097bdf49e76dd9b9d57a016b08b16fa6a33280",
},

{
    "#url"     : "https://albertayu773.pixnet.net/album/set/15078995",
    "#category": ("", "pixnet", "set"),
    "#class"   : pixnet.PixnetSetExtractor,
    "#sha1_url"     : "6535712801af47af51110542f4938a7cef44557f",
    "#sha1_metadata": "bf25d59e5b0959cb1f53e7fd2e2a25f2f67e5925",
},

{
    "#url"     : "https://anrine910070.pixnet.net/album/set/5917493",
    "#category": ("", "pixnet", "set"),
    "#class"   : pixnet.PixnetSetExtractor,
    "#sha1_url"     : "b3eb6431aea0bcf5003432a4a0f3a3232084fc13",
    "#sha1_metadata": "bf7004faa1cea18cf9bd856f0955a69be51b1ec6",
},

{
    "#url"     : "https://sky92100.pixnet.net/album/set/17492544",
    "#comment" : "password-protected",
    "#category": ("", "pixnet", "set"),
    "#class"   : pixnet.PixnetSetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://albertayu773.pixnet.net/album/folder/1405768",
    "#category": ("", "pixnet", "folder"),
    "#class"   : pixnet.PixnetFolderExtractor,
    "#pattern" : pixnet.PixnetSetExtractor.pattern,
    "#count"   : ">= 15",
},

{
    "#url"     : "https://albertayu773.pixnet.net/",
    "#category": ("", "pixnet", "user"),
    "#class"   : pixnet.PixnetUserExtractor,
},

{
    "#url"     : "https://albertayu773.pixnet.net/blog",
    "#category": ("", "pixnet", "user"),
    "#class"   : pixnet.PixnetUserExtractor,
},

{
    "#url"     : "https://albertayu773.pixnet.net/album",
    "#category": ("", "pixnet", "user"),
    "#class"   : pixnet.PixnetUserExtractor,
},

{
    "#url"     : "https://albertayu773.pixnet.net/album/list",
    "#category": ("", "pixnet", "user"),
    "#class"   : pixnet.PixnetUserExtractor,
    "#pattern" : pixnet.PixnetFolderExtractor.pattern,
    "#count"   : ">= 30",
},

{
    "#url"     : "https://anrine910070.pixnet.net/album/list",
    "#category": ("", "pixnet", "user"),
    "#class"   : pixnet.PixnetUserExtractor,
    "#pattern" : pixnet.PixnetSetExtractor.pattern,
    "#count"   : ">= 14",
},

)
