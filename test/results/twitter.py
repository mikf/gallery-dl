# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import twitter
from gallery_dl import util, exception


__tests__ = (
{
    "#url"     : "https://twitter.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
    "#options" : {"include": "all"},
    "#results" : (
        "https://x.com/supernaturepics/info",
        "https://x.com/supernaturepics/photo",
        "https://x.com/supernaturepics/header_photo",
        "https://x.com/supernaturepics/timeline",
        "https://x.com/supernaturepics/tweets",
        "https://x.com/supernaturepics/media",
        "https://x.com/supernaturepics/with_replies",
        "https://x.com/supernaturepics/likes",
    ),
},

{
    "#url"     : "https://mobile.twitter.com/supernaturepics?p=i",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://twitter.com/i/user/2976459548",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://twitter.com/intent/user?user_id=2976459548",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://fxtwitter.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://vxtwitter.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://fixupx.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://fixvx.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://x.com/supernaturepics",
    "#category": ("", "twitter", "user"),
    "#class"   : twitter.TwitterUserExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/timeline",
    "#category": ("", "twitter", "timeline"),
    "#class"   : twitter.TwitterTimelineExtractor,
    "#range"   : "1-40",
    "#sha1_url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",

    "author": {
        "date"            : "dt:2015-01-12 10:25:22",
        "description"     : "The very best nature pictures.",
        "favourites_count": int,
        "followers_count" : int,
        "friends_count"   : int,
        "listed_count"    : int,
        "media_count"     : int,
        "statuses_count"  : int,
        "id"              : 2976459548,
        "location"        : "Earth",
        "name"            : "supernaturepics",
        "nick"            : "Nature Pictures",
        "profile_banner"  : "https://pbs.twimg.com/profile_banners/2976459548/1421058583",
        "profile_image"   : "https://pbs.twimg.com/profile_images/554585280938659841/FLVAlX18.jpeg",
        "protected"       : False,
        "verified"        : False,
    },
    "user": {
        "date"            : "dt:2015-01-12 10:25:22",
        "description"     : "The very best nature pictures.",
        "favourites_count": int,
        "followers_count" : int,
        "friends_count"   : int,
        "listed_count"    : int,
        "media_count"     : int,
        "statuses_count"  : int,
        "id"              : 2976459548,
        "location"        : "Earth",
        "name"            : "supernaturepics",
        "nick"            : "Nature Pictures",
        "profile_banner"  : "https://pbs.twimg.com/profile_banners/2976459548/1421058583",
        "profile_image"   : "https://pbs.twimg.com/profile_images/554585280938659841/FLVAlX18.jpeg",
        "protected"       : False,
        "verified"        : False,
    },
    "tweet_id"       : range(400000000000000000, 800000000000000000),
    "conversation_id": range(400000000000000000, 800000000000000000),
    "quote_id"       : 0,
    "reply_id"       : 0,
    "retweet_id"     : 0,
    "count"          : range(1, 4),
    "num"            : range(1, 4),
    "favorite_count" : int,
    "quote_count"    : int,
    "reply_count"    : int,
    "retweet_count"  : int,
    "content"        : str,
    "lang"           : str,
    "date"           : "type:datetime",
    "sensitive"      : False,
    "source"         : "nature_pics",
},

{
    "#url"     : "https://twitter.com/OptionalTypo/timeline",
    "#comment" : "suspended account (#2216)",
    "#category": ("", "twitter", "timeline"),
    "#class"   : twitter.TwitterTimelineExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://twitter.com/id:772949683521978368/timeline",
    "#comment" : "suspended account user ID",
    "#category": ("", "twitter", "timeline"),
    "#class"   : twitter.TwitterTimelineExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://mobile.twitter.com/supernaturepics/timeline#t",
    "#category": ("", "twitter", "timeline"),
    "#class"   : twitter.TwitterTimelineExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548/timeline",
    "#category": ("", "twitter", "timeline"),
    "#class"   : twitter.TwitterTimelineExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/tweets",
    "#category": ("", "twitter", "tweets"),
    "#class"   : twitter.TwitterTweetsExtractor,
    "#range"   : "1-40",
    "#sha1_url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
},

{
    "#url"     : "https://mobile.twitter.com/supernaturepics/tweets#t",
    "#category": ("", "twitter", "tweets"),
    "#class"   : twitter.TwitterTweetsExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548/tweets",
    "#category": ("", "twitter", "tweets"),
    "#class"   : twitter.TwitterTweetsExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/with_replies",
    "#category": ("", "twitter", "replies"),
    "#class"   : twitter.TwitterRepliesExtractor,
    "#range"   : "1-40",
    "#sha1_url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
},

{
    "#url"     : "https://mobile.twitter.com/supernaturepics/with_replies#t",
    "#category": ("", "twitter", "replies"),
    "#class"   : twitter.TwitterRepliesExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548/with_replies",
    "#category": ("", "twitter", "replies"),
    "#class"   : twitter.TwitterRepliesExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/media",
    "#category": ("", "twitter", "media"),
    "#class"   : twitter.TwitterMediaExtractor,
    "#range"   : "1-40",
    "#sha1_url": "c570ac1aae38ed1463be726cc46f31cac3d82a40",
},

{
    "#url"     : "https://mobile.twitter.com/supernaturepics/media#t",
    "#category": ("", "twitter", "media"),
    "#class"   : twitter.TwitterMediaExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548/media",
    "#category": ("", "twitter", "media"),
    "#class"   : twitter.TwitterMediaExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/likes",
    "#category": ("", "twitter", "likes"),
    "#class"   : twitter.TwitterLikesExtractor,
},

{
    "#url"     : "https://twitter.com/i/bookmarks",
    "#category": ("", "twitter", "bookmark"),
    "#class"   : twitter.TwitterBookmarkExtractor,
},

{
    "#url"     : "https://twitter.com/i/lists/784214683683127296",
    "#category": ("", "twitter", "list"),
    "#class"   : twitter.TwitterListExtractor,
    "#range"   : "1-40",
    "#count"   : 40,
    "#archive" : False,
},

{
    "#url"     : "https://twitter.com/i/lists/784214683683127296/members",
    "#category": ("", "twitter", "list-members"),
    "#class"   : twitter.TwitterListMembersExtractor,
    "#pattern" : twitter.TwitterUserExtractor.pattern,
    "#range"   : "1-40",
    "#count"   : 40,
},

{
    "#url"     : "https://twitter.com/supernaturepics/following",
    "#category": ("", "twitter", "following"),
    "#class"   : twitter.TwitterFollowingExtractor,
},

{
    "#url"     : "https://www.twitter.com/id:2976459548/following",
    "#category": ("", "twitter", "following"),
    "#class"   : twitter.TwitterFollowingExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/followers",
    "#category": ("", "twitter", "followers"),
    "#class"   : twitter.TwitterFollowersExtractor,
},

{
    "#url"     : "https://twitter.com/search?q=nature",
    "#category": ("", "twitter", "search"),
    "#class"   : twitter.TwitterSearchExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
    "#archive" : False,
},

{
    "#url"     : "https://twitter.com/hashtag/nature",
    "#category": ("", "twitter", "hashtag"),
    "#class"   : twitter.TwitterHashtagExtractor,
    "#pattern" : twitter.TwitterSearchExtractor.pattern,
    "#results" : "https://x.com/search?q=%23nature",
},

{
    "#url"     : "https://twitter.com/i/events/1484669206993903616",
    "#category": ("", "twitter", "event"),
    "#class"   : twitter.TwitterEventExtractor,
    "#range"   : "1-20",
    "#count"   : ">=1",
},

{
    "#url"     : "https://twitter.com/i/communities",
    "#category": ("", "twitter", "communities"),
    "#class"   : twitter.TwitterCommunitiesExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://twitter.com/i/communities/1651515740753735697",
    "#category": ("", "twitter", "community"),
    "#class"   : twitter.TwitterCommunityExtractor,
    "#range"   : "1-20",
    "#count"   : 20,
},

{
    "#url"     : "https://twitter.com/supernaturepics/status/604341487988576256",
    "#comment" : "all Tweets from a 'conversation' (#1319)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#sha1_url"    : "88a40f7d25529c2501c46f2218f9e0de9aa634b4",
    "#sha1_content": "ab05e1d8d21f8d43496df284d31e8b362cd3bcab",
},

{
    "#url"     : "https://twitter.com/perrypumas/status/894001459754180609",
    "#comment" : "4 images",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#sha1_url": "3a2a43dc5fb79dd5432c701d8e55e87c4e551f47",

    "type"        : "photo",
    "source_id"   : 0,
    "!source_user": dict,
},

{
    "#url"     : "https://twitter.com/perrypumas/status/1065692031626829824?s=20",
    "#comment" : "video",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#pattern" : r"https://video.twimg.com/ext_tw_video/.+\.mp4\?tag=5",

    "type": "video",
},

{
    "#url"     : "https://x.com/GrimboGrim/status/1839019491835129889",
    "#comment" : "animated GIF",
    "#class"   : twitter.TwitterTweetExtractor,
    "#results" : "https://video.twimg.com/tweet_video/GYWCeZAaMAQ32uh.mp4",

    "extension": "mp4",
    "type"     : "animated_gif",
},

{
    "#url"     : "https://x.com/carrotsprout_/status/1577924293023133696",
    "#comment" : "mixed image & video",
    "#class"   : twitter.TwitterTweetExtractor,
    "#results" : (
        "https://pbs.twimg.com/media/FeXpxOyaYAA9L88?format=jpg&name=orig",
        "https://video.twimg.com/ext_tw_video/1577924276447248386/pu/vid/720x800/kNsjUvJ5knrSx5WM.mp4?tag=12",
    ),
},

{
    "#url"     : "https://x.com/gopherfootball/status/1950259395432239395",
    "#comment" : "mixed images & video; 'videos' disabled (#7932)",
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"videos": False},
    "#results" : (
        "https://pbs.twimg.com/media/GxC2eRJWAAAH_NM?format=jpg&name=orig",
        "https://pbs.twimg.com/media/GxC2eRAWoAA8gGQ?format=jpg&name=orig",
    ),
},

