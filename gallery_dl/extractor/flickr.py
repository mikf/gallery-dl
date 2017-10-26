# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.flickr.com/"""

from .common import Extractor, Message
from .. import text, util, exception


class FlickrExtractor(Extractor):
    """Base class for flickr extractors"""
    category = "flickr"
    filename_fmt = "{category}_{id}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.api = FlickrAPI(self)
        self.item_id = match.group(1)
        self.user = None
        self.load_extra = self.config("metadata", False)

    def items(self):
        info = self.data()
        yield Message.Version, 1
        yield Message.Directory, info
        for photo in self.photos():
            photo.update(info)
            url = photo["photo"]["source"]
            yield Message.Url, url, text.nameext_from_url(url, photo)

    def data(self):
        self.user = self.api.urls_lookupUser(self.item_id)
        return {"user": self.user}

    def photos(self):
        return []


class FlickrImageExtractor(FlickrExtractor):
    """Extractor for individual images from flickr.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.|m\.)?flickr\.com/photos/[^/]+/(\d+)",
               r"(?:https?://)?[^.]+\.static\.?flickr\.com/(?:\d+/)+(\d+)_",
               r"(?:https?://)?flic\.kr/(p)/([A-Za-z1-9]+)"]
    test = [
        ("https://www.flickr.com/photos/departingyyz/16089302239", {
            "url": "7f0887f5953f61c8b79a695cb102ea309c0346b0",
            "keyword": "5ecdaf0192802451b7daca9b81f393f207ff7ee9",
            "content": "6aaad7512d335ca93286fe2046e7fe3bb93d808e",
        }),
        ("http://c2.staticflickr.com/2/1475/24531000464_9a7503ae68_b.jpg", {
            "url": "40f5163488522ca5d918750ed7bd7fcf437982fe"}),
        ("https://farm2.static.flickr.com/1035/1188352415_cb139831d0.jpg", {
            "url": "ef217b4fdcb148a0cc9eae44b9342d4a65f6d697"}),
        ("https://flic.kr/p/FPVo9U", {
            "url": "92c54a00f31040c349cb2abcb1b9abe30cc508ae"}),
        ("https://www.flickr.com/photos/zzz/16089302238", {
            "exception": exception.NotFoundError}),
    ]

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        if self.item_id == "p":
            alphabet = ("123456789abcdefghijkmnopqrstu"
                        "vwxyzABCDEFGHJKLMNPQRSTUVWXYZ")
            self.item_id = util.bdecode(match.group(2), alphabet)

    def items(self):
        size = self.api.photos_getSizes(self.item_id)[-1]

        if self.load_extra:
            info = self.api.photos_getInfo(self.item_id)
            self._clean(info)
        else:
            info = {"id": self.item_id}

        info["photo"] = size
        url = size["source"]
        text.nameext_from_url(url, info)

        yield Message.Version, 1
        yield Message.Directory, info
        yield Message.Url, url, info

    @staticmethod
    def _clean(photo):
        del photo["comments"]
        del photo["views"]

        photo["title"] = photo["title"]["_content"]
        photo["tags"] = [t["raw"] for t in photo["tags"]["tag"]]

        if "location" in photo:
            location = photo["location"]
            for key, value in location.items():
                if isinstance(value, dict):
                    location[key] = value["_content"]


class FlickrAlbumExtractor(FlickrExtractor):
    """Extractor for photo albums from flickr.com"""
    subcategory = "album"
    directory_fmt = ["{category}", "{subcategory}s",
                     "{album[id]} - {album[title]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/"
               r"photos/([^/]+)/(?:album|set)s/(\d+)"]
    test = [(("https://www.flickr.com/photos/"
              "shona_s/albums/72157633471741607"), {
        "url": "baf4a3d1b15afcecf9638000a12c0eb3d5df9024",
        "keyword": "40605c5b22feafcd029d1121f4dc8786b0aa7dcc",
    })]

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.album_id = match.group(2)

    def data(self):
        self._generator = self.api.photosets_getPhotos(self.album_id)
        self._first = next(self._generator)
        photoset = self._first.copy()
        del photoset["photo"]
        return {"album": photoset}

    def photos(self):
        for photo in self._photos():
            self.api._extract_format(photo)
            yield photo

    def _photos(self):
        yield from self._first["photo"]
        for photoset in self._generator:
            yield from photoset["photo"]


class FlickrGalleryExtractor(FlickrExtractor):
    """Extractor for photo galleries from flickr.com"""
    subcategory = "gallery"
    directory_fmt = ["{category}", "galleries",
                     "{user[username]} {gallery[id]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/"
               r"photos/([^/]+)/galleries/(\d+)"]
    test = [(("https://www.flickr.com/photos/flickr/"
              "galleries/72157681572514792/"), {
        "url": "97dd9640b09384f313845b784046da410f70aee6",
        "keyword": "8b11026066ec86290ae18833859623ee5b52d363",
    })]

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def data(self):
        info = FlickrExtractor.data(self)
        if self.load_extra:
            info["gallery"] = self.api.galleries_getInfo(self.gallery_id)
        else:
            info["gallery"] = {"id": self.gallery_id}
        return info

    def photos(self):
        return self.api.galleries_getPhotos(self.gallery_id)


class FlickrGroupExtractor(FlickrExtractor):
    """Extractor for group pools from flickr.com"""
    subcategory = "group"
    directory_fmt = ["{category}", "{subcategory}s", "{group[groupname]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/groups/([^/]+)"]
    test = [("https://www.flickr.com/groups/bird_headshots/", {
        "pattern": (r"https?://farm\d+\.staticflickr\.com"
                    r"/\d+/\d+_[0-9a-f]+(_[a-z])?\.[a-z]+"),
    })]

    def data(self):
        self.group = self.api.urls_lookupGroup(self.item_id)
        return {"group": self.group}

    def photos(self):
        return self.api.groups_pools_getPhotos(self.group["nsid"])


class FlickrUserExtractor(FlickrExtractor):
    """Extractor for the photostream of a flickr user"""
    subcategory = "user"
    directory_fmt = ["{category}", "{user[username]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/photos/([^/]+)/?$"]
    test = [("https://www.flickr.com/photos/shona_s/", {
        "url": "d125b536cd8c4229363276b6c84579c394eec3a2",
        "keyword": "2cdeae22cd9c3ff19ce905215f3782a7494d8264",
    })]

    def photos(self):
        return self.api.people_getPhotos(self.user["nsid"])


class FlickrFavoriteExtractor(FlickrExtractor):
    """Extractor for favorite photos of a flickr user"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "{subcategory}s", "{user[username]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/photos/([^/]+)/favorites"]
    test = [("https://www.flickr.com/photos/shona_s/favorites", {
        "url": "5129b3f5bfa83cc25bdae3ce476036de1488dad2",
        "keyword": "0e1c9521b6051411b585c9b41a4dc0bcde20e616",
    })]

    def photos(self):
        return self.api.favorites_getList(self.user["nsid"])


class FlickrSearchExtractor(FlickrExtractor):
    """Extractor for flickr photos based on search results"""
    subcategory = "search"
    directory_fmt = ["{category}", "{subcategory}", "{search[text]}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/search/?\?([^#]+)"]
    test = [
        (("https://flickr.com/search/?text=mountain"), None),
        (("https://flickr.com/search/?text=tree%20cloud%20house"
          "&color_codes=4&styles=minimalism"), None),
    ]

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.search = text.parse_query(match.group(1))
        if "text" not in self.search:
            self.search["text"] = ""

    def data(self):
        return {"search": self.search}

    def photos(self):
        return self.api.photos_search(self.search)


class FlickrAPI():
    """Minimal interface for the flickr API"""
    API_URL = "https://api.flickr.com/services/rest/"
    API_KEY = "ac4fd7aa98585b9eee1ba761c209de68"
    API_SECRET = "3adb0f568dc68393"
    FORMATS = [
        ("o", "Original", None),
        ("k", "Large 2048", 2048),
        ("h", "Large 1600", 1600),
        ("l", "Large", 1024),
        ("c", "Medium 800", 800),
        ("z", "Medium 640", 640),
        ("m", "Medium", 500),
        ("n", "Small 320", 320),
        ("s", "Small", 240),
        ("q", "Large Square", 150),
        ("t", "Thumbnail", 100),
        ("s", "Square", 75),
    ]

    def __init__(self, extractor):
        self.api_key = extractor.config("api-key", self.API_KEY)
        self.api_secret = extractor.config("api-secret", self.API_SECRET)
        token = extractor.config("access-token")
        token_secret = extractor.config("access-token-secret")
        if token and token_secret:
            self.session = util.OAuthSession(
                extractor.session,
                self.api_key, self.api_secret, token, token_secret)
            self.api_key = None
        else:
            self.session = extractor.session

        self.maxsize = extractor.config("size-max")
        if isinstance(self.maxsize, str):
            for fmt, fmtname, fmtwidth in self.FORMATS:
                if self.maxsize == fmt or self.maxsize == fmtname:
                    self.maxsize = fmtwidth
                    break
            else:
                self.maxsize = None
                extractor.log.warning(
                    "Could not match '%s' to any format", self.maxsize)
        if self.maxsize:
            self.formats = [fmt for fmt in self.FORMATS
                            if not fmt[2] or fmt[2] <= self.maxsize]
        else:
            self.formats = self.FORMATS
        self.formats = self.formats[:4]
        self.subcategory = extractor.subcategory

    def favorites_getList(self, user_id):
        """Returns a list of the user's favorite photos."""
        params = {"user_id": user_id}
        return self._listing("favorites.getList", params)

    def galleries_getInfo(self, gallery_id):
        """Gets information about a gallery."""
        params = {"gallery_id": gallery_id}
        gallery = self._call("galleries.getInfo", params)["gallery"]
        del gallery["count_views"]
        del gallery["count_comments"]
        gallery["title"] = gallery["title"]["_content"]
        gallery["description"] = gallery["description"]["_content"]
        return gallery

    def galleries_getPhotos(self, gallery_id):
        """Return the list of photos for a gallery."""
        params = {"gallery_id": gallery_id}
        return self._listing("galleries.getPhotos", params)

    def groups_pools_getPhotos(self, group_id):
        """Returns a list of pool photos for a given group."""
        params = {"group_id": group_id}
        return self._listing("groups.pools.getPhotos", params)

    def people_getPhotos(self, user_id):
        """Return photos from the given user's photostream."""
        params = {"user_id": user_id}
        return self._listing("people.getPhotos", params)

    def photos_getInfo(self, photo_id):
        """Get information about a photo."""
        params = {"photo_id": photo_id}
        return self._call("photos.getInfo", params)["photo"]

    def photos_getSizes(self, photo_id):
        """Returns the available sizes for a photo."""
        params = {"photo_id": photo_id}
        sizes = self._call("photos.getSizes", params)["sizes"]["size"]
        if sizes[-1]["media"] == "video":
            # filter all non-video and mobile entries
            sizes = [size for size in sizes
                     if size["media"] == "video" and
                     not size["label"].startswith(("Mobile ", "Video "))]
        if self.maxsize:
            for index, size in enumerate(sizes):
                if index > 0 and (int(size["width"]) > self.maxsize or
                                  int(size["height"]) > self.maxsize):
                    del sizes[index:]
                    break
        return sizes

    def photos_search(self, params):
        """Return a list of photos matching some criteria."""
        return self._listing("photos.search", params.copy())

    def photosets_getPhotos(self, photoset_id):
        """Get the list of photos in a set."""
        params = {"photoset_id": photoset_id}
        return self._pagination("photosets.getPhotos", params)

    def urls_lookupGroup(self, groupname):
        """Returns a group NSID, given the url to a group's page."""
        params = {"url": "https://www.flickr.com/groups/" + groupname}
        group = self._call("urls.lookupGroup", params)["group"]
        return {"nsid": group["id"],
                "path_alias": groupname,
                "groupname": group["groupname"]["_content"]}

    def urls_lookupUser(self, username):
        """Returns a user NSID, given the url to a user's photos or profile."""
        params = {"url": "https://www.flickr.com/photos/" + username}
        user = self._call("urls.lookupUser", params)["user"]
        return {"nsid": user["id"],
                "path_alias": username,
                "username": user["username"]["_content"]}

    def _call(self, method, params):
        params["method"] = "flickr." + method
        params["format"] = "json"
        params["nojsoncallback"] = "1"
        if self.api_key:
            params["api_key"] = self.api_key
        data = self.session.get(self.API_URL, params=params).json()
        if "code" in data and data["code"] == 1:
            raise exception.NotFoundError(self.subcategory)
        return data

    def _pagination(self, method, params):
        params["extras"] = ",".join("url_" + fmt[0] for fmt in self.formats)
        params["page"] = 1

        while True:
            data = self._call(method, params)

            for key, obj in data.items():
                if not key.startswith("stat"):
                    break
            del obj["page"]
            del obj["perpage"]
            if "per_page" in obj:
                del obj["per_page"]

            yield obj

            if params["page"] >= obj["pages"]:
                break
            params["page"] += 1

    def _listing(self, method, params):
        for photos in self._pagination(method, params):
            for photo in photos["photo"]:
                self._extract_format(photo)
                yield photo

    def _extract_format(self, photo):
        for fmt, fmtname, fmtwidth in self.formats:
            key = "url_" + fmt
            if key in photo:
                width, height = photo["width_" + fmt], photo["height_" + fmt]
                if self.maxsize and (int(width) > self.maxsize or
                                     int(height) > self.maxsize):
                    continue
                # generate photo info
                photo["photo"] = {
                    "source": photo[key],
                    "width" : width,
                    "height": height,
                    "label" : fmtname,
                    "media" : "photo",
                }
                # remove excess data
                keys = [
                    key for key in photo.keys()
                    if key.startswith(("url_", "width_", "height_"))
                ]
                for key in keys:
                    del photo[key]
                break
        else:
            # extra API call to get photo url and size
            photo["photo"] = self.photos_getSizes(photo["id"])[-1]
