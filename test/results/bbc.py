# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import bbc


__tests__ = (
{
    "#url"     : "https://www.bbc.co.uk/programmes/p084qtzs/p085g9kg",
    "#category": ("", "bbc", "gallery"),
    "#class"   : bbc.BbcGalleryExtractor,
    "#pattern" : r"https://ichef\.bbci\.co\.uk/images/ic/1920xn/\w+\.jpg",
    "#count"   : 37,

    "count"      : 37,
    "num"        : range(1, 37),
    "description": "The Cybermen attack. And for the Doctor, nothing will ever be the same.",
    "programme"  : "p084qtzs",
    "synopsis"   : "The Cybermen attack. And for the Doctor, nothing will ever be the same.",
    "title"      : "The Timeless Children",
    "title_image": {"The Timeless Children", ": The Timeless Children"},
    "path"       : [
        "BBC One",
        "Doctor Who (2005–2022)",
        "The Timeless Children",
    ],
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/p086f8yf/p086f8j6",
    "#category": ("", "bbc", "gallery"),
    "#class"   : bbc.BbcGalleryExtractor,
    "#pattern" : r"https://ichef\.bbci\.co\.uk/images/ic/1920xn/\w+\.jpg",
    "#range"   : "1-2",
    "#count"   : 2,

    "count"      : 9,
    "num"        : {1, 2},
    "description": "Continuing his journey, Colin gives unique insights into the unique animals he finds.",
    "extension"  : "jpg",
    "filename"   : {"p086f7yn", "p086f80n"},
    "programme"  : "p086f8yf",
    "title"      : "Wild Cuba: A Caribbean Journey - Part 2",
    "title_image": {
        "Cuba is home to many unique birds",
        "A Cuban pygmy owl looks out of its tree hole",
    },
    "synopsis"   : {
        "This vibrant Cuban tody is just one of more than 300 species of bird found in Cuba.",
        "Cuban pygmy owls nest in abandoned holes carved out by woodpeckers.",
    },
    "path"       : [
        "BBC Two",
        "Natural World",
        "2019-2020",
        "Wild Cuba: A Caribbean Journey - Part 2",
        "Wildlife camera operator Colin Stafford-Johnson has loved Cuba since he was a little boy"
    ],
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/p084qtzs",
    "#category": ("", "bbc", "gallery"),
    "#class"   : bbc.BbcGalleryExtractor,
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/b006q2x0/galleries",
    "#category": ("", "bbc", "programme"),
    "#class"   : bbc.BbcProgrammeExtractor,
    "#pattern" : bbc.BbcGalleryExtractor.pattern,
    "#range"   : "1-50",
    "#count"   : ">= 50",
},

{
    "#url"     : "https://www.bbc.co.uk/programmes/b006q2x0/galleries?page=25",
    "#category": ("", "bbc", "programme"),
    "#class"   : bbc.BbcProgrammeExtractor,
    "#pattern" : bbc.BbcGalleryExtractor.pattern,
    "#count"   : ">= 100",
},

)
