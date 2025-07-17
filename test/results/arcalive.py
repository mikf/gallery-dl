# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import arcalive


__tests__ = (
{
    "#url"    : "https://arca.live/b/arknights/66031722?p=1",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#pattern": r"https://ac.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg\?type=orig&expires=\d+&key=\w+",
    "#count"  : 1,

    "isEditable": False,
    "isDeletable": False,
    "isReportable": False,
    "id": 66031722,
    "nickname": "Si리링",
    "title": "엑샤 스작함",
    "contentType": "html",
    "content": r"re:^<p>알게또 뽑으려했는데 못뽑아서 엑샤 스작함<br />엑샤에 보카디 3스나 와파린 2스 붙이는거 맞음.+/></p>$",
    "viewCount": range(8000, 20000),
    "ratingUp": 0,
    "ratingDown": 0,
    "ratingUpIp": 0,
    "ratingDownIp": 0,
    "createdAt": "2022-12-25T05:16:55.000Z",
    "updatedAt": "2022-12-25T05:16:55.000Z",
    "lastComment": "2022-12-25T05:22:12.000Z",
    "commentCount": range(2, 9),
    "publicId": None,
    "token": "44bb2dfd0bbc672e",
    "isUser": True,
    "gravatar": "//secure.gravatar.com/avatar/6c3fdbdeea149b29eea8d887c37fc119?d=retro&f=y",
    "preventDelete": False,
    "channelPermission": dict,
    "captcha": True,
    "isSensitive": False,
    "categoryDisplayName": None,
    "blockPreview": False,
    "isSpoilerAlert": False,
    "boardName": "명일방주 채널",
    "boardSlug": "arknights",
    "isBest": False,
    "vote": [],
    "date": "dt:2022-12-25 05:16:55",
    "post_url": "https://arca.live/b/arknights/66031722",
    "count": 1,
    "num": 1,
    "url": str,
    "width": 3200,
    "height": 1440,
    "filename": "e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5",
    "extension": "jpg",
},

{
    "#url"    : "https://arca.live/b/breaking/66031722",
    "#comment": "/b/breaking page URL",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#pattern": r"https://ac.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg\?type=orig",
},

{
    "#url"    : "https://arca.live/b/bluearchive/65031202",
    "#comment": "animated gif",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#pattern": (
        r"https://ac.namu.la/20221211sac/5ea7fbca5e49ec16beb099fc6fc991690d37552e599b1de8462533908346241e.png\?type=orig",
        r"https://ac.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif\?type=orig",
        r"https://ac.namu.la/20221211sac2/3e72f9e05ca97c0c3c0fe5f25632b06eb21ab9f211e9ea22816e16468ee241ca.png\?type=orig",
    ),
},

{
    "#url"    : "https://arca.live/b/arknights/122263340",
    "#comment": "animated webp",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#pattern": (
        r"https://ac.namu.la/20241126sac/b2175d9ef4504945d3d989526120dbb6aded501ddedfba8ecc44a64e7aae9059.gif\?type=orig",
        r"https://ac.namu.la/20241126sac/bc1f3cb388a3a2d099ab67bc09b28f0a93c2c4755152b3ef9190690a9f0a28fb.webp\?type=orig",
    ),
},

{
    "#url"    : "https://arca.live/b/bluearchive/117240135",
    "#comment": ".mp4 video",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#options": {"gifs": "check"},
    "#pattern": r"https://ac.namu.la/20240926sac/16f07778a97f91b935c8a3394ead01a223d96b2a619fdb25c4628ddba88b5fad.mp4\?type=orig",
},

{
    "#url"    : "https://arca.live/b/bluearchive/111191955",
    "#comment": "fake .mp4 GIF",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#options": {"gifs": True},
    "#pattern": r"https://ac.namu.la/20240714sac/c8fcadeb0b578e5121eb7a7e8fb05984cb87c68e7a6e0481a1c8869bf0ecfd2b.gif\?type=orig",

    "_fallback": "len:tuple:1",
},

{
    "#url"    : "https://arca.live/b/bluearchive/111191955",
    "#comment": "fake .mp4 GIF",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#options": {"gifs": False},
    "#pattern": r"https://ac.namu.la/20240714sac/c8fcadeb0b578e5121eb7a7e8fb05984cb87c68e7a6e0481a1c8869bf0ecfd2b.mp4\?type=orig",
},

{
    "#url"    : "https://arca.live/b/arknights/49406926",
    "#comment": "static emoticon",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#pattern": r"https://ac.namu.la/20220428sac2/41f472adcea674aff75f15f146e81c27032bc4d6c8073bd7c19325bd1c97d335.png\?type=orig",
},

{
    "#url"    : "https://arca.live/b/commission/63658702",
    "#comment": "animated emoticon",
    "#class"  : arcalive.ArcalivePostExtractor,
    "#options": {"emoticons": True},
    "#pattern": (
        r"https://ac.namu.la/20221123sac2/14925c5e22ab9f17f2923ae60a39b7af0794c43e478ecaba054ab6131e57e022.png\?type=orig",
        r"https://ac.namu.la/20221123sac2/50c385a4004bca44271a2f6133990f086cfefd29a7968514e9c14d6017d61265.png\?type=orig",
        r"https://ac.namu.la/20221005sac2/28ebe073fffbb2b88f710c2d380b0fe6dd99a856070c4a836db57634a5371366.gif\?type=orig",
    ),
},

{
    "#url"    : "https://arca.live/b/arknights",
    "#class"  : arcalive.ArcaliveBoardExtractor,
    "#pattern": arcalive.ArcalivePostExtractor.pattern,
    "#range"  : "1-100",
    "#count"  : 100,

    "category"    : {str, None},
    "categoryDisplayName": {str, None},
    "commentCount": int,
    "createdAt"   : str,
    "id"          : int,
    "isUser"      : bool,
    "?mark"       : str,
    "nickname"    : str,
    "publicId"    : {int, None},
    "ratingDown"  : int,
    "ratingUp"    : int,
    "thumbnailUrl": {str, None},
    "title"       : str,
    "viewCount"   : int,
},

{
    "#url"  : "https://arca.live/u/@Si%EB%A6%AC%EB%A7%81",
    "#class": arcalive.ArcaliveUserExtractor,
    "#range": "1-5",
    "#results": (
        "https://arca.live/b/vrchat/107257886",
        "https://arca.live/b/soulworkers/95371697",
        "https://arca.live/b/arcalivebreverse/90843346",
        "https://arca.live/b/arcalivebreverse/90841126",
        "https://arca.live/b/arcalivebreverse/90769916",
    ),

    "boardName"   : str,
    "boardSlug"   : {"vrchat", "soulworkers", "arcalivebreverse"},
    "category"    : {str, None},
    "categoryDisplayName": {str, None},
    "commentCount": int,
    "createdAt"   : str,
    "id"          : int,
    "isUser"      : True,
    "?mark"       : "image",
    "nickname"    : "Si리링",
    "publicId"    : {int, None},
    "ratingDown"  : int,
    "ratingUp"    : int,
    "thumbnailUrl": {str, None},
    "title"       : str,
    "viewCount"   : int,
},

)
