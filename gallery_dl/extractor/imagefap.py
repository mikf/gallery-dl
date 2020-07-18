# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
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
            "pattern": r"https://cdn.imagefap.com/images/full/\d+/\d+/\d+.jpg",
            "keyword": "2ba96e84c2952c4750e9fa94a3f2b1f965cec2f3",
            "content": "694a0a57385980a6f90fbc296cadcd6c11ba2dab",
        }),
        ("https://www.imagefap.com/gallery/5486966", {
            "pattern": r"https://cdn.imagefap.com/images/full/\d+/\d+/\d+.jpg",
            "keyword": "3e24eace5b09639b881ebd393165862feb46adde",
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
        yield Message.Version, 1
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
        return {
            "gallery_id": text.parse_int(self.gid),
            "title": text.unescape(title),
            "uploader": uploader,
            "tags": tags[:-11].split(", "),
            "count": text.parse_int(count),
        }

    def get_images(self):
        """Collect image-urls and -metadata"""
        num = 0
        url = "{}/photo/{}/".format(self.root, self.image_id)
        params = {"gid": self.gid, "idx": 0, "partial": "true"}
        while True:
            pos = 0
            page = self.request(url, params=params).text
            for _ in range(24):
                imgurl, pos = text.extract(page, '<a href="', '"', pos)
                if not imgurl:
                    return
                num += 1
                data = text.nameext_from_url(imgurl)
                data["num"] = num
                data["image_id"] = text.parse_int(data["filename"])
                yield imgurl, data
            params["idx"] += 24


class ImagefapImageExtractor(ImagefapExtractor):
    """Extractor for single images from imagefap.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    test = (
        ("https://www.imagefap.com/photo/1369341772/", {
            "pattern": r"https://cdn.imagefap.com/images/full/\d+/\d+/\d+.jpg",
            "keyword": "8894e45f7262020d8d66ce59917315def1fc475b",
        }),
        ("https://beta.imagefap.com/photo/1369341772/"),
    )

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        url, data = self.get_image()
        yield Message.Version, 1
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
               r"/(?:profile(?:\.php\?user=|/)([^/?&#]+)"
               r"|usergallery\.php\?userid=(\d+))")
    test = (
        ("https://www.imagefap.com/profile/LucyRae/galleries", {
            "url": "d941aa906f56a75972a7a5283030eb9a8d27a4fd",
        }),
        ("https://www.imagefap.com/usergallery.php?userid=1862791", {
            "url": "d941aa906f56a75972a7a5283030eb9a8d27a4fd",
        }),
        ("https://www.imagefap.com/profile.php?user=LucyRae"),
        ("https://beta.imagefap.com/profile.php?user=LucyRae"),
    )

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.user, self.user_id = match.groups()

    def items(self):
        yield Message.Version, 1
        for gid, name in self.get_gallery_data():
            url = "{}/gallery/{}".format(self.root, gid)
            data = {
                "gallery_id": text.parse_int(gid),
                "title": text.unescape(name),
                "_extractor": ImagefapGalleryExtractor,
            }
            yield Message.Queue, url, data

    def get_gallery_data(self):
        """Yield all gallery_ids of a specific user"""
        folders = self.get_gallery_folders()
        url = "{}/ajax_usergallery_folder.php".format(self.root)
        params = {"userid": self.user_id}
        for folder_id in folders:
            params["id"] = folder_id
            page = self.request(url, params=params).text

            pos = 0
            while True:
                gid, pos = text.extract(page, '<a  href="/gallery/', '"', pos)
                if not gid:
                    break
                name, pos = text.extract(page, "<b>", "<", pos)
                yield gid, name

    def get_gallery_folders(self):
        """Create a list of all folder_ids of a specific user"""
        if self.user:
            url = "{}/profile/{}/galleries".format(self.root, self.user)
        else:
            url = "{}/usergallery.php?userid={}".format(
                self.root, self.user_id)
        page = self.request(url).text
        self.user_id, pos = text.extract(page, '?userid=', '"')
        folders, pos = text.extract(page, ' id="tgl_all" value="', '"', pos)
        return folders.split("|")[:-1]
