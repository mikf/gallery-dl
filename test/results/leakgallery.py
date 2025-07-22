# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import leakgallery

__tests__ = (
    {
        "#url": "https://leakgallery.com/sophieraiin/12240",
        "#category": ("", "leakgallery", "post"),
        "#class": leakgallery.LeakgalleryPostExtractor,
        "id": 12240,
        "creator": "sophieraiin",
    },
    {
        "#url": "https://leakgallery.com/sophieraiin",
        "#category": ("", "leakgallery", "user"),
        "#class": leakgallery.LeakgalleryUserExtractor,
    },
    {
        "#url": "https://leakgallery.com/trending-medias/Week",
        "#category": ("", "leakgallery", "trending"),
        "#class": leakgallery.LeakgalleryTrendingExtractor,
    },
    {
        "#url": "https://leakgallery.com/most-liked",
        "#category": ("", "leakgallery", "mostliked"),
        "#class": leakgallery.LeakgalleryMostlikedExtractor,
    },
)
