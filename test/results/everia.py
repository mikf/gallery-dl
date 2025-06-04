# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import everia


__tests__ = (
{
    "#url"  : "https://everia.club/2024/09/23/mikacho-조미카-joapictures-someday/",
    "#class": everia.EveriaPostExtractor,
    "#count": 32,

    "title"        : "Mikacho 조미카, JOApictures ‘Someday’",
    "post_category": "Korea",
    "tags"         : ["[JOApictures]", "Mikacho 조미카"],
},

{
    "#url"  : "https://everia.club/2020/12/13/karin-fujiyoshi-%e8%97%a4%e5%90%89%e5%a4%8f%e9%88%b4-rina-matsuda-%e6%9d%be%e7%94%b0%e9%87%8c%e5%a5%88-ex-taishu-2020-no-11-ex%e5%a4%a7%e8%a1%86-2020%e5%b9%b411%e6%9c%88%e5%8f%b7/",
    "#class": everia.EveriaPostExtractor,
    "#count": 21,

    "title"        : "Karin Fujiyoshi 藤吉夏鈴, Rina Matsuda 松田里奈, Ex-Taishu 2020 No.11 (EX大衆 2020年11月号)",
    "post_category": "Uncategorized",
    "tags"         : [
        "Ex-Taishu EX大衆",
        "Karin Fujiyoshi 藤吉夏鈴",
        "Rina Matsuda 松田里奈",
        "Sakurazaka46 櫻坂46",
    ],
},

{
    "#url"  : "https://everia.club/2019/03/26/moeka-yahagi-%e7%9f%a2%e4%bd%9c%e8%90%8c%e5%a4%8f-b-l-t-graph-2019%e5%b9%b403%e6%9c%88%e5%8f%b7-vol-41/",
    "#class": everia.EveriaPostExtractor,
    "#count": 9,

    "title"        : "Moeka Yahagi 矢作萌夏, B.L.T Graph 2019年03月号 Vol.41",
    "post_category": "Uncategorized",
    "tags"         : [
        "AKB48",
        "B.L.T ビー・エル・ティー",
        "Moeka Yahagi 矢作萌夏",
    ],
},

{
    "#url"  : "https://everia.club/2021/03/12/%E9%9B%AF%E5%A6%B9%E4%B8%8D%E8%AE%B2%E9%81%93%E7%90%86-dido-%E3%83%80%E3%82%A4%E3%83%89%E3%83%BC-azur-lane-%E7%A2%A7%E8%93%9D%E8%88%AA%E7%BA%BF/",
    "#class": everia.EveriaPostExtractor,
    "#pattern": r"https://1.bp.blogspot.com/-\S+/\S+/\S+/\S+/s0/(%\w\w|\d|\+)+\.jpg",
    "#count"  : 17,

    "count"    : 17,
    "num"      : range(1, 17),
    "extension": "jpg",
    "filename" : r"re:雯妹不讲道理\+\(\d+\)",
    "title"    : "[雯妹不讲道理] Dido ダイドー (Azur Lane 碧蓝航线)",
    "post_url" : "https://everia.club/2021/03/12/雯妹不讲道理-dido-ダイドー-azur-lane-碧蓝航线/",
    "post_category": "Cosplay",
    "tags": [
        "Cosplay",
        "雯妹不讲道理",
    ],
},

{
    "#url"    : "https://everia.club/tag/miku-tanaka-%e7%94%b0%e4%b8%ad%e7%be%8e%e4%b9%85/",
    "#class"  : everia.EveriaTagExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#count"  : "> 50",
},

{
    "#url"    : "https://everia.club/category/japan/",
    "#class"  : everia.EveriaCategoryExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#range"  : "1-50",
    "#count"  : 50,
},

{
    "#url"    : "https://everia.club/2023/10/05/",
    "#class"  : everia.EveriaDateExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#count"  : 34,
},

{
    "#url"    : "https://everia.club/?s=saika",
    "#class"  : everia.EveriaSearchExtractor,
    "#pattern": everia.EveriaPostExtractor.pattern,
    "#range"  : "1-15",
    "#count"  : 15,
},

)
