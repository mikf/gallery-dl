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
    "#results": (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/51ea6a54-762c-46cf-9588-726461193c96/original=true/00019-2944604798.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/aaa474a8-5a4d-4003-819f-79df2935ad78/original=true/00020-1919126538.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/1bb22783-1c29-405e-9d7e-7c98b5a53d65/original=true/00021-2415646212.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/00004-822988489.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/00005-1059918744.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/00006-3467286319.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/original=true/00013-4238863814.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/original=true/00014-3150861441.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2dd1dc69-45a6-4beb-b36b-2e2bc65e3cda/original=true/00015-2885514572.png",
    ),

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
    "#results": (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/52b6efa7-801c-4901-90b4-fa3964d23480/original=true/00004-822988489.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4d3bcd5-0e23-4f4e-9f34-d13b2f2bf14c/original=true/00005-1059918744.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/68568d22-c4f3-45cb-ac32-82f1cedf968f/original=true/00006-3467286319.png",
    ),

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
    "#results"     : "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/w/00014-3150861441.png",
    "#sha1_content": "a9a9d08f5fcdbc1e1eec7f203717f9df97b7a671",

    "extension": "png",
    "filename" : "00014-3150861441",
    "file": {
        "createdAt": "2024-08-31T01:11:47.021Z",
        "date"     : "dt:2024-08-31 01:11:47",
        "hash"     : "ULN0-w?b4nRjxGM{-;t7M_t7NGae~qRjMyt7",
        "width"    : 1152,
        "height"   : 1536,
        "id"       : 26962948,
        "nsfwLevel": 1,
        "postId"   : 6030721,
        "stats"    : dict,
        "url"      : "69bf3279-df2c-4ec8-b795-479e9cd3db1b",
        "uuid"     : "69bf3279-df2c-4ec8-b795-479e9cd3db1b",
    },
    "user"     : {
        "username": "bolero537",
    },
    "generation": {
        "canRemix"  : True,
        "external"  : None,
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
    "post": {
        "id": 6030721,
        "nsfwLevel": 1,
        "title": "メイド　クラシック/maid classic - v1.0 XL Showcase",
        "detail": None,
        "modelVersionId": 788385,
        "modelVersion": {
            "id": 788385,
        },
        "publishedAt": "2024-08-31T01:11:52.175Z",
        "availability": "Public",
        "tags": [],
        "collectionId": None,
    },
    "tags[*]": {
        "automated"  : bool,
        "concrete"   : bool,
        "downVotes"  : int,
        "id"         : int,
        "lastUpvote" : None,
        "name"       : str,
        "needsReview": bool,
        "nsfwLevel"  : 1,
        "score"      : int,
        "type"       : {"Label", "UserGenerated"},
        "upVotes"    : int,
    },
    "model": {
        "id": 703211,
        "name": "メイド　クラシック/maid classic",
        "type": "LORA",
        "status": "Published",
        "publishedAt": "2024-08-30T15:38:14.770Z",
        "nsfw": False,
        "uploadType": "Created",
        "availability": "Public",
    },
    "version": {
        "id": 788385,
        "name": "v1.0 XL",
        "description": None,
        "baseModel": "SDXL 1.0",
        "baseModelType": "Standard",
        "earlyAccessConfig": None,
        "earlyAccessEndsAt": None,
        "trainedWords": [
            "maid, maid apron, maid headdress, long sleeves",
        ],
        "epochs": None,
        "steps": None,
        "clipSkip": None,
        "status": "Published",
        "createdAt": "2024-08-31T01:11:08.841Z",
        "vaeId": None,
        "trainingDetails": None,
        "trainingStatus": None,
        "uploadType": "Created",
        "usageControl": "Download",
        "requireAuth": True,
        "settings": {
            "strength": 0.8,
        },
        "recommendedResources": [],
        "monetization": None,
        "canGenerate": True,
        "files": None,
    },
},

