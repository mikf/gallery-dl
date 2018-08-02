# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.behance.net/"""

from .common import Extractor, Message
from .. import text


class BehanceGalleryExtractor(Extractor):
    """Extractor for image galleries from www.behance.net"""
    category = "behance"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{user}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>02}.{extension}"
    archive_fmt = "{gallery_id}_{num}"
    root = "https://www.behance.net"
    pattern = [r"(?:https?://)?(?:www\.)?behance\.net/gallery/(\d+)"]
    test = [
        ("https://www.behance.net/gallery/17386197", {
            "count": 2,
            "url": "8c692c208b74fed789288eda9230715be8d02057",
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
        ("https://www.behance.net/gallery/13706563/Fundacja-ING-Dzieciom", {
            "count": 7,
            "url": "3b78be2a5652524529962cf2dc81b383129c1363",
            "keyword": {"user": "UVMW Studio"},
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gallery_id = match.group(1)

    def items(self):
        url = "{}/gallery/{}/a".format(self.root, self.gallery_id)
        page = self.request(url, cookies={"ilo0": "true"}).text

        data = self.get_metadata(page)
        imgs = self.get_images(page)
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], (url, external) in enumerate(imgs, 1):
            if external:
                yield Message.Queue, url, data
            else:
                yield Message.Url, url, text.nameext_from_url(url, data)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        users, pos = text.extract(
            page, 'class="project-owner-info ', 'class="project-owner-actions')
        title, pos = text.extract(
            page, '<div class="project-title">', '</div>', pos)
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
            "title": text.unescape(title),
            "user": ", ".join(users),
            "fields": text.split_html(fields),
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
                results.append((url, False))
            elif "<iframe " in p:
                url = text.extract(p, ' src="', '"')[0]
                results.append((text.unescape(url), True))
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
