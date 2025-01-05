# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import civitai
from gallery_dl import exception


__tests__ = (
{
    "#url"  : "https://civitai.com/models/703211/maid-classic",
    "#class": civitai.CivitaiModelExtractor,
    "#urls" : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/original=true/00013-4238863814.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/original=true/00014-3150861441.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2dd1dc69-45a6-4beb-b36b-2e2bc65e3cda/original=true/00015-2885514572.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/00004-822988489.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/00005-1059918744.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/00006-3467286319.png",
    ],

    "model"  : {
        "description": "<p>The strength of Lora is recommended to be around 1.0.</p>",
        "id"         : 703211,
        "minor"      : False,
        "name"       : "メイド　クラシック/maid classic",
        "nsfwLevel"  : 1,
        "type"       : "LORA",
    },
    "user"   : {
        "image"   : None,
        "username": "bolero537"
    },
    "file"   : {
        "uuid": str,
    },
    "version": dict,
    "num"    : range(1, 3),
},

{
    "#url"    : "https://civitai.com/models/703211?modelVersionId=786644",
    "#comment": "model version ID",
    "#class"  : civitai.CivitaiModelExtractor,
    "#urls"   : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/00004-822988489.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/00005-1059918744.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/00006-3467286319.png",
    ],

    "version": {
        "baseModel"   : "Pony",
        "createdAt"   : "2024-08-30T15:28:47.661Z",
        "date"        : "dt:2024-08-30 15:28:47",
        "files"       : list,
        "id"          : 786644,
        "name"        : "v1.0 pony",
    },
    "user"   : {
        "image"   : None,
        "username": "bolero537"
    },
    "file"   : {
        "id"  : {26887862, 26887856, 26887852},
        "uuid": {"52b6efa7-801c-4901-90b4-fa3964d23480",
                 "c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c",
                 "68568d22-c4f3-45cb-ac32-82f1cedf968f"},
    },
    "model"  : {
        "id": 703211,
    },
    "num"    : range(1, 3),
},

{
    "#url"  : "https://civitai.com/images/26962948",
    "#class": civitai.CivitaiImageExtractor,
    "#options"     : {"quality": "w", "metadata": True},
    "#urls"        : "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/w/00014-3150861441.png",
    "#sha1_content": "a9a9d08f5fcdbc1e1eec7f203717f9df97b7a671",

    "createdAt": "2024-08-31T01:11:47.021Z",
    "date"     : "dt:2024-08-31 01:11:47",
    "extension": "jpg",
    "filename" : "00014-3150861441",
    "hash"     : "ULN0-w?b4nRjxGM{-;t7M_t7NGae~qRjMyt7",
    "height"   : 1536,
    "id"       : 26962948,
    "nsfwLevel": 1,
    "postId"   : 6030721,
    "stats"    : dict,
    "url"      : "69bf3279-df2c-4ec8-b795-479e9cd3db1b",
    "uuid"     : "69bf3279-df2c-4ec8-b795-479e9cd3db1b",
    "width"    : 1152,
    "user"     : {
        "username": "bolero537",
    },
    "generation": {
        "canRemix"  : True,
        "external"  : None,
        "generationProcess": "img2img",
        "resources" : list,
        "techniques": [],
        "tools"     : [],
        "meta"      : {
            "Denoising strength": "0.4",
            "Model"         : "boleromix_XL_V1.3",
            "Model hash"    : "afaf521da2",
            "Size"          : "1152x1536",
            "Tiled Diffusion scale factor": "1.5",
            "Tiled Diffusion upscaler": "R-ESRGAN 4x+ Anime6B",
            "VAE"           : "sdxl_vae.safetensors",
            "Version"       : "v1.7.0",
            "cfgScale"      : 7,
            "negativePrompt": "negativeXL_D,(worst quality,extra legs,extra arms,extra ears,bad fingers,extra fingers,bad anatomy, missing fingers, lowres,username, artist name, text,pubic hair,bar censor,censored,multipul angle,split view,realistic,3D:1)",
            "prompt"        : "masterpiece,ultra-detailed,best quality,8K,illustration,cute face,clean skin ,shiny hair,girl,ultra-detailed-eyes,simple background, <lora:add-detail-xl:1> <lora:classic maid_XL_V1.0:1> maid, maid apron, maid headdress, long sleeves,tray,tea,cup,skirt lift",
            "resources"     : list,
            "sampler"       : "DPM++ 2M Karras",
            "seed"          : 3150861441,
            "steps"         : 20,
            "hashes"        : {
                "lora:add-detail-xl": "9c783c8ce46c",
                "lora:classic maid_XL_V1.0": "e8f6e4297112",
                "model": "afaf521da2",
                "vae": "735e4c3a44",
            },
            "TI hashes"     : {
                "negativeXL_D": "fff5d51ab655",
            },
        },
    },
},

