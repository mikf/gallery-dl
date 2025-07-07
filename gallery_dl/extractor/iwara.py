# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.iwara.tv/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache, memcache
from urllib.parse import urlparse, parse_qs
import hashlib

BASE_PATTERN = r"(?:https?://)?(?:www\.)?iwara\.tv"
USER_PATTERN = rf"{BASE_PATTERN}/profile/([^/?#]+)"


class IwaraExtractor(Extractor):
    """Base class for iwara.tv extractors"""
    category = "iwara"
    root = "https://www.iwara.tv"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{id} {title} {filename}.{extension}"
    archive_fmt = "{type} {username} {id} {filename}"

    def _init(self):
        self.api = IwaraAPI(self)

    def extract_user_info(self, profile):
        user = profile.get("user", {})
        return {
            "user_id": user.get("id"),
            "username": user.get("username"),
            "display_name": user.get("name").strip(),
        }

    def extract_media_info(self, item, key, include_file_info):
        data = {
            "id": item.get("id"),
            "title": item.get("title").strip() if item.get("title") else "",
        }

        if include_file_info:
            file_info = item if key is None else item.get(key, {})
            filename = file_info.get("name")
            filename, extension = filename.rsplit(".", 1)
            createdAt = file_info.get("createdAt")
            dt = text.parse_datetime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
            datetime = dt.strftime(f"%a, %b {dt.day}, %Y %H:%M:%S")
            data.update({
                "file_id": file_info.get("id"),
                "filename": filename,
                "extension": extension,
                "mime": file_info.get("mime"),
                "size": file_info.get("size"),
                "width": file_info.get("width"),
                "height": file_info.get("height"),
                "duration": file_info.get("duration"),
                "datetime": datetime,
                "type": file_info.get("type"),
            })
        return data

    def get_metadata(self, user_info, media_info):
        return {
            **user_info,
            **media_info
        }

    def yield_video(self, video, user_info=None):
        if user_info is None:
            user_info = self.extract_user_info(video)
        video_info = self.extract_media_info(video, "file", True)

        if "fileUrl" not in video:
            video = self.api.video(video["id"])
        file_url = video["fileUrl"]

        file_id = video_info.get("file_id")
        sources = self.api.source(file_id, file_url)
        source = next((r for r in sources if r.get("name") == "Source"), None)
        download_url = source.get('src', {}).get('download')

        url = f"https:{download_url}"
        metadata = self.get_metadata(user_info, video_info)
        yield Message.Directory, metadata
        yield Message.Url, url, metadata

    def yield_image(self, user_info, image_group):
        image_group_info = self.extract_media_info(image_group, "file", False)
        for image_file in image_group.get("files", {}):
            image_file_info = self.extract_media_info(image_file, None, True)
            image_info = {**image_file_info, **image_group_info}
            file_id = image_info.get("file_id")
            extension = image_info.get("extension")
            url = (
                f"https://i.iwara.tv/image/original/"
                f"{file_id}/{file_id}.{extension}"
            )
            metadata = self.get_metadata(user_info, image_info)
            yield Message.Directory, metadata
            yield Message.Url, url, metadata

    def _user_params(self):
        user, qs = self.groups
        params = text.parse_query(qs)
        profile = self.api.profile(user)
        params["user"] = profile["user"]["id"]
        return self.extract_user_info(profile), params


class IwaraUserExtractor(Dispatch, IwaraExtractor):
    """Extractor for iwara.tv profile pages"""
    pattern = rf"{USER_PATTERN}/?$"
    example = "https://www.iwara.tv/profile/USERNAME"

    def items(self):
        base = f"{self.root}/profile/{self.groups[0]}/"
        return self._dispatch_extractors((
            (IwaraUserImagesExtractor   , f"{base}images"),
            (IwaraUserVideosExtractor   , f"{base}videos"),
            (IwaraUserPlaylistsExtractor, f"{base}playlists"),
        ), ("user-images", "user-videos"))


class IwaraUserImagesExtractor(IwaraExtractor):
    subcategory = "user-images"
    pattern = rf"{USER_PATTERN}/images(?:\?([^#]+))?"
    example = "https://www.iwara.tv/profile/USERNAME/images"

    def items(self):
        user, params = self._user_params()
        for image_group in self.api.images(params):
            images = self.api.image(image_group["id"])
            yield from self.yield_image(user, images)


class IwaraUserVideosExtractor(IwaraExtractor):
    subcategory = "user-videos"
    pattern = rf"{USER_PATTERN}/videos(?:\?([^#]+))?"
    example = "https://www.iwara.tv/profile/USERNAME/videos"

    def items(self):
        user, params = self._user_params()
        for video in self.api.videos(params):
            yield from self.yield_video(video, user)


class IwaraUserPlaylistsExtractor(IwaraExtractor):
    subcategory = "user-playlists"
    pattern = rf"{USER_PATTERN}/playlists(?:\?([^#]+))?"
    example = "https://www.iwara.tv/profile/USERNAME/playlists"

    def items(self):
        base = f"{self.root}/playlist/"

        for playlist in self.api.playlists(self._user_params()[1]):
            playlist["_extractor"] = IwaraPlaylistExtractor
            url = f"{base}{playlist['id']}"
            yield Message.Queue, url, playlist


class IwaraVideoExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv videos"""
    subcategory = "video"
    pattern = rf"{BASE_PATTERN}/video/([^/?#]+)"
    example = "https://www.iwara.tv/video/ID"

    def items(self):
        video = self.api.video(self.groups[0])
        return self.yield_video(video)


class IwaraImageExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv image pages"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/image(?:/|$)"
    example = "https://www.iwara.tv/image/image-id/slug"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "image":
            self.image_id = parts[1]
        else:
            return

    def items(self):
        image_group = self.api.item(f"/image/{self.image_id}")
        if not image_group:
            return
        user_info = self.extract_user_info(image_group)
        yield from self.yield_image(user_info, image_group)


class IwaraPlaylistExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv playlist pages"""
    subcategory = "playlist"
    pattern = BASE_PATTERN + r"/playlist(?:/|$)"
    example = "https://www.iwara.tv/playlist/playlist-id"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "playlist":
            self.playlist_id = parts[1]
        else:
            return

    def items(self):
        videos = self.api.collection(f"/playlist/{self.playlist_id}")
        if not videos:
            return
        for video in videos:
            video = self.api.item(f"/video/{video.get('id')}")
            yield from self.yield_video(video)


class IwaraSearchExtractor(IwaraExtractor):
    """Extractor for iwara.tv search pages"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search"
    example = "https://www.iwara.tv/search?query=example&type=search_type"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 1 and parts[0] == "search":
            query_dict = parse_qs(parsed.query)
            self.query = query_dict.get("query", [""])[0]
            self.type = query_dict.get("type", [None])[0]
        else:
            return

    def items(self):
        collection = self.api.collection("/search", self.query)
        if self.type == "video":
            for video in collection:
                video = self.api.item(f"/video/{video.get('id')}")
                yield from self.yield_video(video)
        elif self.type == "image":
            for image_group in collection:
                image_group = self.api.item(f"/image/{image_group.get('id')}")
                if not image_group:
                    return
                user_info = self.extract_user_info(image_group)
                yield from self.yield_image(user_info, image_group)


class IwaraTagExtractor(IwaraExtractor):
    """Extractor for iwara.tv tag search"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/(videos|images)(?:\?.*)?"
    example = "https://www.iwara.tv/videos?tags=example"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 1 and parts[0] in ("videos", "images"):
            query_dict = parse_qs(parsed.query)
            self.type = parts[0]
            self.tags = query_dict.get("tags", [""])[0]
        else:
            return

    def items(self):
        collection = self.api.collection(f"/{self.type}", self.tags)
        if self.type == "videos":
            for video in collection:
                video = self.api.item(f"/video/{video.get('id')}")
                yield from self.yield_video(video)
        elif self.type == "images":
            for image_group in collection:
                image_group = self.api.item(f"/image/{image_group.get('id')}")
                if not image_group:
                    return
                user_info = self.extract_user_info(image_group)
                yield from self.yield_image(user_info, image_group)


class IwaraAPI():
    """Interface for the Iwara API"""
    root = "https://api.iwara.tv"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Referer"     : f"{extractor.root}/",
            "Content-Type": "application/json",
            "Origin"      : extractor.root,
        }

        self.username, self.password = extractor._get_auth_info()
        if not self.username:
            self.authenticate = util.noop

    def image(self, image_id):
        endpoint = f"/image/{image_id}"
        return self._call(endpoint)

    def images(self, params):
        endpoint = "/images"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def video(self, video_id):
        endpoint = f"/video/{video_id}"
        return self._call(endpoint)

    def videos(self, params):
        endpoint = "/videos"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def playlists(self, params):
        endpoint = "/playlists"
        return self._pagination(endpoint, params)

    def search(self, type, query):
        endpoint = "/search"
        params = {"type": type, "query": query}
        return self._pagination(endpoint, params)

    @memcache()
    def profile(self, username):
        endpoint = f"/profile/{username}"
        return self._call(endpoint)

    def user_id(self, username):
        return self.profile(username)["user"]["id"]

    def user_following(self, user_id):
        endpoint = f"/user/{user_id}/following"
        return self._pagination(endpoint)

    def item(self, endpoint):
        url = self.root + endpoint
        return self.extractor.request_json(url, headers=self.headers)

    def source(self, file_id, url):
        expiration = parse_qs(urlparse(url).query).get("expires", [None])[0]
        if not expiration:
            return []
        sha_postfix = "5nFp9kmbNnHdAFhaqMvt"
        sha_key = f"{file_id}_{expiration}_{sha_postfix}"
        hash = hashlib.sha1(sha_key.encode("utf-8")).hexdigest()
        headers = {"X-Version": hash, **self.headers}
        return self.extractor.request_json(url, headers=headers)

    def authenticate(self):
        self.headers["Authorization"] = self._authenticate_impl(
            self.username, self.password)

    @cache(maxage=28*86400, keyarg=1)
    def _authenticate_impl(self, username, password):
        self.extractor.log.info("Logging in as %s", username)

        url = f"{self.root}/user/login"
        json = {
            "email"   : username,
            "password": password
        }
        data = self.extractor.request_json(
            url, method="POST", json=json, fatal=False)

        if token := data.get("token"):
            return f"Bearer {token}"
        raise exception.AuthenticationError(data.get("message"))

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        self.authenticate()
        return self.extractor.request_json(
            url, params=params, headers=self.headers)

    def _pagination(self, endpoint, params=None):
        if params is None:
            params = {}
        params["page"] = 0
        params["limit"] = 50

        while True:
            data = self._call(endpoint, params)

            if not (results := data.get("results")):
                break
            yield from results

            if len(results) < params["limit"]:
                break
            params["page"] += 1
