# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.iwara.tv/"""

from .common import Extractor, Message
from urllib.parse import urlparse, parse_qs
import hashlib

BASE_PATTERN = r"(?:https?://)?(?:www\.)?iwara\.tv"


class IwaraExtractor(Extractor):
    """Base class for iwara.tv extractors"""
    category = "iwara"
    root = "https://www.iwara.tv"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{id} {file_id} {title}.{extension}"
    archive_fmt = "{type} {username} {id} {file_id}"

    def _init(self):
        self.api = IwaraAPI(self)

    def extract_user_info(self, profile):
        if not isinstance(profile, dict):
            return {"user_id": None, "username": None, "display_name": None}
        user = profile.get("user", {})
        if not isinstance(user, dict):
            user = {}
        return {
            "user_id": user.get("id"),
            "username": user.get("username"),
            "display_name": user.get("name"),
        }

    def extract_media_info(self, item, key, include_file_info):
        data = {
            "id": item.get("id"),
            "title": item.get("title"),
        }

        if include_file_info:
            file_info = item if key is None else item.get(key, {})
            filename = file_info.get("name")
            file_id, extension = filename.rsplit(".", 1)
            data.update({
                "file_id": file_id,
                "extension": extension,
                "type": file_info.get("type"),
            })
        return data

    def get_metadata(self, user_info, media_info):
        return {
            **user_info,
            **media_info
        }

    def yield_video(self, user_info, video):
        video_info = self.extract_media_info(video, "file", True)
        video_id = video_info.get("id")
        file_id = video_info.get("file_id")
        video = self.api.item(f"/video/{video_id}")
        file_url = video.get("fileUrl")
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


class IwaraProfileExtractor(IwaraExtractor):
    """Extractor for iwara.tv profile pages"""
    subcategory = "profile"
    pattern = BASE_PATTERN + r"/profile/([^/?#]+)"
    example = "https://www.iwara.tv/profile/username"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        self.profile = match.group(1)

    def items(self):
        profile = self.api.profile(f"/profile/{self.profile}")
        if not profile:
            return
        user_info = self.extract_user_info(profile)
        user_id = user_info.get("user_id")
        if not user_id:
            return

        videos = self.api.collection("/videos", user_id)
        for video in videos:
            yield from self.yield_video(user_info, video)

        playlists = self.api.collection("/playlists", user_id)
        for playlist in playlists:
            videos = self.api.collection(f"/playlist/{playlist["id"]}", None)
            for video in videos:
                user_info = self.extract_user_info(video)
                yield from self.yield_video(user_info, video)

        image_groups = self.api.collection("/images", user_id)
        for image_group in image_groups:
            image_group_id = image_group.get("id")
            images = self.api.item(f"/image/{image_group_id}")
            yield from self.yield_image(user_info, images)


class IwaraVideoExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv videos"""
    subcategory = "video"
    pattern = r"(?:https?://)?(?:www\.)?iwara\.tv/video/([\w-]+)"
    example = "https://www.iwara.tv/video/video-id/slug"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        self.video_id = match.group(1)

    def items(self):
        video = self.api.item(f"/video/{self.video_id}")
        if not video:
            return
        user_info = self.extract_user_info(video)
        yield from self.yield_video(user_info, video)


class IwaraImageExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv image pages"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:www\.)?iwara\.tv/image/([\w-]+)"
    example = "https://www.iwara.tv/image/image-id/slug"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def items(self):
        image_group = self.api.item(f"/image/{self.image_id}")
        if not image_group:
            return
        user_info = self.extract_user_info(image_group)
        yield from self.yield_image(user_info, image_group)


class IwaraPlaylistExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv playlist pages"""
    subcategory = "playlist"
    pattern = r"(?:https?://)?(?:www\.)?iwara\.tv/playlist/([\w-]+)"
    example = "https://www.iwara.tv/playlist/playlist-id"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        self.playlist_id = match.group(1)

    def items(self):
        videos = self.api.collection(f"/playlist/{self.playlist_id}", None)
        if not videos:
            return
        for video in videos:
            video = self.api.item(f"/video/{video.get("id")}")
            user_info = self.extract_user_info(video)
            yield from self.yield_video(user_info, video)


class IwaraSearchExtractor(IwaraExtractor):
    """Extractor for iwara.tv search pages"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search\?query=([^&?#]+)(?:&type=([^&?#]+))?"
    example = "https://www.iwara.tv/search?query=example&type=search_type"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        self.query = match.group(1)
        self.type = match.group(2) if match.lastindex >= 2 else None

    def items(self):
        collection = self.api.collection("/search", self.query, search=True)
        if self.type == "video":
            for video in collection:
                video = self.api.item(f"/video/{video.get("id")}")
                user_info = self.extract_user_info(video)
                yield from self.yield_video(user_info, video)
        elif self.type == "image":
            for image_group in collection:
                image_group = self.api.item(f"/image/{image_group.get("id")}")
                if not image_group:
                    return
                user_info = self.extract_user_info(image_group)
                yield from self.yield_image(user_info, image_group)


class IwaraAPI():
    """Interface for the Iwara API"""
    root = "https://api.iwara.tv"

    def __init__(self, extractor):
        self.extractor = extractor
        self.token = None
        self.headers = {}
        self.login("/user/login")

    def login(self, endpoint):
        url = self.root + endpoint
        email, password = self.extractor._get_auth_info()
        if not email or not password:
            return
        json = {
            "email": email,
            "password": password
        }
        try:
            response = self.extractor.request(url, method="POST", json=json)
            response.raise_for_status()
        except Exception:
            return

        try:
            token = response.json().get("token")
            if token:
                self.token = token
                self.headers = {"Authorization": f"Bearer {token}"}
                self.extractor.log.info(f"Logged in as {email}.")
            else:
                self.extractor.log.warning("No token found in login response.")
        except Exception:
            return

    def profile(self, endpoint):
        url = self.root + endpoint
        try:
            response = self.extractor.request(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}

    def collection(self, endpoint, query, page=0, limit=50, search=False):
        url = self.root + endpoint
        params = {}
        if search:
            params = {
                "type": self.extractor.type,
                "query": query,
                "page": page,
                "limit": limit,
            }
        else:
            params = {
                "user": query,
                "page": page,
                "limit": limit,
            }
        collection = []
        while True:
            try:
                response = self.extractor.request(
                    url,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            except Exception:
                break
            results = data.get("results", [])
            if not results:
                break
            collection.extend(results)
            if len(results) < limit:
                break
            params["page"] += 1
        return collection

    def item(self, endpoint):
        url = self.root + endpoint
        try:
            response = self.extractor.request(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}

    def source(self, file_id, url):
        expiration = parse_qs(urlparse(url).query).get("expires", [None])[0]
        if not expiration:
            return []
        sha_postfix = "5nFp9kmbNnHdAFhaqMvt"
        sha_key = f"{file_id}_{expiration}_{sha_postfix}"
        hash = hashlib.sha1(sha_key.encode("utf-8")).hexdigest()
        headers = {"X-Version": hash, **self.headers}
        try:
            response = self.extractor.request(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return []
