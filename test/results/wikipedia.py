# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import wikimedia


__tests__ = (
{
    "#url"     : "https://www.wikipedia.org/wiki/Title",
    "#category": ("wikimedia", "wikipedia", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

{
    "#url"     : "https://en.wikipedia.org/wiki/Athena",
    "#category": ("wikimedia", "wikipedia", "article"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
    "#pattern" : r"https://upload.wikimedia.org/wikipedia/.+",
    "#count"   : range(50, 100),

    "bitdepth"      : int,
    "canonicaltitle": str,
    "comment"       : str,
    "commonmetadata": dict,
    "date"          : "type:datetime",
    "descriptionshorturl": str,
    "descriptionurl": str,
    "extension"     : str,
    "extmetadata"   : dict,
    "filename"      : str,
    "height"        : int,
    "metadata"      : dict,
    "mime"          : r"re:image/\w+",
    "page"          : "Athena",
    "sha1"          : r"re:^[0-9a-f]{40}$",
    "size"          : int,
    "timestamp"     : str,
    "url"           : str,
    "user"          : str,
    "userid"        : int,
    "width"         : int,
},

{
    "#url"     : "https://en.wikipedia.org/wiki/Category:Physics",
    "#category": ("wikimedia", "wikipedia", "category"),
    "#class"   : wikimedia.WikimediaArticleExtractor,
},

)
