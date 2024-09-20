# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import civitai


__tests__ = (
{
    "#url"     : "https://civitai.com/models/703211/maid-classic",
    "#category": ("", "civitai", "model"),
    "#class"   : civitai.CivitaiModelExtractor,
    "#urls"    : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/w/26962950.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/w/26962948.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2dd1dc69-45a6-4beb-b36b-2e2bc65e3cda/w/26962957.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/w/26887862.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/w/26887856.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/w/26887852.jpeg",
    ],

    "model"  : {
        "allowCommercialUse": ["RentCivit"],
        "allowDerivatives": True,
        "allowDifferentLicense": True,
        "allowNoCredit": True,
        "cosmetic"   : None,
        "description": "<p>The strength of Lora is recommended to be around 1.0.</p>",
        "id"         : 703211,
        "minor"      : False,
        "name"       : "メイド　クラシック/maid classic",
        "nsfw"       : False,
        "nsfwLevel"  : 1,
        "poi"        : False,
        "stats"      : dict,
        "tags"       : ["clothing"],
        "type"       : "LORA"
    },
    "user"   : {
        "image"   : None,
        "username": "bolero537"
    },
    "file"   : dict,
    "version": dict,
    "num"    : range(1, 3),
},

{
    "#url"     : "https://civitai.com/models/703211?modelVersionId=786644",
    "#category": ("", "civitai", "model"),
    "#class"   : civitai.CivitaiModelExtractor,
    "#urls"    : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/w/26887862.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/w/26887856.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/w/26887852.jpeg",
    ],

    "version": {
        "availability": "Public",
        "baseModel"   : "Pony",
        "createdAt"   : "2024-08-30T15:28:47.661Z",
        "date"        : "dt:2024-08-30 15:28:47",
        "downloadUrl" : "https://civitai.com/api/download/models/786644",
        "files"       : list,
        "id"          : 786644,
        "images"      : list,
        "index"       : 1,
        "name"        : "v1.0 pony",
        "nsfwLevel"   : 1,
        "publishedAt" : "2024-08-30T15:39:17.674Z",
        "stats"       : dict,
        "status"      : "Published",
        "trainedWords": [
            "maid",
            "madi apron",
            "maid headdress",
            "long sleeves",
        ],
    },
    "user"   : {
        "image"   : None,
        "username": "bolero537"
    },
    "file"   : dict,
    "model"  : dict,
    "num"    : range(1, 3),
},

)
