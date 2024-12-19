# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.girlswithmuscle")
_gwm = getattr(gallery_dl.extractor, "girlswithmuscle")


__tests__ = (
{
    "#url"           : "https://www.girlswithmuscle.com/2136096/",
    "#category"      : ("", "girlswithmuscle", "post"),
    "#class"         : _gwm.GirlswithmusclePostExtractor,

    'id'             : '2136096',
    'model'          : str,
    'tags'           : list,
    'posted_dt'      : '2023-12-12 16:04:03.438979+00:00',
    'source_filename': 'IMG_8714.png',
    'uploader'       : 'toni1991',
    'score'          : int,
    'extension'      : 'png',
    "type"           : 'picture',
    # These are not available, unless you're logged in
    'is_favorite'    : None,
    'comments'       : list,
},

{
    "#url"           : "https://www.girlswithmuscle.com/1841638/",
    "#category"      : ("", "girlswithmuscle", "post"),
    "#class"         : _gwm.GirlswithmusclePostExtractor,

    'id'             : '1841638',
    'model'          : str,
    'tags'           : list,
    'posted_dt'      : '2022-08-16 17:20:16.006855+00:00',
    'source_filename': 'Snapinsta_299658611_1185267375661829_6167677658282784059_n.mp4',
    'uploader'       : 'BriedFrain',
    'score'          : int,
    'extension'      : 'mp4',
    "type"           : 'video',
},

{
    "#url"           : "https://www.girlswithmuscle.com/images/?name=Samantha%20Jerring",
    "#category"      : ("", "girlswithmuscle", "gallery"),
    "#class"         : _gwm.GirlswithmuscleGalleryExtractor,

    "#count"         : range(300, 3000),
    "gallery_name"   : str
},

)
