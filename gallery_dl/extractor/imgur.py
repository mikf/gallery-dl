# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgur.com/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?:www\.|[im]\.)?imgur\.com"


class ImgurExtractor(Extractor):
    """Base class for imgur extractors"""
    category = "imgur"
    root = "https://imgur.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = ImgurAPI(self)
        self.key = match.group(1)
        self.mp4 = self.config("mp4", True)

    def _prepare(self, image):
        try:
            del image["ad_url"]
            del image["ad_type"]
            del image["ad_config"]
        except KeyError:
            pass

        if image["animated"] and self.mp4 and "mp4" in image:
            url = image["mp4"]
        else:
            url = image["link"]

        image["date"] = text.parse_timestamp(image["datetime"])
        text.nameext_from_url(url, image)

        return url

    def _items_queue(self, items):
        album_ex = ImgurAlbumExtractor
        image_ex = ImgurImageExtractor

        yield Message.Version, 1
        for item in items:
            item["_extractor"] = album_ex if item["is_album"] else image_ex
            yield Message.Queue, item["link"], item


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images on imgur.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/(?!gallery)(\w{7}|\w{5})[sbtmlh]?\.?"
    test = (
        ("https://imgur.com/21yMxCS", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
            "keyword": {
                "account_id"   : None,
                "account_url"  : None,
                "animated"     : False,
                "bandwidth"    : int,
                "date"         : "dt:2016-11-10 14:24:35",
                "datetime"     : 1478787875,
                "description"  : None,
                "edited"       : "0",
                "extension"    : "png",
                "favorite"     : False,
                "filename"     : "21yMxCS",
                "has_sound"    : False,
                "height"       : 32,
                "id"           : "21yMxCS",
                "in_gallery"   : False,
                "in_most_viral": False,
                "is_ad"        : False,
                "link"         : "https://i.imgur.com/21yMxCS.png",
                "nsfw"         : False,
                "section"      : None,
                "size"         : 182,
                "tags"         : [],
                "title"        : "Test",
                "type"         : "image/png",
                "views"        : int,
                "vote"         : None,
                "width"        : 64,
            },
        }),
        ("http://imgur.com/0gybAXR", {  # gifv/mp4 video
            "url": "a2220eb265a55b0c95e0d3d721ec7665460e3fd7",
            "content": "a3c080e43f58f55243ab830569ba02309d59abfc",
        }),
        ("https://imgur.com/XFfsmuC", {  # missing title in API response (#467)
            "keyword": {"title": "Tears are a natural response to irritants"},
        }),
        ("https://imgur.com/HjoXJAd", {  # url ends with '.jpg?1'
            "url": "ec2cf11a2bfb4939feff374781a6e6f3e9af8e8e",
        }),
        ("https://imgur.com/1Nily2P", {  # animated png
            "pattern": "https://i.imgur.com/1Nily2P.png",
        }),
        ("https://imgur.com/zzzzzzz", {  # not found
            "exception": exception.HttpError,
        }),
        ("https://www.imgur.com/21yMxCS"),  # www
        ("https://m.imgur.com/21yMxCS"),  # mobile
        ("https://imgur.com/zxaY6"),  # 5 character key
        ("https://i.imgur.com/21yMxCS.png"),  # direct link
        ("https://i.imgur.com/21yMxCSh.png"),  # direct link thumbnail
        ("https://i.imgur.com/zxaY6.gif"),  # direct link (short)
        ("https://i.imgur.com/zxaY6s.gif"),  # direct link (short; thumb)
    )

    def items(self):
        image = self.api.image(self.key)
        if not image["title"]:
            page = self.request(self.root + "/" + self.key, fatal=False).text
            title = text.extract(page, "<title>", "<")[0] or ""
            image["title"] = text.unescape(title.rpartition(" - ")[0].strip())
        url = self._prepare(image)
        yield Message.Version, 1
        yield Message.Directory, image
        yield Message.Url, url, image


