# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import seiga
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://seiga.nicovideo.jp/user/illust/39537793",
    "#category": ("", "seiga", "user"),
    "#class"   : seiga.SeigaUserExtractor,
    "#pattern" : r"https://lohas\.nicoseiga\.jp/priv/[0-9a-f]+/\d+/\d+",
    "#count"   : ">= 4",

    "user"     : {
        "id"     : 39537793,
        "message": str,
        "name"   : str,
    },
    "clips"    : int,
    "comments" : int,
    "count"    : int,
    "extension": None,
    "image_id" : int,
    "title"    : str,
    "views"    : int,
},

{
    "#url"     : "https://seiga.nicovideo.jp/user/illust/79433",
    "#category": ("", "seiga", "user"),
    "#class"   : seiga.SeigaUserExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://seiga.nicovideo.jp/user/illust/39537793?sort=image_view&target=illust_all",
    "#category": ("", "seiga", "user"),
    "#class"   : seiga.SeigaUserExtractor,
},

{
    "#url"     : "https://sp.seiga.nicovideo.jp/user/illust/39537793",
    "#category": ("", "seiga", "user"),
    "#class"   : seiga.SeigaUserExtractor,
},

{
    "#url"     : "https://seiga.nicovideo.jp/seiga/im5977527",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
    "#sha1_metadata": "c8339781da260f7fc44894ad9ada016f53e3b12a",
    "#sha1_content" : "d9202292012178374d57fb0126f6124387265297",
},

{
    "#url"     : "https://seiga.nicovideo.jp/seiga/im123",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
    "#exception": exception.NotFoundError,
},

{
    "#url"     : "https://seiga.nicovideo.jp/seiga/im10877923",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
    "#pattern" : r"https://lohas\.nicoseiga\.jp/priv/5936a2a6c860a600e465e0411c0822e0b510e286/1688757110/10877923",
},

{
    "#url"     : "https://seiga.nicovideo.jp/image/source/5977527",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
},

{
    "#url"     : "https://sp.seiga.nicovideo.jp/seiga/#!/im5977527",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
},

{
    "#url"     : "https://lohas.nicoseiga.jp/thumb/5977527i",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
},

{
    "#url"     : "https://lohas.nicoseiga.jp/priv/759a4ef1c639106ba4d665ee6333832e647d0e4e/1549727594/5977527",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
},

{
    "#url"     : "https://lohas.nicoseiga.jp/o/759a4ef1c639106ba4d665ee6333832e647d0e4e/1549727594/5977527",
    "#category": ("", "seiga", "image"),
    "#class"   : seiga.SeigaImageExtractor,
},

)
