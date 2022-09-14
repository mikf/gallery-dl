# -*- coding: utf-8 -*-

# Copyright 2017-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.flickr.com/"""

from .common import Extractor, Message
from .. import text, oauth, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.|secure\.|m\.)?flickr\.com"


class FlickrExtractor(Extractor):
    """Base class for flickr extractors"""
    category = "flickr"
    filename_fmt = "{category}_{id}.{extension}"
    directory_fmt = ("{category}", "{user[username]}")
    archive_fmt = "{id}"
    cookiedomain = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = FlickrAPI(self)
        self.item_id = match.group(1)
        self.user = None

    def items(self):
        data = self.metadata()
        extract = self.api._extract_format
        for photo in self.photos():
            try:
                photo = extract(photo)
            except Exception as exc:
                self.log.warning(
                    "Skipping %s (%s)", photo["id"], exc.__class__.__name__)
                self.log.debug("", exc_info=True)
            else:
                photo.update(data)
                url = photo["url"]
                yield Message.Directory, photo
                yield Message.Url, url, text.nameext_from_url(url, photo)

    def metadata(self):
        """Return general metadata"""
        self.user = self.api.urls_lookupUser(self.item_id)
        return {"user": self.user}

    def photos(self):
        """Return an iterable with all relevant photo objects"""


class FlickrImageExtractor(FlickrExtractor):
    """Extractor for individual images from flickr.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:(?:www\.|secure\.|m\.)?flickr\.com/photos/[^/?#]+/"
               r"|[\w-]+\.static\.?flickr\.com/(?:\d+/)+)(\d+)"
               r"|flic\.kr/p/([A-Za-z1-9]+))")
    test = (
        ("https://www.flickr.com/photos/departingyyz/16089302239", {
            "pattern": pattern,
            "content": ("3133006c6d657fe54cf7d4c46b82abbcb0efaf9f",
                        "0821a28ee46386e85b02b67cf2720063440a228c"),
            "keyword": {
                "comments": int,
                "description": str,
                "extension": "jpg",
                "filename": "16089302239_de18cd8017_b",
                "id": 16089302239,
                "height": 683,
                "label": "Large",
                "media": "photo",
                "url": str,
                "views": int,
                "width": 1024,
            },
        }),
        ("https://secure.flickr.com/photos/departingyyz/16089302239"),
        ("https://m.flickr.com/photos/departingyyz/16089302239"),
        ("https://flickr.com/photos/departingyyz/16089302239"),

        ("https://www.flickr.com/photos/145617051@N08/46733161535", {
            "count": 1,
            "keyword": {"media": "video"},
        }),
        ("http://c2.staticflickr.com/2/1475/24531000464_9a7503ae68_b.jpg", {
            "pattern": pattern}),
        ("https://farm2.static.flickr.com/1035/1188352415_cb139831d0.jpg", {
            "pattern": pattern}),
        ("https://flic.kr/p/FPVo9U", {
            "pattern": pattern}),
        ("https://www.flickr.com/photos/zzz/16089302238", {
            "exception": exception.NotFoundError}),
    )

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        if not self.item_id:
            alphabet = ("123456789abcdefghijkmnopqrstu"
                        "vwxyzABCDEFGHJKLMNPQRSTUVWXYZ")
            self.item_id = util.bdecode(match.group(2), alphabet)

    def items(self):
        photo = self.api.photos_getInfo(self.item_id)

        if photo["media"] == "video" and self.api.videos:
            self.api._extract_video(photo)
        else:
            self.api._extract_photo(photo)

        photo["user"] = photo["owner"]
        photo["title"] = photo["title"]["_content"]
        photo["comments"] = text.parse_int(photo["comments"]["_content"])
        photo["description"] = photo["description"]["_content"]
        photo["tags"] = [t["raw"] for t in photo["tags"]["tag"]]
        photo["date"] = text.parse_timestamp(photo["dateuploaded"])
        photo["views"] = text.parse_int(photo["views"])
        photo["id"] = text.parse_int(photo["id"])

        if "location" in photo:
            location = photo["location"]
            for key, value in location.items():
                if isinstance(value, dict):
                    location[key] = value["_content"]

        url = photo["url"]
        yield Message.Directory, photo
        yield Message.Url, url, text.nameext_from_url(url, photo)


class FlickrAlbumExtractor(FlickrExtractor):
    """Extractor for photo albums from flickr.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[username]}",
                     "Albums", "{album[id]} {album[title]}")
    archive_fmt = "a_{album[id]}_{id}"
    pattern = BASE_PATTERN + r"/photos/([^/?#]+)/(?:album|set)s(?:/(\d+))?"
    test = (
        (("https://www.flickr.com/photos/shona_s/albums/72157633471741607"), {
            "pattern": FlickrImageExtractor.pattern,
            "count": 6,
        }),
        ("https://www.flickr.com/photos/shona_s/albums", {
            "pattern": pattern,
            "count": 2,
        }),
        ("https://secure.flickr.com/photos/shona_s/albums"),
        ("https://m.flickr.com/photos/shona_s/albums"),
    )

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.album_id = match.group(2)

    def items(self):
        if self.album_id:
            return FlickrExtractor.items(self)
        return self._album_items()

    def _album_items(self):
        data = FlickrExtractor.metadata(self)
        data["_extractor"] = FlickrAlbumExtractor

        for album in self.api.photosets_getList(self.user["nsid"]):
            self.api._clean_info(album).update(data)
            url = "https://www.flickr.com/photos/{}/albums/{}".format(
                self.user["path_alias"], album["id"])
            yield Message.Queue, url, album

    def metadata(self):
        data = FlickrExtractor.metadata(self)
        data["album"] = self.api.photosets_getInfo(
            self.album_id, self.user["nsid"])
        return data

    def photos(self):
        return self.api.photosets_getPhotos(self.album_id)


