# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.iwara.tv/"""

from .common import Extractor, Message
from .. import text
from urllib.parse import unquote, urlparse, parse_qs
import hashlib

BASE_PATTERN = r"(?:https?://)?(?:www\.)?iwara\.tv"


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
    pattern = BASE_PATTERN + r"/profile(?:/|$)"
    example = "https://www.iwara.tv/profile/username"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "profile":
            self.profile = parts[1]
        else:
            return

    def items(self):
        profile = self.api.profile(f"/profile/{self.profile}")
        if not profile:
            return
        user_info = self.extract_user_info(profile)
        user_id = user_info.get("user_id")
        videos = self.api.collection("/videos", user_id)
        for video in videos:
            yield from self.yield_video(user_info, video)

        playlists = self.api.collection("/playlists", user_id)
        for playlist in playlists:
            videos = self.api.collection(f"/playlist/{playlist.get("id")}")
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
    pattern = BASE_PATTERN + r"/video(?:/|$)"
    example = "https://www.iwara.tv/video/video-id/slug"

    def __init__(self, match):
        IwaraExtractor.__init__(self, match)
        parsed = urlparse(self.url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "video":
            self.video_id = parts[1]
        else:
            return

    def items(self):
        video = self.api.item(f"/video/{self.video_id}")
        if not video:
            return
        user_info = self.extract_user_info(video)
        yield from self.yield_video(user_info, video)


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
            video = self.api.item(f"/video/{video.get("id")}")
            user_info = self.extract_user_info(video)
            yield from self.yield_video(user_info, video)


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
                video = self.api.item(f"/video/{video.get("id")}")
                user_info = self.extract_user_info(video)
                yield from self.yield_video(user_info, video)
        elif self.type == "images":
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
        response = self.extractor.request(url, method="POST", json=json)
        token = response.json().get("token")
        if token:
            self.token = token
            self.headers = {"Authorization": f"Bearer {token}"}
            self.extractor.log.info(f"Logged in as {email}.")

    def profile(self, endpoint):
        url = self.root + endpoint
        return self.extractor.request_json(url, headers=self.headers)

    def collection(self, endpoint, search=None):
        url = self.root + endpoint
        params = {}
        page = 0
        limit = 50
        if self.extractor.subcategory == "search":
            params = {
                "query": unquote(search) if search else "",
                "page": page,
                "limit": limit,
                "type": self.extractor.type,
            }
        elif self.extractor.subcategory == "tag":
            params = {
                "tags": unquote(search) if search else "",
                "page": page,
                "limit": limit,
            }
        else:
            params = {
                "user": unquote(search) if search else "",
                "page": page,
                "limit": limit,
            }
        collection = []
        while True:
            data = self.extractor.request_json(
                url,
                headers=self.headers,
                params=params
            )
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
