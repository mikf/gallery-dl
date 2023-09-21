# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import readcomiconline


__tests__ = (
{
    "#url"     : "https://readcomiconline.li/Comic/W-i-t-c-h/Issue-130?id=22289",
    "#category": ("", "readcomiconline", "issue"),
    "#class"   : readcomiconline.ReadcomiconlineIssueExtractor,
    "#pattern"      : r"https://2\.bp\.blogspot\.com/[\w-]+=s0\?.+",
    "#count"        : 36,
    "#sha1_metadata": "2d9ec81ce1b11fac06ebf96ce33cdbfca0e85eb5",
},

{
    "#url"     : "https://readcomiconline.li/Comic/W-i-t-c-h",
    "#category": ("", "readcomiconline", "comic"),
    "#class"   : readcomiconline.ReadcomiconlineComicExtractor,
    "#sha1_url"     : "74eb8b9504b4084fcc9367b341300b2c52260918",
    "#sha1_metadata": "3986248e4458fa44a201ec073c3684917f48ee0c",
},

{
    "#url"     : "https://readcomiconline.to/Comic/Bazooka-Jules",
    "#category": ("", "readcomiconline", "comic"),
    "#class"   : readcomiconline.ReadcomiconlineComicExtractor,
    "#sha1_url"     : "2f66a467a772df4d4592e97a059ddbc3e8991799",
    "#sha1_metadata": "f5ba5246cd787bb750924d9690cb1549199bd516",
},

)
