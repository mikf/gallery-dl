# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixeldrain
import datetime

__tests__ = (
{
    "#url"     : "https://pixeldrain.com/u/jW9E6s4h",
    "#category": ("", "pixeldrain", "file"),
    "#class"   : pixeldrain.PixeldrainFileExtractor,
    "#urls"        : "https://pixeldrain.com/api/file/jW9E6s4h?download",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",

    "abuse_reporter_name" : "",
    "abuse_type"          : "",
    "allow_video_player"  : True,
    "availability"        : "",
    "availability_message": "",
    "bandwidth_used"      : int,
    "bandwidth_used_paid" : 0,
    "can_download"        : True,
    "can_edit"            : False,
    "date"                : "dt:2023-11-22 16:33:27",
    "date_last_view"      : r"re:\d+-\d+-\d+T\d+:\d+:\d+\.\d+Z",
    "date_upload"         : "2023-11-22T16:33:27.744Z",
    "delete_after_date"   : "0001-01-01T00:00:00Z",
    "delete_after_downloads": 0,
    "download_speed_limit": 0,
    "downloads"           : int,
    "extension"           : "png",
    "filename"            : "test-テスト-\"&>",
    "hash_sha256"         : "eb359cd8f02a7d6762f9863798297ff6a22569c5c87a9d38c55bdb3a3e26003f",
    "id"                  : "jW9E6s4h",
    "mime_type"           : "image/png",
    "name"                : "test-テスト-\"&>.png",
    "show_ads"            : True,
    "size"                : 182,
    "success"             : True,
    "thumbnail_href"      : "/file/jW9E6s4h/thumbnail",
    "url"                 : "https://pixeldrain.com/api/file/jW9E6s4h?download",
    "views"               : int,
},

{
    "#url"     : "https://pixeldrain.com/u/yEK1n2Qc",
    "#category": ("", "pixeldrain", "file"),
    "#class"   : pixeldrain.PixeldrainFileExtractor,
    "#urls"        : "https://pixeldrain.com/api/file/yEK1n2Qc?download",
    "#sha1_content": "08463261191d403de2133d829060050d8b04609f",

    "date"       : "dt:2023-11-22 16:38:04",
    "date_upload": "2023-11-22T16:38:04.928Z",
    "extension"  : "txt",
    "filename"   : '"&>',
    "hash_sha256": "4c1e2bbcbe1dea8b6f895f5cdd8461c37c561bce4f1b3556ba58392d95964294",
    "id"         : "yEK1n2Qc",
    "mime_type"  : "text/plain; charset=utf-8",
    "name"       : '"&>.txt',
    "size"       : 14,
},

{
    "#url"     : "https://pixeldrain.com/l/zQ7XpWfM",
    "#category": ("", "pixeldrain", "album"),
    "#class"   : pixeldrain.PixeldrainAlbumExtractor,
    "#urls"    : (
        "https://pixeldrain.com/api/file/yEK1n2Qc?download",
        "https://pixeldrain.com/api/file/jW9E6s4h?download",
    ),

    "album"      : {
        "can_edit"    : False,
        "count"       : 2,
        "date"        : "dt:2023-11-22 16:40:39",
        "date_created": "2023-11-22T16:40:39.218Z",
        "id"          : "zQ7XpWfM",
        "success"     : True,
        "title"       : "アルバム",
    },
    "date"       : datetime.datetime,
    "description": "",
    "detail_href": r"re:/file/(yEK1n2Qc|jW9E6s4h)/info",
    "hash_sha256": r"re:\w{64}",
    "id"         : r"re:yEK1n2Qc|jW9E6s4h",
    "mime_type"  : str,
},

)
