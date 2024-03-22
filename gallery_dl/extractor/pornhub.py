# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pornhub.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:[\w-]+\.)?pornhub\.com"


class PornhubExtractor(Extractor):
    """Base class for pornhub extractors"""
    category = "pornhub"
    root = "https://www.pornhub.com"

    def _init(self):
        self.cookies.set(
            "accessAgeDisclaimerPH", "1", domain=".pornhub.com")

    def _pagination(self, user, path):
        if "/" not in path:
            path += "/public"

        url = "{}/{}/{}/ajax".format(self.root, user, path)
        params = {"page": 1}
        headers = {
            "Referer": url[:-5],
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            response = self.request(
                url, method="POST", headers=headers, params=params,
                allow_redirects=False)

            if 300 <= response.status_code < 400:
                url = "{}{}/{}/ajax".format(
                    self.root, response.headers["location"], path)
                continue

            yield response.text

            params["page"] += 1


class PornhubGalleryExtractor(PornhubExtractor):
    """Extractor for image galleries on pornhub.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user}", "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/album/(\d+)"
    example = "https://www.pornhub.com/album/12345"

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.gallery_id = match.group(1)
        self._first = None

    def items(self):
        data = self.metadata()
        yield Message.Directory, data
        for num, image in enumerate(self.images(), 1):
            url = image["url"]
            image.update(data)
            image["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        url = "{}/album/{}".format(
            self.root, self.gallery_id)
        extr = text.extract_from(self.request(url).text)

        title = extr("<title>", "</title>")
        score = extr('<div id="albumGreenBar" style="width:', '"')
        views = extr('<div id="viewsPhotAlbumCounter">', '<')
        tags = extr('<div id="photoTagsBox"', '<script')
        self._first = extr('<a href="/photo/', '"')
        title, _, user = title.rpartition(" - ")

        return {
            "user" : text.unescape(user[:-14]),
            "gallery": {
                "id"   : text.parse_int(self.gallery_id),
                "title": text.unescape(title),
                "score": text.parse_int(score.partition("%")[0]),
                "views": text.parse_int(views.partition(" ")[0]),
                "tags" : text.split_html(tags)[2:],
            },
        }

    def images(self):
        url = "{}/album/show_album_json?album={}".format(
            self.root, self.gallery_id)
        response = self.request(url)

        if response.content == b"Permission denied":
            raise exception.AuthorizationError()
        images = response.json()
        key = end = self._first

        while True:
            img = images[key]
            yield {
                "url"    : img["img_large"],
                "caption": img["caption"],
                "id"     : text.parse_int(img["id"]),
                "views"  : text.parse_int(img["times_viewed"]),
                "score"  : text.parse_int(img["vote_percent"]),
            }
            key = str(img["next"])
            if key == end:
                return


class PornhubGifExtractor(PornhubExtractor):
    """Extractor for pornhub.com gifs"""
    subcategory = "gif"
    directory_fmt = ("{category}", "{user}", "gifs")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/gif/(\d+)"
    example = "https://www.pornhub.com/gif/12345"

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.gallery_id = match.group(1)

    def items(self):
        url = "{}/gif/{}".format(self.root, self.gallery_id)
        extr = text.extract_from(self.request(url).text)

        gif = {
            "id"   : self.gallery_id,
            "tags" : extr("data-context-tag='", "'").split(","),
            "title": extr('"name": "', '"'),
            "url"  : extr('"contentUrl": "', '"'),
            "date" : text.parse_datetime(
                extr('"uploadDate": "', '"'), "%Y-%m-%d"),
            "viewkey"  : extr('From this video: '
                              '<a href="/view_video.php?viewkey=', '"'),
            "timestamp": extr('lass="directLink tstamp" rel="nofollow">', '<'),
            "user" : text.remove_html(extr("Created by:", "</div>")),
        }

        yield Message.Directory, gif
        yield Message.Url, gif["url"], text.nameext_from_url(gif["url"], gif)


class PornhubUserExtractor(PornhubExtractor):
    """Extractor for a pornhub user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/((?:users|model|pornstar)/[^/?#]+)/?$"
    example = "https://www.pornhub.com/model/USER"

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.user = match.group(1)

    def initialize(self):
        pass

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (PornhubPhotosExtractor, base + "photos"),
            (PornhubGifsExtractor  , base + "gifs"),
        ), ("photos",))


class PornhubPhotosExtractor(PornhubExtractor):
    """Extractor for all galleries of a pornhub user"""
    subcategory = "photos"
    pattern = (BASE_PATTERN + r"/((?:users|model|pornstar)/[^/?#]+)"
               "/(photos(?:/[^/?#]+)?)")
    example = "https://www.pornhub.com/model/USER/photos"

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.user, self.path = match.groups()

    def items(self):
        data = {"_extractor": PornhubGalleryExtractor}
        for page in self._pagination(self.user, self.path):
            gid = None
            for gid in text.extract_iter(page, 'id="albumphoto', '"'):
                yield Message.Queue, self.root + "/album/" + gid, data
            if gid is None:
                return


class PornhubGifsExtractor(PornhubExtractor):
    """Extractor for a pornhub user's gifs"""
    subcategory = "gifs"
    pattern = (BASE_PATTERN + r"/((?:users|model|pornstar)/[^/?#]+)"
               "/(gifs(?:/[^/?#]+)?)")
    example = "https://www.pornhub.com/model/USER/gifs"

    def __init__(self, match):
        PornhubExtractor.__init__(self, match)
        self.user, self.path = match.groups()

    def items(self):
        data = {"_extractor": PornhubGifExtractor}
        for page in self._pagination(self.user, self.path):
            gid = None
            for gid in text.extract_iter(page, 'id="gif', '"'):
                yield Message.Queue, self.root + "/gif/" + gid, data
            if gid is None:
                return
