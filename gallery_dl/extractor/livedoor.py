# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
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
        tags = text.extract(body, '</dt><dd>', '</dl>')[0]

        return {
            "id"        : text.parse_int(extr("id : '", "'")),
            "title"     : text.unescape(extr("title : '", "'")),
            "categories": [extr("name:'", "'"), extr("name:'", "'")],
            "date"      : text.parse_datetime(
                extr("date : '", "'"), "%Y-%m-%d %H:%M:%S"),
            "tags"      : text.split_html(tags),
            "user"      : self.user,
            "body"      : body,
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
                url = src.replace("-s.", ".")
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
            "pattern": r"https?://livedoor.blogimg.jp/\w+/imgs/\w/\w/\w+\.\w+",
            "keyword": {
                "post": {
                    "categories": list,
                    "date": "type:datetime",
                    "id": int,
                    "tags": list,
                    "title": str,
                    "user": "zatsu_ke"
                },
                "filename": str,
                "hash": r"re:\w{4,}",
                "num": int,
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
                data = extr('.articles.push(', ');')
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
            "url": "8826fe623f19dc868e7538e8519bf8491e92a0a2",
            "keyword": "52fcba9253a000c339bcd658572d252e282626af",
        }),
        ("http://blog.livedoor.jp/amaumauma/archives/7835811.html", {
            "url": "fc1d6a9557245b5a27d3a10bf0fa9922ef377215",
            "keyword": "0229072abb5cd8a221df72e0ffdfc13336c0e9ce",
        }),
        ("http://blog.livedoor.jp/uotapo/archives/1050616939.html", {
            "url": "3f3581807ec4776e6a67ed7985a22494d4bc4904",
            "keyword": "2eb3e383c68e909c4dd3d563c16d0b6e2fe6627b",
        }),
    )

    def __init__(self, match):
        LivedoorExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/{}/archives/{}.html".format(
            self.root, self.user, self.post_id)
        extr = text.extract_from(self.request(url).text)
        data = extr('articles :', '</script>')
        body = extr('class="article-body-inner">',
                    'class="article-footer">')
        return (self._load(data, body),)
