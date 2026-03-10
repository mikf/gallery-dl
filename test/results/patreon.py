# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import patreon
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://www.patreon.com/koveliana",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#range"   : "1-15",
    "#count"   : 15,

    "attachments"  : list,
    "campaign"     : dict,
    "comment_count": int,
    "content"      : str,
    "!content_json_string": str,
    "creator"      : dict,
    "date"         : "type:datetime",
    "id"           : int,
    "images"       : list,
    "like_count"   : int,
    "post_type"    : str,
    "published_at" : str,
    "title"        : str,
},

{
    "#url"     : "https://www.patreon.com/koveliana/posts?filters[month]=2020-3",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#count"   : 1,

    "date": "dt:2020-03-30 21:21:44",
},

{
    "#url"     : "https://www.patreon.com/kovelianot",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/cw/anythingelse",
    "#comment" : "Next.js 13 - /cw/ URL",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/c/koveliana",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user/posts/?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/user?c=369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/profile/creators?u=2931440",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/profile/creators?c=369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/id:369707",
    "#class"   : patreon.PatreonCreatorExtractor,
},

{
    "#url"     : "https://www.patreon.com/create",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#fail"    : True,
},

{
    "#url"     : "https://www.patreon.com/login",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#fail"    : True,
},

{
    "#url"     : "https://www.patreon.com/search?q=foobar",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#fail"    : True,
},

{
    "#url"     : "https://www.patreon.com/messages/?mode=user&tab=chats",
    "#class"   : patreon.PatreonCreatorExtractor,
    "#fail"    : True,
},

{
    "#url"     : "https://www.patreon.com/home",
    "#class"   : patreon.PatreonUserExtractor,
},

{
    "#url"     : "https://www.patreon.com/posts/precious-metal-23563293",
    "#comment" : "postfile + attachments",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 4,

    "content"  : "<p>+3 outfits ^_^</p>",
    "file"     : {dict, None},
},

{
    "#url"     : "https://www.patreon.com/posts/free-mari-8s-113049301",
    "#comment" : "'This page has been removed' - postfile + attachments_media (#6241)",
    "#class"   : patreon.PatreonPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/posts/56127163",
    "#comment" : "account suspended",
    "#class"   : patreon.PatreonPostExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "tags (#1539)",
    "#class"   : patreon.PatreonPostExtractor,
    "#pattern" : r"https://c10.patreonusercontent.com/4/patreon-media/p/post/12497641/3d99f5f5b635428ca237fedf0f223f1a/eyJhIjoxLCJwIjoxfQ%3D%3D/1\.JPG\?.+",

    "content"  : "<p>AWMedia brought his camera to our night out in LA </p><p><br/></p><p>took a few pics ✨</p><p>patrons comment below why you love pledging to my page! </p>",
    "tags"     : ["AWMedia"],
    "campaign" : {
        "avatar_photo_image_urls": dict,
        "avatar_photo_url": "https://c10.patreonusercontent.com/4/patreon-media/p/campaign/350434/cadc16f03fa1460f9185505b0a858c1b/eyJ3Ijo2MjB9/1.png?token-hash=tpUv_bM0-mEuUSizstb00UrVA-btPS5RyGSCWRx24oc%3D",
        "creation_name": "creating Art Photography/Videography",
        "currency": "USD",
        "current_user_can_be_free_member": True,
        "current_user_is_free_member": False,
        "is_free_membership_paused": False,
        "is_monthly": True,
        "name": "ReedandWeep",
        "offers_free_membership": True,
        "offers_paid_membership": True,
        "pay_per_name": "month",
        "pledge_url": "https://www.patreon.com/checkout/Reedandweep",
        "primary_theme_color": None,
        "show_audio_post_download_links": True,
        "show_free_membership_cta": False,
        "url": "https://www.patreon.com/Reedandweep",
    },

},

{
    "#url"     : "https://www.patreon.com/posts/free-post-12497641",
    "#comment" : "custom image format (#6569)",
    "#class"   : patreon.PatreonPostExtractor,
    "#options" : {"format-images": "thumbnail"},
    "#pattern"     : r"https://c10.patreonusercontent.com/4/patreon-media/p/post/12497641/3d99f5f5b635428ca237fedf0f223f1a/eyJoIjozNjAsInciOjM2MH0%3D/1\.JPG\?.+",
    "#sha1_content": (
        "2967d7567d55debdfa59cfd27cd5edf89d9c3503",
        "190e249295eeca1a8ffbcf1aece788b4f69bbb64",
    ),
},

{
    "#url"     : "https://www.patreon.com/posts/m3u8-94714289",
    "#class"   : patreon.PatreonPostExtractor,
    "#pattern" : [
        r"https://c10\.patreonusercontent\.com/4/patreon-media/p/post/94714289/be3d8eb994ae44eca4baffcdc6dd25fc/eyJhIjoxLCJwIjoxfQ%3D%3D/1\.png",
        r"ytdl:https://stream\.mux\.com/NLrxTLdxyGStpOgapJAtB8uPGAaokEcj8YovML00y2DY\.m3u8\?token=ey",
    ],

    "content": "<p>The year 12,023 of the Human Era is nearing its end – and what a year it has been!  <br/>Thank you for being on this journey with us and sharing our passion for the universe and the world we live in. <br/>We hope you have a wonderful end of the year and an amazing 12,024. <br/>Much love from all of us at kurzgesagt ❤</p>",
},

