# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import pixeldrain

__tests__ = (
{
    "#url"     : "https://pixeldrain.com/u/jW9E6s4h",
    "#category": ("", "pixeldrain", "file"),
    "#class"   : pixeldrain.PixeldrainFileExtractor,
    "#results"     : "https://pixeldrain.com/api/file/jW9E6s4h?download",
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
    "#results"     : "https://pixeldrain.com/api/file/yEK1n2Qc?download",
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
    "#results" : (
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
    "date"       : "type:datetime",
    "description": "",
    "detail_href": r"re:/file/(yEK1n2Qc|jW9E6s4h)/info",
    "hash_sha256": r"re:\w{64}",
    "id"         : r"re:yEK1n2Qc|jW9E6s4h",
    "mime_type"  : str,
},

{
    "#url"     : "https://pixeldrain.com/l/zQ7XpWfM#item=0",
    "#category": ("", "pixeldrain", "album"),
    "#class"   : pixeldrain.PixeldrainAlbumExtractor,
    "#results"     : "https://pixeldrain.com/api/file/jW9E6s4h?download",
    "#sha1_content": "0c8768055e4e20e7c7259608b67799171b691140",
},

{
    "#url"     : "https://pixeldrain.com/d/8xz8hcYJ",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,
    "#results"     : "https://pixeldrain.com/api/filesystem/8xz8hcYJ?attach",
    "#sha1_content": "edfea851cad717f5643cb94ac04b32335611acf2",

    "date"       : "dt:2025-05-19 15:27:54",
    "extension"  : "mp4",
    "filename"   : "test",
    "id"         : "8xz8hcYJ",
    "mime_type"  : "video/mp4",
    "name"       : "test.mp4",
    "path"       : "/8xz8hcYJ",
    "hash_sha256": "c6293d8359cb84723bbf8cf355da6cf1ef9c3e8b3d465110e91db485e53ada54",
    "share_url"  : "https://pixeldrain.com/d/8xz8hcYJ",
    "size"       : 3026,
    "type"       : "file",
},

{
    "#url"     : "https://pixeldrain.com/api/filesystem/8xz8hcYJ",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,
    "#results"     : "https://pixeldrain.com/api/filesystem/8xz8hcYJ?attach",
    "#sha1_content": "edfea851cad717f5643cb94ac04b32335611acf2",

    "date"       : "dt:2025-05-19 15:27:54",
    "extension"  : "mp4",
    "filename"   : "test",
    "id"         : "8xz8hcYJ",
    "mime_type"  : "video/mp4",
    "name"       : "test.mp4",
    "path"       : "/8xz8hcYJ",
    "hash_sha256": "c6293d8359cb84723bbf8cf355da6cf1ef9c3e8b3d465110e91db485e53ada54",
    "share_url"  : "https://pixeldrain.com/d/8xz8hcYJ",
    "size"       : 3026,
    "type"       : "file",
},

{
    "#url"     : "https://pixeldrain.com/d/DkdR6QRh",
    "#comment" : "dir with file",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,
    "#results" : ("https://pixeldrain.com/api/filesystem/DkdR6QRh/test.mp4?attach"),

    "id": "DkdR6QRh",
},

{
    "#url"     : "https://pixeldrain.com/d/STAcYjEh",
    "#comment" : "dir with subdir",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,

    "id": "STAcYjEh",
},

{
    "#url"     : "https://pixeldrain.com/d/qTnZkhCJ",
    "#comment" : "dir with subdir and files",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,
    "#results" : (
        "https://pixeldrain.com/api/filesystem/qTnZkhCJ/test1.mp4?attach",
        "https://pixeldrain.com/api/filesystem/qTnZkhCJ/test2.mp4?attach",
    ),

    "id": "qTnZkhCJ",
},

{
    "#url"     : "https://pixeldrain.com/d/qTnZkhCJ/subdir/test3.mp4",
    "#comment" : "file in subdir",
    "#category": ("", "pixeldrain", "folder"),
    "#class"   : pixeldrain.PixeldrainFolderExtractor,
    "#results" : (
        "https://pixeldrain.com/api/filesystem/qTnZkhCJ/subdir/test3.mp4?attach",
    ),

    "date"       : "dt:2025-05-20 19:02:08",
    "extension"  : "mp4",
    "filename"   : "test3",
    "hash_sha256": "c6293d8359cb84723bbf8cf355da6cf1ef9c3e8b3d465110e91db485e53ada54",
    "id"         : "qTnZkhCJ",
    "mime_type"  : "video/mp4",
    "name"       : "test3.mp4",
    "path"       : "/qTnZkhCJ/subdir/test3.mp4",
    "share_url"  : "https://pixeldrain.com/d/qTnZkhCJ/subdir/test3.mp4",
    "size"       : 3026,
    "type"       : "file",
},

)
