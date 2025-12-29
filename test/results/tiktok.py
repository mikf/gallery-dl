# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tiktok

PATTERN = r"https://p1[69]-[^/?#.]+\.tiktokcdn[^/?#.]*\.com/[^/?#]+/\w+~.*\.jpe?g"
PATTERN_WITH_AUDIO = r"(?:" + PATTERN + r"|https://v\d+m?\.tiktokcdn[^/?#.]*\.com/[^?#]+\?[^/?#]+)"
VIDEO_PATTERN = r"https://v1[69]-webapp-prime.tiktok.com/video/tos/[^?#]+\?[^/?#]+"
OLD_VIDEO_PATTERN = r"https://www.tiktok.com/aweme/v1/play/\?[^/?#]+"
COMBINED_VIDEO_PATTERN = r"(?:" + VIDEO_PATTERN + r")|(?:" + OLD_VIDEO_PATTERN + r")"
USER_PATTERN = r"(https://www.tiktok.com/@([\w_.-]+)/video/(\d+)|" + PATTERN + r")"


__tests__ = (
{
    "#url"      : "https://www.tiktok.com/@chillezy/photo/7240568259186019630",
    "#comment"  : "/photo/ link: many photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
    "#comment"  : "/video/ link: many photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7240568259186019630",
    "#comment"  : "www.tiktokv.com link: many photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@hullcity/photo/7557376330036153622",
    "#comment"  : "/photo/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@hullcity/video/7557376330036153622",
    "#comment"  : "/video/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7557376330036153622",
    "#comment"  : "www.tiktokv.com link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@hullcity/photo/7553302113757990166",
    "#comment"  : "/photo/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@hullcity/video/7553302113757990166",
    "#comment"  : "/video/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7553302113757990166",
    "#comment"  : "www.tiktokv.com link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@ughuwhguweghw/video/1",
    "#comment"  : "deleted post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#options"  : {"videos": False, "audio": False},
    "#count"    : 0,
},

{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Video post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : COMBINED_VIDEO_PATTERN,
    "#options"  : {"videos": True, "audio": True},
},

{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Video post (via yt-dlp)",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#results"  : "ytdl:https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#options"  : {"videos": "ytdl", "audio": True},
},

{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "video post cover image",
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : r"https://p19-common-sign-useastred.tiktokcdn-eu.com/tos-useast2a-p-0037-euttp/o4rVzhI1bABhooAaEqtCAYGi6nijIsDib8NGfC~tplv-tiktokx-origin.image\?dr=10395&x-expires=\d+&x-signature=.+",
    "#options"  : {"videos": False, "covers": True},


},

{
    "#url"      : "https://www.tiktok.com/@memezar/photo/7449708266168274208",
    "#comment"  : "Video post as a /photo/ link",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : COMBINED_VIDEO_PATTERN,
    "#options"  : {"videos": True, "audio": True},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7240568259186019630",
    "#comment"  : "www.tiktokv.com link: many photos with audio",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#options"  : {"audio": True},
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#count"    : 17,
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7240568259186019630",
    "#comment"  : "www.tiktokv.com link: many photos with audio disabled",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#options"  : {"audio": False},
    "#pattern"  : PATTERN,
    "#count"    : 16,
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7449708266168274208",
    "#comment"  : "Video post as a share link",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : COMBINED_VIDEO_PATTERN,
    "#options"  : {"videos": True},
},

{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Skipping video post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#results"  : (),
    "#options"  : {"videos": False},
},

{
    "#url"      : "https://www.tiktok.com/@chillezy/photo/7240568259186019630",
    "#comment"  : "/photo/ link: many photos with audio",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True},
},

{
    "#url"      : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
    "#comment"  : "/video/ link: many photos with audio",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True},
},

{
    "#url"      : "https://www.tiktok.com/@/video/7240568259186019630",
    "#class"    : tiktok.TiktokPostExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@veronicaperasso_1/video/7212008840433274118",
    "#comment" : "no 'author' (#8189)",
    "#class"   : tiktok.TiktokPostExtractor,
    "#results" : "ytdl:https://www.tiktok.com/@veronicaperasso_1/video/7212008840433274118",
    "#options" : {"videos": "ytdl"},
},

{
    "#url"      : "https://vm.tiktok.com/ZGdh4WUhr/",
    "#comment"  : "vm.tiktok.com link: many photos",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://vm.tiktok.com/ZGdhVtER2/",
    "#comment"  : "vm.tiktok.com link: single photo",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://vm.tiktok.com/ZGdhVW3cu/",
    "#comment"  : "vm.tiktok.com link: few photos",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://vm.tiktok.com/ZGdht7cjp/",
    "#comment"  : "Video post as a VM link",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://vm.tiktok.com/ZGdh4WUhr/",
    "#comment"  : "vm.tiktok.com link: many photos with audio",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://vt.tiktok.com/ZGdhVtER2",
    "#comment"  : "vt.tiktok.com link: single photo",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://www.tiktok.com/t/ZGdhVtER2//",
    "#comment"  : "www.tiktok.com/t/ link: single photo",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : tiktok.TiktokPostExtractor.pattern,
},

{
    "#url"      : "https://www.tiktok.com/@chillezy",
    "#comment"  : "User profile",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : USER_PATTERN,
    "#count"    : 11,  # 10 posts + 1 avatar
    "#options"  : {"videos": True, "audio": True, "tiktok-range": "1-10"},
},

# order-posts currently has no effect if logged-in cookies aren't used.

# {
#     "#url"      : "https://www.tiktok.com/@chillezy",
#     "#comment"  : "User profile ascending order",
#     "#category" : ("", "tiktok", "user"),
#     "#class"    : tiktok.TiktokUserExtractor,
#     "#results"  : "https://www.tiktok.com/@chillezy/video/7112145009356344622",
#     "#options"  : {"videos": True, "audio": True, "avatar": False, "tiktok-range": "1", "order-posts": "asc"},
# },

# {
#     "#url"      : "https://www.tiktok.com/@chillezy",
#     "#comment"  : "User profile popular order",
#     "#category" : ("", "tiktok", "user"),
#     "#class"    : tiktok.TiktokUserExtractor,
#     "#results"  : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
#     "#options"  : {"videos": True, "audio": True, "avatar": False, "tiktok-range": "1", "order-posts": "popular"},
# },

{
    "#url"      : "https://www.tiktok.com/@chillezy",
    "#comment"  : "User profile via yt-dlp",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : USER_PATTERN,
    "#count"    : 11,  # 10 posts + 1 avatar
    "#options"  : {"videos": True, "audio": True, "tiktok-range": "1-10", "tiktok-user-extractor": "ytdl"},
},

{
    "#url"      : "https://www.tiktok.com/@chillezy",
    "#comment"  : "User profile without avatar",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : USER_PATTERN,
    "#count"    : 10,  # 10 posts
    "#options"  : {"videos": True, "audio": True, "avatar": False, "tiktok-range": "1-10"},
},

{
    "#url"      : "https://www.tiktok.com/@joeysc14/",
    "#comment"  : "Public user profile with no content",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "tiktok-range": "1"},
    "#count"    : 1,  # 1 avatar
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/avatar",
    "#class"   : tiktok.TiktokAvatarExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/posts",
    "#class"   : tiktok.TiktokPostsExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/reposts",
    "#class"   : tiktok.TiktokRepostsExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/stories",
    "#class"   : tiktok.TiktokStoriesExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/likes",
    "#class"   : tiktok.TiktokLikesExtractor,
},

{
    "#url"     : "https://www.tiktok.com/@chillezy/saved",
    "#class"   : tiktok.TiktokSavedExtractor,
},

)
