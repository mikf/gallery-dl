# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import tiktok

PATTERN = r"https://p1[69]-.*\.tiktokcdn.*\.com/.*/[0-9a-fA-F]+~.*\.jpeg"


__tests__ = (
# Test many photos.
{
    "#url"      : "https://www.tiktok.com/@chillezy/photo/7240568259186019630",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://www.tiktok.com/@chillezy/video/7240568259186019630",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://vm.tiktok.com/ZGdh4WUhr/",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN
},
# Test one photo.
{
    "#url"      : "https://www.tiktok.com/@d4vinefem/photo/7449575367024626974",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://www.tiktok.com/@d4vinefem/video/7449575367024626974",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://vm.tiktok.com/ZGdhVtER2/",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN
},
# Test a few photos.
{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/photo/7449701420934122785",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://www.tiktok.com/@.mcfc.central/video/7449701420934122785",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokPostExtractor,
    "#pattern"  : PATTERN
},
{
    "#url"      : "https://vm.tiktok.com/ZGdhVW3cu/",
    "#category" : ("", "tiktok", "post"),
    "#class"    : tiktok.TiktokVmpostExtractor,
    "#pattern"  : PATTERN
}
)
