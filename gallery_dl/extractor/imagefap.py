# -*- coding: utf-8 -*-

# Copyright 2016-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagefap.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.|beta\.)?imagefap\.com"


class ImagefapExtractor(Extractor):
    """Base class for imagefap extractors"""
    category = "imagefap"
    root = "https://www.imagefap.com"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = ("{category}_{gallery_id}_{num:?/_/>04}"
                    "{filename}.{extension}")
    archive_fmt = "{gallery_id}_{image_id}"
    request_interval = (2.0, 4.0)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history and response.url.endswith("/human-verification"):
            self.log.warning("HTTP redirect to '%s'", response.url)
            if msg := text.extr(response.text, '<div class="mt-4', '<'):
                msg = " ".join(msg.partition(">")[2].split())
                raise exception.AbortExtraction(f"'{msg}'")

        return response


class ImagefapGalleryExtractor(ImagefapExtractor):
    """Extractor for image galleries from imagefap.com"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/(?:gallery\.php\?gid=|gallery/|pictures/)(\d+)"
    example = "https://www.imagefap.com/gallery/12345"

    def items(self):
        self.gid = self.groups[0]
        url = f"{self.root}/gallery/{self.gid}"
        page = self.request(url).text
        data = self.get_job_metadata(page)
        yield Message.Directory, "", data
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
        url = f"{self.root}/photo/{self.image_id}/"
        params = {"gid": self.gid, "idx": 0, "partial": "true"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{url}?pgid=&gid={self.image_id}&page=0"
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

    def items(self):
        url, data = self.get_image()
        yield Message.Directory, "", data
        yield Message.Url, url, data

    def get_image(self):
        url = f"{self.root}/photo/{self.groups[0]}/"
        page = self.request(url).text

        url, pos = text.extract(
            page, 'original="', '"')
        image_id, pos = text.extract(
            page, 'id="imageid_input" value="', '"', pos)
        gallery_id, pos = text.extract(
            page, 'id="galleryid_input" value="', '"', pos)
        info = self._extract_jsonld(page)

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
               r"|profile/([^/?#]+)/galleries\?)folderid=(?!0\b))(\d+|-1)")
    example = "https://www.imagefap.com/organizer/12345"

    def items(self):
        for gallery_id, name, folder in self.galleries():
            url = f"{self.root}/gallery/{gallery_id}"
            data = {
                "gallery_id": gallery_id,
                "title"     : text.unescape(name),
                "folder"    : text.unescape(folder),
                "_extractor": ImagefapGalleryExtractor,
            }
            yield Message.Queue, url, data

    def galleries(self):
        """Yield gallery IDs and titles of a folder"""
        _id, user, profile, folder_id = self.groups

        if folder_id == "-1":
            folder_name = "Uncategorized"
            if _id:
                url = (f"{self.root}/usergallery.php"
                       f"?userid={user}&folderid=-1")
            else:
                url = (f"{self.root}/profile/"
                       f"{user or profile}/galleries?folderid=-1")
        else:
            folder_name = None
            url = f"{self.root}/organizer/{folder_id}/"

        params = {"page": 0}
        extr = text.extract_from(self.request(url, params=params).text)
        if folder_name is None:
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
               r"/(?:profile(?:\.php\?user=|/)([^/?#]+)"
               r"(?:/galleries(?:\?folderid=0)?)?"
               r"|usergallery\.php\?userid=(\d+))(?:$|#)")
    example = "https://www.imagefap.com/profile/USER"

    def items(self):
        data = {"_extractor": ImagefapFolderExtractor}

        for folder_id in self.folders():
            if folder_id == "-1":
                url = (f"{self.root}/profile/{self.user}/galleries"
                       f"?folderid=-1")
            else:
                url = f"{self.root}/organizer/{folder_id}/"
            yield Message.Queue, url, data

    def folders(self):
        """Return a list of folder IDs of a user"""
        user, user_id = self.groups
        if user:
            url = f"{self.root}/profile/{user}/galleries"
        else:
            url = f"{self.root}/usergallery.php?userid={user_id}"
        params = {"page": 0}
        pnum = 0

        self.user = None
        while True:
            response = self.request(url, params=params)

            if self.user is None:
                url = response.url.partition("?")[0]
                self.user = url.rsplit("/", 2)[1]

            page = response.text
            folders = text.extr(
                page, ' id="tgl_all" value="', '"').rstrip("|").split("|")
            if folders[-1] == "-1":
                last = folders.pop()
                if not pnum:
                    folders.insert(0, last)
            elif not folders[0]:
                break
            yield from folders

            params["page"] = pnum = pnum + 1
            if f'href="?page={pnum}">{pnum+1}</a>' not in page:
                break