class ImgurAlbumExtractor(ImgurExtractor):
    """Extractor for imgur albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{album[id]}{album[title]:? - //}")
    filename_fmt = "{category}_{album[id]}_{num:>03}_{id}.{extension}"
    archive_fmt = "{album[id]}_{id}"
    pattern = BASE_PATTERN + r"/a/(\w{7}|\w{5})"
    test = (
        ("https://imgur.com/a/TcBmP", {
            "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
            "keyword": {
                "album": {
                    "account_id"  : None,
                    "account_url" : None,
                    "cover"       : "693j2Kr",
                    "cover_edited": None,
                    "cover_height": 1400,
                    "cover_width" : 951,
                    "date"        : "dt:2015-10-09 10:37:50",
                    "datetime"    : 1444387070,
                    "description" : None,
                    "favorite"    : False,
                    "id"          : "TcBmP",
                    "images_count": 19,
                    "in_gallery"  : False,
                    "is_ad"       : False,
                    "is_album"    : True,
                    "layout"      : "blog",
                    "link"        : "https://imgur.com/a/TcBmP",
                    "nsfw"        : bool,
                    "privacy"     : "hidden",
                    "section"     : None,
                    "title"       : "138",
                    "views"       : int,
                },
                "account_id" : None,
                "account_url": None,
                "animated"   : bool,
                "bandwidth"  : int,
                "date"       : "type:datetime",
                "datetime"   : int,
                "description": None,
                "edited"     : "0",
                "favorite"   : False,
                "has_sound"  : False,
                "height"     : int,
                "id"         : str,
                "in_gallery" : False,
                "is_ad"      : False,
                "link"       : r"re:https://i\.imgur\.com/\w+\.jpg",
                "nsfw"       : None,
                "num"        : int,
                "section"    : None,
                "size"       : int,
                "tags"       : list,
                "title"      : None,
                "type"       : "image/jpeg",
                "views"      : int,
                "vote"       : None,
                "width"      : int,
            },
        }),
        ("https://imgur.com/a/eD9CT", {  # large album
            "url": "de748c181a04d18bef1de9d4f4866ef0a06d632b",
        }),
        ("https://imgur.com/a/RhJXhVT/all", {  # 7 character album hash
            "url": "695ef0c950023362a0163ee5041796300db76674",
        }),
        ("https://imgur.com/a/TcBmQ", {
            "exception": exception.HttpError,
        }),
        ("https://www.imgur.com/a/TcBmP"),  # www
        ("https://m.imgur.com/a/TcBmP"),  # mobile
    )

    def items(self):
        album = self.api.album(self.key)
        album["date"] = text.parse_timestamp(album["datetime"])
        images = album["images"]
        count = len(images)

        try:
            del album["images"]
            del album["ad_config"]
        except KeyError:
            pass

        yield Message.Version, 1
        for num, image in enumerate(images, 1):
            url = self._prepare(image)
            image["num"] = num
            image["count"] = count
            image["album"] = album
            yield Message.Directory, image
            yield Message.Url, url, image


class ImgurGalleryExtractor(ImgurExtractor):
    """Extractor for imgur galleries"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/(?:gallery|t/unmuted)/(\w{7}|\w{5})"
    test = (
        ("https://imgur.com/gallery/zf2fIms", {  # non-album gallery (#380)
            "pattern": "https://imgur.com/zf2fIms",
        }),
        ("https://imgur.com/gallery/eD9CT", {
            "pattern": "https://imgur.com/a/eD9CT",
        }),
        ("https://imgur.com/t/unmuted/26sEhNr", {  # unmuted URL
            "pattern": "https://imgur.com/26sEhNr",
        }),
    )

    def items(self):
        url = self.root + "/a/" + self.key
        with self.request(url, method="HEAD", fatal=False) as response:
            if response.status_code < 400:
                extr = ImgurAlbumExtractor
            else:
                extr = ImgurImageExtractor
                url = self.root + "/" + self.key

        yield Message.Version, 1
        yield Message.Queue, url, {"_extractor": extr}


class ImgurUserExtractor(ImgurExtractor):
    """Extractor for all images posted by a user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)(?:/posts|/submitted)?/?$"
    test = (
        ("https://imgur.com/user/Miguenzo", {
            "range": "1-100",
            "count": 100,
            "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
        }),
        ("https://imgur.com/user/Miguenzo/posts"),
        ("https://imgur.com/user/Miguenzo/submitted"),
    )

    def items(self):
        return self._items_queue(self.api.account_submissions(self.key))


class ImgurFavoriteExtractor(ImgurExtractor):
    """Extractor for a user's favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)/favorites"
    test = ("https://imgur.com/user/Miguenzo/favorites", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        return self._items_queue(self.api.account_favorites(self.key))


class ImgurSubredditExtractor(ImgurExtractor):
    """Extractor for a subreddits's imgur links"""
    subcategory = "subreddit"
    pattern = BASE_PATTERN + r"/r/([^/?&#]+)"
    test = ("https://imgur.com/r/pics", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        return self._items_queue(self.api.gallery_subreddit(self.key))


class ImgurAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Authorization": "Client-ID " + extractor.config(
                "client-id", "546c25a59c58ad7"),
        }

    def account_favorites(self, account):
        endpoint = "account/{}/gallery_favorites".format(account)
        return self._pagination(endpoint)

    def account_submissions(self, account):
        endpoint = "account/{}/submissions".format(account)
        return self._pagination(endpoint)

    def gallery_subreddit(self, subreddit):
        endpoint = "gallery/r/{}".format(subreddit)
        return self._pagination(endpoint)

    def album(self, album_hash):
        return self._call("album/" + album_hash)

    def image(self, image_hash):
        return self._call("image/" + image_hash)

    def _call(self, endpoint):
        return self.extractor.request(
            "https://api.imgur.com/3/" + endpoint, headers=self.headers,
        ).json()["data"]

    def _pagination(self, endpoint):
        num = 0

        while True:
            data = self._call("{}/{}".format(endpoint, num))
            if not data:
                return
            yield from data
            num += 1
