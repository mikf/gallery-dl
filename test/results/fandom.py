# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.fandom.com/wiki/Title",
    "#comment" : "for scripts/supportedsites.py",
    "#category": ("wikimedia", "fandom-www", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://mushishi.fandom.com/wiki/Yahagi",
    "#category": ("wikimedia", "fandom-mushishi", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#urls"    : "https://static.wikia.nocookie.net/mushi-shi/images/f/f8/Yahagi.png/revision/latest?cb=20150128052255",

    "bitdepth"      : 8,
    "canonicaltitle": "File:Yahagi.png",
    "comment"       : "",
    "commonmetadata": {
        "ResolutionUnit": 3,
        "XResolution"   : "3779/100",
        "YResolution"   : "3779/100",
    },
    "date"          : "dt:2015-01-28 05:22:55",
    "descriptionshorturl": "https://mushishi.fandom.com/index.php?curid=2595",
    "descriptionurl": "https://mushishi.fandom.com/wiki/File:Yahagi.png",
    "extension"     : "png",
    "extmetadata"   : {
        "DateTime": {
            "hidden": "",
            "source": "mediawiki-metadata",
            "value": "2015-01-28T05:22:55Z",
        },
        "ObjectName": {
            "hidden": "",
            "source": "mediawiki-metadata",
            "value": "Yahagi",
        },
    },
    "filename"      : "Yahagi",
    "height"        : 410,
    "metadata"      : {
        "bitDepth"  : 8,
        "colorType" : "truecolour",
        "duration"  : 0,
        "frameCount": 0,
        "loopCount" : 1,
        "metadata"  : [
            {
                "name" : "XResolution",
                "value": "3779/100",
            },
            {
                "name" : "YResolution",
                "value": "3779/100",
            },
            {
                "name" : "ResolutionUnit",
                "value": 3,
            },
            {
                "name" : "_MW_PNG_VERSION",
                "value": 1,
            },
        ],
    },
    "mime"          : "image/png",
    "page"          : "Yahagi",
    "sha1"          : "e3078a97976215323dbabb0c86b7acc55b512d16",
    "size"          : 429912,
    "timestamp"     : "2015-01-28T05:22:55Z",
    "url"           : "https://static.wikia.nocookie.net/mushi-shi/images/f/f8/Yahagi.png/revision/latest?cb=20150128052255",
    "user"          : "ITHYRIAL",
    "userid"        : 4637089,
    "width"         : 728,
},

{
    "#url"     : "https://hearthstone.fandom.com/wiki/Flame_Juggler",
    "#comment" : "empty 'metadata'",
    "#category": ("wikimedia", "fandom-hearthstone", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,

    "metadata" : {},
},

{
    "#url"     : "https://projectsekai.fandom.com/wiki/Project_SEKAI_Wiki",
    "#category": ("wikimedia", "fandom-projectsekai", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