{
    "#url"    : "https://civitai.com/posts/6877551",
    "#class"  : civitai.CivitaiPostExtractor,
    "#options": {"metadata": "generation"},
    "#urls"   : [
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6220fa0f-9037-4b1d-bfbd-a740a06eeb7c/original=true/30748752.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/cd1edb7f-7b50-4da5-bf23-d38f24d8aef0/original=true/30748747.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/cfd5b231-accd-49bd-8bde-370880f63aa6/original=true/30748733.png",
    ],

    "post": {
        "id"  : 6877551,
        "date": "dt:2024-09-22 12:54:15",
    },
    "file": {
        "id"  : {30748752, 30748747, 30748733},
        "uuid": {"6220fa0f-9037-4b1d-bfbd-a740a06eeb7c",
                 "cd1edb7f-7b50-4da5-bf23-d38f24d8aef0",
                 "cfd5b231-accd-49bd-8bde-370880f63aa6"},
        "generation": {
            "resources" : list,
            "techniques": [],
            "tools"     : [],
            "meta"      : {
                "prompt"        : str,
                "negativePrompt": str,
            },
        },
    },
},

{
    "#url"  : "https://civitai.com/tag/mecha",
    "#class": civitai.CivitaiTagExtractor,
},

{
    "#url"  : "https://civitai.com/images?tags=482",
    "#class": civitai.CivitaiImagesExtractor,
},

{
    "#url"  : "https://civitai.com/images?modelVersionId=786644",
    "#class": civitai.CivitaiImagesExtractor,
},

{
    "#url"  : "https://civitai.com/models",
    "#class": civitai.CivitaiModelsExtractor,
},

{
    "#url"  : "https://civitai.com/search/models?sortBy=models_v9&query=mecha",
    "#class": civitai.CivitaiSearchExtractor,
},

{
    "#url"  : "https://civitai.com/user/waomodder",
    "#class": civitai.CivitaiUserExtractor,
    "#urls" : [
        "https://civitai.com/user/waomodder/models",
        "https://civitai.com/user/waomodder/posts",
    ],
},

{
    "#url"  : "https://civitai.com/user/waomodder/models",
    "#class": civitai.CivitaiUserModelsExtractor,
    "#pattern": civitai.CivitaiModelExtractor.pattern,
    "#count"  : ">= 8",
},

{
    "#url"  : "https://civitai.com/user/waomodder/posts",
    "#class": civitai.CivitaiUserPostsExtractor,
    "#pattern": r"https://image\.civitai\.com/xG1nkqKTMzGDvpLrqFT7WA/[0-9a-f-]+/original=true/\S+\.(jpe?g|png)",
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"  : "https://civitai.com/user/waomodder/images",
    "#class": civitai.CivitaiUserImagesExtractor,
    "#pattern": r"https://image\.civitai\.com/xG1nkqKTMzGDvpLrqFT7WA/[0-9a-f-]+/original=true/\S+\.png",
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"     : "https://civitai.com/user/USER/images?section=reactions",
    "#category": ("", "civitai", "reactions"),
    "#class"   : civitai.CivitaiUserImagesExtractor,
    "#auth"    : True,
    "#urls"    : (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/dd29c97a-1e95-4186-8df5-632736cbae79/original=true/00012-2489035818.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/original=true/00013-4238863814.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/original=true/00014-3150861441.png",
    ),
},

{
    "#url"     : "https://civitai.com/user/USER/images?section=reactions",
    "#category": ("", "civitai", "reactions"),
    "#class"   : civitai.CivitaiUserImagesExtractor,
    "#auth"     : False,
    "#exception": exception.AuthorizationError,
},

{
    "#url"  : "https://civitai.com/user/jboogx_creative/videos",
    "#class": civitai.CivitaiUserVideosExtractor,
    "#pattern": r"https://image\.civitai\.com/xG1nkqKTMzGDvpLrqFT7WA/[0-9a-f-]+/original=true/\S+\.mp4",
    "#range"  : "1-50",
    "#count"  : 50,
},

)
