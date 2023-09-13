# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import gofile


__tests__ = (
{
    "#url"     : "https://gofile.io/d/k6BomI",
    "#category": ("", "gofile", "folder"),
    "#class"   : gofile.GofileFolderExtractor,
    "#pattern" : r"https://store\d+\.gofile\.io/download/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}/test-%E3%83%86%E3%82%B9%E3%83%88-%2522%26!\.png",

    "createTime"   : int,
    "directLink"   : r"re:https://store5.gofile.io/download/direct/.+",
    "downloadCount": int,
    "extension"    : "png",
    "filename"     : "test-テスト-%22&!",
    "folder"       : {
        "childs"            : [
            "b0367d79-b8ba-407f-8342-aaf8eb815443",
            "7fd4a36a-c1dd-49ff-9223-d93f7d24093f",
        ],
        "code"              : "k6BomI",
        "createTime"        : 1654076165,
        "id"                : "fafb59f9-a7c7-4fea-a098-b29b8d97b03c",
        "name"              : "root",
        "public"            : True,
        "totalDownloadCount": int,
        "totalSize"         : 182,
        "type"              : "folder",
    },
    "id"           : r"re:\w{8}-\w{4}-\w{4}-\w{4}-\w{12}",
    "link"         : r"re:https://store5.gofile.io/download/.+\.png",
    "md5"          : r"re:[0-9a-f]{32}",
    "mimetype"     : "image/png",
    "name"         : "test-テスト-%22&!.png",
    "num"          : int,
    "parentFolder" : "fafb59f9-a7c7-4fea-a098-b29b8d97b03c",
    "serverChoosen": "store5",
    "size"         : 182,
    "thumbnail"    : r"re:https://store5.gofile.io/download/.+\.png",
    "type"         : "file",
},

{
    "#url"     : "https://gofile.io/d/7fd4a36a-c1dd-49ff-9223-d93f7d24093f",
    "#category": ("", "gofile", "folder"),
    "#class"   : gofile.GofileFolderExtractor,
    "#options"     : {"website-token": None},
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",
},

)