class FlickrGalleryExtractor(FlickrExtractor):
    """Extractor for photo galleries from flickr.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[username]}",
                     "Galleries", "{gallery[gallery_id]} {gallery[title]}")
    archive_fmt = "g_{gallery[id]}_{id}"
    pattern = BASE_PATTERN + r"/photos/([^/?#]+)/galleries/(\d+)"
    test = (("https://www.flickr.com/photos/flickr/"
             "galleries/72157681572514792/"), {
        "pattern": FlickrImageExtractor.pattern,
        "count": ">= 10",
    })

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def metadata(self):
        data = FlickrExtractor.metadata(self)
        data["gallery"] = self.api.galleries_getInfo(self.gallery_id)
        return data

    def photos(self):
        return self.api.galleries_getPhotos(self.gallery_id)


class FlickrGroupExtractor(FlickrExtractor):
    """Extractor for group pools from flickr.com"""
    subcategory = "group"
    directory_fmt = ("{category}", "Groups", "{group[groupname]}")
    archive_fmt = "G_{group[nsid]}_{id}"
    pattern = BASE_PATTERN + r"/groups/([^/?#]+)"
    test = ("https://www.flickr.com/groups/bird_headshots/", {
        "pattern": FlickrImageExtractor.pattern,
        "count": "> 150",
    })

    def metadata(self):
        self.group = self.api.urls_lookupGroup(self.item_id)
        return {"group": self.group}

    def photos(self):
        return self.api.groups_pools_getPhotos(self.group["nsid"])


class FlickrUserExtractor(FlickrExtractor):
    """Extractor for the photostream of a flickr user"""
    subcategory = "user"
    archive_fmt = "u_{user[nsid]}_{id}"
    pattern = BASE_PATTERN + r"/photos/([^/?#]+)/?$"
    test = ("https://www.flickr.com/photos/shona_s/", {
        "pattern": FlickrImageExtractor.pattern,
        "count": 28,
    })

    def photos(self):
        return self.api.people_getPhotos(self.user["nsid"])


class FlickrFavoriteExtractor(FlickrExtractor):
    """Extractor for favorite photos of a flickr user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "{user[username]}", "Favorites")
    archive_fmt = "f_{user[nsid]}_{id}"
    pattern = BASE_PATTERN + r"/photos/([^/?#]+)/favorites"
    test = ("https://www.flickr.com/photos/shona_s/favorites", {
        "pattern": FlickrImageExtractor.pattern,
        "count": 4,
    })

    def photos(self):
        return self.api.favorites_getList(self.user["nsid"])


