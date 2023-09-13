# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import smugmug


__tests__ = (
{
    "#url"     : "smugmug:album:cr4C7f",
    "#category": ("", "smugmug", "album"),
    "#class"   : smugmug.SmugmugAlbumExtractor,
    "#sha1_url": "2c2e576e47d4e9ce60b44871f08a8c66b5ebaceb",
},

{
    "#url"     : "smugmug:album:Fb7hMs",
    "#comment" : "empty",
    "#category": ("", "smugmug", "album"),
    "#class"   : smugmug.SmugmugAlbumExtractor,
    "#count"   : 0,
},

{
    "#url"     : "smugmug:album:6VRT8G",
    "#comment" : "no 'User'",
    "#category": ("", "smugmug", "album"),
    "#class"   : smugmug.SmugmugAlbumExtractor,
    "#sha1_url": "c4a0f4c4bfd514b93cbdeb02b3345bf7ef6604df",
},

{
    "#url"     : "https://tdm.smugmug.com/Nature/Dove/i-kCsLJT6",
    "#category": ("", "smugmug", "image"),
    "#class"   : smugmug.SmugmugImageExtractor,
    "#sha1_url"     : "e6408fd2c64e721fd146130dceb56a971ceb4259",
    "#sha1_metadata": "b31a63d07c9c26eb0f79f52d60d171a98938f99b",
    "#sha1_content" : "ecbd9d7b4f75a637abc8d35319be9ec065a44eb0",
},

{
    "#url"     : "https://tstravels.smugmug.com/Dailies/Daily-Dose-2015/i-39JFNzB",
    "#comment" : "video",
    "#category": ("", "smugmug", "image"),
    "#class"   : smugmug.SmugmugImageExtractor,
    "#sha1_url"     : "04d0ab1ff829ca7d78f5acb5548953df08e9a5ee",
    "#sha1_metadata": "2b545184592c282b365fcbb7df6ca7952b8a3173",
},

{
    "#url"     : "https://tdm.smugmug.com/Nature/Dove",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
    "#pattern" : "smugmug:album:cr4C7f$",
},

{
    "#url"     : "https://tdm.smugmug.com/",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
    "#pattern" : smugmug.SmugmugAlbumExtractor.pattern,
    "#sha1_url": "1640028712875b90974e5aecd91b60e6de6138c7",
},

{
    "#url"     : "https://www.smugmug.com/gallery/n-GLCjnD/",
    "#comment" : "gallery node without owner",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
    "#pattern" : "smugmug:album:6VRT8G$",
},

{
    "#url"     : "smugmug:www.sitkapics.com/TREES-and-TRAILS/",
    "#comment" : "custom domain",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
    "#pattern" : "smugmug:album:ct8Nds$",
},

{
    "#url"     : "smugmug:www.sitkapics.com/",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
    "#pattern" : r"smugmug:album:\w{6}$",
    "#count"   : ">= 14",
},

{
    "#url"     : "smugmug:https://www.sitkapics.com/",
    "#category": ("", "smugmug", "path"),
    "#class"   : smugmug.SmugmugPathExtractor,
},

)
