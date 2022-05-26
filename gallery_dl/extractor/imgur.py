# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
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
        image.update(image["metadata"])
        del image["metadata"]

        if image["ext"] == "jpeg":
            image["ext"] = "jpg"
        elif image["is_animated"] and self.mp4 and image["ext"] == "gif":
            image["ext"] = "mp4"

        image["url"] = url = "https://i.imgur.com/{}.{}".format(
            image["id"], image["ext"])
        image["date"] = text.parse_datetime(image["created_at"])
        text.nameext_from_url(url, image)

        return url

    def _items_queue(self, items):
        album_ex = ImgurAlbumExtractor
        image_ex = ImgurImageExtractor

        for item in items:
            item["_extractor"] = album_ex if item["is_album"] else image_ex
            yield Message.Queue, item["link"], item


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images on imgur.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = (BASE_PATTERN + r"/(?!gallery|search)"
               r"(?:r/\w+/)?(\w{7}|\w{5})[sbtmlh]?")
    test = (
        ("https://imgur.com/21yMxCS", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
            "keyword": {
                "account_id"    : 0,
                "comment_count" : int,
                "cover_id"      : "21yMxCS",
                "date"          : "dt:2016-11-10 14:24:35",
                "description"   : "",
                "downvote_count": int,
                "duration"      : 0,
                "ext"           : "png",
                "favorite"      : False,
                "favorite_count": 0,
                "has_sound"     : False,
                "height"        : 32,
                "id"            : "21yMxCS",
                "image_count"   : 1,
                "in_most_viral" : False,
                "is_ad"         : False,
                "is_album"      : False,
                "is_animated"   : False,
                "is_looping"    : False,
                "is_mature"     : False,
                "is_pending"    : False,
                "mime_type"     : "image/png",
                "name"          : "test-テスト",
                "point_count"   : int,
                "privacy"       : "",
                "score"         : int,
                "size"          : 182,
                "title"         : "Test",
                "upvote_count"  : int,
                "url"           : "https://i.imgur.com/21yMxCS.png",
                "view_count"    : int,
                "width"         : 64,
            },
        }),
        ("http://imgur.com/0gybAXR", {  # gifv/mp4 video
            "url": "a2220eb265a55b0c95e0d3d721ec7665460e3fd7",
            "content": "a3c080e43f58f55243ab830569ba02309d59abfc",
        }),
        ("https://imgur.com/XFfsmuC", {  # missing title in API response (#467)
            "keyword": {"title": "Tears are a natural response to irritants"},
        }),
        ("https://imgur.com/1Nily2P", {  # animated png
            "pattern": "https://i.imgur.com/1Nily2P.png",
        }),
        ("https://imgur.com/zzzzzzz", {  # not found
            "exception": exception.HttpError,
        }),
        ("https://m.imgur.com/r/Celebs/iHJ7tsM"),
        ("https://www.imgur.com/21yMxCS"),     # www
        ("https://m.imgur.com/21yMxCS"),       # mobile
        ("https://imgur.com/zxaY6"),           # 5 character key
        ("https://i.imgur.com/21yMxCS.png"),   # direct link
        ("https://i.imgur.com/21yMxCSh.png"),  # direct link thumbnail
        ("https://i.imgur.com/zxaY6.gif"),     # direct link (short)
        ("https://i.imgur.com/zxaY6s.gif"),    # direct link (short; thumb)
    )

    def items(self):
        image = self.api.image(self.key)

        try:
            del image["ad_url"]
            del image["ad_type"]
        except KeyError:
            pass

        image.update(image["media"][0])
        del image["media"]
        url = self._prepare(image)
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
                    "account_id"    : 0,
                    "comment_count" : int,
                    "cover_id"      : "693j2Kr",
                    "date"          : "dt:2015-10-09 10:37:50",
                    "description"   : "",
                    "downvote_count": 0,
                    "favorite"      : False,
                    "favorite_count": 0,
                    "id"            : "TcBmP",
                    "image_count"   : 19,
                    "in_most_viral" : False,
                    "is_ad"         : False,
                    "is_album"      : True,
                    "is_mature"     : False,
                    "is_pending"    : False,
                    "privacy"       : "private",
                    "score"         : int,
                    "title"         : "138",
                    "upvote_count"  : int,
                    "url"           : "https://imgur.com/a/TcBmP",
                    "view_count"    : int,
                    "virality"      : int,
                },
                "account_id" : 0,
                "count"      : 19,
                "date"       : "type:datetime",
                "description": "",
                "ext"        : "jpg",
                "has_sound"  : False,
                "height"     : int,
                "id"         : str,
                "is_animated": False,
                "is_looping" : False,
                "mime_type"  : "image/jpeg",
                "name"       : str,
                "num"        : int,
                "size"       : int,
                "title"      : str,
                "type"       : "image",
                "updated_at" : None,
                "url"        : str,
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
        ("https://imgur.com/a/pjOnJA0", {  # empty, no 'media' (#2557)
            "count": 0,
        }),
        ("https://www.imgur.com/a/TcBmP"),  # www
        ("https://m.imgur.com/a/TcBmP"),  # mobile
    )

    def items(self):
        album = self.api.album(self.key)

        try:
            images = album["media"]
        except KeyError:
            return

        del album["media"]
        count = len(images)
        album["date"] = text.parse_datetime(album["created_at"])

        try:
            del album["ad_url"]
            del album["ad_type"]
        except KeyError:
            pass

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
    pattern = BASE_PATTERN + r"/(?:gallery|t/\w+)/(\w{7}|\w{5})"
    test = (
        ("https://imgur.com/gallery/zf2fIms", {  # non-album gallery (#380)
            "pattern": "https://imgur.com/zf2fIms",
        }),
        ("https://imgur.com/gallery/eD9CT", {
            "pattern": "https://imgur.com/a/eD9CT",
        }),
        ("https://imgur.com/t/unmuted/26sEhNr"),
        ("https://imgur.com/t/cat/qSB8NbN"),
    )

    def items(self):
        if self.api.gallery(self.key)["is_album"]:
            url = "{}/a/{}".format(self.root, self.key)
            extr = ImgurAlbumExtractor
        else:
            url = "{}/{}".format(self.root, self.key)
            extr = ImgurImageExtractor
        yield Message.Queue, url, {"_extractor": extr}


