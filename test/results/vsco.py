# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import vsco


__tests__ = (
{
    "#url"     : "https://vsco.co/missuri/gallery",
    "#category": ("", "vsco", "user"),
    "#class"   : vsco.VscoUserExtractor,
    "#pattern" : r"https://image(-aws.+)?\.vsco\.co/[0-9a-f/]+/[\w-]+\.\w+",
    "#range"   : "1-80",
    "#count"   : 80,
},

{
    "#url"     : "https://vsco.co/missuri/images/1",
    "#category": ("", "vsco", "user"),
    "#class"   : vsco.VscoUserExtractor,
},

{
    "#url"     : "https://vsco.co/missuri",
    "#category": ("", "vsco", "user"),
    "#class"   : vsco.VscoUserExtractor,
},

{
    "#url"     : "https://vsco.co/vsco/collection/1",
    "#category": ("", "vsco", "collection"),
    "#class"   : vsco.VscoCollectionExtractor,
    "#pattern" : r"https://image(-aws.+)?\.vsco\.co/[0-9a-f/]+/[\w\s-]+\.\w+",
    "#range"   : "1-80",
    "#count"   : 80,
},

{
    "#url"     : "https://vsco.co/spaces/6320a3e1e0338d1350b33fea",
    "#category": ("", "vsco", "space"),
    "#class"   : vsco.VscoSpaceExtractor,
    "#pattern" : r"https://image(-aws.+)?\.vsco\.co/[0-9a-f/]+/[\w\s-]+\.\w+",
    "#count"   : range(100, 150),
},

{
    "#url"     : "https://vsco.co/missuri/spaces",
    "#category": ("", "vsco", "spaces"),
    "#class"   : vsco.VscoSpacesExtractor,
    "#urls"    : (
        "https://vsco.co/spaces/62e4934e6920440801d19f05",
    ),
},

{
    "#url"     : "https://vsco.co/erenyildiz/media/5d34b93ef632433030707ce2",
    "#category": ("", "vsco", "image"),
    "#class"   : vsco.VscoImageExtractor,
    "#sha1_url"    : "a45f9712325b42742324b330c348b72477996031",
    "#sha1_content": "1394d070828d82078035f19a92f404557b56b83f",

    "id"         : "5d34b93ef632433030707ce2",
    "user"       : "erenyildiz",
    "grid"       : "erenyildiz",
    "meta"       : dict,
    "tags"       : list,
    "date"       : "dt:2019-07-21 19:12:11",
    "video"      : False,
    "width"      : 1537,
    "height"     : 1537,
    "description": r"re:Ni seviyorum. #vsco #vscox #vscochallenges",
},

{
    "#url"     : "https://vsco.co/jimenalazof/media/5b4feec558f6c45c18c040fd",
    "#category": ("", "vsco", "image"),
    "#class"   : vsco.VscoImageExtractor,
    "#sha1_url"    : "08e7eef3301756ce81206c0b47c1e9373756a74a",
    "#sha1_content": "e739f058d726ee42c51c180a505747972a7dfa47",

    "video": True,
},

)
