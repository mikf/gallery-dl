# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import koofr


__tests__ = (
{
    "#url"     : "https://k00.fr/cltf71jr",
    "#class"   : koofr.KoofrSharedExtractor,
    "#results" : "https://app.koofr.net/content/links/923b4f56-3aaf-49ee-95e3-d85c52b687b0/files/get/wsf-form-job-application-form.json?path=/&force",
    "#sha1_content": "f65ccc63a99165ecb9ff2ab92302c25b245a904f",

    "contentType": "application/json",
    "extension"  : "json",
    "filename"   : "wsf-form-job-application-form",
    "hash"       : "99271125b819ee7907dc47ab723f6dc7",
    "modified"   : 1728623530078,
    "name"       : "wsf-form-job-application-form.json",
    "size"       : 18023,
    "tags"       : {},
    "type"       : "file",
},

{
    "#url"     : "https://app.koofr.net/links/923b4f56-3aaf-49ee-95e3-d85c52b687b0",
    "#class"   : koofr.KoofrSharedExtractor,
    "#results" : "https://app.koofr.net/content/links/923b4f56-3aaf-49ee-95e3-d85c52b687b0/files/get/wsf-form-job-application-form.json?path=/&force",
    "#sha1_content": "f65ccc63a99165ecb9ff2ab92302c25b245a904f",

    "contentType": "application/json",
    "extension"  : "json",
    "filename"   : "wsf-form-job-application-form",
    "hash"       : "99271125b819ee7907dc47ab723f6dc7",
    "modified"   : 1728623530078,
    "name"       : "wsf-form-job-application-form.json",
    "size"       : 18023,
    "tags"       : {},
    "type"       : "file",
},

{
    "#url"     : "https://app.koofr.eu/links/923b4f56-3aaf-49ee-95e3-d85c52b687b0",
    "#class"   : koofr.KoofrSharedExtractor,
},

{
    "#url"     : "https://app.koofr.net/links/01deac62-f5d6-4d2b-7043-53b24cc0a038",
    "#comment" : "individual files",
    "#class"   : koofr.KoofrSharedExtractor,
    "#options" : {"zip": False},
    "#pattern" : r"https://app\.koofr\.net/content/links/01deac62\-f5d6\-4d2b\-7043\-53b24cc0a038/files/get/smw_msu1\-\d+\.pcm\?path=/smw_msu1\-\d+\.pcm",
    "#count"   : 18,

    "contentType": "application/octet-stream",
    "!count"     : 18,
    "!num"       : range(1, 18),
    "date"       : "type:datetime",
    "extension"  : "pcm",
    "filename"   : r"re:smw_msu1-\d+",
    "hash"       : "hash:md5",
    "modified"   : int,
    "name"       : r"re:smw_msu1-\d+\.pcm",
    "size"       : range(500_000, 20_000_000),
    "tags"       : {},
    "type"       : "file",
    "post"       : {
        "!count"     : 18,
        "date"       : "dt:2023-11-19 16:27:56",
        "id"         : "01deac62-f5d6-4d2b-7043-53b24cc0a038",
        "title"      : "Church of Kondo",
    },
},

{
    "#url"     : "https://app.koofr.net/links/01deac62-f5d6-4d2b-7043-53b24cc0a038",
    "#comment" : ".zip container",
    "#class"   : koofr.KoofrSharedExtractor,
    "#options" : {"recursive": False},
    "#results" : "https://app.koofr.net/content/links/01deac62-f5d6-4d2b-7043-53b24cc0a038/files/get/Church of Kondo?path=/&force",

    "contentType": "",
    "!count"     : 1,
    "!num"       : 1,
    "date"       : "dt:2023-11-19 16:27:56",
    "extension"  : "",
    "filename"   : "Church of Kondo",
    "modified"   : 1700411276087,
    "name"       : "Church of Kondo",
    "size"       : 0,
    "tags"       : {},
    "type"       : "dir",
    "post"       : {
        "!count"     : 1,
        "date"       : "dt:2023-11-19 16:27:56",
        "id"         : "01deac62-f5d6-4d2b-7043-53b24cc0a038",
        "title"      : "Church of Kondo",
    },
},

{
    "#url"     : "https://app.koofr.net/links/7667d857-c639-4f38-93d1-c42394492a0c",
    "#comment" : "recursive directories",
    "#class"   : koofr.KoofrSharedExtractor,
    "#pattern" : r"https://app\.koofr\.net/content/links/7667d857\-c639\-4f38\-93d1\-c42394492a0c/files/get/[\w]\.png\?path=/.*\w\.png",
    "#count"   : 16,

    "contentType": "image/png",
    "date"       : "type:datetime",
    "extension"  : "png",
    "filename"   : r"re:^[1-8a-d]$",
    "hash"       : "hash:md5",
    "modified"   : range(1767688000000, 1767700000000),
    "name"       : r"re:^[1-8a-d]\.png",
    "path"       : {(), ("dir-l1-1",), ("dir-l1-2",), ("dir-l1-1", "dir-l2-1")},
    "size"       : range(200, 999),
    "tags"       : {},
    "type"       : "file",
    "post"       : {
        "date" : "dt:2026-01-06 08:27:26",
        "id"   : "7667d857-c639-4f38-93d1-c42394492a0c",
        "title": "dir",
    },
},

)