class ImgurUserExtractor(ImgurExtractor):
    """Extractor for all images posted by a user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)(?:/posts|/submitted)?/?$"
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
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/favorites"
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
    pattern = BASE_PATTERN + r"/r/([^/?#]+)/?$"
    test = ("https://imgur.com/r/pics", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        return self._items_queue(self.api.gallery_subreddit(self.key))


class ImgurTagExtractor(ImgurExtractor):
    """Extractor for imgur tag searches"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/t/([^/?#]+)$"
    test = ("https://imgur.com/t/animals", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        return self._items_queue(self.api.gallery_tag(self.key))


class ImgurSearchExtractor(ImgurExtractor):
    """Extractor for imgur search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(?:/[^?#]+)?/?\?q=([^&#]+)"
    test = ("https://imgur.com/search?q=cute+cat", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        key = text.unquote(self.key.replace("+", " "))
        return self._items_queue(self.api.gallery_search(key))


class ImgurAPI():
    """Interface for the Imgur API

    Ref: https://apidocs.imgur.com/
    """
    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Authorization": "Client-ID " + extractor.config(
                "client-id", "546c25a59c58ad7"),
        }

    def account_favorites(self, account):
        endpoint = "/3/account/{}/gallery_favorites".format(account)
        return self._pagination(endpoint)

    def gallery_search(self, query):
        endpoint = "/3/gallery/search"
        params = {"q": query}
        return self._pagination(endpoint, params)

    def account_submissions(self, account):
        endpoint = "/3/account/{}/submissions".format(account)
        return self._pagination(endpoint)

    def gallery_subreddit(self, subreddit):
        endpoint = "/3/gallery/r/{}".format(subreddit)
        return self._pagination(endpoint)

    def gallery_tag(self, tag):
        endpoint = "/3/gallery/t/{}".format(tag)
        return self._pagination(endpoint, key="items")

    def image(self, image_hash):
        endpoint = "/post/v1/media/" + image_hash
        params = {"include": "media,tags,account"}
        return self._call(endpoint, params)

    def album(self, album_hash):
        endpoint = "/post/v1/albums/" + album_hash
        params = {"include": "media,tags,account"}
        return self._call(endpoint, params)

    def gallery(self, gallery_hash):
        endpoint = "/post/v1/posts/" + gallery_hash
        return self._call(endpoint)

    def _call(self, endpoint, params=None):
        while True:
            try:
                return self.extractor.request(
                    "https://api.imgur.com" + endpoint,
                    params=params, headers=self.headers,
                ).json()
            except exception.HttpError as exc:
                if exc.status not in (403, 429) or \
                        b"capacity" not in exc.response.content:
                    raise
            self.extractor.wait(seconds=600)

    def _pagination(self, endpoint, params=None, key=None):
        num = 0

        while True:
            data = self._call("{}/{}".format(endpoint, num), params)["data"]
            if key:
                data = data[key]
            if not data:
                return
            yield from data
            num += 1
