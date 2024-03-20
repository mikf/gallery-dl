# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fapello.com/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?:www\.)?fapello\.(?:com|su)"


class FapelloPostExtractor(Extractor):
    """Extractor for individual posts on fapello.com"""
    category = "fapello"
    subcategory = "post"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{id}.{extension}"
    archive_fmt = "{type}_{model}_{id}"
    pattern = BASE_PATTERN + r"/(?!search/|popular_videos/)([^/?#]+)/(\d+)"
    example = "https://fapello.com/MODEL/12345/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = text.root_from_url(match.group(0))
        self.model, self.id = match.groups()

    def items(self):
        url = "{}/{}/{}/".format(self.root, self.model, self.id)
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
        url = text.extr(page, 'src="', '"').replace(
            ".md", "").replace(".th", "")
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class FapelloModelExtractor(Extractor):
    """Extractor for all posts from a fapello model"""
    category = "fapello"
    subcategory = "model"
    pattern = (BASE_PATTERN + r"/(?!top-(?:likes|followers)|popular_videos"
               r"|videos|trending|search/?$)"
               r"([^/?#]+)/?$")
    example = "https://fapello.com/model/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = text.root_from_url(match.group(0))
        self.model = match.group(1)

    def items(self):
        num = 1
        data = {"_extractor": FapelloPostExtractor}
        while True:
            url = "{}/ajax/model/{}/page-{}/".format(
                self.root, self.model, num)
            page = self.request(url).text
            if not page:
                return

            for url in text.extract_iter(page, '<a href="', '"'):
                if url == "javascript:void(0);":
                    continue
                yield Message.Queue, url, data
            num += 1


class FapelloPathExtractor(Extractor):
    """Extractor for models and posts from fapello.com paths"""
    category = "fapello"
    subcategory = "path"
    pattern = (BASE_PATTERN +
               r"/(?!search/?$)(top-(?:likes|followers)|videos|trending"
               r"|popular_videos/[^/?#]+)/?$")
    example = "https://fapello.com/trending/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = text.root_from_url(match.group(0))
        self.path = match.group(1)

    def items(self):
        num = 1
        if self.path in ("top-likes", "top-followers"):
            data = {"_extractor": FapelloModelExtractor}
        else:
            data = {"_extractor": FapelloPostExtractor}

        if "fapello.su" in self.root:
            self.path = self.path.replace("-", "/")
            if self.path == "trending":
                data = {"_extractor": FapelloModelExtractor}

        while True:
            page = self.request("{}/ajax/{}/page-{}/".format(
                self.root, self.path, num)).text
            if not page:
                return

            for item in text.extract_iter(
                    page, 'uk-transition-toggle">', "</a>"):
                yield Message.Queue, text.extr(item, '<a href="', '"'), data
            num += 1
