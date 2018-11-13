# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.behance.net/"""

from .common import Extractor, Message
from .. import text


class BehanceExtractor(Extractor):
    """Base class for behance extractors"""
    category = "behance"
    root = "https://www.behance.net"


class BehanceGalleryExtractor(BehanceExtractor):
    """Extractor for image galleries from www.behance.net"""
    subcategory = "gallery"
    directory_fmt = ["{category}", "{user}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>02}.{extension}"
    archive_fmt = "{gallery_id}_{num}"
    pattern = [r"(?:https?://)?(?:www\.)?behance\.net/gallery/(\d+)"]
    test = [
        ("https://www.behance.net/gallery/17386197/A-Short-Story", {
            "count": 2,
            "url": "ebe032f78e8af98f9873f85eb77a1e49a3f8e648",
            "keyword": {
                "title": 're:"Hi". A short story about the important things ',
                "user": "Place Studio, Julio César Velazquez",
                "fields": ["Animation", "Character Design", "Directing"],
                "date": 1401810111,
                "views": int,
                "votes": int,
                "comments": int,
            },
        }),
        ("https://www.behance.net/gallery/21324767/Nevada-City", {
            "count": 6,
            "url": "2b2a689d57f113617088eeab4dc81b884bf24410",
            "keyword": {"user": "Alex Strohl"},
        }),
    ]

    def __init__(self, match):
        BehanceExtractor.__init__(self)
        self.gallery_id = match.group(1)

    def items(self):
        url = "{}/gallery/{}/a".format(self.root, self.gallery_id)
        page = self.request(url, cookies={"ilo0": "true"}).text

        data = self.get_metadata(page)
        imgs = self.get_images(page)
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        users, pos = text.extract(
            page, 'class="project-owner-info ', 'class="project-owner-actions')
        title, pos = text.extract(
            page, 'project-title">', '</div>', pos)
        fields, pos = text.extract(
            page, '<ul id="project-fields-list">', '</ul>', pos)
        stats, pos = text.extract(
            page, '<div id="project-stats">', 'Published', pos)
        date, pos = text.extract(
            page, ' data-timestamp="', '"', pos)

        users = self._parse_userinfo(users)
        stats = text.split_html(stats)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title": text.unescape(title or ""),
            "user": ", ".join(users),
            "fields": [f for f in text.split_html(fields) if f != ", "],
            "date": text.parse_int(date),
            "views": text.parse_int(stats[0]),
            "votes": text.parse_int(stats[1]),
            "comments": text.parse_int(stats[2]),
        }

    @staticmethod
    def get_images(page):
        """Extract and return a list of all image- and external urls"""
        results = []
        for p in text.extract_iter(page, "js-lightbox-slide-content", "<a "):
            srcset = text.extract(p, 'srcset="', '"')[0]
            if srcset:
                url = srcset.rstrip(",").rpartition(",")[2].partition(" ")[0]
                results.append(url)
            elif "<iframe " in p:
                url = text.extract(p, ' src="', '"')[0]
                results.append("ytdl:" + text.unescape(url))
        return results

    @staticmethod
    def _parse_userinfo(users):
        if users.startswith("multiple"):
            return [
                text.remove_html(user)
                for user in text.extract_iter(
                    users, '<div class="rf-profile-item__info">', '</a>',
                )
            ]

        user = text.extract(users, ' class="profile-list-name"', '</a>')[0]
        return (user.rpartition(">")[2],)


class BehanceUserExtractor(BehanceExtractor):
    """Extractor for a user's galleries from www.behance.net"""
    subcategory = "user"
    categorytransfer = True
    pattern = [r"(?:https?://)?(?:www\.)?behance\.net"
               r"/(?!gallery/)([^/?&#]+)/?$"]
    test = [("https://www.behance.net/alexstrohl", {
        "count": ">= 8",
        "pattern": BehanceGalleryExtractor.pattern[0],
    })]

    def __init__(self, match):
        BehanceExtractor.__init__(self)
        self.user = match.group(1)

    def items(self):
        url = "{}/{}".format(self.root, self.user)
        headers = {"X-Requested-With": "XMLHttpRequest"}
        params = {"offset": None}

        yield Message.Version, 1
        while True:
            data = self.request(url, headers=headers, params=params).json()

            for gallery in data["section_content"]:
                yield Message.Queue, gallery["url"], gallery

            if "offset" not in data:
                return
            params["offset"] = data["offset"]
