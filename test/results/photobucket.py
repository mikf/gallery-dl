# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import photobucket


__tests__ = (
{
    "#url"     : "https://s369.photobucket.com/user/CrpyLrkr/library",
    "#category": ("", "photobucket", "album"),
    "#class"   : photobucket.PhotobucketAlbumExtractor,
    "#pattern" : r"https?://[oi]+\d+.photobucket.com/albums/oo139/",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://s271.photobucket.com/user/lakerfanryan/library/",
    "#comment" : "subalbums of main 'directory'",
    "#category": ("", "photobucket", "album"),
    "#class"   : photobucket.PhotobucketAlbumExtractor,
    "#options" : {"image-filter": "False"},
    "#pattern" : photobucket.PhotobucketAlbumExtractor.pattern,
    "#count"   : 1,
},

{
    "#url"     : "https://s271.photobucket.com/user/lakerfanryan/library/Basketball",
    "#comment" : "subalbums of subalbum without images",
    "#category": ("", "photobucket", "album"),
    "#class"   : photobucket.PhotobucketAlbumExtractor,
    "#pattern" : photobucket.PhotobucketAlbumExtractor.pattern,
    "#count"   : ">= 9",
},

{
    "#url"     : "https://s1277.photobucket.com/user/sinisterkat44/library/",
    "#comment" : "private (missing JSON data)",
    "#category": ("", "photobucket", "album"),
    "#class"   : photobucket.PhotobucketAlbumExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://s1110.photobucket.com/user/chndrmhn100/library/Chandu%20is%20the%20King?sort=3&page=1",
    "#category": ("", "photobucket", "album"),
    "#class"   : photobucket.PhotobucketAlbumExtractor,
},

{
    "#url"     : "https://s271.photobucket.com/user/lakerfanryan/media/Untitled-3-1.jpg.html",
    "#category": ("", "photobucket", "image"),
    "#class"   : photobucket.PhotobucketImageExtractor,
    "#sha1_url"     : "3b647deeaffc184cc48c89945f67574559c9051f",
    "#sha1_metadata": "69732741b2b351db7ecaa77ace2fdb39f08ca5a3",
},

{
    "#url"     : "https://s271.photobucket.com/user/lakerfanryan/media/IsotopeswBros.jpg.html?sort=3&o=2",
    "#category": ("", "photobucket", "image"),
    "#class"   : photobucket.PhotobucketImageExtractor,
    "#sha1_url"     : "12c1890c09c9cdb8a88fba7eec13f324796a8d7b",
    "#sha1_metadata": "61200a223df6c06f45ac3d30c88b3f5b048ce9a8",
},

)
