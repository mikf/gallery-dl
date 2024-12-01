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
    "#class"   : pinterest.PinterestPinExtractor,
    "#pattern" : r"https://v\d*\.pinimg\.com/videos/mc/hls/d7/22/ff/d722ff00ab2352981b89974b37909de8.m3u8",
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://jp.pinterest.com/pin/858146904010573850/",
    "#comment" : "story pin with images",
    "#class"   : pinterest.PinterestPinExtractor,
    "#urls"    : (
        "https://i.pinimg.com/originals/0f/b0/8c/0fb08c519067dd263a1fcfecea775450.jpg",
        "https://i.pinimg.com/originals/2f/27/f3/2f27f3eb781b107ce58bf588c12a12b7.jpg",
        "https://i.pinimg.com/originals/55/fd/df/55fddf8d26aa0d96071af52ac6a0c25f.jpg",
    ),
},

{
    "#url"     : "https://www.pinterest.com/pin/63824519713049795/",
    "#comment" : "story pin with video (#6188)",
    "#class"   : pinterest.PinterestPinExtractor,
    "#urls"    : "ytdl:https://v1.pinimg.com/videos/iht/hls/7a/b0/cc/7ab0cc56dcbfc1508b8d650af7b0a593.m3u8",

    "extension"     : "mp4",
    "_ytdl_manifest": "hls",
},

{
    "#url"     : "https://www.pinterest.com/pin/606508274845593025/",
    "#comment" : "story pin with audio (#6188)",
    "#class"   : pinterest.PinterestPinExtractor,
    "#range"   : "2",
    "#urls"    : "https://v1.pinimg.com/audios/mp3/5d/37/74/5d37749bde03855c1292f8869c8d9387.mp3",

    "extension": "mp3",
},

{
    "#url"     : "https://jp.pinterest.com/pin/851532242064221228/",
    "#comment" : "story pin with text",
    "#class"   : pinterest.PinterestPinExtractor,
    "#range"   : "2",
    "#urls"    : "text:Everskies character+outfits i made",
},

{
    "#url"     : "https://www.pinterest.com/pin/858146903966145188/",
    "#category": ("", "pinterest", "pin"),
    "#class"   : pinterest.PinterestPinExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.pinterest.com/g1952849/test-/",
    "#class"   : pinterest.PinterestBoardExtractor,
    "#urls"    : "https://i.pinimg.com/originals/d4/f4/7f/d4f47fa2fce4c4c28475af5d94972904.jpg",
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
    "#url"     : "https://www.pinterest.jp/gdldev/bname/",
    "#comment" : "board & section with /?# in name (#5104)",
    "#category": ("", "pinterest", "board"),
    "#class"   : pinterest.PinterestBoardExtractor,
    "#options" : {"sections": True},
    "#urls"    : "https://www.pinterest.jp/gdldev/bname/id:5345901183739414095",
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
    "#count"   : 9,
},

{
    "#url"     : "https://www.pinterest.de/digitalmomblog/_created/",
    "#category": ("", "pinterest", "created"),
    "#class"   : pinterest.PinterestCreatedExtractor,
    "#pattern" : r"ytdl:|https://i\.pinimg\.com/originals/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.(jpg|png|webp)",
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
