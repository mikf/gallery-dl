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
    """Extract all images from a gallery at imagefap.com"""
    category = "imagefap"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{name}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.)?imagefap\.com/"
                r"(?:gallery\.php\?gid=|gallery/|pictures/)(\d+)")]
    test = [("http://www.imagefap.com/gallery/6316217", {
        "url": "d814dc37efcfd3723c30cfe86fd9e51415e7eecf",
        "keyword": "b55344341b1b79f8eb803098d24551bb79cada0f",
        "content": "ead241b083da2e1d01c4c28a5faa1aa32c01700f",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)

    def items(self):
        imgurl_fmt = ("http://x.imagefapusercontent.com/u/{uploader}/"
                      "{gallery-id}/{image-id}/{filename}")
        url  = "http://www.imagefap.com/pictures/" + self.gid + "/?view=2"
        page = self.request(url).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for image in self.get_images(page):
            data.update(image)
            yield Message.Url, imgurl_fmt.format(**data), data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = text.extract_all(page, (
            ("section" , '<meta name="description" content="', '"'),
            ("title"   , '<title>Porn pics of ', ' (Page 1)</title>'),
            ("uploader", '>Uploaded by ', '</font>'),
            ("count"   , ' 1 of ', ' pics"'),
        ), values={"category": self.category, "gallery-id": self.gid})[0]
        data["title"] = text.unescape(data["title"])
        return data

    @staticmethod
    def get_images(page):
        """Collect image-metadata"""
        pos = 0
        num = 0
        while True:
            imgid, pos = text.extract(page, '<td id="', '"', pos)
            if not imgid:
                return
            name , pos = text.extract(page, '<i>', '</i>', pos)
            num += 1
            yield text.nameext_from_url(name, {"image-id": imgid, "num": num})



class ImagefapImageExtractor(Extractor):
    """Extract a single image from imagefap.com"""
    category = "imagefap"
    subcategory = "image"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{name}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?imagefap\.com/photo/(\d+)"]
    test = [("http://www.imagefap.com/photo/776391972/", {
        "url": "d814dc37efcfd3723c30cfe86fd9e51415e7eecf",
        "keyword": "c7e2f9bf70e2357d35c21b2602faf0416a5c39d0",
        "content": "ead241b083da2e1d01c4c28a5faa1aa32c01700f",
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
            "category": self.category,
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
        url  = "http://www.imagefap.com/photo/" + self.image_id + "/"
        page = self.request(url).text
        section  , pos = text.extract(page, '<meta name="description" content="', '"')
        json_data, pos = text.extract(page,
            '<script type="application/ld+json">', '</script>', pos)
        json_dict = json.loads(json_data)
        json_dict["section"] = section
        return json_dict
