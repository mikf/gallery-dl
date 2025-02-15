# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgur.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.|[im]\.)?imgur\.(?:com|io)"


class ImgurExtractor(Extractor):
    """Base class for imgur extractors"""
    category = "imgur"
    root = "https://imgur.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)

    def _init(self):
        self.api = ImgurAPI(self)
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
        image["_http_validate"] = self._validate
        text.nameext_from_url(url, image)

        return url

    def _validate(self, response):
        return (not response.history or
                not response.url.endswith("/removed.png"))

    def _items_queue(self, items):
        album_ex = ImgurAlbumExtractor
        image_ex = ImgurImageExtractor

        for item in items:
            if item["is_album"]:
                url = "https://imgur.com/a/" + item["id"]
                item["_extractor"] = album_ex
            else:
                url = "https://imgur.com/" + item["id"]
                item["_extractor"] = image_ex
            yield Message.Queue, url, item


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images on imgur.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = (BASE_PATTERN + r"/(?!gallery|search)"
               r"(?:r/\w+/)?(?:[^/?#]+-)?(\w{7}|\w{5})[sbtmlh]?")
    example = "https://imgur.com/abcdefg"

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
    pattern = BASE_PATTERN + r"/a/(?:[^/?#]+-)?(\w{7}|\w{5})"
    example = "https://imgur.com/a/abcde"

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
    pattern = BASE_PATTERN + r"/(?:gallery|t/\w+)/(?:[^/?#]+-)?(\w{7}|\w{5})"
    example = "https://imgur.com/gallery/abcde"

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
    pattern = (BASE_PATTERN + r"/user/(?!me(?:/|$|\?|#))"
               r"([^/?#]+)(?:/posts|/submitted)?/?$")
    example = "https://imgur.com/user/USER"

    def items(self):
        return self._items_queue(self.api.account_submissions(self.key))


class ImgurFavoriteExtractor(ImgurExtractor):
    """Extractor for a user's favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/favorites/?$"
    example = "https://imgur.com/user/USER/favorites"

    def items(self):
        return self._items_queue(self.api.account_favorites(self.key))


class ImgurFavoriteFolderExtractor(ImgurExtractor):
    """Extractor for a user's favorites folder"""
    subcategory = "favorite-folder"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)/favorites/folder/(\d+)"
    example = "https://imgur.com/user/USER/favorites/folder/12345/TITLE"

    def __init__(self, match):
        ImgurExtractor.__init__(self, match)
        self.folder_id = match.group(2)

    def items(self):
        return self._items_queue(self.api.account_favorites_folder(
            self.key, self.folder_id))


class ImgurMeExtractor(ImgurExtractor):
    """Extractor for your personal uploads"""
    subcategory = "me"
    pattern = BASE_PATTERN + r"/user/me(?:/posts)?(/hidden)?"
    example = "https://imgur.com/user/me"

    def items(self):
        if not self.cookies_check(("accesstoken",)):
            self.log.error("'accesstoken' cookie required")

        if self.groups[0]:
            posts = self.api.accounts_me_hiddenalbums()
        else:
            posts = self.api.accounts_me_allposts()
        return self._items_queue(posts)


class ImgurSubredditExtractor(ImgurExtractor):
    """Extractor for a subreddits's imgur links"""
    subcategory = "subreddit"
    pattern = BASE_PATTERN + r"/r/([^/?#]+)/?$"
    example = "https://imgur.com/r/SUBREDDIT"

    def items(self):
        return self._items_queue(self.api.gallery_subreddit(self.key))


class ImgurTagExtractor(ImgurExtractor):
    """Extractor for imgur tag searches"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/t/([^/?#]+)$"
    example = "https://imgur.com/t/TAG"

    def items(self):
        return self._items_queue(self.api.gallery_tag(self.key))


class ImgurSearchExtractor(ImgurExtractor):
    """Extractor for imgur search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(?:/[^?#]+)?/?\?q=([^&#]+)"
    example = "https://imgur.com/search?q=UERY"

    def items(self):
        key = text.unquote(self.key.replace("+", " "))
        return self._items_queue(self.api.gallery_search(key))


class ImgurAPI():
    """Interface for the Imgur API

    Ref: https://apidocs.imgur.com/
    """
    def __init__(self, extractor):
        self.extractor = extractor
        self.client_id = extractor.config("client-id") or "546c25a59c58ad7"
        self.headers = {"Authorization": "Client-ID " + self.client_id}

    def account_submissions(self, account):
        endpoint = "/3/account/{}/submissions".format(account)
        return self._pagination(endpoint)

    def account_favorites(self, account):
        endpoint = "/3/account/{}/gallery_favorites".format(account)
        return self._pagination(endpoint)

    def account_favorites_folder(self, account, folder_id):
        endpoint = "/3/account/{}/folders/{}/favorites".format(
            account, folder_id)
        return self._pagination_v2(endpoint)

    def accounts_me_allposts(self):
        endpoint = "/post/v1/accounts/me/all_posts"
        params = {
            "include": "media,tags,account",
            "page"   : 1,
            "sort"   : "-created_at",
        }
        return self._pagination_v2(endpoint, params)

    def accounts_me_hiddenalbums(self):
        endpoint = "/post/v1/accounts/me/hidden_albums"
        params = {
            "include": "media,tags,account",
            "page"   : 1,
            "sort"   : "-created_at",
        }
        return self._pagination_v2(endpoint, params)

    def gallery_search(self, query):
        endpoint = "/3/gallery/search"
        params = {"q": query}
        return self._pagination(endpoint, params)

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

    def _call(self, endpoint, params=None, headers=None):
        while True:
            try:
                return self.extractor.request(
                    "https://api.imgur.com" + endpoint,
                    params=params, headers=(headers or self.headers),
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

    def _pagination_v2(self, endpoint, params=None, key=None):
        if params is None:
            params = {}
        params["client_id"] = self.client_id
        if "page" not in params:
            params["page"] = 0
        if "sort" not in params:
            params["sort"] = "newest"
        headers = {"Origin": "https://imgur.com"}

        while True:
            data = self._call(endpoint, params, headers)
            if "data" in data:
                data = data["data"]
            if not data:
                return
            yield from data

            params["page"] += 1
