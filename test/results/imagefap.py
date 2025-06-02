# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import imagefap
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.imagefap.com/gallery/7102714",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
    "#exception": exception.HttpError,
},

{
    "#url"     : "https://www.imagefap.com/gallery/7876223",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
    "#pattern" : r"https://cdn[ch]?\.imagefap\.com/images/full/\d+/\d+/\d+\.jpg",
    "#count"   : 44,

    "categories" : [
        "Asses",
        "Softcore",
        "Pornstars",
    ],
    "count"      : 44,
    "description": "",
    "gallery_id" : 7876223,
    "image_id"   : int,
    "num"        : int,
    "tags"       : [
        "big ass",
        "panties",
        "horny",
        "pussy",
        "exposed",
        "outdoor",
    ],
    "title"      : "Kelsi Monroe in lingerie",
    "uploader"   : "BdRachel",
},

{
    "#url"     : "https://www.imagefap.com/gallery/6706356",
    "#comment" : "description (#3905)",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
    "#range"   : "1",

    "categories" : [
        "Lesbian",
        "Fetish",
        "Animated GIFS",
    ],
    "count"      : 75,
    "description": "A mixed collection of pics and gifs depicting lesbian femdom.\n\nAll images originally found on various Tumblr blogs and through the internet.\n\nObviously I don't own any of the images so if you do and you would like them removed please just let me know and I shall remove them straight away.",
    "gallery_id" : 6706356,
    "tags"       : [
        "lesbian",
        "femdom",
        "lesbian femdom",
        "lezdom",
        "dominant women",
        "submissive women",
    ],
    "title"      : "Lezdom, Lesbian Femdom, Lesbian Domination - 3",
    "uploader"   : "pussysimon",
},

{
    "#url"     : "https://www.imagefap.com/pictures/7102714",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
},

{
    "#url"     : "https://www.imagefap.com/gallery.php?gid=7102714",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
},

{
    "#url"     : "https://beta.imagefap.com/gallery.php?gid=7102714",
    "#category": ("", "imagefap", "gallery"),
    "#class"   : imagefap.ImagefapGalleryExtractor,
},

{
    "#url"     : "https://www.imagefap.com/photo/1962981893",
    "#category": ("", "imagefap", "image"),
    "#class"   : imagefap.ImagefapImageExtractor,
    "#pattern" : r"https://cdn[ch]?\.imagefap\.com/images/full/65/196/1962981893\.jpg",

    "date"      : "21/08/2014",
    "gallery_id": 7876223,
    "height"    : 1600,
    "image_id"  : 1962981893,
    "title"     : "Kelsi Monroe in lingerie",
    "uploader"  : "BdRachel",
    "width"     : 1066,
},

{
    "#url"     : "https://beta.imagefap.com/photo/1962981893",
    "#category": ("", "imagefap", "image"),
    "#class"   : imagefap.ImagefapImageExtractor,
},

{
    "#url"     : "https://www.imagefap.com/organizer/409758",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#pattern" : r"https://www\.imagefap\.com/gallery/7876223",
    "#count"   : 1,
    "#sha1_url": "37822523e6e4a56feb9dea35653760c86b44ff89",
},

{
    "#url"     : "https://www.imagefap.com/organizer/613950/Grace-Stout",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#pattern" : imagefap.ImagefapGalleryExtractor.pattern,
    "#count"   : 31,

    "title": r"re:Grace Stout .+",
},

{
    "#url"     : "https://www.imagefap.com/usergallery.php?userid=1981976&folderid=409758",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#urls"    : "https://www.imagefap.com/gallery/7876223",

    "folder"    : "Softcore",
    "gallery_id": "7876223",
    "title"     : "Kelsi Monroe in lingerie",
},

{
    "#url"     : "https://www.imagefap.com/usergallery.php?user=BdRachel&folderid=409758",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#sha1_url": "37822523e6e4a56feb9dea35653760c86b44ff89",
},

{
    "#url"     : "https://www.imagefap.com/profile/BdRachel/galleries?folderid=-1",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#pattern" : imagefap.ImagefapGalleryExtractor.pattern,
    "#range"   : "1-40",

    "folder": "Uncategorized",
},

{
    "#url"     : "https://www.imagefap.com/usergallery.php?userid=1981976&folderid=-1",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#pattern" : imagefap.ImagefapGalleryExtractor.pattern,
    "#range"   : "1-40",
},

{
    "#url"     : "https://www.imagefap.com/usergallery.php?user=BdRachel&folderid=-1",
    "#category": ("", "imagefap", "folder"),
    "#class"   : imagefap.ImagefapFolderExtractor,
    "#pattern" : imagefap.ImagefapGalleryExtractor.pattern,
    "#range"   : "1-40",
},

{
    "#url"     : "https://www.imagefap.com/profile/BdRachel",
    "#category": ("", "imagefap", "user"),
    "#class"   : imagefap.ImagefapUserExtractor,
    "#pattern" : imagefap.ImagefapFolderExtractor.pattern,
    "#count"   : ">= 18",
},

{
    "#url"     : "https://www.imagefap.com/usergallery.php?userid=1862791",
    "#category": ("", "imagefap", "user"),
    "#class"   : imagefap.ImagefapUserExtractor,
    "#pattern" : r"https://www\.imagefap\.com/profile/LucyRae/galleries\?folderid=-1",
    "#count"   : 1,
},

{
    "#url"     : "https://www.imagefap.com/profile/BdRachel/galleries",
    "#category": ("", "imagefap", "user"),
    "#class"   : imagefap.ImagefapUserExtractor,
},

{
    "#url"     : "https://www.imagefap.com/profile.php?user=BdRachel",
    "#category": ("", "imagefap", "user"),
    "#class"   : imagefap.ImagefapUserExtractor,
},

{
    "#url"     : "https://beta.imagefap.com/profile.php?user=BdRachel",
    "#category": ("", "imagefap", "user"),
    "#class"   : imagefap.ImagefapUserExtractor,
},

)
