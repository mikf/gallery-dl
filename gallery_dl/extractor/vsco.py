# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vsco.co/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vsco\.co"
USER_PATTERN = BASE_PATTERN + r"/([^/?#]+)"


class VscoExtractor(Extractor):
    """Base class for vsco extractors"""
    category = "vsco"
    root = "https://vsco.co"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1).lower()

    def items(self):
        videos = self.config("videos", True)
        yield Message.Directory, {"user": self.user}
        for img in self.images():

            if not img:
                continue
            elif "playback_url" in img:
                img = self._transform_video(img)
            elif "responsive_url" not in img:
                continue

            if img["is_video"]:
                if not videos:
                    continue
                url = text.ensure_http_scheme(img["video_url"])
            else:
                base = img["responsive_url"].partition("/")[2]
                cdn, _, path = base.partition("/")
                if cdn.startswith("aws"):
                    url = "https://image-{}.vsco.co/{}".format(cdn, path)
                elif cdn.isdecimal():
                    url = "https://image.vsco.co/" + base
                elif img["responsive_url"].startswith("http"):
                    url = img["responsive_url"]
                else:
                    url = "https://" + img["responsive_url"]

            data = text.nameext_from_url(url, {
                "id"    : img["_id"],
                "user"  : self.user,
                "grid"  : img["grid_name"],
                "meta"  : img.get("image_meta") or {},
                "tags"  : [tag["text"] for tag in img.get("tags") or ()],
                "date"  : text.parse_timestamp(img["upload_date"] // 1000),
                "video" : img["is_video"],
                "width" : img["width"],
                "height": img["height"],
                "description": img.get("description") or "",
            })
            if data["extension"] == "m3u8":
                url = "ytdl:" + url
                data["_ytdl_manifest"] = "hls"
                data["extension"] = "mp4"
            yield Message.Url, url, data

    def images(self):
        """Return an iterable with all relevant image objects"""

    def _extract_preload_state(self, url):
        page = self.request(url, notfound=self.subcategory).text
        return util.json_loads(text.extr(page, "__PRELOADED_STATE__ = ", "<")
                               .replace('"prevPageToken":undefined,', ''))

    def _pagination(self, url, params, token, key, extra=None):
        headers = {
            "Referer"          : "{}/{}".format(self.root, self.user),
            "Authorization"    : "Bearer " + token,
            "X-Client-Platform": "web",
            "X-Client-Build"   : "1",
        }

        if extra:
            yield from map(self._transform_media, extra)

        while True:
            data = self.request(url, params=params, headers=headers).json()
            medias = data.get(key)
            if not medias:
                return

            if "cursor" in params:
                for media in medias:
                    yield media[media["type"]]
                cursor = data.get("next_cursor")
                if not cursor:
                    return
                params["cursor"] = cursor
            else:
                yield from medias
                params["page"] += 1

    @staticmethod
    def _transform_media(media):
        if "responsiveUrl" not in media:
            return None
        media["_id"] = media["id"]
        media["is_video"] = media["isVideo"]
        media["grid_name"] = media["gridName"]
        media["upload_date"] = media["uploadDate"]
        media["responsive_url"] = media["responsiveUrl"]
        media["video_url"] = media.get("videoUrl")
        media["image_meta"] = media.get("imageMeta")
        return media

    @staticmethod
    def _transform_video(media):
        media["is_video"] = True
        media["grid_name"] = ""
        media["video_url"] = media["playback_url"]
        media["responsive_url"] = media["poster_url"]
        media["upload_date"] = media["created_date"]
        return media


class VscoUserExtractor(VscoExtractor):
    """Extractor for a vsco user profile"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?$"
    example = "https://vsco.co/USER"

    def initialize(self):
        pass

    def items(self):
        base = "{}/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (VscoAvatarExtractor    , base + "avatar"),
            (VscoGalleryExtractor   , base + "gallery"),
            (VscoSpacesExtractor    , base + "spaces"),
            (VscoCollectionExtractor, base + "collection"),
        ), ("gallery",))


class VscoGalleryExtractor(VscoExtractor):
    """Extractor for a vsco user's gallery"""
    subcategory = "gallery"
    pattern = USER_PATTERN + r"/(?:gallery|images)"
    example = "https://vsco.co/USER/gallery"

    def images(self):
        url = "{}/{}/gallery".format(self.root, self.user)
        data = self._extract_preload_state(url)
        tkn = data["users"]["currentUser"]["tkn"]
        sid = str(data["sites"]["siteByUsername"][self.user]["site"]["id"])

        url = "{}/api/3.0/medias/profile".format(self.root)
        params = {
            "site_id"  : sid,
            "limit"    : "14",
            "cursor"   : None,
        }

        return self._pagination(url, params, tkn, "media")


class VscoCollectionExtractor(VscoExtractor):
    """Extractor for images from a collection on vsco.co"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{user}", "collection")
    archive_fmt = "c_{user}_{id}"
    pattern = USER_PATTERN + r"/collection"
    example = "https://vsco.co/USER/collection/1"

    def images(self):
        url = "{}/{}/collection/1".format(self.root, self.user)
        data = self._extract_preload_state(url)

        tkn = data["users"]["currentUser"]["tkn"]
        cid = (data["sites"]["siteByUsername"][self.user]
               ["site"]["siteCollectionId"])

        url = "{}/api/2.0/collections/{}/medias".format(self.root, cid)
        params = {"page": 2, "size": "20"}
        return self._pagination(url, params, tkn, "medias", (
            data["medias"]["byId"][mid["id"]]["media"]
            for mid in data
            ["collections"]["byId"][cid]["1"]["collection"]
        ))


class VscoSpaceExtractor(VscoExtractor):
    """Extractor for a vsco.co space"""
    subcategory = "space"
    directory_fmt = ("{category}", "space", "{user}")
    archive_fmt = "s_{user}_{id}"
    pattern = BASE_PATTERN + r"/spaces/([^/?#]+)"
    example = "https://vsco.co/spaces/a1b2c3d4e5f"

    def images(self):
        url = "{}/spaces/{}".format(self.root, self.user)
        data = self._extract_preload_state(url)

        tkn = data["users"]["currentUser"]["tkn"]
        sid = self.user

        posts = data["entities"]["posts"]
        images = data["entities"]["postImages"]
        for post in posts.values():
            post["image"] = images[post["image"]]

        space = data["spaces"]["byId"][sid]
        space["postsList"] = [posts[pid] for pid in space["postsList"]]

        url = "{}/grpc/spaces/{}/posts".format(self.root, sid)
        params = {}
        return self._pagination(url, params, tkn, space)

    def _pagination(self, url, params, token, data):
        headers = {
            "Accept"       : "application/json",
            "Referer"      : "{}/spaces/{}".format(self.root, self.user),
            "Content-Type" : "application/json",
            "Authorization": "Bearer " + token,
        }

        while True:
            for post in data["postsList"]:
                post = self._transform_media(post["image"])
                post["upload_date"] = post["upload_date"]["sec"] * 1000
                yield post

            cursor = data["cursor"]
            if cursor.get("atEnd"):
                return
            params["cursor"] = cursor["postcursorcontext"]["postId"]

            data = self.request(url, params=params, headers=headers).json()


class VscoSpacesExtractor(VscoExtractor):
    """Extractor for a vsco.co user's spaces"""
    subcategory = "spaces"
    pattern = USER_PATTERN + r"/spaces"
    example = "https://vsco.co/USER/spaces"

    def items(self):
        url = "{}/{}/spaces".format(self.root, self.user)
        data = self._extract_preload_state(url)

        tkn = data["users"]["currentUser"]["tkn"]
        uid = data["sites"]["siteByUsername"][self.user]["site"]["userId"]

        headers = {
            "Accept"       : "application/json",
            "Referer"      : url,
            "Content-Type" : "application/json",
            "Authorization": "Bearer " + tkn,
        }
        # this would theoretically need to be paginated
        url = "{}/grpc/spaces/user/{}".format(self.root, uid)
        data = self.request(url, headers=headers).json()

        for space in data["spacesWithRoleList"]:
            space = space["space"]
            url = "{}/spaces/{}".format(self.root, space["id"])
            space["_extractor"] = VscoSpaceExtractor
            yield Message.Queue, url, space


class VscoAvatarExtractor(VscoExtractor):
    """Extractor for vsco.co user avatars"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://vsco.co/USER/avatar"

    def images(self):
        url = "{}/{}/gallery".format(self.root, self.user)
        page = self.request(url).text
        piid = text.extr(page, '"profileImageId":"', '"')

        url = "https://im.vsco.co/" + piid
        # needs GET request, since HEAD does not redirect to full URL
        response = self.request(url, allow_redirects=False)

        return ({
            "_id"           : piid,
            "is_video"      : False,
            "grid_name"     : "",
            "upload_date"   : 0,
            "responsive_url": response.headers["Location"],
            "video_url"     : "",
            "image_meta"    : None,
            "width"         : 0,
            "height"        : 0,
        },)


class VscoImageExtractor(VscoExtractor):
    """Extractor for individual images on vsco.co"""
    subcategory = "image"
    pattern = USER_PATTERN + r"/media/([0-9a-fA-F]+)"
    example = "https://vsco.co/USER/media/0123456789abcdef"

    def images(self):
        url = "{}/{}/media/{}".format(self.root, self.user, self.groups[1])
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]
        return (self._transform_media(media),)


class VscoVideoExtractor(VscoExtractor):
    """Extractor for vsco.co videos links"""
    subcategory = "video"
    pattern = USER_PATTERN + r"/video/([^/?#]+)"
    example = "https://vsco.co/USER/video/012345678-9abc-def0"

    def images(self):
        url = "{}/{}/video/{}".format(self.root, self.user, self.groups[1])
        data = self._extract_preload_state(url)
        media = data["medias"]["byId"].popitem()[1]["media"]

        return ({
            "_id"           : media["id"],
            "is_video"      : True,
            "grid_name"     : "",
            "upload_date"   : media["createdDate"],
            "responsive_url": media["posterUrl"],
            "video_url"     : media.get("playbackUrl"),
            "image_meta"    : None,
            "width"         : media["width"],
            "height"        : media["height"],
            "description"   : media["description"],
        },)
