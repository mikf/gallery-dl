# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import paheal


__tests__ = (
{
    "#url"     : "https://rule34.paheal.net/post/list/Ayane_Suzuki/1",
    "#category": ("shimmie2", "paheal", "tag"),
    "#class"   : paheal.PahealTagExtractor,
    "#pattern" : r"https://[^.]+\.paheal\.net/_images/\w+/\d+%20-%20|https://r34i\.paheal-cdn\.net/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}$",
    "#count"   : range(70, 200),

    "date"     : "type:datetime",
    "extension": r"re:jpg|png",
    "filename" : r"re:\d+ - \w+",
    "duration" : float,
    "height"   : int,
    "id"       : int,
    "md5"      : r"re:[0-9a-f]{32}",
    "search_tags": "Ayane_Suzuki",
    "size"     : int,
    "tags"     : str,
    "width"    : int,

},

{
    "#url"     : "https://rule34.paheal.net/post/list/Ayane_Suzuki/1",
    "#category": ("shimmie2", "paheal", "tag"),
    "#class"   : paheal.PahealTagExtractor,
    "#options" : {"metadata": True},
    "#range"   : "1",

    "date"       : "dt:2018-01-07 07:04:05",
    "duration"   : 0.0,
    "extension"  : "jpg",
    "filename"   : "2446128 - Ayane_Suzuki Idolmaster idolmaster_dearly_stars Zanzi",
    "height"     : 768,
    "id"         : 2446128,
    "md5"        : "b0ceda9d860df1d15b60293a7eb465c1",
    "search_tags": "Ayane_Suzuki",
    "size"       : 204800,
    "source"     : "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=19957280",
    "tags"       : "Ayane_Suzuki Idolmaster idolmaster_dearly_stars Zanzi",
    "uploader"   : "XXXname",
    "width"      : 1024,
},

{
    "#url"     : "https://rule34.paheal.net/post/list/Ranma_1%2F2/1",
    "#comment" : "percent-encoded character in tag (#7642)",
    "#category": ("shimmie2", "paheal", "tag"),
    "#class"   : paheal.PahealTagExtractor,
    "#range"   : "1-200",
    "#count"   : 200,
},

{
    "#url"     : "https://rule34.paheal.net/post/list/non_existant_tag/1",
    "#category": ("shimmie2", "paheal", "tag"),
    "#class"   : paheal.PahealTagExtractor,
    "#count"   : 0,
},

{
    "#url"     : "https://rule34.paheal.net/post/view/481609",
    "#category": ("shimmie2", "paheal", "post"),
    "#class"   : paheal.PahealPostExtractor,
    "#results"     : "https://r34i.paheal-cdn.net/bb/dc/bbdc1c33410c2cdce7556c7990be26b7",
    "#sha1_content": "7b924bcf150b352ac75c9d281d061e174c851a11",

    "date"     : "dt:2010-06-17 15:40:23",
    "extension": "jpg",
    "file_url" : "https://r34i.paheal-cdn.net/bb/dc/bbdc1c33410c2cdce7556c7990be26b7",
    "filename" : "481609 - Ayumu_Kasuga Azumanga_Daioh inanimate Vuvuzela",
    "height"   : 660,
    "id"       : 481609,
    "md5"      : "bbdc1c33410c2cdce7556c7990be26b7",
    "size"     : 157696,
    "source"   : "",
    "tags"     : "Ayumu_Kasuga Azumanga_Daioh inanimate Vuvuzela",
    "uploader" : "CaptainButtface",
    "width"    : 614,
},

{
    "#url"     : "https://rule34.paheal.net/post/view/488534",
    "#category": ("shimmie2", "paheal", "post"),
    "#class"   : paheal.PahealPostExtractor,

    "date"    : "dt:2010-06-25 13:51:17",
    "height"  : 800,
    "md5"     : "b39edfe455a0381110c710d6ed2ef57d",
    "size"    : 758784,
    "source"  : "http://www.furaffinity.net/view/4057821/",
    "tags"    : "inanimate thelost-dragon Vuvuzela",
    "uploader": "leacheate_soup",
    "width"   : 1200,
},

{
    "#url"     : "https://rule34.paheal.net/post/view/3864982",
    "#comment" : "video",
    "#category": ("shimmie2", "paheal", "post"),
    "#class"   : paheal.PahealPostExtractor,
    "#results" : "https://r34i.paheal-cdn.net/76/29/7629fc0ff77e32637dde5bf4f992b2cb",

    "date"     : "dt:2020-09-06 01:59:03",
    "duration" : 30.0,
    "extension": "webm",
    "height"   : 2500,
    "id"       : 3864982,
    "md5"      : "7629fc0ff77e32637dde5bf4f992b2cb",
    "size"     : 18874368,
    "source"   : "https://twitter.com/VG_Worklog/status/1302407696294055936",
    "tags"     : "animated Metal_Gear Metal_Gear_Solid_V Quiet Vg_erotica webm",
    "uploader" : "justausername",
    "width"    : 1768,
},

{
    "#url"     : "https://rule34.paheal.net/post/view/7",
    "#category": ("shimmie2", "paheal", "post"),
    "#class"   : paheal.PahealPostExtractor,
    "#count"   : 0,
},

)