{
    "#url"    : "https://civitai.com/images/44789630",
    "#comment": "video - 'post' metadata (#7548)",
    "#class"  : civitai.CivitaiImageExtractor,
    "#options": {"metadata": "post"},
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6a09ec54-6de4-4af1-b11d-2d0d8a66d651/quality=100/copy_C6C532CE-EC47-4A52-9138-AEF1D7756F16.Mp4",

    "extension": "mp4",
    "filename" : "copy_C6C532CE-EC47-4A52-9138-AEF1D7756F16",
    "file"     : {
        "date"     : "dt:2024-12-10 19:19:14",
        "hash"     : "U9D8%cIU03Rk02?F$$WE0gs,?GSg~B9ut6sl",
        "width"    : 1080,
        "height"   : 1920,
        "id"       : 44789630,
        "mimeType" : "video/mp4",
        "nsfwLevel": 2,
        "postId"   : 10151863,
        "stats"    : dict,
        "type"     : "video",
        "url"      : "6a09ec54-6de4-4af1-b11d-2d0d8a66d651",
        "uuid"     : "6a09ec54-6de4-4af1-b11d-2d0d8a66d651",
        "metadata" : {
            "audio"   : True,
            "duration": 15.033,
            "hash"    : "U9D8%cIU03Rk02?F$$WE0gs,?GSg~B9ut6sl",
            "height"  : 1920,
            "size"    : 23984479,
            "width"   : 1080,
        },
    },
    "post": {
        "availability": "Public",
        "collectionId": None,
        "date"        : "dt:2024-12-10 19:20:51",
        "detail"      : None,
        "id"          : 10151863,
        "modelVersion": None,
        "modelVersionId": None,
        "nsfwLevel"   : 2,
        "publishedAt" : "2024-12-10T19:20:51.579Z",
        "tags"        : [],
        "title"       : None,
    },
    "user"     : {
        "username": "jboogx_creative",
    },
},

{
    "#url"  : "https://civitai.com/images/74353746",
    "#comment": "video, rated 'R', WebP download (#7502)",
    "#class": civitai.CivitaiImageExtractor,
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c7e3744b-8f0d-4124-94c1-75e2af00431d/quality=100/2025-04-25-23h40m21s_seed665048144_A man appears from off screen and spanks her butto_2.webm",

    "extension": "webm",
    "filename" : "2025-04-25-23h40m21s_seed665048144_A man appears from off screen and spanks her butto_2",
    "file"     : {
        "date"     : "dt:2025-05-05 12:27:28",
        "hash"     : "UMCsEoRPivxY~VjuWBoenMWBx]WrxvV?xvbb",
        "width"    : 512,
        "height"   : 752,
        "id"       : 74353746,
        "mimeType" : "video/webm",
        "nsfwLevel": 4,
        "postId"   : 16509805,
        "stats"    : dict,
        "type"     : "video",
        "url"      : "c7e3744b-8f0d-4124-94c1-75e2af00431d",
        "uuid"     : "c7e3744b-8f0d-4124-94c1-75e2af00431d",
        "metadata" : {
            "audio"   : False,
            "duration": 5.016,
            "hash"    : "UMCsEoRPivxY~VjuWBoenMWBx]WrxvV?xvbb",
            "height"  : 752,
            "size"    : 6011344,
            "skipScannedAtReassignment": True,
            "width"   : 512,
        },
    },
    "user"     : {
        "id"      : 4856161,
        "username": "VlrgRomNS",
    },
},

{
    "#url"    : "https://civitai.com/images/76635747",
    "#comment": "no 'modelVersionId' (#7432)",
    "#class"  : civitai.CivitaiImageExtractor,
    "#options": {"metadata": "version"},
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/65c1a01c-2583-4495-b4e9-bdb94218004e/original=true/5b5b95f8-9923-4c27-b50a-c801c0311375-0.jpg",

    "model"  : None,
    "version": None,
},

{
    "#url"    : "https://civitai.com/images/68947296",
    "#comment": "rated R / nsfwlevel 4",
    "#class"  : civitai.CivitaiImageExtractor,
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/2d1fbe1b-6038-479f-8c37-39d338198fb1/quality=100/received_687641707052140.mp4",

    "file": {
        "nsfwLevel": 4,
    },
},

{
    "#url"    : "https://civitai.com/images/68852050",
    "#comment": "rated X / nsfwlevel 8",
    "#class"  : civitai.CivitaiImageExtractor,
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/1107208c-14cc-46fd-848d-2efa14fa6180/original=true/QRQC7HE5DFW3QZ85R3MXQXY440.jpeg",

    "file": {
        "nsfwLevel": 8,
    },
},

