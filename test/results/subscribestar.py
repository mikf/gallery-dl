# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import subscribestar


__tests__ = (
{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#pattern" : r"https://(www\.subscribestar\.com/uploads\?payload=.+|(ss-uploads-prod\.b-cdn|\w+\.cloudfront)\.net/uploads(_v2)?/users/11/)",
    "#count"   : range(20, 50),

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : str,
    "date"       : "type:datetime",
    "id"         : int,
    "num"        : int,
    "post_id"    : int,
    "tags"       : list,
    "title"      : str,
    "type"       : r"re:image|video|attachment",
    "url"        : str,
    "?pinned"    : bool,
},

{
    "#url"     : "https://www.subscribestar.com/subscribestar",
    "#category": ("", "subscribestar", "user"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#options" : {"metadata": True},
    "#range"   : "1",

    "date": "type:datetime",
},

{
    "#url"     : "https://www.subscribestar.com/subscribestar?tag=Security",
    "#comment" : "'tag' query parameter (#8737)",
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#count"   : 0,
    "#metadata": "post",

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : "\n<h1>Enhance Your Account Security with OTP</h1>\n<div>In addition to our existing email-based Two-Factor Authentication (2FA), we encourage everyone to use a more secure and convenient method: One-Time Password (OTP) 2FA using authentication apps like 1Password, Google Authenticator etc. To get started:</div>\n<ol>\n<li>Navigate to <strong>Menu → Account Settings</strong>, scroll down to the Authenticator Apps (OTP 2FA) section.</li>\n<li>Click the \"<strong>Set up OTP</strong>\" button and follow the instructions.<br><br>\n</li>\n</ol>\n<div>The entire process should take less than 5 minutes. You can opt out of using email 2FA then.</div>\n<div><br></div>\n<div><strong>Why Choose OTP 2FA Over Email 2FA?</strong></div>\n<div>\n<strong>Stronger Security</strong>: While email 2FA adds an extra layer of protection, OTP 2FA generates codes directly on your mobile device, reducing the risk associated with email interception or unauthorized access.</div>\n<div>\n<strong>Instant Access</strong>: Authentication apps provide time-sensitive codes without the need for an internet connection or waiting for an email to arrive.</div>\n<div>\n<strong>Enhanced Protection Against Phishing</strong>: OTP codes from authentication apps are less susceptible to phishing attacks compared to email-based codes.</div>\n\n",
    "date"       : "dt:2024-09-30 20:46:00",
    "post_id"    : 1320999,
    "search_tags": "Security",
    "title"      : "Enhance Your Account Security with OTP",
    "tags"       : [
        "Security",
        "PlatformUpdates",
    ],
},

{
    "#url"     : "https://subscribestar.adult/kanashiipanda",
    "#category": ("", "subscribestar", "user-adult"),
    "#class"   : subscribestar.SubscribestarUserExtractor,
    "#auth"    : True,
    "#range"   : "1-10",
    "#count"   : 10,
},

{
    "#url"     : "https://www.subscribestar.com/posts/102468",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#count"   : 1,

    "author_id"  : 11,
    "author_name": "subscribestar",
    "author_nick": "SubscribeStar",
    "content"    : r"re:<h1>Brand Guidelines and Assets</h1>",
    "date"       : "dt:2020-05-07 12:33:00",
    "extension"  : "jpg",
    "filename"   : "ss_page-brand",
    "group"      : "imgs_and_videos",
    "height"     : 291,
    "id"         : 203885,
    "num"        : 1,
    "pinned"     : False,
    "post_id"    : 102468,
    "tags"       : [],
    "title"      : "Brand Guidelines and Assets",
    "type"       : "image",
    "width"      : 700,
},

{
    "#url"     : "https://www.subscribestar.com/posts/920015",
    "#comment" : "attachment (#6721)",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#range"   : "2",
    "#pattern" : r"https://\w+.cloudfront.net/uploads_v2/users/11/posts/920015/bc018a55-9668-47f4-a664-b5fd66b56aaa.pdf\?filename=Training%2520for%2520freelancers%2520-%2520Fiverr.pdf&.+",
    "date"     : "dt:2023-05-30 09:20:00",
    "extension": "pdf",
    "filename" : "Training for freelancers - Fiverr",
    "id"       : 1957727,
    "name"     : "Training for freelancers - Fiverr.pdf",
    "num"      : 2,
    "post_id"  : 920015,
    "title"    : "",
    "type"     : "attachment",
},

{
    "#url"     : "https://www.subscribestar.com/posts/1851025",
    "#comment" : "content / title not inside <body> (#7486)",
    "#category": ("", "subscribestar", "post"),
    "#class"   : subscribestar.SubscribestarPostExtractor,

    "author_id"  : 581352,
    "author_name": "inelia-benz",
    "author_nick": "Inelia Benz",
    "content"    : "<h1>Listening to Sasquatch - Driving to the Rez - Episode 243 - Part One</h1>\n\n<p>Topics we cover:</p>\n\n<p>Tree breaks, Foot stomps, Tracks and trackways, Hoots/calls with answers, \nTree structures, nests, Portal Cracks, Shapeshifting, Shimmer/invisibility \ncloaking, direct physical interaction inside the cloaking field, manipulation \nof canoe while we are in it, face to face interactions with multiple individuals \nteen aged and adult, male and female, cloaked and not cloaked, \nand vocalizations like drops of water. Truly amazing stories.</p>\n\n<p><a href=\"https://www.subscribestar.com/posts/1853792\" data-href=\"https://www.subscribestar.com/posts/1853792\">Go To Part Two</a></p>\n\n<p><a href=\"/away?url=aHR0cHM6Ly92aWRlby5pbmVsaWFiZW56LmNvbS9saXN0ZW5pbmctdG8tc2Fz%0AcXVhdGNoLWRyaXZpbmctdG8tdGhlLXJlei1lcGlzb2RlLTI0My1wYXJ0LW9u%0AZQ==%0A\" data-href=\"https://video.ineliabenz.com/listening-to-sasquatch-driving-to-the-rez-episode-243-part-one\">Watch the Video</a></p>\n\n<p><a href=\"/away?url=aHR0cHM6Ly9pbmVsaWEuc3Vic3RhY2suY29tL3AvbGlzdGVuaW5nLXRvLXNh%0Ac3F1YXRjaA==%0A\" data-href=\"https://inelia.substack.com/p/listening-to-sasquatch\">Read the article</a></p>\n\n<p>Audio is attached to this post.</p>",
    "date"       : "dt:2025-05-07 13:23:00",
    "extension"  : {"mp3", "jpg"},
    "filename"   : {"dttr-243-sasquatch-part1", "yt-243-pt1"},
    "id"         : {0, 4627253},
    "num"        : range(1, 2),
    "post_id"    : 1851025,
    "tags"       : [],
    "title"      : "Listening to Sasquatch - Driving to the Rez - Episode 243 - Part One",
    "type"       : {"audio", "image"},
},

{
    "#url"     : "https://subscribestar.adult/posts/22950",
    "#category": ("", "subscribestar", "post-adult"),
    "#class"   : subscribestar.SubscribestarPostExtractor,
    "#auth"    : True,
    "#count"   : 1,

    "date": "dt:2019-04-28 07:32:00",
},

)