{
    "#url"     : "https://twitter.com/playpokemon/status/1263832915173048321/",
    "#comment" : "content with emoji, newlines, hashtags (#338)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,

    "source" : "Sprinklr",
    "content": r"""re:Gear up for #PokemonSwordShieldEX with special Mystery Gifts! \n
You’ll be able to receive four Galarian form Pokémon with Hidden Abilities, plus some very useful items. It’s our \(Mystery\) Gift to you, Trainers! \n
❓🎁➡️ """,
},

{
    "#url"     : "https://twitter.com/i/web/status/1170041925560258560",
    "#comment" : "'replies' option (#705)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#pattern" : "https://pbs.twimg.com/media/EDzS7VrU0AAFL4_",
},

{
    "#url"     : "https://twitter.com/i/web/status/1170041925560258560",
    "#comment" : "'replies' option (#705)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"replies": False},
    "#count"   : 0,
},

{
    "#url"     : "https://twitter.com/i/web/status/1424882930803908612",
    "#comment" : "'replies' to self (#1254)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"replies": "self"},
    "#count"   : 4,

    "user": {
        "description": r"re:business email-- rhettaro.bloom@gmail.com patreon- http://patreon.com/Princecanary",
        "url"        : "http://princecanary.tumblr.com",
    },
},

