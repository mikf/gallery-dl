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
    "#results" : "https://static.wikia.nocookie.net/mushi-shi/images/f/f8/Yahagi.png/revision/latest?cb=20150128052255&format=original",

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
            "source": "mediawiki-metadata",
            "value": "2015-01-28T05:22:55Z",
        },
        "ObjectName": {
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
    "url"           : "https://static.wikia.nocookie.net/mushi-shi/images/f/f8/Yahagi.png/revision/latest?cb=20150128052255&format=original",
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
    "#url"     : "https://hildatheseries.fandom.com/wiki/Burku",
    "#comment" : "'.webp' file without 'format=original' (#5512)",
    "#category": ("wikimedia", "fandom-hildatheseries", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#options" : {"format": ""},
    "#range"   : "1",
    "#results" : "https://static.wikia.nocookie.net/hildatheseries/images/2/24/Burku.png/revision/latest?cb=20251010033752",
    "#sha1_content": "36dce0e511fa8f6e1f834b92150126804fde971f",
},

{
    "#url"     : "https://discogs.fandom.com/zh/wiki/File:CH-0430D2.jpg",
    "#comment" : "non-English language prefix (#6370)",
    "#category": ("wikimedia", "fandom-discogs", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#results" : "https://static.wikia.nocookie.net/discogs/images/a/ab/CH-0430D2.jpg/revision/latest?cb=20241007150151&path-prefix=zh&format=original",

    "lang": "zh",
},

{
    "#url"     : "https://projectsekai.fandom.com/wiki/Project_SEKAI_Wiki",
    "#category": ("wikimedia", "fandom-projectsekai", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://youtube.fandom.com/wiki/File:(500)_Montage_-_Reason_2_Die_Awakening",
    "#comment" : "file without extension",
    "#category": ("wikimedia", "fandom-youtube", "file"),
    "#class"   : wikimedia.WikimediaArticleExtractor,

    "extension": "",
    "filename" : "(500) Montage - Reason 2 Die Awakening",
    "page"     : "File:(500)_Montage_-_Reason_2_Die_Awakening",
    "sha1"     : "6819869792d85927d60cc0a0cdc9e33dbd446731",
    "size"     : 81905,
},

{
    "#url"     : "https://youtube.fandom.com",
    "#category": ("wikimedia", "fandom-youtube", "wiki"),
    "#class"   : wikimedia.WikimediaWikiExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

)
