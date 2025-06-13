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
    "#results": (
        "https://photos.smugmug.com/Nature/Dove/i-XvZFJFG/0/DMk7cm6qRBSFPvQgT9C4t4jtBJKF7JSK9jszgHZnr/O/Dual%20Suicide_20070721-DSC_4804.jpg",
        "https://photos.smugmug.com/Nature/Dove/i-2wVPqHf/0/DBXmTSTqVWzTLZxL3JPVK7hGT9zp8tzsFdhtWm68v/O/Morning%20Dove2_20070621-DSC_3222.jpg",
        "https://photos.smugmug.com/Nature/Dove/i-QHFnmb8/0/GKLvnm7zFQWX2G2VcJRprx8WZqTfFJkn8C5nRnCk/O/Speed%20Skater_03082008_POR7728.jpg",
        "https://photos.smugmug.com/Nature/Dove/i-MXQZKws/0/D6XCS9xnncDVtZ9NtVq66ZK9xjL4D2H9KSbpFMjfM/O/Airing%20it%20Out0_5142008_DSC_8166.jpg",
        "https://photos.smugmug.com/Nature/Dove/i-kCsLJT6/0/FfB6gSx8X6MS7Hvww7GK7tWsrfdtwCx79hCVzwSm/O/Fluff_20090521-_DSC1542.jpg",
        "https://photos.smugmug.com/Nature/Dove/i-T9Qv5Pm/0/CFT4MB9hg7rKwWmbFhGQTCnmxdpnGBKPDbHTPLSgV/O/D2F_D300_20090827-_TDM5650.jpg",
    ),
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
    "#sha1_url": "17837ff2c78a6e2335291666f43d620d82f2926a",

    "User": {
        "Name"         : "",
        "NickName"     : "",
        "QuickShare"   : False,
        "RefTag"       : "",
        "ResponseLevel": "Public",
        "Uri"          : "",
        "ViewPassHint" : "",
        "WebUri"       : "",
    },
},

{
    "#url"     : "https://tdm.smugmug.com/Nature/Dove/i-kCsLJT6",
    "#category": ("", "smugmug", "image"),
    "#class"   : smugmug.SmugmugImageExtractor,
    "#results"     : "https://photos.smugmug.com/Nature/Dove/i-kCsLJT6/0/FfB6gSx8X6MS7Hvww7GK7tWsrfdtwCx79hCVzwSm/O/Fluff_20090521-_DSC1542.jpg",
    "#sha1_content": "ecbd9d7b4f75a637abc8d35319be9ec065a44eb0",

    "Image": {
        "Altitude"   : 0,
        "CanBuy"     : True,
        "CanEdit"    : False,
        "CanShare"   : True,
        "Caption"    : "White Wing Dove",
        "Collectable": False,
        "Comments"   : True,
        "ComponentFileTypes": [],
        "Date"       : "2009-08-01T23:00:56+00:00",
        "DateTimeOriginal": "2009-05-22T00:05:36+00:00",
        "DateTimeUploaded": "2009-08-01T23:00:56+00:00",
        "EZProject"  : False,
        "FileName"   : "Fluff_20090521-_DSC1542.jpg",
        "Format"     : "JPG",
        "FormattedValues": {
            "Caption": {
                "html": "White Wing Dove",
                "text": "White Wing Dove",
            },
            "FileName": {
                "html": "Fluff_20090521-_DSC1542.jpg",
                "text": "Fluff_20090521-_DSC1542.jpg",
            },
        },
        "Height"     : 1008,
        "Hidden"     : False,
        "ImageKey"   : "kCsLJT6",
        "IsArchive"  : False,
        "IsVideo"    : False,
        "KeywordArray": [
            "Birds",
            "Dove",
            "White Wing Dove",
        ],
        "Keywords"   : "Birds; Dove; White Wing Dove",
        "LastUpdated": "2012-11-03T20:01:15+00:00",
        "Latitude"   : "0",
        "Longitude"  : "0",
        "OriginalHeight": 1008,
        "OriginalSize": 381297,
        "OriginalWidth": 1024,
        "PreferredDisplayFileExtension": "JPG",
        "Processing" : False,
        "Protected"  : True,
        "Serial"     : 0,
        "ShowKeywords": True,
        "Size"       : 381297,
        "Status"     : "Open",
        "SubStatus"  : "NFS",
        "ThumbnailUrl": "https://photos.smugmug.com/Nature/Dove/i-kCsLJT6/0/Df2nQXwHWSmmh4W2CjhJJdxDcZWbhkKTG86JXp9x2/Th/Fluff_20090521-_DSC1542-Th.jpg",
        "Title"      : "",
        "UploadKey"  : "608043804",
        "Uri"        : "/api/v2/image/kCsLJT6-0",
        "Url"        : "https://photos.smugmug.com/Nature/Dove/i-kCsLJT6/0/FfB6gSx8X6MS7Hvww7GK7tWsrfdtwCx79hCVzwSm/O/Fluff_20090521-_DSC1542.jpg",
        "Watermark"  : "No",
        "Watermarked": False,
        "Width"      : 1024,
    },
    "extension": "jpg",
    "filename": "Fluff_20090521-_DSC1542",
},

{
    "#url"     : "https://tstravels.smugmug.com/Dailies/Daily-Dose-2015/i-39JFNzB",
    "#comment" : "video",
    "#category": ("", "smugmug", "image"),
    "#class"   : smugmug.SmugmugImageExtractor,
    "#results"      : "https://photos.smugmug.com/Dailies/Daily-Dose-2015/i-39JFNzB/0/Q4Qg6kt4SqVcKsSLWM4PnhMhSTS2r5BkmBMd9Dx4/1920/657%20WS3-1920.mp4",
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
