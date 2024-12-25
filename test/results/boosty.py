# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import boosty


__tests__ = (
{
    "#url"     : "https://boosty.to/milshoo",
    "#class"   : boosty.BoostyUserExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://boosty.to/milshoo?postsFrom=1706742000&postsTo=1709247599",
    "#class"   : boosty.BoostyUserExtractor,
    "#urls"    : "https://images.boosty.to/image/ff0d2006-3ee7-483d-a5fc-2a05b531742c?change_time=1707829201",
},

{
    "#url"     : "https://boosty.to/milshoo/media/all",
    "#class"   : boosty.BoostyMediaExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://boosty.to/milshoo/posts/4304d8f0-3f49-4f97-a3f3-9f064bc32b2f",
    "#class"   : boosty.BoostyPostExtractor,
    "#urls"    : "https://images.boosty.to/image/75f86086-fc67-4ed2-9365-2958d3d1a8f7?change_time=1711027786",

    "count"    : 1,
    "num"      : 1,
    "extension": "",
    "filename" : "75f86086-fc67-4ed2-9365-2958d3d1a8f7",

    "file": {
        "height"   : 2048,
        "id"       : "75f86086-fc67-4ed2-9365-2958d3d1a8f7",
        "rendition": "",
        "size"     : 1094903,
        "type"     : "image",
        "url"      : "https://images.boosty.to/image/75f86086-fc67-4ed2-9365-2958d3d1a8f7?change_time=1711027786",
        "width"    : 2048,
    },
    "user": {
        "avatarUrl": "https://images.boosty.to/user/173542/avatar?change_time=1580888689",
        "blogUrl"  : "milshoo",
        "flags"    : {
            "showPostDonations": True,
        },
        "hasAvatar": True,
        "id"       : 173542,
        "name"     : "Милшу",
    },
    "post": {
        "comments"   : dict,
        "content"    : [
            "Привет! Это Милшу ) Я открываю комментарии в своём телеграм канале Милшу ( ",
            "https://t.me/milshoonya",
            " ) и хочу, чтобы вы первые протестировали его работу :3\nСсылку на вступление в чат оставлю здесь ",
            "https://t.me/+Z_5ph-XnIQU2YWMy",
            "\nТакже хотела напомнить, что мы собираем деньги на два арта от Ананаси: ",
            "https://boosty.to/milshoo/single-payment/donation/550562/target?share=target_link",
            "\nБуду очень благодарна за помощь :D  ",
        ],
        "contentCounters": list,
        "count"      : dict,
        "createdAt"  : 1711027834,
        "currencyPrices": {
            "RUB": 0,
            "USD": 0,
        },
        "date"       : "dt:2024-03-21 13:30:34",
        "donations"  : 0,
        "donators"   : dict,
        "hasAccess"  : True,
        "id"         : "4304d8f0-3f49-4f97-a3f3-9f064bc32b2f",
        "int_id"     : 5547124,
        "isBlocked"  : False,
        "isCommentsDenied": False,
        "isDeleted"  : False,
        "isLiked"    : False,
        "isPublished": True,
        "isRecord"   : False,
        "isWaitingVideo": False,
        "links"      : [
            "https://t.me/milshoonya",
            "https://t.me/+Z_5ph-XnIQU2YWMy",
            "https://boosty.to/milshoo/single-payment/donation/550562/target?share=target_link",
        ],
        "price"      : 0,
        "publishTime": 1711027834,
        "showViewsCounter": False,
        "signedQuery": "",
        "tags"       : [],
        "teaser"     : [],
        "title"      : "Открываю чат в телеге",
        "updatedAt"  : 1711027904
    },
},

{
    "#url"     : "https://boosty.to/geekmedia/posts/31bb8fb6-83f1-404f-a597-f84bbe611d1d",
    "#comment" : "video",
    "#class"   : boosty.BoostyPostExtractor,
},

{
    "#url"     : "https://boosty.to/xcang/posts/5d4d6f90-5d48-4442-a7e5-2164a858681d",
    "#comment" : "audio",
    "#class"   : boosty.BoostyPostExtractor,
},

{
    "#url"     : "https://boosty.to/",
    "#class"   : boosty.BoostyFeedExtractor,
    "#auth"    : True,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://boosty.to/app/settings/subscriptions",
    "#class"   : boosty.BoostyFollowingExtractor,
    "#pattern" : boosty.BoostyUserExtractor,
    "#auth"    : True,
},


)
