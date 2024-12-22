# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import directlink


__tests__ = (
{
    "#url"     : "https://en.wikipedia.org/static/images/project-logos/enwiki.png",
    "#category": ("", "directlink", "wikipedia.org"),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "18c5d00077332e98e53be9fed2ee4be66154b88d",
    "#sha1_metadata": "326ac83735d3a103ccd71f2aeea831f6d62e7836",
    "#sha1_content" : "e6f58aaec8f31eb222f9e10fa9e9f64b79ae888c",

    "category"   : "directlink",
    "subcategory": "wikipedia.org",
    "domain"     : "en.wikipedia.org",
    "path"       : "static/images/project-logos",
    "filename"   : "enwiki",
    "extension"  : "png",
    "query"      : None,
    "fragment"   : None,
},

{
    "#url"     : "https://example.org/file.webm",
    "#comment" : "empty path",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
    "#urls"    : "https://example.org/file.webm",

    "domain"   : "example.org",
    "path"     : "",
    "filename" : "file",
    "extension": "webm",
},

{
    "#url"     : "https://example.org/path/to/file.webm?que=1?&ry=2/#fragment",
    "#comment" : "more complex example",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
    "#urls"    : "https://example.org/path/to/file.webm?que=1?&ry=2/#fragment",

    "domain"   : "example.org",
    "path"     : "path/to",
    "filename" : "file",
    "extension": "webm",
    "query"    : "que=1?&ry=2/",
    "fragment" : "fragment",
},

{
    "#url"     : "https://example.org/%27%3C%23/%23%3E%27.jpg?key=%3C%26%3E",
    "#comment" : "percent-encoded characters",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
    "#urls"    : "https://example.org/%27%3C%23/%23%3E%27.jpg?key=%3C%26%3E",

    "domain"   : "example.org",
    "path"     : "'<#",
    "filename" : "#>'",
    "extension": "jpg",
    "query"    : "key=<&>",
    "fragment" : None,
},

{
    "#url"     : "https://post-phinf.pstatic.net/MjAxOTA1MjlfMTQ4/MDAxNTU5MTI2NjcyNTkw.JUzkGb4V6dj9DXjLclrOoqR64uDxHFUO5KDriRdKpGwg.88mCtd4iT1NHlpVKSCaUpPmZPiDgT8hmQdQ5K_gYyu0g.JPEG/2.JPG",
    "#comment" : "upper case file extension (#296)",
    "#category": ("", "directlink", "pstatic.net"),
    "#class"   : directlink.DirectlinkExtractor,
},

{
    "#url"     : "https://räksmörgås.josefsson.org/raksmorgas.jpg",
    "#comment" : "internationalized domain name",
    "#category": ("", "directlink", "josefsson.org"),
    "#class"   : directlink.DirectlinkExtractor,
    "#urls"    : "https://räksmörgås.josefsson.org/raksmorgas.jpg",

    "domain"   : "räksmörgås.josefsson.org",
    "path"     : "",
    "filename" : "raksmorgas",
    "extension": "jpg",
    "query"    : None,
    "fragment" : None,
},

{
    "#url"     : "https://example.org/file.gif",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.bmp",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.svg",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.webp",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.avif",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.heic",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.psd",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.mp4",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.m4v",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.mov",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.mkv",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.ogg",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.ogm",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.ogv",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.wav",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.mp3",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.opus",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.zip",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.rar",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.7z",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.pdf",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},
{
    "#url"     : "https://example.org/file.swf",
    "#category": ("", "directlink", "example.org"),
    "#class"   : directlink.DirectlinkExtractor,
},

)
