# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://photobucket.com/"""

from .common import Extractor, Message
from .. import text, exception
import binascii
import json


class PhotobucketAlbumExtractor(Extractor):
    """Extractor for albums on photobucket.com"""
    category = "photobucket"
    subcategory = "album"
    directory_fmt = ("{category}", "{username}", "{location}")
    filename_fmt = "{offset:>03}{pictureId:?_//}_{titleOrFilename}.{extension}"
    archive_fmt = "{id}"
    pattern = (r"(?:https?://)?((?:[\w-]+\.)?photobucket\.com)"
               r"/user/[^/?&#]+/library(?:/[^?&#]*)?")
    example = "https://s123.photobucket.com/user/USER/library"

    def __init__(self, match):
        self.root = "https://" + match.group(1)
        Extractor.__init__(self, match)

    def _init(self):
        self.session.headers["Referer"] = self.url

    def items(self):
        for image in self.images():
            image["titleOrFilename"] = text.unescape(image["titleOrFilename"])
            image["title"] = text.unescape(image["title"])
            image["extension"] = image["ext"]
            yield Message.Directory, image
            yield Message.Url, image["fullsizeUrl"], image

        if self.config("subalbums", True):
            for album in self.subalbums():
                album["_extractor"] = PhotobucketAlbumExtractor
                yield Message.Queue, album["url"], album

    def images(self):
        """Yield all images of the current album"""
        url = self.url
        params = {"sort": "3", "page": 1}

        while True:
            page = self.request(url, params=params).text
            json_data = text.extract(page, "collectionData:", ",\n")[0]
            if not json_data:
                msg = text.extr(page, 'libraryPrivacyBlock">', "</div>")
                msg = ' ("{}")'.format(text.remove_html(msg)) if msg else ""
                self.log.error("Unable to get JSON data%s", msg)
                return
            data = json.loads(json_data)

            yield from data["items"]["objects"]

            if data["total"] <= data["offset"] + data["pageSize"]:
                self.album_path = data["currentAlbumPath"]
                return
            params["page"] += 1

    def subalbums(self):
        """Return all subalbum objects"""
        url = self.root + "/component/Albums-SubalbumList"
        params = {
            "albumPath": self.album_path,
            "fetchSubAlbumsOnly": "true",
            "deferCollapsed": "true",
            "json": "1",
        }

        data = self.request(url, params=params).json()
        return data["body"].get("subAlbums", ())


class PhotobucketImageExtractor(Extractor):
    """Extractor for individual images from photobucket.com"""
    category = "photobucket"
    subcategory = "image"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{pictureId:?/_/}{titleOrFilename}.{extension}"
    archive_fmt = "{username}_{id}"
    pattern = (r"(?:https?://)?(?:[\w-]+\.)?photobucket\.com"
               r"(?:/gallery/user/([^/?&#]+)/media/([^/?&#]+)"
               r"|/user/([^/?&#]+)/media/[^?&#]+\.html)")
    example = "https://s123.photobucket.com/user/USER/media/NAME.EXT.html"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1) or match.group(3)
        self.media_id = match.group(2)

    def _init(self):
        self.session.headers["Referer"] = self.url

    def items(self):
        url = "https://photobucket.com/galleryd/search.php"
        params = {"userName": self.user, "searchTerm": "", "ref": ""}

        if self.media_id:
            params["mediaId"] = self.media_id
        else:
            params["url"] = self.url

        # retry API call up to 5 times, since it can randomly fail
        tries = 0
        while tries < 5:
            data = self.request(url, method="POST", params=params).json()
            image = data["mediaDocuments"]
            if "message" not in image:
                break  # success
            tries += 1
            self.log.debug(image["message"])
        else:
            raise exception.StopExtraction(image["message"])

        # adjust metadata entries to be at least somewhat similar
        # to what the 'album' extractor provides
        if "media" in image:
            image = image["media"][image["mediaIndex"]]
            image["albumView"] = data["mediaDocuments"]["albumView"]
            image["username"] = image["ownerId"]
        else:
            image["fileUrl"] = image.pop("imageUrl")

        image.setdefault("title", "")
        image.setdefault("description", "")
        name, _, ext = image["fileUrl"].rpartition("/")[2].rpartition(".")
        image["ext"] = image["extension"] = ext
        image["titleOrFilename"] = image["title"] or name
        image["tags"] = image.pop("clarifaiTagList", [])

        mtype, _, mid = binascii.a2b_base64(image["id"]).partition(b":")
        image["pictureId"] = mid.decode() if mtype == b"mediaId" else ""

        yield Message.Directory, image
        yield Message.Url, image["fileUrl"], image
