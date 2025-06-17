# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tiktok

PATTERN = r"https://p1[69]-[^/?#.]+\.tiktokcdn[^/?#.]*\.com/[^/?#]+/\w+~.*\.jpe?g"
PATTERN_WITH_AUDIO = r"(?:" + PATTERN + r"|https://v\d+m?\.tiktokcdn[^/?#.]*\.com/[^?#]+\?[^/?#]+)"
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
    "#url"      : "https://www.tiktok.com/@d4vinefem/photo/7449575367024626974",
    "#comment"  : "/photo/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@d4vinefem/video/7449575367024626974",
    "#comment"  : "/video/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7449575367024626974",
    "#comment"  : "www.tiktokv.com link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/photo/7449701420934122785",
    "#comment"  : "/photo/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/video/7449701420934122785",
    "#comment"  : "/video/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"      : "https://www.tiktokv.com/share/video/7449701420934122785",
    "#comment"  : "www.tiktokv.com link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "audio": False},
},

{
    "#url"       : "https://www.tiktok.com/@ughuwhguweghw/video/1",
    "#comment"   : "deleted post",
    "#category"  : ("", "tiktok", "post"),
    "#class"     : tiktok.TiktokPostExtractor,
    "#options"   : {"videos": False, "audio": False},
    "count"      : 0,
},

{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Video post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#results"  : "ytdl:https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#options"  : {"videos": True, "audio": True},
},

{
    "#url"      : "https://www.tiktok.com/@memezar/photo/7449708266168274208",
    "#comment"  : "Video post as a /photo/ link",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#results"  : "ytdl:https://www.tiktok.com/@memezar/video/7449708266168274208",
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
    "#results"  : "ytdl:https://www.tiktok.com/@/video/7449708266168274208",
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
    "#options"  : {"videos": True, "audio": True, "tiktok-range": "1-10"},
},

{
    "#url"      : "https://www.tiktok.com/@joeysc14/",
    "#comment"  : "Public user profile with no content",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "tiktok-range": "1"},
    "#count"    : 1,
},

)
