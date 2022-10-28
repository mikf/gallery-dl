# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagefap.com/"""

from .common import Extractor, Message
from .. import text
import json


BASE_PATTERN = r"(?:https?://)?(?:www\.|beta\.)?imagefap\.com"


class ImagefapExtractor(Extractor):
    """Base class for imagefap extractors"""
    category = "imagefap"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = "{category}_{gallery_id}_{filename}.{extension}"
    archive_fmt = "{gallery_id}_{image_id}"
    root = "https://www.imagefap.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root


class ImagefapGalleryExtractor(ImagefapExtractor):
    """Extractor for image galleries from imagefap.com"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/(?:gallery\.php\?gid=|gallery/|pictures/)(\d+)"

    test = (
        ("https://www.imagefap.com/pictures/7102714", {
            "pattern": r"https://cdnh?\.imagefap\.com"
                       r"/images/full/\d+/\d+/\d+\.jpg",
            "keyword": "2ba96e84c2952c4750e9fa94a3f2b1f965cec2f3",
            "content": "694a0a57385980a6f90fbc296cadcd6c11ba2dab",
        }),
        ("https://www.imagefap.com/gallery/5486966", {
            "pattern": r"https://cdnh?\.imagefap\.com"
                       r"/images/full/\d+/\d+/\d+\.jpg",
            "keyword": "8d2e562df7a0bc9e8eecb9d1bb68d32b4086bf98",
            "archive": False,
            "count": 62,
        }),
        ("https://www.imagefap.com/gallery.php?gid=7102714"),
        ("https://beta.imagefap.com/gallery.php?gid=7102714"),
    )

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.gid = match.group(1)
        self.image_id = ""

    def items(self):
        url = "{}/pictures/{}/".format(self.root, self.gid)
        page = self.request(url).text
        data = self.get_job_metadata(page)
        yield Message.Directory, data
        for url, image in self.get_images():
            data.update(image)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        descr, pos = text.extract(
            page, '<meta name="description" content="Browse ', '"')
        count, pos = text.extract(page, ' 1 of ', ' pics"', pos)
        self.image_id = text.extract(page, 'id="img_ed_', '"', pos)[0]

        title, _, descr = descr.partition(" porn picture gallery by ")
        uploader, _, tags = descr.partition(" to see hottest ")
        self._count = text.parse_int(count)
        return {
            "gallery_id": text.parse_int(self.gid),
            "title": text.unescape(title),
            "uploader": uploader,
            "tags": tags[:-11].split(", "),
            "count": self._count,
        }

    def get_images(self):
        """Collect image-urls and -metadata"""
        url = "{}/photo/{}/".format(self.root, self.image_id)
        params = {"gid": self.gid, "idx": 0, "partial": "true"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "{}?pgid=&gid={}&page=0".format(url, self.image_id)
        }

        num = 0
        total = self._count
        while True:
            page = self.request(url, params=params, headers=headers).text

            cnt = 0
            for image_url in text.extract_iter(page, '<a href="', '"'):
                num += 1
                cnt += 1
                data = text.nameext_from_url(image_url)
                data["num"] = num
                data["image_id"] = text.parse_int(data["filename"])
                yield image_url, data

            if cnt < 24 and num >= total:
                return
            params["idx"] += cnt


class ImagefapImageExtractor(ImagefapExtractor):
    """Extractor for single images from imagefap.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    test = (
        ("https://www.imagefap.com/photo/1369341772/", {
            "pattern": r"https://cdnh?\.imagefap\.com"
                       r"/images/full/\d+/\d+/\d+\.jpg",
            "keyword": "8894e45f7262020d8d66ce59917315def1fc475b",
        }),
        ("https://beta.imagefap.com/photo/1369341772/"),
    )

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        url, data = self.get_image()
        yield Message.Directory, data
        yield Message.Url, url, data

    def get_image(self):
        url = "{}/photo/{}/".format(self.root, self.image_id)
        page = self.request(url).text

        info, pos = text.extract(
            page, '<script type="application/ld+json">', '</script>')
        image_id, pos = text.extract(
            page, 'id="imageid_input" value="', '"', pos)
        gallery_id, pos = text.extract(
            page, 'id="galleryid_input" value="', '"', pos)
        info = json.loads(info)
        url = info["contentUrl"]

        return url, text.nameext_from_url(url, {
            "title": text.unescape(info["name"]),
            "uploader": info["author"],
            "date": info["datePublished"],
            "width": text.parse_int(info["width"]),
            "height": text.parse_int(info["height"]),
            "gallery_id": text.parse_int(gallery_id),
            "image_id": text.parse_int(image_id),
        })


class ImagefapUserExtractor(ImagefapExtractor):
    """Extractor for all galleries from a user at imagefap.com"""
    subcategory = "user"
    categorytransfer = True
    pattern = (BASE_PATTERN +
               r"/(?:profile(?:\.php\?user=|/)([^/?#]+)"
               r"|usergallery\.php\?userid=(\d+))")
    test = (
        ("https://www.imagefap.com/profile/LucyRae/galleries", {
            "url": "822cb6cbb6f474ca2d0f58d1d6d253bc2338937a",
        }),
        ("https://www.imagefap.com/usergallery.php?userid=1862791", {
            "url": "822cb6cbb6f474ca2d0f58d1d6d253bc2338937a",
        }),
        ("https://www.imagefap.com/profile.php?user=LucyRae"),
        ("https://beta.imagefap.com/profile.php?user=LucyRae"),
    )

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.user, self.user_id = match.groups()

    def items(self):
        for folder_id in self.folders():
            for gallery_id, name in self.galleries(folder_id):
                url = "{}/gallery/{}".format(self.root, gallery_id)
                data = {
                    "gallery_id": text.parse_int(gallery_id),
                    "title"     : text.unescape(name),
                    "_extractor": ImagefapGalleryExtractor,
                }
                yield Message.Queue, url, data

    def folders(self):
        """Return a list of folder_ids of a specific user"""
        if self.user:
            url = "{}/profile/{}/galleries".format(self.root, self.user)
        else:
            url = "{}/usergallery.php?userid={}".format(
                self.root, self.user_id)

        response = self.request(url)
        self.user = response.url.split("/")[-2]
        folders = text.extract(response.text, ' id="tgl_all" value="', '"')[0]
        return folders.rstrip("|").split("|")

    def galleries(self, folder_id):
        """Yield gallery_ids of a folder"""
        if folder_id == "-1":
            url = "{}/profile/{}/galleries?folderid=-1".format(
                self.root, self.user)
        else:
            url = "{}/organizer/{}/".format(self.root, folder_id)
        params = {"page": 0}

        while True:
            extr = text.extract_from(self.request(url, params=params).text)
            cnt = 0

            while True:
                gid = extr('<a  href="/gallery/', '"')
                if not gid:
                    break
                yield gid, extr("<b>", "<")
                cnt += 1

            if cnt < 25:
                break
            params["page"] += 1