{
    "#url"     : "https://www.patreon.com/posts/closed-color-139862716",
    "#class"   : patreon.PatreonPostExtractor,

    "content"  : """<p><em>All slots are now filled — thank you so much for your support!</em> 🥰🙏✨</p><p></p><p>Hello everyone!</p><p>Thank you for waiting 🥰 Commissions are now open!</p><p>This time, I’m offering <strong>color sketch commissions</strong>:</p><ul><li><p>One character only</p></li><li><p>No background</p></li><li><p>A bit rougher finish compared to my usual works</p></li><li><p><strong>Pose cannot be revised</strong> (I will provide several pose options, and you may choose from them)</p></li></ul><p></p><p>💲 <strong>Pricing</strong></p><ul><li><p>Thigh-up: $250</p></li><li><p>Full-body: $300</p></li></ul><p></p><p>⏰ <strong>Slots</strong></p><p><s>Limited to 3 slots only (first come, first served)</s></p><p></p><p>📩 <strong>How to Apply</strong></p><p>If you would like to participate, please <strong>switch to the “Color Sketch Commission (Half-body)” plan</strong>.</p><ul><li><p>Half-body: $250</p></li><li><p>For Full-body, please add $50 (for a total of $300) when you join.</p></li></ul><p>After confirming your subscription, please <strong>contact me via Patreon message or Discord DM</strong>.<br/>After that, I will deliver the sketches and the finished illustration <strong>via Discord DM or Dropbox</strong>.</p><p>👉 <strong>Apply here:</strong><br/><a href="https://www.patreon.com/checkout/PI_Art314?rid=26956166" target="_blank"><s>https://www.patreon.com/checkout/PI_Art314?rid=26956166</s></a></p><p></p><p>💡 <strong>Note</strong></p><p>Once your commission is confirmed, you may <strong>cancel the plan afterwards</strong>.<br/>(There is no need to keep paying every month, so please don’t worry.)</p><p>Sexy themes are welcome within the following limits:</p><ul><li><p>❌ No depiction of nipples</p></li><li><p>❌ No genitals or sexual acts</p></li></ul><p></p><p>Other Notes</p><ul><li><p>Commercial use is prohibited.</p></li><li><p>Personal use, such as posting on social media, is permitted.</p></li><li><p>Illustrations created for commissions may be shared on social media and other platforms.</p></li><li><p>Commissioned illustrations may be further modified to create other works.</p></li></ul><p></p><p>I look forward to your requests! 🖌🥰🎨✨</p>""",
},

{
    "#url"     : "https://www.patreon.com/posts/143480584",
    "#class"   : patreon.PatreonPostExtractor,

    "content"  : "<h3>I’m late again, everyone — here are the WIPs for the <strong>second</strong> and <strong>third</strong> October rewards:<br/><strong>Ino Yamanaka</strong> and <strong>Kyoka Jiro</strong> (WIP)</h3><blockquote><p><em>As you can see, there isn’t much time left in November, and I’ll also be traveling with my family for a short trip at the end of the month. Because of that, the November rewards will be paused again, and I will pause the system’s billing for December.</em></p></blockquote><p><u>If you joined in </u><strong><u>November</u></strong><u>, once I finish all of the October rewards, I will upload them to the shop.</u><br/><u>(For a short period, the shop price will match the Patreon tier.)</u></p><p></p><p>I know my time management is terrible — thank you so much to everyone who continues to support me. 💖</p><p></p><p>--------------------------------------------------------------------------------</p><p></p><p>各位我來遲了，這是十月的第二個獎勵與第三個獎勵的WIP 山中井野和耳郎響香(wip)</p><p> *如各位所見，十一月所剩時間不多加上十一月底我要跟家人出去旅行一小段時間，因此十一月獎勵又將暫停一次，我會暫停系統十二月的收款。 如果你是十一月才加入，等我把十月獎勵都完成之後會一起上架至到商店。(上架短時間會與patreon價格相同) </p><p></p><p>我知道我的時間控管很差，謝謝每一位願意支持我的人。</p>",
},

{
    "#url"     : "https://www.patreon.com/posts/not-found-123",
    "#class"   : patreon.PatreonPostExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://www.patreon.com/collection/15764",
    "#class"   : patreon.PatreonCollectionExtractor,
    "#range"   : "1-3",
    "#pattern" : (
        r"https://c10.patreonusercontent.com/4/patreon-media/p/post/32798362/957d49296e4f48ef80718d0de98c15a4/eyJhIjoxLCJwIjoxfQ%3D%3D/2.jpg\?token-hash=.+",
        r"ytdl:https://stream.mux.com/h4DYqFU901qkkAwYmRWZPraVk5DvTJTlcSdhGV00006KBE.m3u8\?token=ey.+",
        r"https://c10.patreonusercontent.com/4/patreon-media/p/post/32798374/357b0133a476427a99169b4400ee03d4/eyJhIjoxLCJwIjoxfQ%3D%3D/2.jpg\?token-hash=.+",
    ),

    "campaign"        : {
        "currency"        : "USD",
        "is_monthly"      : True,
        "is_nsfw"         : False,
        "name"            : "YaBoyRoshi",
    },
    "collection"      : {
        "created_at"     : "2023-08-31T14:10:41.000+00:00",
        "date"           : "dt:2023-08-31 14:10:41",
        "default_layout" : "grid",
        "description"    : "",
        "edited_at"      : "2025-07-16T22:58:10.834+00:00",
        "id"             : "15764",
        "num_draft_posts": 0,
        "num_posts"      : 207,
        "num_posts_visible_for_creation": 207,
        "num_scheduled_posts": 8,
        "post_sort_type" : "custom",
        "title"          : "JoJo's Bizarre Adventure",
        "post_ids"       : list,
        "thumbnail"      : dict,
    },
    "creator"         : {
        "date"      : "dt:2018-10-17 05:45:19",
        "first_name": "YaBoyRoshi",
        "full_name" : "YaBoyRoshi",
        "id"        : "14264111",
        "vanity"    : "yaboyroshi",
    },
},

)
