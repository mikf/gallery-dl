# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

gallery_dl = __import__("gallery_dl.extractor.8chan")
_8chan = getattr(gallery_dl.extractor, "8chan")


__tests__ = (
{
    "#url"  : "https://8chan.moe/vhs/res/4.html",
    "#class": _8chan._8chanThreadExtractor,
    "#pattern": r"https://8chan\.moe/\.media/[0-9a-f]{64}\.\w+$",
    "#count"  : 14,

    "archived"        : False,
    "autoSage"        : False,
    "boardDescription": "Film and Cinema",
    "boardMarkdown"   : None,
    "boardName"       : "Movies",
    "boardUri"        : "vhs",
    "creation"        : r"re:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z",
    "cyclic"          : False,
    "email"           : None,
    "id"              : r"re:^[0-9a-f]{6}$",
    "locked"          : False,
    "markdown"        : str,
    "maxFileCount"    : 5,
    "maxFileSize"     : "32.00 MB",
    "maxMessageLength": 12000,
    "message"         : str,
    "mime"            : str,
    "name"            : "Anonymous",
    "num"             : int,
    "originalName"    : str,
    "path"            : r"re:/.media/[0-9a-f]{64}\.\w+$",
    "pinned"          : False,
    "postId"          : int,
    "signedRole"      : None,
    "size"            : int,
    "threadId"        : 4,
    "thumb"           : r"re:/.media/t_[0-9a-f]{64}$",
    "uniquePosters"   : 9,
    "usesCustomCss"   : True,
    "usesCustomJs"    : False,
    "?wsPort"         : int,
    "?wssPort"        : int,
},

{
    "#url"  : "https://8chan.moe/vhs/last/4.html",
    "#class": _8chan._8chanThreadExtractor,
},

{
    "#url"  : "https://8chan.se/vhs/res/4.html",
    "#class": _8chan._8chanThreadExtractor,
},

{
    "#url"  : "https://8chan.cc/vhs/res/4.html",
    "#class": _8chan._8chanThreadExtractor,
},

{
    "#url"  : "https://8chan.moe/vhs/",
    "#class": _8chan._8chanBoardExtractor,
},

{
    "#url"  : "https://8chan.moe/vhs/2.html",
    "#class": _8chan._8chanBoardExtractor,
    "#pattern": _8chan._8chanThreadExtractor.pattern,
    "#count"  : range(24, 32),
},

{
    "#url"  : "https://8chan.se/vhs/",
    "#class": _8chan._8chanBoardExtractor,
},

{
    "#url"  : "https://8chan.cc/vhs/",
    "#class": _8chan._8chanBoardExtractor,
},

)