class FlickrSearchExtractor(FlickrExtractor):
    """Extractor for flickr photos based on search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search[text]}")
    archive_fmt = "s_{search}_{id}"
    pattern = BASE_PATTERN + r"/search/?\?([^#]+)"
    test = (
        ("https://flickr.com/search/?text=mountain"),
        ("https://flickr.com/search/?text=tree%20cloud%20house"
         "&color_codes=4&styles=minimalism"),
    )

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        self.search = text.parse_query(match.group(1))
        if "text" not in self.search:
            self.search["text"] = ""

    def metadata(self):
        return {"search": self.search}

    def photos(self):
        return self.api.photos_search(self.search)


class FlickrAPI(oauth.OAuth1API):
    """Minimal interface for the flickr API

    https://www.flickr.com/services/api/
    """

    API_URL = "https://api.flickr.com/services/rest/"
    API_KEY = "ac4fd7aa98585b9eee1ba761c209de68"
    API_SECRET = "3adb0f568dc68393"
    FORMATS = [
        ("o" , "Original"    , None),
        ("6k", "X-Large 6K"  , 6144),
        ("5k", "X-Large 5K"  , 5120),
        ("4k", "X-Large 4K"  , 4096),
        ("3k", "X-Large 3K"  , 3072),
        ("k" , "Large 2048"  , 2048),
        ("h" , "Large 1600"  , 1600),
        ("l" , "Large"       , 1024),
        ("c" , "Medium 800"  , 800),
        ("z" , "Medium 640"  , 640),
        ("m" , "Medium"      , 500),
        ("n" , "Small 320"   , 320),
        ("s" , "Small"       , 240),
        ("q" , "Large Square", 150),
        ("t" , "Thumbnail"   , 100),
        ("s" , "Square"      , 75),
    ]
    VIDEO_FORMATS = {
        "orig"       : 9,
        "1080p"      : 8,
        "720p"       : 7,
        "360p"       : 6,
        "288p"       : 5,
        "700"        : 4,
        "300"        : 3,
        "100"        : 2,
        "appletv"    : 1,
        "iphone_wifi": 0,
    }

    def __init__(self, extractor):
        oauth.OAuth1API.__init__(self, extractor)

        self.videos = extractor.config("videos", True)
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
        self.formats = self.formats[:8]

    def favorites_getList(self, user_id):
        """Returns a list of the user's favorite photos."""
        params = {"user_id": user_id}
        return self._pagination("favorites.getList", params)

    def galleries_getInfo(self, gallery_id):
        """Gets information about a gallery."""
        params = {"gallery_id": gallery_id}
        gallery = self._call("galleries.getInfo", params)["gallery"]
        return self._clean_info(gallery)

    def galleries_getPhotos(self, gallery_id):
        """Return the list of photos for a gallery."""
        params = {"gallery_id": gallery_id}
        return self._pagination("galleries.getPhotos", params)

    def groups_pools_getPhotos(self, group_id):
        """Returns a list of pool photos for a given group."""
        params = {"group_id": group_id}
        return self._pagination("groups.pools.getPhotos", params)

    def people_getPhotos(self, user_id):
        """Return photos from the given user's photostream."""
        params = {"user_id": user_id}
        return self._pagination("people.getPhotos", params)

    def photos_getInfo(self, photo_id):
        """Get information about a photo."""
        params = {"photo_id": photo_id}
        return self._call("photos.getInfo", params)["photo"]

    def photos_getSizes(self, photo_id):
        """Returns the available sizes for a photo."""
        params = {"photo_id": photo_id}
        sizes = self._call("photos.getSizes", params)["sizes"]["size"]
        if self.maxsize:
            for index, size in enumerate(sizes):
                if index > 0 and (int(size["width"]) > self.maxsize or
                                  int(size["height"]) > self.maxsize):
                    del sizes[index:]
                    break
        return sizes

    def photos_search(self, params):
        """Return a list of photos matching some criteria."""
        return self._pagination("photos.search", params.copy())

    def photosets_getInfo(self, photoset_id, user_id):
        """Gets information about a photoset."""
        params = {"photoset_id": photoset_id, "user_id": user_id}
        photoset = self._call("photosets.getInfo", params)["photoset"]
        return self._clean_info(photoset)

    def photosets_getList(self, user_id):
        """Returns the photosets belonging to the specified user."""
        params = {"user_id": user_id}
        return self._pagination_sets("photosets.getList", params)

    def photosets_getPhotos(self, photoset_id):
        """Get the list of photos in a set."""
        params = {"photoset_id": photoset_id}
        return self._pagination("photosets.getPhotos", params, "photoset")

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
        return {
            "nsid"      : user["id"],
            "username"  : user["username"]["_content"],
            "path_alias": username,
        }

    def video_getStreamInfo(self, video_id, secret=None):
        """Returns all available video streams"""
        params = {"photo_id": video_id}
        if not secret:
            secret = self._call("photos.getInfo", params)["photo"]["secret"]
        params["secret"] = secret
        stream = self._call("video.getStreamInfo", params)["streams"]["stream"]
        return max(stream, key=lambda s: self.VIDEO_FORMATS.get(s["type"], 0))

    def _call(self, method, params):
        params["method"] = "flickr." + method
        params["format"] = "json"
        params["nojsoncallback"] = "1"
        if self.api_key:
            params["api_key"] = self.api_key
        data = self.request(self.API_URL, params=params).json()
        if "code" in data:
            msg = data.get("message")
            self.log.debug("Server response: %s", data)
            if data["code"] == 1:
                raise exception.NotFoundError(self.extractor.subcategory)
            elif data["code"] == 98:
                raise exception.AuthenticationError(msg)
            elif data["code"] == 99:
                raise exception.AuthorizationError(msg)
            raise exception.StopExtraction("API request failed: %s", msg)
        return data

    def _pagination(self, method, params, key="photos"):
        params["extras"] = ("description,date_upload,tags,views,media,"
                            "path_alias,owner_name,")
        params["extras"] += ",".join("url_" + fmt[0] for fmt in self.formats)
        params["page"] = 1

        while True:
            data = self._call(method, params)[key]
            yield from data["photo"]
            if params["page"] >= data["pages"]:
                return
            params["page"] += 1

    def _pagination_sets(self, method, params):
        params["page"] = 1

        while True:
            data = self._call(method, params)["photosets"]
            yield from data["photoset"]
            if params["page"] >= data["pages"]:
                return
            params["page"] += 1

    def _extract_format(self, photo):
        photo["description"] = photo["description"]["_content"].strip()
        photo["views"] = text.parse_int(photo["views"])
        photo["date"] = text.parse_timestamp(photo["dateupload"])
        photo["tags"] = photo["tags"].split()
        photo["id"] = text.parse_int(photo["id"])

        if "owner" in photo:
            photo["owner"] = {
                "nsid"      : photo["owner"],
                "username"  : photo["ownername"],
                "path_alias": photo["pathalias"],
            }
        else:
            photo["owner"] = self.extractor.user
        del photo["pathalias"]
        del photo["ownername"]

        if photo["media"] == "video" and self.videos:
            return self._extract_video(photo)

        for fmt, fmtname, fmtwidth in self.formats:
            key = "url_" + fmt
            if key in photo:
                photo["width"] = text.parse_int(photo["width_" + fmt])
                photo["height"] = text.parse_int(photo["height_" + fmt])
                if self.maxsize and (photo["width"] > self.maxsize or
                                     photo["height"] > self.maxsize):
                    continue
                photo["url"] = photo[key]
                photo["label"] = fmtname

                # remove excess data
                keys = [
                    key for key in photo
                    if key.startswith(("url_", "width_", "height_"))
                ]
                for key in keys:
                    del photo[key]
                break
        else:
            self._extract_photo(photo)

        return photo

    def _extract_photo(self, photo):
        size = self.photos_getSizes(photo["id"])[-1]
        photo["url"] = size["source"]
        photo["label"] = size["label"]
        photo["width"] = text.parse_int(size["width"])
        photo["height"] = text.parse_int(size["height"])
        return photo

    def _extract_video(self, photo):
        stream = self.video_getStreamInfo(photo["id"], photo.get("secret"))
        photo["url"] = stream["_content"]
        photo["label"] = stream["type"]
        photo["width"] = photo["height"] = 0
        return photo

    @staticmethod
    def _clean_info(info):
        info["title"] = info["title"]["_content"]
        info["description"] = info["description"]["_content"]
        return info
