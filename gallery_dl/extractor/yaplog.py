# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yaplog.jp/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, util


BASE_PATTERN = r"(?:https?://)?(?:www\.)?yaplog\.jp/([\w-]+)"


class YaplogExtractor(AsynchronousMixin, Extractor):
    """Base class for yaplog extractors"""
    category = "yaplog"
    root = "https://yaplog.jp"
    filename_fmt = "{post[id]}_{post[title]}_{id}.{extension}"
    directory_fmt = ("{category}", "{post[user]}")
    archive_fmt = "{post[user]}_{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        yield Message.Version, 1
        for post, urls in self.posts():
            yield Message.Directory, {"post": post}
            for num, url in enumerate(urls, 1):
                page = self.request(url).text if num > 1 else url
                iurl = text.extract(page, '<img src="', '"')[0]
                if iurl[0] == "/":
                    iurl = text.urljoin(self.root, iurl)
                name, _, ext = iurl.rpartition("/")[2].rpartition(".")
                iid = name.rpartition("_")[0] or name
                image = {
                    "url"      : iurl,
                    "num"      : num,
                    "id"       : text.parse_int(iid, iid),
                    "filename" : name,
                    "extension": ext,
                    "post"     : post,
                }
                yield Message.Url, iurl, image

    def posts(self):
        """Return an iterable with (data, image page URLs) tuples"""

    def _parse_post(self, url):
        page = self.request(url).text
        title, pos = text.extract(page, 'class="title">', '<')
        date , pos = text.extract(page, 'class="date">' , '<', pos)
        pid  , pos = text.extract(page, '/archive/'     , '"', pos)
        prev , pos = text.extract(page, 'class="last"><a href="', '"', pos)

        urls = list(text.extract_iter(page, '<li><a href="', '"', pos))
        if urls:
            urls[0] = page  # cache HTML of first page

        if len(urls) == 24 and text.extract(page, '(1/', ')')[0] != '24':
            # there are a maximum of 24 image entries in an /image/ page
            # -> search /archive/ page for the rest
            url = "{}/{}/archive/{}".format(self.root, self.user, pid)
            page = self.request(url).text

            base = "{}/{}/image/{}/".format(self.root, self.user, pid)
            for part in util.advance(text.extract_iter(
                    page, base, '"', pos), 24):
                urls.append(base + part)

        return prev, urls, {
            "id"   : text.parse_int(pid),
            "title": text.unescape(title[:-3]),
            "user" : self.user,
            "date" : text.parse_datetime(date, "%B %d [%a], %Y, %H:%M"),
        }


class YaplogBlogExtractor(YaplogExtractor):
    """Extractor for a user's blog on yaplog.jp"""
    subcategory = "blog"
    pattern = BASE_PATTERN + r"/?(?:$|[?&#])"
    test = ("https://yaplog.jp/omitakashi3", {
        "pattern": r"https://img.yaplog.jp/img/18/pc/o/m/i/omitakashi3/0/",
        "count": ">= 2",
    })

    def posts(self):
        url = "{}/{}/image/".format(self.root, self.user)
        while url:
            url, images, data = self._parse_post(url)
            yield data, images


class YaplogPostExtractor(YaplogExtractor):
    """Extractor for images from a blog post on yaplog.jp"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:archive|image)/(\d+)"
    test = (
        ("https://yaplog.jp/imamiami0726/image/1299", {
            "url": "896cae20fa718735a57e723c48544e830ff31345",
            "keyword": "22df8ad6cb534514c6bb2ff000381d156769a620",
        }),
        # complete image URLs (#443)
        ("https://yaplog.jp/msjane/archive/246", {
            "pattern": r"https://yaplog.jp/cv/msjane/img/246/img\d+_t.jpg"
        }),
        # empty post (#443)
        ("https://yaplog.jp/f_l_a_s_c_o/image/872", {
            "count": 0,
        }),
        # blog names with '-' (#443)
        ("https://yaplog.jp/a-pierrot-o/image/3946/22779"),
    )

    def __init__(self, match):
        YaplogExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/{}/image/{}".format(self.root, self.user, self.post_id)
        _, images, data = self._parse_post(url)
        return ((data, images),)
