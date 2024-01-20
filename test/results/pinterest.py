# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pinterest
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.pinterest.com/pin/858146903966145189/",
    "#category": ("", "pinterest", "pin"),
    "#class"   : pinterest.PinterestPinExtractor,
    "#sha1_url"    : "afb3c26719e3a530bb0e871c480882a801a4e8a5",
    "#sha1_content": [
        "4c435a66f6bb82bb681db2ecc888f76cf6c5f9ca",
        "d3e24bc9f7af585e8c23b9136956bd45a4d9b947",
    ],
},

{
    "#url"     : "https://www.pinterest.com/pin/422564377542934214/",
    "#comment" : "video pin (#1189)",
    "#category": ("", "pinterest", "pin"),
    "#class"   : pinterest.PinterestPinExtractor,
    "#pattern" : r"https://v\d*\.pinimg\.com/videos/mc/hls/d7/22/ff/d722ff00ab2352981b89974b37909de8.m3u8",
},

{
    "#url"     : "https://www.pinterest.com/pin/858146903966145188/",
    "#category": ("", "pinterest", "pin"),
    "#class"   : pinterest.PinterestPinExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/test-/",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
    "#pattern" : r"https://i\.pinimg\.com/originals/",
    "#count"   : 2,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/stuff/",
    "#comment" : "board with sections (#835)",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
    "#options" : {"sections": True},
    "#count"   : 4,
},

{
    "#url"     : "https://www.pinterest.de/g1952849/secret/",
    "#comment" : "secret board (#1055)",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
    "#auth"    : True,
    "#count"   : 2,
},

{
    "#url"     : "https://www.pinterest.com/g1952848/test/",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
    "#exception": exception.GalleryDLException,
},

{
    "#url"     : "https://www.pinterest.co.uk/hextra7519/based-animals/",
    "#comment" : ".co.uk TLD (#914)",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/",
    "#category": ("", "pinterest", "user"),
    "#class"   : pinterest.PinterestUserExtractor,
    "#pattern" : pinterest.PinterestBoardExtractor.pattern,
    "#count"   : ">= 2",
},

{
    "#url"     : "https://www.pinterest.com/g1952849/_saved/",
    "#category": ("", "pinterest", "user"),
    "#class"   : pinterest.PinterestUserExtractor,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/pins/",
    "#category": ("", "pinterest", "allpins"),
    "#class"   : pinterest.PinterestAllpinsExtractor,
    "#pattern" : r"https://i\.pinimg\.com/originals/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w{3}",
    "#count"   : 7,
},

{
    "#url"     : "https://www.pinterest.de/digitalmomblog/_created/",
    "#category": ("", "pinterest", "created"),
    "#class"   : pinterest.PinterestCreatedExtractor,
    "#pattern" : r"https://i\.pinimg\.com/originals/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.(jpg|png)",
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/stuff/section",
    "#category": ("", "pinterest", "section"),
    "#class"   : pinterest.PinterestSectionExtractor,
    "#count"   : 2,
},

{
    "#url"     : "https://www.pinterest.com/search/pins/?q=nature",
    "#category": ("", "pinterest", "search"),
    "#class"   : pinterest.PinterestSearchExtractor,
    "#range"   : "1-50",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://www.pinterest.com/pin/858146903966145189/#related",
    "#category": ("", "pinterest", "related-pin"),
    "#class"   : pinterest.PinterestRelatedPinExtractor,
    "#range"   : "31-70",
    "#count"   : 40,
    "#archive" : False,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/test-/#related",
    "#category": ("", "pinterest", "related-board"),
    "#class"   : pinterest.PinterestRelatedBoardExtractor,
    "#range"   : "31-70",
    "#count"   : 40,
    "#archive" : False,
},

{
    "#url"     : "https://pin.it/Hvt8hgT",
    "#category": ("", "pinterest", "pinit"),
    "#class"   : pinterest.PinterestPinitExtractor,
    "#sha1_url": "8daad8558382c68f0868bdbd17d05205184632fa",
},

{
    "#url"     : "https://pin.it/Hvt8hgS",
    "#category": ("", "pinterest", "pinit"),
    "#class"   : pinterest.PinterestPinitExtractor,
    "#exception": exception.NotFoundError,
},

)
