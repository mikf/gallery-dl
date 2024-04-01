# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import reddit


__tests__ = (
{
    "#url"     : "https://www.reddit.com/r/lavaporn/",
    "#category": ("", "reddit", "subreddit"),
    "#class"   : reddit.RedditSubredditExtractor,
    "#range"   : "1-20",
    "#count"   : ">= 20",
},

{
    "#url"     : "https://www.reddit.com/r/lavaporn/top/?sort=top&t=month",
    "#category": ("", "reddit", "subreddit-top"),
    "#class"   : reddit.RedditSubredditExtractor,
},

{
    "#url"     : "https://old.reddit.com/r/lavaporn/",
    "#category": ("", "reddit", "subreddit"),
    "#class"   : reddit.RedditSubredditExtractor,
},

{
    "#url"     : "https://np.reddit.com/r/lavaporn/",
    "#category": ("", "reddit", "subreddit"),
    "#class"   : reddit.RedditSubredditExtractor,
},

{
    "#url"     : "https://m.reddit.com/r/lavaporn/",
    "#category": ("", "reddit", "subreddit"),
    "#class"   : reddit.RedditSubredditExtractor,
},

{
    "#url"     : "https://www.reddit.com/",
    "#category": ("", "reddit", "home"),
    "#class"   : reddit.RedditHomeExtractor,
    "#range"   : "1-20",
    "#count"   : ">= 20",
    "#archive" : False,
},

{
    "#url"     : "https://old.reddit.com/top/?sort=top&t=month",
    "#category": ("", "reddit", "home-top"),
    "#class"   : reddit.RedditHomeExtractor,
},

{
    "#url"     : "https://www.reddit.com/user/username/",
    "#category": ("", "reddit", "user"),
    "#class"   : reddit.RedditUserExtractor,
    "#count"   : ">= 2",
},

{
    "#url"     : "https://www.reddit.com/user/username/gilded/?sort=top&t=month",
    "#category": ("", "reddit", "user-gilded"),
    "#class"   : reddit.RedditUserExtractor,
},

{
    "#url"     : "https://old.reddit.com/user/username/",
    "#category": ("", "reddit", "user"),
    "#class"   : reddit.RedditUserExtractor,
},

{
    "#url"     : "https://www.reddit.com/u/username/",
    "#category": ("", "reddit", "user"),
    "#class"   : reddit.RedditUserExtractor,
},

{
    "#url"     : "https://www.reddit.com/r/lavaporn/comments/8cqhub/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#pattern" : r"https://c2.staticflickr.com/8/7272/\w+_k.jpg",
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/r/lavaporn/comments/8cqhub/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#options" : {"comments": 500},
    "#pattern" : "https://",
    "#count"   : 3,
},

{
    "#url"     : "https://www.reddit.com/gallery/hrrh23",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#count"       : 3,
    "#sha1_url"    : "25b91ede15459470274dd17291424b037ed8b0ae",
    "#sha1_content": "1e7dde4ee7d5f4c4b45749abfd15b2dbfa27df3f",
},

{
    "#url"     : "https://www.reddit.com/r/aww/comments/90bu6w/",
    "#comment" : "video (dash)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#pattern" : "ytdl:https://v.redd.it/gyh95hiqc0b11",
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/r/aww/comments/90bu6w/",
    "#comment" : "video (dash)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#options" : {"videos": "ytdl"},
    "#pattern" : "ytdl:https://www.reddit.com/r/aww/comments/90bu6w/heat_index_was_110_degrees_so_we_offered_him_a/",
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/r/aww/comments/90bu6w/",
    "#comment" : "video (dash)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#options" : {"videos": "dash"},
    "#pattern" : r"ytdl:https://v.redd.it/gyh95hiqc0b11/DASHPlaylist.mpd\?a=",
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/gallery/icfgzv",
    "#comment" : "deleted gallery (#953)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.reddit.com/r/araragi/comments/ib32hm",
    "#comment" : "animated gallery items (#955)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#pattern" : r"https://i\.redd\.it/\w+\.gif",
    "#count"   : 2,
},

{
    "#url"     : "https://www.reddit.com/r/cosplay/comments/jvwaqr",
    "#comment" : "'failed' gallery item (#1127)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/r/kpopfap/comments/qjj04q/",
    "#comment" : "gallery with no 'media_metadata' (#2001)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://www.reddit.com/r/RobloxArt/comments/15ko0qu/",
    "#comment" : "comment embeds (#5366)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#options" : {"comments": 10},
    "#urls"    : (
        "https://i.redd.it/ppt5yciyipgb1.jpg",
        "https://i.redd.it/u0ojzd69kpgb1.png",
    ),
},

{
    "#url"     : "https://www.reddit.com/user/TheSpiritTree/comments/srilyf/",
    "#comment" : "user page submission (#2301)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#pattern" : "https://i.redd.it/8fpgv17yqlh81.jpg",
    "#count"   : 1,
},

{
    "#url"     : "https://www.reddit.com/r/kittengifs/comments/12m0b8d",
    "#comment" : "cross-posted video (#887, #3586, #3976)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#pattern" : r"ytdl:https://v\.redd\.it/cvabpjacrvta1",
},

{
    "#url"     : "https://www.reddit.com/r/europe/comments/pm4531/the_name_of/",
    "#comment" : "preview.redd.it (#4470)",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
    "#urls"    : "https://preview.redd.it/u9ud4k6xaf271.jpg?auto=webp&s=19b1334cb4409111cda136c01f7b44c2c42bf9fb",
},

{
    "#url"     : "https://old.reddit.com/r/lavaporn/comments/2a00np/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
},

{
    "#url"     : "https://np.reddit.com/r/lavaporn/comments/2a00np/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
},

{
    "#url"     : "https://m.reddit.com/r/lavaporn/comments/2a00np/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
},

{
    "#url"     : "https://redd.it/2a00np/",
    "#category": ("", "reddit", "submission"),
    "#class"   : reddit.RedditSubmissionExtractor,
},

{
    "#url"     : "https://i.redd.it/upjtjcx2npzz.jpg",
    "#category": ("", "reddit", "image"),
    "#class"   : reddit.RedditImageExtractor,
    "#sha1_url"    : "0de614900feef103e580b632190458c0b62b641a",
    "#sha1_content": "cc9a68cf286708d5ce23c68e79cd9cf7826db6a3",
},

{
    "#url"     : "https://i.reddituploads.com/0f44f1b1fca2461f957c713d9592617d?fit=max&h=1536&w=1536&s=e96ce7846b3c8e1f921d2ce2671fb5e2",
    "#category": ("", "reddit", "image"),
    "#class"   : reddit.RedditImageExtractor,
    "#sha1_url"    : "f24f25efcedaddeec802e46c60d77ef975dc52a5",
    "#sha1_content": "541dbcc3ad77aa01ee21ca49843c5e382371fae7",
},

{
    "#url"     : "https://preview.redd.it/00af44lpn0u51.jpg?width=960&crop=smart&auto=webp&v=enabled&s=dbca8ab84033f4a433772d9c15dbe0429c74e8ac",
    "#comment" : "preview.redd.it -> i.redd.it",
    "#category": ("", "reddit", "image"),
    "#class"   : reddit.RedditImageExtractor,
    "#pattern" : r"^https://i\.redd\.it/00af44lpn0u51\.jpg$",
},

{
    "#url"     : "https://www.reddit.com/r/analog/s/hKrTTvFVwZ",
    "#comment" : "Mobile share URL",
    "#category": ("", "reddit", "redirect"),
    "#class"   : reddit.RedditRedirectExtractor,
    "#pattern" : r"^https://www\.reddit\.com/r/analog/comments/179exao/photographing_the_recent_annular_eclipse_with_a",
},

)
