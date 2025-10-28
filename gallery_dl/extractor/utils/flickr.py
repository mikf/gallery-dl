# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import oauth, text, exception


class FlickrOAuthAPI(oauth.OAuth1API):
    """Interface for the Flickr OAuth API

    https://www.flickr.com/services/api/
    """

    API_URL = "https://api.flickr.com/services/rest/"
    API_KEY = "90c368449018a0cb880ea4889cbb8681"
    API_SECRET = "e4b83e319c11e9e1"
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
    LICENSES = {
        "0": "All Rights Reserved",
        "1": "Attribution-NonCommercial-ShareAlike License",
        "2": "Attribution-NonCommercial License",
        "3": "Attribution-NonCommercial-NoDerivs License",
        "4": "Attribution License",
        "5": "Attribution-ShareAlike License",
        "6": "Attribution-NoDerivs License",
        "7": "No known copyright restrictions",
        "8": "United States Government Work",
        "9": "Public Domain Dedication (CC0)",
        "10": "Public Domain Mark",
    }

    def __init__(self, extractor):
        oauth.OAuth1API.__init__(self, extractor)

        self.videos = extractor.config("videos", True)
        self.meta_exif = extractor.config("exif", False)
        self.meta_info = extractor.config("info", False)
        self.meta_contexts = extractor.config("contexts", False)

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

    def people_getInfo(self, user_id):
        """Get information about a user."""
        params = {"user_id": user_id}
        user = self._call("people.getInfo", params)

        try:
            user = user["person"]
            for key in ("description", "username", "realname", "location",
                        "profileurl", "photosurl", "mobileurl"):
                if isinstance(user.get(key), dict):
                    user[key] = user[key]["_content"]
            photos = user["photos"]
            for key in ("count", "firstdate", "firstdatetaken"):
                if isinstance(photos.get(key), dict):
                    photos[key] = photos[key]["_content"]
        except Exception:
            pass

        return user

    def people_getPhotos(self, user_id):
        """Return photos from the given user's photostream."""
        params = {"user_id": user_id}
        return self._pagination("people.getPhotos", params)

    def photos_getAllContexts(self, photo_id):
        """Returns all visible sets and pools the photo belongs to."""
        params = {"photo_id": photo_id}
        data = self._call("photos.getAllContexts", params)
        del data["stat"]
        return data

    def photos_getExif(self, photo_id):
        """Retrieves a list of EXIF/TIFF/GPS tags for a given photo."""
        params = {"photo_id": photo_id}
        return self._call("photos.getExif", params)["photo"]

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
        response = self.request(self.API_URL, params=params)
        try:
            data = response.json()
        except ValueError:
            data = {"code": -1, "message": response.content}
        if "code" in data:
            msg = data.get("message")
            self.log.debug("Server response: %s", data)
            if data["code"] == 1:
                raise exception.NotFoundError(self.extractor.subcategory)
            elif data["code"] == 2:
                raise exception.AuthorizationError(msg)
            elif data["code"] == 98:
                raise exception.AuthenticationError(msg)
            elif data["code"] == 99:
                raise exception.AuthorizationError(msg)
            raise exception.AbortExtraction(f"API request failed: {msg}")
        return data

    def _pagination(self, method, params, key="photos"):
        extras = ("description,date_upload,tags,views,media,"
                  "path_alias,owner_name,")
        if includes := self.extractor.config("metadata"):
            if isinstance(includes, (list, tuple)):
                includes = ",".join(includes)
            elif not isinstance(includes, str):
                includes = ("license,date_taken,original_format,last_update,"
                            "geo,machine_tags,o_dims")
            extras = extras + includes + ","
        extras += ",".join("url_" + fmt[0] for fmt in self.formats)

        params["extras"] = extras
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
        photo["date"] = self.parse_timestamp(photo["dateupload"])
        photo["tags"] = photo["tags"].split()

        self._extract_metadata(photo)
        photo["id"] = text.parse_int(photo["id"])

        if "owner" not in photo:
            photo["owner"] = self.extractor.user
        elif not self.meta_info:
            photo["owner"] = {
                "nsid"      : photo["owner"],
                "username"  : photo["ownername"],
                "path_alias": photo["pathalias"],
            }

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

    def _extract_metadata(self, photo, info=True):
        if info and self.meta_info:
            try:
                photo.update(self.photos_getInfo(photo["id"]))
                photo["title"] = photo["title"]["_content"]
                photo["comments"] = text.parse_int(
                    photo["comments"]["_content"])
                photo["description"] = photo["description"]["_content"]
                photo["tags"] = [t["raw"] for t in photo["tags"]["tag"]]
                photo["views"] = text.parse_int(photo["views"])
                photo["id"] = text.parse_int(photo["id"])
            except Exception as exc:
                self.log.warning(
                    "Unable to retrieve 'info' data for %s (%s: %s)",
                    photo["id"], exc.__class__.__name__, exc)

        if self.meta_exif:
            try:
                photo.update(self.photos_getExif(photo["id"]))
            except Exception as exc:
                self.log.warning(
                    "Unable to retrieve 'exif' data for %s (%s: %s)",
                    photo["id"], exc.__class__.__name__, exc)

        if self.meta_contexts:
            try:
                photo.update(self.photos_getAllContexts(photo["id"]))
            except Exception as exc:
                self.log.warning(
                    "Unable to retrieve 'contexts' data for %s (%s: %s)",
                    photo["id"], exc.__class__.__name__, exc)

        if "license" in photo:
            photo["license_name"] = self.LICENSES.get(photo["license"])

    def _clean_info(self, info):
        info["title"] = info["title"]["_content"]
        info["description"] = info["description"]["_content"]
        return info
