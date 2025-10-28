# -*- coding: utf-8 -*-

# Copyright 2017-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.flickr.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.|secure\.|m\.)?flickr\.com"


class FlickrExtractor(Extractor):
    """Base class for flickr extractors"""
    category = "flickr"
    filename_fmt = "{category}_{id}.{extension}"
    directory_fmt = ("{category}", "{user[username]}")
    archive_fmt = "{id}"
    request_interval = (1.0, 2.0)
    request_interval_min = 0.5

    def _init(self):
        self.api = self.utils().FlickrOAuthAPI(self)
        self.user = None
        self.item_id = self.groups[0]

    def items(self):
        data = self.metadata()
        extract = self.api._extract_format
        for photo in self.photos():
            try:
                photo = extract(photo)
            except Exception as exc:
                self.log.warning(
                    "Skipping photo %s (%s: %s)",
                    photo["id"], exc.__class__.__name__, exc)
                self.log.traceback(exc)
            else:
                photo.update(data)
                url = self._file_url(photo)
                yield Message.Directory, photo
                yield Message.Url, url, text.nameext_from_url(url, photo)

    def metadata(self):
        """Return general metadata"""
        self.user = self.api.urls_lookupUser(self.item_id)
        if self.config("profile", False):
            self.user.update(self.api.people_getInfo(self.user["nsid"]))
        return {"user": self.user}

    def photos(self):
        """Return an iterable with all relevant photo objects"""

    def _file_url(self, photo):
        url = photo["url"]

        if "/video/" in url:
            return url

        path, _, ext = url.rpartition(".")
        return path + "_d." + ext


class FlickrImageExtractor(FlickrExtractor):
    """Extractor for individual images from flickr.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:(?:www\.|secure\.|m\.)?flickr\.com/photos/[^/?#]+/"
               r"|[\w-]+\.static\.?flickr\.com/(?:\d+/)+)(\d+)"
               r"|flic\.kr/p/([A-Za-z1-9]+))")
    example = "https://www.flickr.com/photos/USER/12345"

    def items(self):
        item_id, enc_id = self.groups
        if enc_id is not None:
            alphabet = ("123456789abcdefghijkmnopqrstu"
                        "vwxyzABCDEFGHJKLMNPQRSTUVWXYZ")
            item_id = util.bdecode(enc_id, alphabet)

        photo = self.api.photos_getInfo(item_id)

        self.api._extract_metadata(photo, False)
        if photo["media"] == "video" and self.api.videos:
            self.api._extract_video(photo)
        else:
            self.api._extract_photo(photo)

        if self.config("profile", False):
            photo["user"] = self.api.people_getInfo(photo["owner"]["nsid"])
        else:
            photo["user"] = photo["owner"]

        photo["title"] = photo["title"]["_content"]
        photo["comments"] = text.parse_int(photo["comments"]["_content"])
        photo["description"] = photo["description"]["_content"]
        photo["tags"] = [t["raw"] for t in photo["tags"]["tag"]]
        photo["date"] = self.parse_timestamp(photo["dateuploaded"])
        photo["views"] = text.parse_int(photo["views"])
        photo["id"] = text.parse_int(photo["id"])

        if "location" in photo:
            location = photo["location"]
            for key, value in location.items():
                if isinstance(value, dict):
                    location[key] = value["_content"]

        url = self._file_url(photo)
        yield Message.Directory, photo
        yield Message.Url, url, text.nameext_from_url(url, photo)


class FlickrAlbumExtractor(FlickrExtractor):
    """Extractor for photo albums from flickr.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[username]}",
                     "Albums", "{album[id]} {album[title]}")
    archive_fmt = "a_{album[id]}_{id}"
    pattern = rf"{BASE_PATTERN}/photos/([^/?#]+)/(?:album|set)s(?:/(\d+))?"
    example = "https://www.flickr.com/photos/USER/albums/12345"

    def items(self):
        self.album_id = self.groups[1]
        if self.album_id:
            return FlickrExtractor.items(self)
        return self._album_items()

    def _album_items(self):
        data = FlickrExtractor.metadata(self)
        data["_extractor"] = FlickrAlbumExtractor

        for album in self.api.photosets_getList(self.user["nsid"]):
            self.api._clean_info(album).update(data)
            url = (f"https://www.flickr.com/photos/{self.user['path_alias']}"
                   f"/albums/{album['id']}")
            yield Message.Queue, url, album

    def metadata(self):
        data = FlickrExtractor.metadata(self)
        try:
            data["album"] = self.api.photosets_getInfo(
                self.album_id, self.user["nsid"])
        except Exception:
            data["album"] = {}
            self.log.warning("%s: Unable to retrieve album metadata",
                             self.album_id)
        return data

    def photos(self):
        return self.api.photosets_getPhotos(self.album_id)


class FlickrGalleryExtractor(FlickrExtractor):
    """Extractor for photo galleries from flickr.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}",
                     "Galleries", "{gallery[gallery_id]} {gallery[title]}")
    archive_fmt = "g_{gallery[id]}_{id}"
    pattern = rf"{BASE_PATTERN}/photos/([^/?#]+)/galleries/(\d+)"
    example = "https://www.flickr.com/photos/USER/galleries/12345/"

    def metadata(self):
        data = FlickrExtractor.metadata(self)
        self.gallery_id = self.groups[1]
        data["gallery"] = self.api.galleries_getInfo(self.gallery_id)
        return data

    def photos(self):
        return self.api.galleries_getPhotos(self.gallery_id)


class FlickrGroupExtractor(FlickrExtractor):
    """Extractor for group pools from flickr.com"""
    subcategory = "group"
    directory_fmt = ("{category}", "Groups", "{group[groupname]}")
    archive_fmt = "G_{group[nsid]}_{id}"
    pattern = rf"{BASE_PATTERN}/groups/([^/?#]+)"
    example = "https://www.flickr.com/groups/NAME/"

    def metadata(self):
        self.group = self.api.urls_lookupGroup(self.item_id)
        return {"group": self.group}

    def photos(self):
        return self.api.groups_pools_getPhotos(self.group["nsid"])


class FlickrUserExtractor(FlickrExtractor):
    """Extractor for the photostream of a flickr user"""
    subcategory = "user"
    archive_fmt = "u_{user[nsid]}_{id}"
    pattern = rf"{BASE_PATTERN}/photos/([^/?#]+)/?$"
    example = "https://www.flickr.com/photos/USER/"

    def photos(self):
        return self.api.people_getPhotos(self.user["nsid"])


class FlickrFavoriteExtractor(FlickrExtractor):
    """Extractor for favorite photos of a flickr user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user[username]}", "Favorites")
    archive_fmt = "f_{user[nsid]}_{id}"
    pattern = rf"{BASE_PATTERN}/photos/([^/?#]+)/favorites"
    example = "https://www.flickr.com/photos/USER/favorites"

    def photos(self):
        return self.api.favorites_getList(self.user["nsid"])


class FlickrSearchExtractor(FlickrExtractor):
    """Extractor for flickr photos based on search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search[text]}")
    archive_fmt = "s_{search}_{id}"
    pattern = rf"{BASE_PATTERN}/search/?\?([^#]+)"
    example = "https://flickr.com/search/?text=QUERY"

    def metadata(self):
        self.search = text.parse_query(self.groups[0])
        if "text" not in self.search:
            self.search["text"] = ""
        return {"search": self.search}

    def photos(self):
        return self.api.photos_search(self.search)
