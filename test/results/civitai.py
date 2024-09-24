# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import civitai


__tests__ = (
{
    "#url"  : "https://civitai.com/models/703211/maid-classic",
    "#class": civitai.CivitaiModelExtractor,
    "#urls" : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/original=true/26962950.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/original=true/26962948.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2dd1dc69-45a6-4beb-b36b-2e2bc65e3cda/original=true/26962957.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/26887862.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/26887856.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/26887852.jpeg",
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
    "#url"  : "https://civitai.com/models/703211?modelVersionId=786644",
    "#class": civitai.CivitaiModelExtractor,
    "#urls" : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/26887862.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/26887856.jpeg",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/26887852.jpeg",
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

{
    "#url"  : "https://civitai.com/images/26962948",
    "#class": civitai.CivitaiImageExtractor,
    "#options"     : {"image-flags": "w"},
    "#urls"        : "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/w/69bf3279-df2c-4ec8-b795-479e9cd3db1b.jpeg",
    "#sha1_content": "a9a9d08f5fcdbc1e1eec7f203717f9df97b7a671",

    "browsingLevel": 1,
    "createdAt": "2024-08-31T01:11:47.021Z",
    "date"     : "dt:2024-08-31 01:11:47",
    "extension": "jpeg",
    "filename" : "69bf3279-df2c-4ec8-b795-479e9cd3db1b",
    "hash"     : "ULN0-w?b4nRjxGM{-;t7M_t7NGae~qRjMyt7",
    "height"   : 1536,
    "id"       : 26962948,
    "meta": {
        "Denoising strength": "0.4",
        "Model": "boleromix_XL_V1.3",
        "Model hash": "afaf521da2",
        "Size": "1152x1536",
        "TI hashes": {
            "negativeXL_D": "fff5d51ab655"
        },
        "Tiled Diffusion scale factor": "1.5",
        "Tiled Diffusion upscaler": "R-ESRGAN 4x+ Anime6B",
        "VAE": "sdxl_vae.safetensors",
        "Version": "v1.7.0",
        "cfgScale": 7,
        "hashes": {
            "lora:add-detail-xl": "9c783c8ce46c",
            "lora:classic maid_XL_V1.0": "e8f6e4297112",
            "model": "afaf521da2",
            "vae": "735e4c3a44",
        },
        "negativePrompt": "negativeXL_D,(worst quality,extra legs,extra arms,extra ears,bad fingers,extra fingers,bad anatomy, missing fingers, lowres,username, artist name, text,pubic hair,bar censor,censored,multipul angle,split view,realistic,3D:1)",
        "prompt": "masterpiece,ultra-detailed,best quality,8K,illustration,cute face,clean skin ,shiny hair,girl,ultra-detailed-eyes,simple background, <lora:add-detail-xl:1> <lora:classic maid_XL_V1.0:1> maid, maid apron, maid headdress, long sleeves,tray,tea,cup,skirt lift",
        "resources": [
            {
                "hash": "9c783c8ce46c",
                "name": "add-detail-xl",
                "type": "lora",
                "weight": 1,
            },
            {
                "hash": "e8f6e4297112",
                "name": "classic maid_XL_V1.0",
                "type": "lora",
            },
            {
                "hash": "afaf521da2",
                "name": "boleromix_XL_V1.3",
                "type": "model",
            },
        ],
        "sampler": "DPM++ 2M Karras",
        "seed": 3150861441,
        "steps": 20,
    },
    "nsfw": False,
    "nsfwLevel": "None",
    "postId": 6030721,
    "stats": {
        "commentCount": int,
        "cryCount"    : int,
        "dislikeCount": int,
        "heartCount"  : int,
        "laughCount"  : int,
        "likeCount"   : int,
    },
    "url": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/width=1152/69bf3279-df2c-4ec8-b795-479e9cd3db1b.jpeg",
    "username": "bolero537",
    "width": 1152,
},

)
