# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import hentaifoundry
import datetime


__tests__ = (
{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/profile",
    "#category": ("", "hentaifoundry", "user"),
    "#class"   : hentaifoundry.HentaifoundryUserExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura",
    "#category": ("", "hentaifoundry", "pictures"),
    "#class"   : hentaifoundry.HentaifoundryPicturesExtractor,
    "#sha1_url": "ebbc981a85073745e3ca64a0f2ab31fab967fc28",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/page/3",
    "#category": ("", "hentaifoundry", "pictures"),
    "#class"   : hentaifoundry.HentaifoundryPicturesExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps",
    "#category": ("", "hentaifoundry", "scraps"),
    "#class"   : hentaifoundry.HentaifoundryScrapsExtractor,
    "#sha1_url": "7cd9c6ec6258c4ab8c44991f7731be82337492a7",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Evulchibi/scraps/page/3",
    "#category": ("", "hentaifoundry", "scraps"),
    "#class"   : hentaifoundry.HentaifoundryScrapsExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/faves/pictures",
    "#category": ("", "hentaifoundry", "favorite"),
    "#class"   : hentaifoundry.HentaifoundryFavoriteExtractor,
    "#sha1_url": "56f9ae2e89fe855e9fe1da9b81e5ec6212b0320b",
},

{
    "#url"     : "https://www.hentai-foundry.com/user/Tenpura/faves/pictures/page/3",
    "#category": ("", "hentaifoundry", "favorite"),
    "#class"   : hentaifoundry.HentaifoundryFavoriteExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/recent/2018-09-20",
    "#category": ("", "hentaifoundry", "recent"),
    "#class"   : hentaifoundry.HentaifoundryRecentExtractor,
    "#pattern" : r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
    "#range"   : "20-30",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/popular",
    "#category": ("", "hentaifoundry", "popular"),
    "#class"   : hentaifoundry.HentaifoundryPopularExtractor,
    "#pattern" : r"https://pictures.hentai-foundry.com/[^/]/[^/?#]+/\d+/",
    "#range"   : "20-30",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/407501/shimakaze",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#sha1_url"    : "fbf2fd74906738094e2575d2728e8dc3de18a8a3",
    "#sha1_content": "91bf01497c39254b6dfb234a18e8f01629c77fd1",

    "artist"     : "Tenpura",
    "date"       : "dt:2016-02-22 14:41:19",
    "description": "Thank you!",
    "height"     : 700,
    "index"      : 407501,
    "media"      : "Other digital art",
    "ratings"    : [
        "Sexual content",
        "Contains female nudity",
    ],
    "score"      : int,
    "tags"       : [
        "collection",
        "kancolle",
        "kantai",
        "shimakaze",
    ],
    "title"      : "shimakaze",
    "user"       : "Tenpura",
    "views"      : int,
    "width"      : 495,
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/suuxe/161533/ANIMATION-of-Insane-Black-Rock-Shooter-FAN-ART",
    "#comment" : "SWF / rumble embed (#4641)",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#urls"    : "https://pictures.hentai-foundry.com/s/suuxe/161533/suuxe-161533-ANIMATION_of_Insane_Black_Rock_Shooter_FAN_ART.swf",

    "artist"     : "suuxe",
    "date"       : "dt:2012-09-15 09:50:45",
    "description": "Here is one of my fav drawings I have made NOW with ANIMATIONS! \"yay\" \n\nTook me ages to get this animation to right size because when I was rendering it out from after effects it crop the freaking drawing so it would be \"widescreen\" for some reason after effects wants that  but I was able to \"fix it\" by making it believe the whole drawing was widescreen while the drawing was in the corner then I crop it in flash to get the right size  I am soooo smart mohahahaha.....!\n\nYou can also find it on my deviantart site:\nhttp://suuxe.deviantart.com/art/ANIMATION-of-Insane-Black-Rock-Shooter-FAN-ART-327072898\n\nUPDATE:\n-Her left arm moves\n-\"Eye flame\" glow is stronger\n-Fire sparkle on the eye flame\n-Rain animations are more visible now\n-Front mist animation also moves around\n-Sparkle animation down left is more visible now\n-Changed the color on the flying dust so it looks more like flame/glow\n\nOld animations made in After Effects:\n-Fire sparkle thingy down left \n-Two layers of rain \n-Glow on her left eye \n-Four layers of mist \n-Some dust particles or what ever you want to call it \n\nStep by Step video: http://www.youtube.com/watch?v=m_-4PLmOCNg",
    "extension"  : "swf",
    "filename"   : "suuxe-161533-ANIMATION_of_Insane_Black_Rock_Shooter_FAN_ART",
    "height"     : 900,
    "index"      : 161533,
    "media"      : "Digital drawing or painting",
    "ratings"    : ["Teen content"],
    "score"      : range(10, 30),
    "src"        : "https://pictures.hentai-foundry.com/s/suuxe/161533/suuxe-161533-ANIMATION_of_Insane_Black_Rock_Shooter_FAN_ART.swf",
    "tags"       : [
        "animation",
        "art",
        "black",
        "brs",
        "epic",
        "fan",
        "flash",
        "hot",
        "insane",
        "kid",
        "rock",
        "shooter"
    ],
    "title"      : "ANIMATION of Insane Black Rock Shooter FAN ART",
    "user"       : "suuxe",
    "views"      : range(30000, 40000),
    "width"      : 393,
},

{
    "#url"     : "http://www.hentai-foundry.com/pictures/user/Tenpura/407501/",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
    "#pattern" : "http://pictures.hentai-foundry.com/t/Tenpura/407501/",
},

{
    "#url"     : "https://www.hentai-foundry.com/pictures/user/Tenpura/407501/",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
},

{
    "#url"     : "https://pictures.hentai-foundry.com/t/Tenpura/407501/Tenpura-407501-shimakaze.png",
    "#category": ("", "hentaifoundry", "image"),
    "#class"   : hentaifoundry.HentaifoundryImageExtractor,
},

{
    "#url"     : "https://www.hentai-foundry.com/stories/user/SnowWolf35",
    "#category": ("", "hentaifoundry", "stories"),
    "#class"   : hentaifoundry.HentaifoundryStoriesExtractor,
    "#count"   : ">= 35",

    "author"     : "SnowWolf35",
    "chapters"   : int,
    "comments"   : int,
    "date"       : datetime.datetime,
    "description": str,
    "index"      : int,
    "rating"     : int,
    "ratings"    : list,
    "status"     : r"re:(Inc|C)omplete",
    "title"      : str,
    "user"       : "SnowWolf35",
    "views"      : int,
    "words"      : int,
},

{
    "#url"     : "https://www.hentai-foundry.com/stories/user/SnowWolf35/26416/Overwatch-High-Chapter-Voting-Location",
    "#category": ("", "hentaifoundry", "story"),
    "#class"   : hentaifoundry.HentaifoundryStoryExtractor,
    "#sha1_url": "5a67cfa8c3bf7634c8af8485dd07c1ea74ee0ae8",

    "title": "Overwatch High Chapter Voting Location",
},

)
