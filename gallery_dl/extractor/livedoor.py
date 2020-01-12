# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
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
        yield Message.Version, 1
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
        tags = text.extract(body, 'class="article-tags">', '</dl>')[0]
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
            src = text.extract(img, 'src="', '"')[0]
            alt = text.extract(img, 'alt="', '"')[0]

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
    pattern = r"(?:https?://)?blog\.livedoor\.jp/(\w+)/?(?:$|[?&#])"
    test = (
        ("http://blog.livedoor.jp/zatsu_ke/", {
            "range": "1-50",
            "count": 50,
            "archive": False,
            "pattern": r"https?://livedoor.blogimg.jp/\w+/imgs/\w/\w/\w+\.\w+",
            "keyword": {
                "post": {
                    "categories" : tuple,
                    "date"       : "type:datetime",
                    "description": str,
                    "id"         : int,
                    "tags"       : list,
                    "title"      : str,
                    "user"       : "zatsu_ke"
                },
                "filename": str,
                "hash"    : r"re:\w{4,}",
                "num"     : int,
            },
        }),
        ("http://blog.livedoor.jp/uotapo/", {
            "range": "1-5",
            "count": 5,
        }),
    )

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
    test = (
        ("http://blog.livedoor.jp/zatsu_ke/archives/51493859.html", {
            "url": "9ca3bbba62722c8155be79ad7fc47be409e4a7a2",
            "keyword": "1f5b558492e0734f638b760f70bfc0b65c5a97b9",
        }),
        ("http://blog.livedoor.jp/amaumauma/archives/7835811.html", {
            "url": "204bbd6a9db4969c50e0923855aeede04f2e4a62",
            "keyword": "05821c7141360e6057ef2d382b046f28326a799d",
        }),
        ("http://blog.livedoor.jp/uotapo/archives/1050616939.html", {
            "url": "4b5ab144b7309eb870d9c08f8853d1abee9946d2",
            "keyword": "84fbf6e4eef16675013d6333039a7cfcb22c2d50",
        }),
    )

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