{
    "#url"     : "https://twitter.com/i/web/status/1424898916156284928",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"replies": "self"},
    "#count"   : 1,
},

{
    "#url"     : "https://twitter.com/StobiesGalaxy/status/1270755918330896395",
    "#comment" : "quoted tweet (#526, #854)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"quoted": True},
    "#pattern" : r"https://pbs\.twimg\.com/media/Ea[KG].+=jpg",
    "#count"   : 8,
},

{
    "#url"     : "https://twitter.com/StobiesGalaxy/status/1270755918330896395",
    "#comment" : "quoted tweet (#526, #854)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#pattern" : r"https://pbs\.twimg\.com/media/EaK.+=jpg",
    "#count"   : 4,
},

{
    "#url"     : "https://twitter.com/web/status/1644907989109751810",
    "#comment" : "different 'user' and 'author' in quoted Tweet (#3922)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,

    "author": {
        "id"  : 321629993,
        "name": "Cakes_Comics",
    },
    "user"  : {
        "id"  : 718928225360080897,
        "name": "StobiesGalaxy",
    },
},

{
    "#url"     : "https://twitter.com/i/web/status/112900228289540096",
    "#comment" : "TwitPic embeds (#579)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {
        "twitpic": True,
        "cards"  : False,
    },
    "#pattern" : r"https://\w+.cloudfront.net/photos/large/\d+.jpg",
    "#count"   : 2,
},