{
    "#url"    : "https://civitai.com/images/68851932",
    "#comment": "rated XXX / nsfwlevel 16",
    "#class"  : civitai.CivitaiImageExtractor,
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/fdbaa27d-4278-496b-8209-21591e5dc6fe/original=true/Q8AE16QCMCYCCBX49PG8VVWWD0.jpeg",

    "file": {
        "nsfwLevel": 16,
    },
},

{
    "#url"    : "https://civitai.com/posts/6877551",
    "#class"  : civitai.CivitaiPostExtractor,
    "#options": {"metadata": "generation"},
    "#results": (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6220fa0f-9037-4b1d-bfbd-a740a06eeb7c/original=true/30748752.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/cd1edb7f-7b50-4da5-bf23-d38f24d8aef0/original=true/30748747.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/cfd5b231-accd-49bd-8bde-370880f63aa6/original=true/30748733.png",
    ),

    "post": {
        "id"  : 6877551,
        "date": "dt:2024-09-22 12:54:15",
    },
    "file": {
        "id"  : {30748752, 30748747, 30748733},
        "date": "dt:2024-09-22 12:54:15",
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
    "#url"    : "https://civitai.com/posts/17021768",
    "#comment": "no 'modelVersionId' (#7432)",
    "#class"  : civitai.CivitaiPostExtractor,
    "#options": {"metadata": "version"},

    "model"  : None,
    "version": None,
},

{
    "#url"     : "https://civitai.com/posts/20403514",
    "#comment" : "mixed image & video (#8053)",
    "#class"   : civitai.CivitaiPostExtractor,
    "#results" : (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/62dbebbe-48e9-4232-b4da-33c70d19683d/original=true/91967659.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/e5786ddc-29b3-4a69-aec9-fba4dc2c78b5/quality=100/91967639.webm",
    ),
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
    "#url"     : "https://civitai.com/videos",
    "#class"   : civitai.CivitaiVideosExtractor,
},

{
    "#url"     : "https://civitai.com/videos?tags=5169",
    "#class"   : civitai.CivitaiVideosExtractor,
},

{
    "#url"  : "https://civitai.com/models",
    "#class": civitai.CivitaiModelsExtractor,
},

{
    "#url"  : "https://civitai.com/search/models?sortBy=models_v9&query=Voynich",
    "#class": civitai.CivitaiSearchModelsExtractor,
    "#results": (
        "https://civitai.com/models/99868",
        "https://civitai.com/models/341330",
        "https://civitai.com/models/884509",
        "https://civitai.com/models/1003064",
    ),
},

{
    "#url"    : "https://civitai.com/search/images?sortBy=images_v6&query=Voynich",
    "#class"  : civitai.CivitaiSearchImagesExtractor,
    "#options": {"nsfw": False},
    "#count"  : range(150, 200),
    "#archive": False,
},

{
    "#url"  : "https://civitai.com/user/waomodder",
    "#class": civitai.CivitaiUserExtractor,
    "#results": (
        "https://civitai.com/user/waomodder/images",
        "https://civitai.com/user/waomodder/videos",
    ),
},

{
    "#url"  : "https://civitai.com/user/waomodder/models",
    "#class": civitai.CivitaiUserModelsExtractor,
    "#pattern": civitai.CivitaiModelExtractor.pattern,
    "#count"  : ">= 8",
},

{
    "#url"    : "https://civitai.com/user/waomodder/models?tag=character&types=Checkpoint&types=TextualInversion&types=Hypernetwork&types=LORA&checkpointType=Trained&fileFormats=SafeTensor&fileFormats=PickleTensor",
    "#comment": "various filters (#7138)",
    "#class"  : civitai.CivitaiUserModelsExtractor,
    "#results": (
        "https://civitai.com/models/42166",
        "https://civitai.com/models/79845",
        "https://civitai.com/models/81424",
        "https://civitai.com/models/75925",
        "https://civitai.com/models/65818",
        "https://civitai.com/models/64272",
    ),
},

{
    "#url"  : "https://civitai.com/user/waomodder/posts",
    "#class": civitai.CivitaiUserPostsExtractor,
    "#pattern": r"https://image\.civitai\.com/xG1nkqKTMzGDvpLrqFT7WA/[0-9a-f-]+/original=true/\S+\.(jpe?g|png)",
    "#range"  : "1-50",
    "#count"  : 50,

    "file": {
        "id"  : int,
        "date": "type:datetime",
    },
    "post": {
        "id"  : int,
        "date": "type:datetime",
    },
},

{
    "#url"      : "https://civitai.com/user/jackietop515100/posts",
    "#comment"  : "deleted user (#8299)",
    "#class"    : civitai.CivitaiUserPostsExtractor,
    "#options"  : {"timeout": 5, "retries": 2},
    "#exception": exception.HttpError,
},

{
    "#url"  : "https://civitai.com/user/waomodder/images",
    "#class": civitai.CivitaiUserImagesExtractor,
    "#pattern": r"https://image\.civitai\.com/xG1nkqKTMzGDvpLrqFT7WA/[0-9a-f-]+/original=true/\S+\.png",
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://civitai.com/user/waomodder/images?tags=5132",
    "#comment": "tags (#7138)",
    "#class"  : civitai.CivitaiUserImagesExtractor,
    "#results": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/8cc7c513-ba77-4444-a21f-7e3907d29a4e/original=true/982824.png",
},

{
    "#url"    : "https://civitai.com/user/waomodder/images?sort=Most+Collected&period=AllTime&tags=6594&baseModels=Illustrious&baseModels=PixArt+a&baseModels=Other&baseModels=Pony&remixesOnly=false",
    "#comment": "various filters (#7138)",
    "#class"  : civitai.CivitaiUserImagesExtractor,
    "#range"  : "1-3",
    "#results": (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c44c116a-263b-457d-8fa8-cc3d7716a0aa/original=true/36800924.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0f6cf303-8b12-4401-914e-bff33371e9c6/original=true/36801099.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/9a682316-e451-4b98-8873-cc6c2e2d39bb/original=true/36801079.png",
    ),
},

{
    "#url"     : "https://civitai.com/user/USER/images?section=reactions",
    "#category": ("", "civitai", "reactions-images"),
    "#class"   : civitai.CivitaiUserImagesExtractor,
    "#auth"    : True,
    "#results" : (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/dd29c97a-1e95-4186-8df5-632736cbae79/original=true/00012-2489035818.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/5c4efa68-bb58-47c5-a716-98cd0f51f047/original=true/00013-4238863814.png",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/69bf3279-df2c-4ec8-b795-479e9cd3db1b/original=true/00014-3150861441.png",
    ),
},

{
    "#url"     : "https://civitai.com/user/USER/images?section=reactions",
    "#category": ("", "civitai", "reactions-images"),
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

{
    "#url"     : "https://civitai.com/user/USER/videos?section=reactions",
    "#category": ("", "civitai", "reactions-videos"),
    "#class"   : civitai.CivitaiUserVideosExtractor,
    "#auth"    : True,
    "#results" : (
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/6a09ec54-6de4-4af1-b11d-2d0d8a66d651/quality=100/copy_C6C532CE-EC47-4A52-9138-AEF1D7756F16.Mp4",
        "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/74cd3e71-7833-4e32-9724-b8d1702693be/quality=100/1_THANKSGIVING_CLAYMATION_TOPAZ.mp4",
    ),
},

{
    "#url"     : "https://civitai.com/user/USER/videos?section=reactions",
    "#category": ("", "civitai", "reactions-videos"),
    "#class"   : civitai.CivitaiUserVideosExtractor,
    "#auth"     : False,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://civitai.com/generate",
    "#class"   : civitai.CivitaiGeneratedExtractor,
    "#auth"    : True,
},

{
    "#url"     : "https://civitai.com/collections/11035869",
    "#class"   : civitai.CivitaiCollectionExtractor,
    "#results" : "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/9b9c64b4-60de-4a9c-becd-a386ecf3fa7a/original=true/DailyWorldMorphChallenge_Base_0003.png",

    "filename"       : "DailyWorldMorphChallenge_Base_0003",
    "extension"      : "png",
    "url"            : "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/9b9c64b4-60de-4a9c-becd-a386ecf3fa7a/original=true/DailyWorldMorphChallenge_Base_0003.png",
    "collection"     : {
        "availability": "Public",
        "description" : "",
        "id"          : 11035869,
        "image"       : None,
        "metadata"    : {},
        "mode"        : None,
        "name"        : "Trees, Bonsai, and so one",
        "nsfw"        : False,
        "nsfwLevel"   : 1,
        "read"        : "Public",
        "tags"        : [],
        "type"        : "Image",
        "userId"      : 4831516,
        "write"       : "Private",
    },
    "file"           : {
        "acceptableMinor": False,
        "availability"   : "Public",
        "blockedFor"     : None,
        "cosmetic"       : None,
        "createdAt"      : "2025-04-30T20:20:44.015Z",
        "date"           : "dt:2025-04-30 20:20:44",
        "hasMeta"        : True,
        "hasPositivePrompt": True,
        "hash"           : "UHEfvNWC?dof00oc4Uae$,ofV}WFxeWCxwWV",
        "height"         : 1152,
        "hideMeta"       : False,
        "id"             : 73339178,
        "index"          : 1,
        "ingestion"      : "Scanned",
        "metadata"       : {
            "hash"  : "UHEfvNWC?dof00oc4Uae$,ofV}WFxeWCxwWV",
            "height": 1152,
            "size"  : 1523677,
            "width" : 896,
        },
        "mimeType"       : "image/png",
        "minor"          : False,
        "modelVersionId" : None,
        "modelVersionIds": [],
        "modelVersionIdsManual": [],
        "name"           : "DailyWorldMorphChallenge_Base_0003.png",
        "needsReview"    : None,
        "nsfwLevel"      : 1,
        "onSite"         : False,
        "poi"            : False,
        "postId"         : 16290779,
        "postTitle"      : None,
        "publishedAt"    : "2025-04-30T20:23:40.409Z",
        "reactions"      : [],
        "remixOfId"      : None,
        "scannedAt"      : "2025-04-30T20:20:48.072Z",
        "sortAt"         : "2025-04-30T20:23:40.409Z",
        "stats"          : {
            "collectedCountAllTime": 1,
            "commentCountAllTime": 0,
            "cryCountAllTime" : 1,
            "dislikeCountAllTime": 0,
            "heartCountAllTime": 1,
            "laughCountAllTime": 0,
            "likeCountAllTime": 5,
            "tippedAmountCountAllTime": 0,
            "viewCountAllTime": 0,
        },
        "tagIds"         : [
            5248,
            9143,
            111839,
            112019,
            116352,
            120250,
            161904,
            234268,
        ],
        "tags"           : None,
        "thumbnailUrl"   : None,
        "type"           : "image",
        "url"            : "9b9c64b4-60de-4a9c-becd-a386ecf3fa7a",
        "uuid"           : "9b9c64b4-60de-4a9c-becd-a386ecf3fa7a",
        "width"          : 896,
    },
    "user"           : {
        "cosmetics"     : list,
        "deletedAt"     : None,
        "id"            : 2624648,
        "image"         : "ce0f7d5e-cc4a-41e2-8587-75d823c85ce9",
        "profilePicture": None,
        "username"      : "AIArtsChannel",
    },
    "user_collection": {
        "cosmetics"     : [],
        "deletedAt"     : None,
        "id"            : 4831516,
        "image"         : "https://lh3.googleusercontent.com/a/ACg8ocKeClAsD6kmHOATnC4Li1PLYw9-J41LCaVHdzcLLGZi9ElNUQ=s96-c",
        "profilePicture": None,
        "username"      : "TettyCo",
    },
},

{
    "#url"     : "https://civitai.com/collections/11453135",
    "#class"   : civitai.CivitaiCollectionExtractor,
    "#count"   : 12,

    "collection"     : {
        "availability": "Public",
        "description" : "",
        "id"          : 11453135,
        "image"       : None,
        "metadata"    : {},
        "mode"        : None,
        "name"        : "Sakura Trees",
        "nsfw"        : False,
        "nsfwLevel"   : 3,
        "read"        : "Public",
        "tags"        : [],
        "type"        : "Image",
        "userId"      : 8511981,
        "write"       : "Private",
    },
},

{
    "#url"     : "https://civitai.com/user/SakuraCherryBlossoms/collections",
    "#class"   : civitai.CivitaiUserCollectionsExtractor,
    "#results" : (
        "https://civitai.com/collections/11462456",
        "https://civitai.com/collections/11453431",
        "https://civitai.com/collections/11453135",
        "https://civitai.com/collections/11407164",
        "https://civitai.com/collections/11405046",
        "https://civitai.com/collections/11395523",
        "https://civitai.com/collections/11395467",
    ),
},

)
