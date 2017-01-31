# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://imagefap.com/"""

from .common import Extractor, Message
from .. import text
import json


class ImagefapGalleryExtractor(Extractor):
    """Extractor for image galleries from imagefap.com"""
    category = "imagefap"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{name}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?imagefap\.com/"
                r"(?:gallery\.php\?gid=|gallery/|pictures/)(\d+)")]
    test = [("http://www.imagefap.com/gallery/6318447", {
        "url": "f63e6876df83a40e1a98dad70e46952dd9edb7a7",
        "keyword": "715f99ad154c4cf608afc7cd77dd1e896030646a",
        "content": "38e50699db9518ae68648c45ecdd6be614efc324",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)
        self.image_id = ""

    def items(self):
        url = "http://www.imagefap.com/pictures/" + self.gid + "/"
        page = self.request(url).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for url, image in self.get_images(int(data["count"])):
            data.update(image)
            yield Message.Url, url, data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data, pos = text.extract_all(page, (
            ("section" , '<meta name="description" content="', '"'),
            ("title"   , '<title>Porn pics of ', ' (Page 1)</title>'),
            ("uploader", '>Uploaded by ', '</font>'),
            ("count"   , ' 1 of ', ' pics"'),
        ), values={"gallery-id": self.gid})
        self.image_id = text.extract(page, 'id="img_ed_', '"', pos)[0]
        data["title"] = text.unescape(data["title"])
        return data

    def get_images(self, count):
        """Collect image-urls and -metadata"""
        num = 0
        url = "http://www.imagefap.com/photo/" + self.image_id + "/"
        params = {"gid": self.gid, "idx": 0, "partial": "true"}
        while True:
            pos = 0
            page = self.request(url, params=params).text
            for _ in range(24):
                imgurl, pos = text.extract(page, '<a href="', '"', pos)
                num += 1
                _, imgid, name = imgurl.rsplit("/", 2)
                data = {"image-id": imgid, "num": num}
                yield imgurl, text.nameext_from_url(name, data)
                if num >= count:
                    return
            params["idx"] += 24


class ImagefapImageExtractor(Extractor):
    """Extractor for single images from imagefap.com"""
    category = "imagefap"
    subcategory = "image"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{name}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?imagefap\.com/photo/(\d+)"]
    test = [("http://www.imagefap.com/photo/1616331218/", {
        "url": "8a05c0ccdcf84e63c962803bc41d247628c549ea",
        "keyword": "c9880c6731b3fdc6d98d25dbff56f4342c11683e",
        "content": "964b8c62c9d5c2a039a2fccf1b1e10aaf7a18a96",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.image_id = match.group(1)

    def items(self):
        info = self.load_json()
        data = self.get_job_metadata(info)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, info["contentUrl"], data

    def get_job_metadata(self, info):
        """Collect metadata for extractor-job"""
        parts = info["contentUrl"].rsplit("/", 3)
        return text.nameext_from_url(parts[3], {
            "title": text.unescape(info["name"]),
            "section": info["section"],
            "uploader": info["author"],
            "date": info["datePublished"],
            "width": info["width"],
            "height": info["height"],
            "gallery-id": parts[1],
            "image-id": parts[2],
        })

    def load_json(self):
        """Load the JSON dictionary associated with the image"""
        url = "http://www.imagefap.com/photo/" + self.image_id + "/"
        page = self.request(url).text
        section  , pos = text.extract(
            page, '<meta name="description" content="', '"'
        )
        json_data, pos = text.extract(
            page, '<script type="application/ld+json">', '</script>', pos
        )
        json_dict = json.loads(json_data)
        json_dict["section"] = section
        return json_dict


class ImagefapUserExtractor(Extractor):
    """Extractor for all galleries from a user at imagefap.com"""
    category = "imagefap"
    subcategory = "user"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{name}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?imagefap\.com/"
                r"profile(?:\.php\?user=|/)([^/]+)"),
               (r"(?:https?://)?(?:www\.)?imagefap\.com/"
                r"usergallery\.php\?userid=(\d+)")]
    test = [("http://www.imagefap.com/profile/Mr Bad Example/galleries", {
        "url": "145e98a8648c7695c150800ff8fd578ab26c28c1",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        try:
            self.user_id = int(match.group(1))
            self.user = None
        except ValueError:
            self.user_id = None
            self.user = match.group(1)

    def items(self):
        yield Message.Version, 1
        for gallery in self.get_gallery_ids():
            yield Message.Queue, "http://www.imagefap.com/gallery/" + gallery

    def get_gallery_ids(self):
        """Yield all gallery-ids of a specific user"""
        folders = self.get_gallery_folders()
        url = "http://www.imagefap.com/ajax_usergallery_folder.php"
        params = {"userid": self.user_id}
        for folder_id in folders:
            params["id"] = folder_id
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, '<a  href="/gallery/', '"')

    def get_gallery_folders(self):
        """Create a list of all folder-ids of a specific user"""
        if self.user:
            url = "http://www.imagefap.com/profile/" + self.user + "/galleries"
        else:
            url = ("http://www.imagefap.com/usergallery.php?userid=" +
                   str(self.user_id))
        page = self.request(url).text
        self.user_id, pos = text.extract(page, '?userid=', '"')
        folders, pos = text.extract(page, ' id="tgl_all" value="', '"', pos)
        return folders.split("|")[:-1]