{
    "#url"     : "https://twitter.com/shimoigusaP/status/8138669971",
    "#comment" : "TwitPic URL not in 'urls' (#3792)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"twitpic": True},
    "#pattern" : r"https://\w+.cloudfront.net/photos/large/\d+.png",
    "#count"   : 1,
},

{
    "#url"     : "https://twitter.com/billboard/status/1306599586602135555",
    "#comment" : "Twitter card (#1005)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#pattern" : r"https://pbs.twimg.com/card_img/\d+/",
},

{
    "#url"     : "https://twitter.com/i/web/status/1561674543323910144",
    "#comment" : "unified_card image_website (#2875)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#pattern" : r"https://pbs\.twimg\.com/media/F.+=jpg",
},

{
    "#url"     : "https://twitter.com/doax_vv_staff/status/1479438945662685184",
    "#comment" : "unified_card image_carousel_website",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#pattern" : r"https://pbs\.twimg\.com/media/F.+=png",
    "#count"   : 6,
},

{
    "#url"     : "https://twitter.com/bang_dream_1242/status/1561548715348746241",
    "#comment" : "unified_card video_website (#2875)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#pattern" : r"https://video\.twimg\.com/amplify_video/1560607284333449216/vid/720x720/\w+\.mp4",
},

{
    "#url"     : "https://twitter.com/i/web/status/1466183847628865544",
    "#comment" : "unified_card without type",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://twitter.com/i/web/status/1571141912295243776",
    "#comment" : "'cards-blacklist' option",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {
        "cards"          : "ytdl",
        "cards-blacklist": ("twitch.tv",),
    },
    "#count"   : 0,
},

{
    "#url"     : "https://twitter.com/jessica_3978/status/1296304589591810048",
    "#comment" : "original retweets (#1026)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"retweets": True},
    "#count"   : 2,

    "tweet_id"     : 1296304589591810048,
    "retweet_id"   : 1296296016002547713,
    "date"         : "dt:2020-08-20 04:34:32",
    "date_original": "dt:2020-08-20 04:00:28",
},

{
    "#url"     : "https://twitter.com/jessica_3978/status/1296304589591810048",
    "#comment" : "original retweets (#1026)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"retweets": "original"},
    "#count"   : 2,

    "tweet_id"     : 1296296016002547713,
    "retweet_id"   : 1296296016002547713,
    "date"         : "dt:2020-08-20 04:00:28",
    "date_original": "dt:2020-08-20 04:00:28",
},

{
    "#url"     : "https://twitter.com/supernaturepics/status/604341487988576256",
    "#comment" : "all Tweets from a 'conversation' (#1319)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"conversations": True},
    "#count"   : 5,
},

