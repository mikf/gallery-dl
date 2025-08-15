# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import readcomiconline


__tests__ = (
{
    "#url"     : "https://readcomiconline.li/Comic/W-i-t-c-h/Issue-130?id=22289",
    "#class"   : readcomiconline.ReadcomiconlineIssueExtractor,
    "#pattern"      : r"https://2\.bp\.blogspot\.com/[\w-]+=s0\?.+",
    "#count"        : 36,
    "#sha1_metadata": "2d9ec81ce1b11fac06ebf96ce33cdbfca0e85eb5",

    "comic"      : "W.i.t.c.h.",
    "count"      : 36,
    "extension"  : "",
    "filename"   : str,
    "issue"      : "130",
    "issue_id"   : 22289,
    "lang"       : "en",
    "language"   : "English",
    "page"       : range(1, 36),
},

{
    "#url"     : "https://readcomiconline.li/Comic/Captain-Planet/Issue-1?id=238698&s=&readType=1",
    "#comment" : "'One page' Reading mode (#7890)",
    "#class"   : readcomiconline.ReadcomiconlineIssueExtractor,
    "#pattern" : r"https://2\.bp\.blogspot\.com/pw/[\w-]+=s0\?.+",
    "#count"   : 31,

    "comic"      : "Captain Planet",
    "count"      : 31,
    "extension"  : "",
    "filename"   : str,
    "issue"      : "1",
    "issue_id"   : 238698,
    "lang"       : "en",
    "language"   : "English",
    "page"       : range(1, 31),
},

{
    "#url"     : "https://readcomiconline.li/Comic/W-i-t-c-h",
    "#class"   : readcomiconline.ReadcomiconlineComicExtractor,
    "#pattern" : readcomiconline.ReadcomiconlineIssueExtractor.pattern,
    "#sha1_url"     : "74eb8b9504b4084fcc9367b341300b2c52260918",
    "#sha1_metadata": "574051aaf7a5c92dafed9e94baa40a1a93db5c90",
},

{
    "#url"     : "https://readcomiconline.to/Comic/Bazooka-Jules",
    "#class"   : readcomiconline.ReadcomiconlineComicExtractor,
    "#pattern" : readcomiconline.ReadcomiconlineIssueExtractor.pattern,
    "#sha1_url"     : "2f66a467a772df4d4592e97a059ddbc3e8991799",
    "#sha1_metadata": "9563a19454e1b4e0da5b7a28112bf00a3e8069a8",
},

)
