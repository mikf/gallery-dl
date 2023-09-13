# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import directlink


__tests__ = (
{
    "#url"     : "https://en.wikipedia.org/static/images/project-logos/enwiki.png",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "18c5d00077332e98e53be9fed2ee4be66154b88d",
    "#sha1_metadata": "105770a3f4393618ab7b811b731b22663b5d3794",
},

{
    "#url"     : "https://example.org/file.webm",
    "#comment" : "empty path",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "2d807ed7059d1b532f1bb71dc24b510b80ff943f",
    "#sha1_metadata": "29dad729c40fb09349f83edafa498dba1297464a",
},

{
    "#url"     : "https://example.org/path/to/file.webm?que=1?&ry=2/#fragment",
    "#comment" : "more complex example",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "6fb1061390f8aada3db01cb24b51797c7ee42b31",
    "#sha1_metadata": "3d7abc31d45ba324e59bc599c3b4862452d5f29c",
},

{
    "#url"     : "https://example.org/%27%3C%23/%23%3E%27.jpg?key=%3C%26%3E",
    "#comment" : "percent-encoded characters",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "2627e8140727fdf743f86fe18f69f99a052c9718",
    "#sha1_metadata": "831790fddda081bdddd14f96985ab02dc5b5341f",
},

{
    "#url"     : "https://post-phinf.pstatic.net/MjAxOTA1MjlfMTQ4/MDAxNTU5MTI2NjcyNTkw.JUzkGb4V6dj9DXjLclrOoqR64uDxHFUO5KDriRdKpGwg.88mCtd4iT1NHlpVKSCaUpPmZPiDgT8hmQdQ5K_gYyu0g.JPEG/2.JPG",
    "#comment" : "upper case file extension (#296)",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
},

{
    "#url"     : "https://räksmörgås.josefsson.org/raksmorgas.jpg",
    "#comment" : "internationalized domain name",
    "#category": ("", "directlink", ""),
    "#class"   : directlink.DirectlinkExtractor,
    "#sha1_url"     : "a65667f670b194afbd1e3ea5e7a78938d36747da",
    "#sha1_metadata": "fd5037fe86eebd4764e176cbaf318caec0f700be",
},

)