{
    "#url"     : "https://twitter.com/supernaturepics/status/604341487988576256/photo/1",
    "#comment" : "/photo/ URL (#5443)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
},

{
    "#url"     : "https://twitter.com/perrypumas/status/1065692031626829824/video/1",
    "#comment" : "/video/ URL",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
},

{
    "#url"     : "https://twitter.com/morino_ya/status/1392763691599237121",
    "#comment" : "retweet with missing media entities (#1555)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"retweets": True},
    "#count"   : 4,
},

{
    "#url"     : "https://twitter.com/i/web/status/1460044411165888515",
    "#comment" : "deleted quote tweet (#2225)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://twitter.com/i/web/status/1486373748911575046",
    "#comment" : "'Misleading' content",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#count"   : 4,
},

{
    "#url"     : "https://twitter.com/mightbecursed/status/1492954264909479936",
    "#comment" : "age-restricted (#2354)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#auth"     : False,
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://twitter.com/my0nruri/status/1528379296041299968",
    "#comment" : "media alt texts / descriptions (#2617)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,

    "description": "oc",
    "type"       : "photo",
},

{
    "#url"     : "https://twitter.com/poco_dandy/status/1150646424461176832",
    "#comment" : "'?format=...&name=...'-style URLs",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#pattern" : r"https://pbs.twimg.com/card_img/17\d+/[\w-]+\?format=(jpg|png)&name=orig$",
    "#range"   : "1,3",
},

{
    "#url"     : "https://twitter.com/i/web/status/1629193457112686592",
    "#comment" : "note tweet with long 'content'",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,

    "content": """BREAKING - DEADLY LIES: Independent researchers at Texas A&M University have just contradicted federal government regulators, saying that toxic air pollutants in East Palestine, Ohio, could pose long-term risks. \n
The Washington Post writes, "Three weeks after the toxic train derailment in Ohio, an analysis of Environmental Protection Agency data has found nine air pollutants at levels that could raise long-term health concerns in and around East Palestine, according to an independent analysis. \n
"The analysis by Texas A&M University seems to contradict statements by state and federal regulators that air near the crash site is completely safe, despite residents complaining about rashes, breathing problems and other health effects." Your reaction.""",
},

{
    "#url"     : "https://twitter.com/KrisKobach1787/status/1765935595702919299",
    "#comment" : "'birdwatch' note (#5317)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"text-tweets": True},

    "birdwatch": "In addition to the known harm of lead exposure, especially to children, Mr. Kobach is incorrect when he states the mandate is unfunded. In fact, the BIPARTISAN Infrastructure Law Joe Biden signed into law in Nov 2021 provides $15B toward lead service line replacement projects. epa.gov/ground-water-a…",
    "content"  : "Biden wants to replace lead pipes. He failed to mention that the unfunded mandate sets an almost impossible timeline, will cost billions, infringe on the rights of the States and their residents – all for benefits that may be entirely speculative. #sotu https://ag.ks.gov/media-center/news-releases/2024/02/09/kobach-leads-coalition-demanding-biden-drop-unnecessary-epa-rule",
},

{
    "#url"     : "https://x.com/jsports_motor/status/1801338077618524583",
    "#comment" : "geo-restricted video (#5736)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://x.com/fw_rion_/status/1866737025824829544",
    "#comment" : "grok share (#7040)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#options" : {"cards": True},
    "#results" : "https://pbs.twimg.com/grok-img-share/1866736156786008064.jpg",
},

{
    "#url"     : "https://x.com/gdldev/status/1932109706354733077",
    "#comment" : "'source_id' and 'source_user' metadata (#7470, #7640)",
    "#category": ("", "twitter", "tweet"),
    "#class"   : twitter.TwitterTweetExtractor,
    "#results" : (
        "https://video.twimg.com/amplify_video/1932079443264376832/vid/avc1/640x336/7xo7NCPkMLRWb8NZ.mp4?tag=14",
        "https://video.twimg.com/ext_tw_video/1930425322333229056/pu/vid/avc1/1024x576/6f_cdEPY3a5CcbZP.mp4?tag=12",
    ),

    "source_id"  : {1932079546590982508, 1930425346404274416},
    "source_user": {
        "name": {"Satorin69", "Derlan144p_"},
    },
},

