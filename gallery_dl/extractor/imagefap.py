# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagefap.com/"""

from .common import Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.|beta\.)?imagefap\.com"


class ImagefapExtractor(Extractor):
    """Base class for imagefap extractors"""
    category = "imagefap"
    root = "https://www.imagefap.com"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = "{category}_{gallery_id}_{filename}.{extension}"
    archive_fmt = "{gallery_id}_{image_id}"
    request_interval = (2.0, 4.0)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history and response.url.endswith("/human-verification"):
            msg = text.extr(response.text, '<div class="mt-4', '<')
            if msg:
                msg = " ".join(msg.partition(">")[2].split())
                raise exception.StopExtraction("'%s'", msg)
            self.log.warning("HTTP redirect to %s", response.url)

        return response


class ImagefapGalleryExtractor(ImagefapExtractor):
    """Extractor for image galleries from imagefap.com"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/(?:gallery\.php\?gid=|gallery/|pictures/)(\d+)"
    example = "https://www.imagefap.com/gallery/12345"

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.gid = match.group(1)
        self.image_id = ""

    def items(self):
        url = "{}/gallery/{}".format(self.root, self.gid)
        page = self.request(url).text
        data = self.get_job_metadata(page)
        yield Message.Directory, data
        for url, image in self.get_images():
            data.update(image)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        extr = text.extract_from(page)

        data = {
            "gallery_id": text.parse_int(self.gid),
            "uploader": extr("porn picture gallery by ", " to see hottest"),
            "title": text.unescape(extr("<title>", "<")),
            "description": text.unescape(extr(
                'id="gdesc_text"', '<').partition(">")[2]),
            "categories": text.split_html(extr(
                'id="cnt_cats"', '</div>'))[1::2],
            "tags": text.split_html(extr(
                'id="cnt_tags"', '</div>'))[1::2],
            "count": text.parse_int(extr(' 1 of ', ' pics"')),
        }

        self.image_id = extr('id="img_ed_', '"')
        self._count = data["count"]

        return data

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

            if not cnt or cnt < 24 and num >= total:
                return
            params["idx"] += cnt


class ImagefapImageExtractor(ImagefapExtractor):
    """Extractor for single images from imagefap.com"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/(\d+)"
    example = "https://www.imagefap.com/photo/12345"

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

        url, pos = text.extract(
            page, 'original="', '"')
        info, pos = text.extract(
            page, '<script type="application/ld+json">', '</script>', pos)
        image_id, pos = text.extract(
            page, 'id="imageid_input" value="', '"', pos)
        gallery_id, pos = text.extract(
            page, 'id="galleryid_input" value="', '"', pos)
        info = util.json_loads(info)

        return url, text.nameext_from_url(url, {
            "title": text.unescape(info["name"]),
            "uploader": info["author"],
            "date": info["datePublished"],
            "width": text.parse_int(info["width"]),
            "height": text.parse_int(info["height"]),
            "gallery_id": text.parse_int(gallery_id),
            "image_id": text.parse_int(image_id),
        })


class ImagefapFolderExtractor(ImagefapExtractor):
    """Extractor for imagefap user folders"""
    subcategory = "folder"
    pattern = (BASE_PATTERN + r"/(?:organizer/|"
               r"(?:usergallery\.php\?user(id)?=([^&#]+)&"
               r"|profile/([^/?#]+)/galleries\?)folderid=)(\d+|-1)")
    example = "https://www.imagefap.com/organizer/12345"

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self._id, user, profile, self.folder_id = match.groups()
        self.user = user or profile

    def items(self):
        for gallery_id, name, folder in self.galleries(self.folder_id):
            url = "{}/gallery/{}".format(self.root, gallery_id)
            data = {
                "gallery_id": gallery_id,
                "title"     : text.unescape(name),
                "folder"    : text.unescape(folder),
                "_extractor": ImagefapGalleryExtractor,
            }
            yield Message.Queue, url, data

    def galleries(self, folder_id):
        """Yield gallery IDs and titles of a folder"""
        if folder_id == "-1":
            folder_name = "Uncategorized"
            if self._id:
                url = "{}/usergallery.php?userid={}&folderid=-1".format(
                    self.root, self.user)
            else:
                url = "{}/profile/{}/galleries?folderid=-1".format(
                    self.root, self.user)
        else:
            folder_name = None
            url = "{}/organizer/{}/".format(self.root, folder_id)

        params = {"page": 0}
        extr = text.extract_from(self.request(url, params=params).text)
        if not folder_name:
            folder_name = extr("class'blk_galleries'><b>", "</b>")

        while True:
            cnt = 0

            while True:
                gid = extr(' id="gid-', '"')
                if not gid:
                    break
                yield gid, extr("<b>", "<"), folder_name
                cnt += 1

            if cnt < 20:
                break
            params["page"] += 1
            extr = text.extract_from(self.request(url, params=params).text)


class ImagefapUserExtractor(ImagefapExtractor):
    """Extractor for an imagefap user profile"""
    subcategory = "user"
    pattern = (BASE_PATTERN +
               r"/(?:profile(?:\.php\?user=|/)([^/?#]+)(?:/galleries)?"
               r"|usergallery\.php\?userid=(\d+))(?:$|#)")
    example = "https://www.imagefap.com/profile/USER"

    def __init__(self, match):
        ImagefapExtractor.__init__(self, match)
        self.user, self.user_id = match.groups()

    def items(self):
        data = {"_extractor": ImagefapFolderExtractor}

        for folder_id in self.folders():
            if folder_id == "-1":
                url = "{}/profile/{}/galleries?folderid=-1".format(
                    self.root, self.user)
            else:
                url = "{}/organizer/{}/".format(self.root, folder_id)
            yield Message.Queue, url, data

    def folders(self):
        """Return a list of folder IDs of a user"""
        if self.user:
            url = "{}/profile/{}/galleries".format(self.root, self.user)
        else:
            url = "{}/usergallery.php?userid={}".format(
                self.root, self.user_id)

        response = self.request(url)
        self.user = response.url.split("/")[-2]
        folders = text.extr(response.text, ' id="tgl_all" value="', '"')
        return folders.rstrip("|").split("|")
