# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import simplyhentai
from gallery_dl import exception


__tests__ = (
{
    "#url"     : "https://original-work.simply-hentai.com/amazon-no-hiyaku-amazon-elixir",
    "#category": ("", "simplyhentai", "gallery"),
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
    "#sha1_url"     : "21613585ae5ec2f69ea579e9713f536fceab5bd5",
    "#sha1_metadata": "9e87a0973553b2922ddee37958b8f5d87910af72",
},

{
    "#url"     : "https://www.simply-hentai.com/notfound",
    "#category": ("", "simplyhentai", "gallery"),
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
    "#exception": exception.GalleryDLException,
},

{
    "#url"     : "https://pokemon.simply-hentai.com/mao-friends-9bc39",
    "#comment" : "custom subdomain",
    "#category": ("", "simplyhentai", "gallery"),
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
},

{
    "#url"     : "https://www.simply-hentai.com/vocaloid/black-magnet",
    "#comment" : "www subdomain, two path segments",
    "#category": ("", "simplyhentai", "gallery"),
    "#class"   : simplyhentai.SimplyhentaiGalleryExtractor,
},

{
    "#url"     : "https://www.simply-hentai.com/image/pheromomania-vol-1-kanzenban-isao-3949d8b3-400c-4b6",
    "#category": ("", "simplyhentai", "image"),
    "#class"   : simplyhentai.SimplyhentaiImageExtractor,
    "#sha1_url"     : "3d8eb55240a960134891bd77fe1df7988fcdc455",
    "#sha1_metadata": "e10e5588481cab68329ef6ec1e5325206b2079a2",
},

{
    "#url"     : "https://www.simply-hentai.com/gif/8915dfcf-0b6a-47c",
    "#category": ("", "simplyhentai", "image"),
    "#class"   : simplyhentai.SimplyhentaiImageExtractor,
    "#sha1_url"     : "f73916527211b4a40f26568ee26cd8999f5f4f30",
    "#sha1_metadata": "f94d775177fed918759c8a78a50976f867425b48",
},

{
    "#url"     : "https://videos.simply-hentai.com/creamy-pie-episode-02",
    "#category": ("", "simplyhentai", "video"),
    "#class"   : simplyhentai.SimplyhentaiVideoExtractor,
    "#options"      : {"verify": False},
    "#pattern"      : r"https://www\.googleapis\.com/drive/v3/files/0B1ecQ8ZVLm3JcHZzQzBnVy1ZUmc\?alt=media&key=[\w-]+",
    "#count"        : 1,
    "#sha1_metadata": "706790708b14773efc1e075ddd3b738a375348a5",
},

{
    "#url"     : "https://videos.simply-hentai.com/1715-tifa-in-hentai-gang-bang-3d-movie",
    "#category": ("", "simplyhentai", "video"),
    "#class"   : simplyhentai.SimplyhentaiVideoExtractor,
    "#sha1_url"     : "ad9a36ae06c601b6490e3c401834b4949d947eb0",
    "#sha1_metadata": "f9dad94fbde9c95859e631ff4f07297a9567b874",
},

)