{
    "#url"     : "https://twitter.com/playpokemon/status/1263832915173048321/quotes",
    "#category": ("", "twitter", "quotes"),
    "#class"   : twitter.TwitterQuotesExtractor,
    "#pattern" : twitter.TwitterSearchExtractor.pattern,
    "#results" : "https://x.com/search?q=quoted_tweet_id:1263832915173048321",
},

{
    "#url"     : "https://twitter.com/supernaturepics/info",
    "#category": ("", "twitter", "info"),
    "#class"   : twitter.TwitterInfoExtractor,
},

{
    "#url"     : "https://twitter.com/supernaturepics/photo",
    "#category": ("", "twitter", "avatar"),
    "#class"   : twitter.TwitterAvatarExtractor,
    "#results" : "https://pbs.twimg.com/profile_images/554585280938659841/FLVAlX18.jpeg",

    "date"     : "dt:2015-01-12 10:26:49",
    "extension": "jpeg",
    "filename" : "FLVAlX18",
    "tweet_id" : 554585280938659841,
},

{
    "#url"     : "https://twitter.com/User16/photo",
    "#category": ("", "twitter", "avatar"),
    "#class"   : twitter.TwitterAvatarExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://twitter.com/i_n_u/photo",
    "#comment" : "old avatar with small ID and no valid 'date' (#4696)",
    "#category": ("", "twitter", "avatar"),
    "#class"   : twitter.TwitterAvatarExtractor,
    "#results" : "https://pbs.twimg.com/profile_images/2946444489/32028c6affdab425e037ff5a6bf77c1d.jpeg",

    "date"     : util.NONE,
    "tweet_id" : 2946444489,
},

{
    "#url"     : "https://twitter.com/supernaturepics/header_photo",
    "#category": ("", "twitter", "background"),
    "#class"   : twitter.TwitterBackgroundExtractor,
    "#pattern" : r"https://pbs\.twimg\.com/profile_banners/2976459548/1421058583",

    "date"    : "dt:2015-01-12 10:29:43",
    "filename": "1421058583",
    "tweet_id": 554586009367478272,
},

{
    "#url"     : "https://twitter.com/User16/header_photo",
    "#category": ("", "twitter", "background"),
    "#class"   : twitter.TwitterBackgroundExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://pbs.twimg.com/media/EqcpviCVoAAG-QG?format=jpg&name=orig",
    "#category": ("", "twitter", "image"),
    "#class"   : twitter.TwitterImageExtractor,
    "#options" : {"size": "4096x4096,orig"},
    "#sha1_url": "cb3042a6f6826923da98f0d2b66c427e9385114c",
},

{
    "#url"     : "https://pbs.twimg.com/media/EqcpviCVoAAG-QG.jpg:orig",
    "#category": ("", "twitter", "image"),
    "#class"   : twitter.TwitterImageExtractor,
},

{
    "#url"     : "https://x.com/tetsuoai/highlights",
    "#class"   : twitter.TwitterHighlightsExtractor,
},

{
    "#url"     : "https://x.com/home",
    "#class"   : twitter.TwitterHomeExtractor,
},

{
    "#url"     : "https://x.com/home/for_you",
    "#class"   : twitter.TwitterHomeExtractor,
},

{
    "#url"     : "https://x.com/home/following",
    "#class"   : twitter.TwitterHomeExtractor,
},

{
    "#url"     : "https://x.com/notifications",
    "#class"   : twitter.TwitterNotificationsExtractor,
},

{
    "#url"     : "https://x.com/i/timeline",
    "#class"   : twitter.TwitterNotificationsExtractor,
},

)
