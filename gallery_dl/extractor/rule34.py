# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://rule34.xxx/"""

from . import booru


class Rule34Extractor(booru.XmlParserMixin,
                      booru.GelbooruPageMixin,
                      booru.BooruExtractor):
    """Base class for rule34 extractors"""
    category = "rule34"
    api_url = "https://rule34.xxx/index.php"
    post_url = "https://rule34.xxx/index.php?page=post&s=view&id={}"
    pool_url = "https://rule34.xxx/index.php?page=pool&s=show&id={}"
    page_limit = 4000

    def __init__(self, match):
        super().__init__(match)
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class Rule34TagExtractor(booru.TagMixin, Rule34Extractor):
    """Extractor for images from rule34.xxx based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
               r"\?page=post&s=list&tags=(?P<tags>[^&#]+)")
    test = ("https://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
        "content": "97e4bbf86c3860be18de384d02d544251afe1d45",
        "pattern": r"https?://([^.]+\.)?rule34\.xxx/images/\d+/[0-9a-f]+\.jpg",
        "count": 1,
    })


class Rule34PoolExtractor(booru.GelbooruPoolMixin, Rule34Extractor):
    """Extractor for image-pools from rule34.xxx"""
    pattern = (r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
               r"\?page=pool&s=show&id=(?P<pool>\d+)")
    test = ("https://rule34.xxx/index.php?page=pool&s=show&id=179", {
        "count": 3,
    })


class Rule34PostExtractor(booru.PostMixin, Rule34Extractor):
    """Extractor for single images from rule34.xxx"""
    pattern = (r"(?:https?://)?(?:www\.)?rule34\.xxx/(?:index\.php)?"
               r"\?page=post&s=view&id=(?P<post>\d+)")
    test = ("https://rule34.xxx/index.php?page=post&s=view&id=1995545", {
        "content": "97e4bbf86c3860be18de384d02d544251afe1d45",
        "options": (("tags", True),),
        "keyword": {
            "tags_artist": "danraku",
            "tags_character": "kashima_(kantai_collection)",
            "tags_copyright": "kantai_collection",
            "tags_general": str,
            "tags_metadata": str,
        },
    })
