# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fapello.com/"""

from .common import Extractor, Message
from .. import text, exception


class FapelloPostExtractor(Extractor):
    """Extractor for individual posts on fapello.com"""
    category = "fapello"
    subcategory = "post"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{id}.{extension}"
    archive_fmt = "{type}_{model}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?fapello\.com"
               r"/(?!search/|popular_videos/)([^/?#]+)/(\d+)")
    test = (
        ("https://fapello.com/carrykey/530/", {
            "pattern": (r"https://fapello\.com/content/c/a"
                        r"/carrykey/1000/carrykey_0530\.jpg"),
            "keyword": {
                "model": "carrykey",
                "id"   : 530,
                "type" : "photo",
                "thumbnail": "",
            },
        }),
        ("https://fapello.com/vladislava-661/693/", {
            "pattern": (r"https://cdn\.fapello\.com/content/v/l"
                        r"/vladislava-661/1000/vladislava-661_0693\.mp4"),
            "keyword": {
                "model": "vladislava-661",
                "id"   : 693,
                "type" : "video",
                "thumbnail": ("https://fapello.com/content/v/l"
                              "/vladislava-661/1000/vladislava-661_0693.jpg"),
            },
        }),
        ("https://fapello.com/carrykey/000/", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.model, self.id = match.groups()

    def items(self):
        url = "https://fapello.com/{}/{}/".format(self.model, self.id)
        page = text.extr(
            self.request(url, allow_redirects=False).text,
            'class="uk-align-center"', "</div>", None)
        if page is None:
            raise exception.NotFoundError("post")

        data = {
            "model": self.model,
            "id"   : text.parse_int(self.id),
            "type" : "video" if 'type="video' in page else "photo",
            "thumbnail": text.extr(page, 'poster="', '"'),
        }
        url = text.extr(page, 'src="', '"')
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class FapelloModelExtractor(Extractor):
    """Extractor for all posts from a fapello model"""
    category = "fapello"
    subcategory = "model"
    pattern = (r"(?:https?://)?(?:www\.)?fapello\.com"
               r"/(?!top-(?:likes|followers)|popular_videos"
               r"|videos|trending|search/?$)"
               r"([^/?#]+)/?$")
    test = (
        ("https://fapello.com/hyoon/", {
            "pattern": FapelloPostExtractor.pattern,
            "range"  : "1-50",
            "count"  : 50,
        }),
        ("https://fapello.com/kobaebeefboo/"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.model = match.group(1)

    def items(self):
        num = 1
        data = {"_extractor": FapelloPostExtractor}
        while True:
            url = "https://fapello.com/ajax/model/{}/page-{}/".format(
                self.model, num)
            page = self.request(url).text
            if not page:
                return

            for url in text.extract_iter(page, '<a href="', '"'):
                yield Message.Queue, url, data
            num += 1


class FapelloPathExtractor(Extractor):
    """Extractor for models and posts from fapello.com paths"""
    category = "fapello"
    subcategory = "path"
    pattern = (r"(?:https?://)?(?:www\.)?fapello\.com"
               r"/(?!search/?$)(top-(?:likes|followers)|videos|trending"
               r"|popular_videos/[^/?#]+)/?$")
    test = (
        ("https://fapello.com/top-likes/", {
            "pattern": FapelloModelExtractor.pattern,
            "range"  : "1-10",
            "count"  : 10,
        }),
        ("https://fapello.com/videos/", {
            "pattern": FapelloPostExtractor.pattern,
            "range"  : "1-10",
            "count"  : 10,
        }),
        ("https://fapello.com/top-followers/"),
        ("https://fapello.com/trending/"),
        ("https://fapello.com/popular_videos/twelve_hours/"),
        ("https://fapello.com/popular_videos/week/"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def items(self):
        num = 1
        if self.path in ("top-likes", "top-followers"):
            data = {"_extractor": FapelloModelExtractor}
        else:
            data = {"_extractor": FapelloPostExtractor}

        while True:
            page = self.request("https://fapello.com/ajax/{}/page-{}/".format(
                self.path, num)).text
            if not page:
                return

            for item in text.extract_iter(
                    page, 'uk-transition-toggle">', "</a>"):
                yield Message.Queue, text.extr(item, '<a href="', '"'), data
            num += 1
