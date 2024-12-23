# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tiktok
from gallery_dl import exception

PATTERN = r"https://p1[69]-.*\.tiktokcdn.*\.com/.*/[0-9a-fA-F]+~.*\.jpeg"
PATTERN_WITH_AUDIO = r"(?:" + PATTERN + r")|(?:ytdl\:)"


__tests__ = (
{
    "#url"      : "https://www.tiktok.com/@chillezy/photo/7240568259186019630",
    "#comment"  : "/photo/ link: many photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
    "#comment"  : "/video/ link: many photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://vm.tiktok.com/ZGdh4WUhr/",
    "#comment"  : "vm.tiktok.com link: many photos",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@d4vinefem/photo/7449575367024626974",
    "#comment"  : "/photo/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@d4vinefem/video/7449575367024626974",
    "#comment"  : "/video/ link: single photo",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://vm.tiktok.com/ZGdhVtER2/",
    "#comment"  : "vm.tiktok.com link: single photo",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/photo/7449701420934122785",
    "#comment"  : "/photo/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/video/7449701420934122785",
    "#comment"  : "/video/ link: few photos",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://vm.tiktok.com/ZGdhVW3cu/",
    "#comment"  : "vm.tiktok.com link: few photos",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"       : "https://www.tiktok.com/@ughuwhguweghw/video/1",
    "#comment"   : "deleted post",
    "#category"  : ("", "tiktok", "post"),
    "#class"     : tiktok.TiktokPostExtractor,
    "#exception" : exception.NotFoundError,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Video post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://www.tiktok.com/@memezar/photo/7449708266168274208",
    "#comment"  : "Video post as a /photo/ link",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://vm.tiktok.com/ZGdht7cjp/",
    "#comment"  : "Video post as a VM link",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://www.tiktok.com/@memezar/video/7449708266168274208",
    "#comment"  : "Skipping video post",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False}
},
{
    "#url"      : "https://www.tiktok.com/@chillezy/photo/7240568259186019630",
    "#comment"  : "/photo/ link: many photos with audio",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
    "#comment"  : "/video/ link: many photos with audio",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://vm.tiktok.com/ZGdh4WUhr/",
    "#comment"  : "vm.tiktok.com link: many photos with audio",
    "#category" : ("", "tiktok", "vmpost"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True}
},
{
    "#url"      : "https://www.tiktok.com/@chillezy",
    "#comment"  : "User profile",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : PATTERN_WITH_AUDIO,
    "#options"  : {"videos": True, "tiktok-range": "1-10"}
},
{
    "#url"      : "https://www.tiktok.com/@chillezy/",
    "#comment"  : "User profile without audio or videos",
    "#category" : ("", "tiktok", "user"),
    "#class"    : tiktok.TiktokUserExtractor,
    "#pattern"  : PATTERN,
    "#options"  : {"videos": False, "tiktok-range": "1-10"}
},
)
