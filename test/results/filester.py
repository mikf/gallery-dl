# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import filester


__tests__ = (
{
    "#url"     : "https://filester.me/d/aPc9D5g",
    "#class"   : filester.FilesterFileExtractor,
    "#pattern" : r"https://cache[16].filester.me/d/37313437[0-9a-f]+\.\w{64}\?download=true",

    "date"     : "dt:2026-03-06 00:00:00",
    "extension": "png",
    "filename" : """test-テスト-"&>""",
    "hash"     : "eb359cd8f02a7d6762f9863798297ff6a22569c5c87a9d38c55bdb3a3e26003f",
    "id"       : "aPc9D5g",
    "mime"     : "image/png",
    "size"     : "182 bytes",
    "uuid"     : "7147825c-5216-4d2a-b126-0e98e0b58d13",
},

{
    "#url"     : "https://filester.me/f/1725bc5b793e8a4a",
    "#class"   : filester.FilesterFolderExtractor,
    "#pattern" : (
        r"https://cache[16].filester.me/d/33343537[0-9a-f]+\.\w{64}\?download=true",
        r"https://cache[16].filester.me/d/30386462[0-9a-f]+\.\w{64}\?download=true",
        r"https://cache[16].filester.me/d/66663562[0-9a-f]+\.\w{64}\?download=true",
        r"https://cache[16].filester.me/d/63396533[0-9a-f]+\.\w{64}\?download=true",
        r"https://cache[16].filester.me/d/63343162[0-9a-f]+\.\w{64}\?download=true",
        r"https://cache[16].filester.me/d/39623935[0-9a-f]+\.\w{64}\?download=true",
    ),

    "count"      : 6,
    "num"        : range(1, 6),
    "date"       : "dt:2026-03-06 00:00:00",
    "extension"  : {"png", "mp4"},
    "filename"   : r"re:\d+_1",
    "folder_date": "dt:2026-03-06 00:00:00",
    "folder_id"  : "1725bc5b793e8a4a",
    "folder_name": '''"&>''',
    "folder_size": 194734,
    "folder_uuid": "34576704-dc5f-44a9-843c-ae0e5284309d",
    "id"         : r"re:\w+",
    "size"       : r"re:\d+",
    "uuid"       : "iso:uuid",
},

)
