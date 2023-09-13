# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://blog.livedoor.jp/"""

from .common import Extractor, Message
from .. import text


class LivedoorExtractor(Extractor):
    """Base class for livedoor extractors"""
    category = "livedoor"
    root = "http://blog.livedoor.jp"
    filename_fmt = "{post[id]}_{post[title]}_{num:>02}.{extension}"
    directory_fmt = ("{category}", "{post[user]}")
    archive_fmt = "{post[id]}_{hash}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        for post in self.posts():
            images = self._images(post)
            if images:
                yield Message.Directory, {"post": post}
                for image in images:
                    yield Message.Url, image["url"], image

    def posts(self):
        """Return an iterable with post objects"""

    def _load(self, data, body):
        extr = text.extract_from(data)
        tags = text.extr(body, 'class="article-tags">', '</dl>')
        about = extr('rdf:about="', '"')

        return {
            "id"         : text.parse_int(
                about.rpartition("/")[2].partition(".")[0]),
            "title"      : text.unescape(extr('dc:title="', '"')),
            "categories" : extr('dc:subject="', '"').partition(",")[::2],
            "description": extr('dc:description="', '"'),
            "date"       : text.parse_datetime(extr('dc:date="', '"')),
            "tags"       : text.split_html(tags)[1:] if tags else [],
            "user"       : self.user,
            "body"       : body,
        }

    def _images(self, post):
        imgs = []
        body = post.pop("body")

        for num, img in enumerate(text.extract_iter(body, "<img ", ">"), 1):
            src = text.extr(img, 'src="', '"')
            alt = text.extr(img, 'alt="', '"')

            if not src:
                continue
            if "://livedoor.blogimg.jp/" in src:
                url = src.replace("http:", "https:", 1).replace("-s.", ".")
            else:
                url = text.urljoin(self.root, src)
            name, _, ext = url.rpartition("/")[2].rpartition(".")

            imgs.append({
                "url"      : url,
                "num"      : num,
                "hash"     : name,
                "filename" : alt or name,
                "extension": ext,
                "post"     : post,
            })

        return imgs


class LivedoorBlogExtractor(LivedoorExtractor):
    """Extractor for a user's blog on blog.livedoor.jp"""
    subcategory = "blog"
    pattern = r"(?:https?://)?blog\.livedoor\.jp/(\w+)/?(?:$|[?#])"
    example = "http://blog.livedoor.jp/USER/"

    def posts(self):
        url = "{}/{}".format(self.root, self.user)
        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                data = extr('<rdf:RDF', '</rdf:RDF>')
                if not data:
                    break
                body = extr('class="article-body-inner">',
                            'class="article-footer">')
                yield self._load(data, body)
            url = extr('<a rel="next" href="', '"')


class LivedoorPostExtractor(LivedoorExtractor):
    """Extractor for images from a blog post on blog.livedoor.jp"""
    subcategory = "post"
    pattern = r"(?:https?://)?blog\.livedoor\.jp/(\w+)/archives/(\d+)"
    example = "http://blog.livedoor.jp/USER/archives/12345.html"

    def __init__(self, match):
        LivedoorExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/{}/archives/{}.html".format(
            self.root, self.user, self.post_id)
        extr = text.extract_from(self.request(url).text)
        data = extr('<rdf:RDF', '</rdf:RDF>')
        body = extr('class="article-body-inner">', 'class="article-footer">')
        return (self._load(data, body),)
