# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import cyberfile
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://cyberfile.me/bpfD",
    "#class"   : cyberfile.CyberfileFileExtractor,
    "#pattern" : r"https://p1.cyberfile.me/bpfD/Raindrops.mp4\?download_token=[0-9a-f]{64}",
    "#count"   : 1,

    "date"       : "dt:2024-01-04 16:01:26",
    "extension"  : "mp4",
    "file_id"    : "bpfD",
    "file_num"   : 718677,
    "file_url"   : str,
    "filename"   : "Raindrops",
    "folder"     : "Videos",
    "name"       : "Raindrops.mp4",
    "size"       : 3659530,
    "uploader"   : "barbarella",
    "permissions": [
        "View",
        "Download",
    ],
    "tags"       : [
        "raindrops",
        "mp4",
    ],
},

{
    "#url"     : "https://cyberfile.me/7d79",
    "#comment" : "password-protected",
    "#class"   : cyberfile.CyberfileFileExtractor,
    "#options" : {"password": "sample_pwd"},
    "#pattern" : r"https://p1.cyberfile.me/7d79/Raindrops.mp4\?download_token=[0-9a-f]{64}",
    "#count"   : 1,

    "date"       : "dt:2024-01-04 17:50:59",
    "extension"  : "mp4",
    "file_id"    : "7d79",
    "file_num"   : 718711,
    "file_url"   : str,
    "filename"   : "Raindrops",
    "folder"     : "Playlist Protected",
    "name"       : "Raindrops.mp4",
    "size"       : 3659530,
    "tags"       : [],
    "uploader"   : "barbarella",
    "permissions": [
        "View",
        "Download",
    ],
},

{
    "#url"     : "https://cyberfile.me/7d79",
    "#comment" : "password-protected",
    "#class"   : cyberfile.CyberfileFileExtractor,
    "#options"  : {"password": "abc"},
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://cyberfile.me/folder/82d0aab0853fdd13294171577081f4d8/Playlist",
    "#class"   : cyberfile.CyberfileFolderExtractor,
    "#results" : (
        "https://cyberfile.me/7d76",
        "https://cyberfile.me/7d77",
    ),

    "folder"     : "Playlist",
    "folder_hash": "82d0aab0853fdd13294171577081f4d8",
    "folder_num" : 56050,
},

{
    "#url"     : "https://cyberfile.me/folder/1524a09fa9d773dcc88c841ed2e098c9/Playlist_Protected",
    "#comment" : "password-protected",
    "#class"   : cyberfile.CyberfileFolderExtractor,
    "#options" : {"password": "sample_pwd"},
    "#results" : (
        "https://cyberfile.me/7d7a",
        "https://cyberfile.me/7d79",
    ),

    "folder"     : "Playlist Protected",
    "folder_hash": "1524a09fa9d773dcc88c841ed2e098c9",
    "folder_num" : 56051,
},

{
    "#url"     : "https://cyberfile.me/folder/1524a09fa9d773dcc88c841ed2e098c9/Playlist_Protected",
    "#comment" : "password-protected",
    "#class"   : cyberfile.CyberfileFolderExtractor,
    "#options"  : {"password": "abc"},
    "#exception": exception.AuthorizationError,
},

{
    "#url"     : "https://cyberfile.me/folder/8b17bbfdf25fca19aa51176bd246c97c/Helena_Price_Onlyfans",
    "#class"   : cyberfile.CyberfileFolderExtractor,
    "#results" : (
        "https://cyberfile.me/folder/c2cfdcfcf1a6e6e57de7bc948804b0fc/PICS",
        "https://cyberfile.me/folder/bdc7c36e7d4dfdc3fb908a6d3fe1cae5/VIDEO",
    ),

    "folder"     : "Helena Price Onlyfans",
    "folder_hash": "8b17bbfdf25fca19aa51176bd246c97c",
    "folder_num" : 18322,
},

{
    "#url"     : "https://cyberfile.me/shared/tao35avvfc",
    "#class"   : cyberfile.CyberfileSharedExtractor,
},

{
    "#url"     : "https://cyberfile.me/shared/l7zoinbctg",
    "#class"   : cyberfile.CyberfileSharedExtractor,
    "#results" : (
        "https://cyberfile.me/gb3s",
        "https://cyberfile.me/gb8m"
    ),
},

{
    "#url"     : "https://cyberfile.me/shared/wqpd9n0si5",
    "#class"   : cyberfile.CyberfileSharedExtractor,
    "#results" : "https://cyberfile.me/folder/9f611ebab76f363e4b818397c7828a73/CF_DSPRMTRS",
},

)
