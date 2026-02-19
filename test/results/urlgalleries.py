# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import urlgalleries


__tests__ = (
{
    "#url"     : "https://urlgalleries.com/photos2q/7851311/clarice-window-8/",
    "#comment" : "'legacy' gallery",
    "#class"   : urlgalleries.UrlgalleriesGalleryExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://fappic.com/x207mqkn2463/4gq1yv.jpg",
        "https://fappic.com/q684ua2rp0j9/4gq1xv.jpg",
        "https://fappic.com/8vf3n8fgz9po/4gq1ya.jpg",
    ),

    "blog"      : "photos2q",
    "count"     : 39,
    "num"       : range(1, 3),
    "date"      : "dt:2023-12-08 12:59:31",
    "gallery_id": "7851311",
    "title"     : "Clarice window 8",
    "tags"      : [
        "Blondes",
        "Softcore",
        "Teens",
        "Brunettes",
    ],
},

{
    "#url"     : "https://urlgalleries.com/dreamer/7645840",
    "#comment" : "no slug",
    "#class"   : urlgalleries.UrlgalleriesGalleryExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://www.fappic.com/vj7up04ny487/AmourAngels-0001.jpg",
        "https://www.fappic.com/zfgsmpm36iyv/AmourAngels-0002.jpg",
        "https://www.fappic.com/rqpt37rdbwa5/AmourAngels-0003.jpg",
    ),

    "blog"      : "Dreamer",
    "count"     : 105,
    "num"       : range(1, 3),
    "date"      : "dt:2020-03-10 20:17:23",
    "gallery_id": "7645840",
    "title"     : "Angelika - Rustic Charm - AmourAngels 2016-09-27",
    "tags": [
        "Outdoors",
        "Teens",
        "Complete-Sets",
        "Brunettes",
    ],
},

{
    "#url"     : "https://urlgalleries.com/xarchivesx/6722560/caroline/",
    "#comment" : "image host URLs with query parameters (#7888)",
    "#class"   : urlgalleries.UrlgalleriesGalleryExtractor,
    "#range"   : "1-3",
    "#results" : (
        "http://img272.imagevenue.com/img.php?image=63353_qedf2jsd4j_123_376lo.jpg",
        "http://img220.imagevenue.com/img.php?image=63140_hl2kkhv0n4_123_621lo.jpg",
        "http://img217.imagevenue.com/img.php?image=63140_z2edqlkpkz_123_986lo.jpg",
    ),

    "blog"      : "The Archives Blog",
    "count"     : 141,
    "num"       : range(1, 3),
    "date"      : "dt:2016-06-11 12:20:06",
    "gallery_id": "6722560",
    "title"     : "Caroline",
    "tags"      : ["Complete-Sets"],
},

{
    "#url"     : "https://urlgalleries.com/beautiesonearth/7893239/bianca-bell-alluring-smile/",
    "#comment" : "'new-style' gallery",
    "#class"   : urlgalleries.UrlgalleriesGalleryExtractor,
    "#range"   : "1-3",
    "#results" : (
        "https://fappic.com/8w2tgkh73bqw/89nywrd17cru.jpg",
        "https://fappic.com/rc7rvvlqq6tz/8opev82wdj12.jpg",
        "https://fappic.com/61j49l13pc1x/7b3d9bydrsg0.jpg",
    ),

    "blog"      : "Beautiesonearth",
    "count"     : 44,
    "num"       : range(1, 3),
    "date"      : "dt:2026-02-19 05:02:37",
    "gallery_id": "7893239",
    "title"     : "Bianca Bell - Alluring Smile",
    "tags"      : [
        "Blondes",
        "Softcore",
        "Teens",
        "Voyeur",
    ],
},

)
