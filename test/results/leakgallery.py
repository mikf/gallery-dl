# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import leakgallery
from gallery_dl import exception

__tests__ = (
    {
        "#url": "https://leakgallery.com/sophieraiin/12240",
        "#category": ("", "leakgallery", "post"),
        "#class": leakgallery.LeakGalleryPostExtractor,
        "id": 12240,
        "creator": "sophieraiin",
    },
    {
        "#url": "https://leakgallery.com/sophieraiin",
        "#category": ("", "leakgallery", "user"),
        "#class": leakgallery.LeakGalleryUserExtractor,
    },
    {
        "#url": "https://leakgallery.com/trending-medias/Week",
        "#category": ("", "leakgallery", "trending"),
        "#class": leakgallery.LeakGalleryTrendingExtractor,
    },
    {
        "#url": "https://leakgallery.com/most-liked",
        "#category": ("", "leakgallery", "mostliked"),
        "#class": leakgallery.LeakGalleryMostLikedExtractor,
    },
)