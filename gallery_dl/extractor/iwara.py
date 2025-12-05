# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.iwara.tv/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache, memcache
import hashlib

BASE_PATTERN = r"(?:https?://)?(?:www\.)?iwara\.tv"
USER_PATTERN = rf"{BASE_PATTERN}/profile/([^/?#]+)"


class IwaraExtractor(Extractor):
    """Base class for iwara.tv extractors"""
    category = "iwara"
    root = "https://www.iwara.tv"
    directory_fmt = ("{category}", "{user[name]}")
    filename_fmt = "{date} {id} {title[:200]} {filename}.{extension}"
    archive_fmt = "{type} {user[name]} {id} {file_id}"

    def _init(self):
        self.api = IwaraAPI(self)

    def items_image(self, images, user=None):
        for image in images:
            try:
                if "image" in image:
                    # could extract 'date_favorited' here
                    image = image["image"]
                if not (files := image.get("files")):
                    image = self.api.image(image["id"])
                    files = image["files"]

                group_info = self.extract_media_info(image, "file", False)
                group_info["user"] = (self.extract_user_info(image)
                                      if user is None else user)
            except Exception as exc:
                self.status |= 1
                self.log.error("Failed to process image %s (%s: %s)",
                               image["id"], exc.__class__.__name__, exc)
                continue

            group_info["type"] = "image"
            group_info["count"] = len(files)
            yield Message.Directory, "", group_info
            for num, file in enumerate(files, 1):
                file_info = self.extract_media_info(file, None)
                file_id = file_info["file_id"]
                url = (f"https://i.iwara.tv/image/original/"
                       f"{file_id}/{file_id}.{file_info['extension']}")
                yield Message.Url, url, {**file_info, **group_info, "num": num}

    def items_video(self, videos, user=None):
        for video in videos:
            try:
                if "video" in video:
                    video = video["video"]
                if "fileUrl" not in video:
                    video = self.api.video(video["id"])
                file_url = video["fileUrl"]
                sources = self.api.source(file_url)
                source = next((s for s in sources
                              if s.get("name") == "Source"), None)
                download_url = source.get('src', {}).get('download')

                info = self.extract_media_info(video, "file")
                info["count"] = info["num"] = 1
                info["user"] = (self.extract_user_info(video)
                                if user is None else user)
            except Exception as exc:
                self.status |= 1
                self.log.error("Failed to process video %s (%s: %s)",
                               video["id"], exc.__class__.__name__, exc)
                continue

            yield Message.Directory, "", info
            yield Message.Url, f"https:{download_url}", info

    def items_user(self, users, key=None):
        base = f"{self.root}/profile/"
        for user in users:
            if key is not None:
                user = user[key]
            if (username := user["username"]) is None:
                continue
            user["type"] = "user"
            user["_extractor"] = IwaraUserExtractor
            yield Message.Queue, f"{base}{username}", user

    def items_by_type(self, type, results):
        if type == "image":
            return self.items_image(results)
        if type == "video":
            return self.items_video(results)
        if type == "user":
            return self.items_user(results)

        raise exception.AbortExtraction(f"Unsupported result type '{type}'")

    def extract_media_info(self, item, key, include_file_info=True):
        info = {
            "id"      : item["id"],
            "slug"    : item.get("slug"),
            "rating"  : item.get("rating"),
            "likes"   : item.get("numLikes"),
            "views"   : item.get("numViews"),
            "comments": item.get("numComments"),
            "tags"    : [t["id"] for t in item.get("tags") or ()],
            "title"   : t.strip() if (t := item.get("title")) else "",
            "description": t.strip() if (t := item.get("body")) else "",
        }

        if include_file_info:
            file_info = item if key is None else item.get(key) or {}
            filename, _, extension = file_info.get("name", "").rpartition(".")

            info["file_id"] = file_info.get("id")
            info["filename"] = filename
            info["extension"] = extension
            info["date"] = self.parse_datetime_iso(
                file_info.get("createdAt"))
            info["date_updated"] = self.parse_datetime_iso(
                file_info.get("updatedAt"))
            info["mime"] = file_info.get("mime")
            info["size"] = file_info.get("size")
            info["width"] = file_info.get("width")
            info["height"] = file_info.get("height")
            info["duration"] = file_info.get("duration")
            info["type"] = file_info.get("type")

        return info

    def extract_user_info(self, profile):
        user = profile.get("user") or {}
        return {
            "id"     : user.get("id"),
            "name"   : user.get("username"),
            "nick"   : user.get("name").strip(),
            "status" : user.get("status"),
            "role"   : user.get("role"),
            "premium": user.get("premium"),
            "date"   : self.parse_datetime_iso(user.get("createdAt")),
            "description": profile.get("body"),
        }

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
        return self.items_image(self.api.images(params), user)


class IwaraUserVideosExtractor(IwaraExtractor):
    subcategory = "user-videos"
    pattern = rf"{USER_PATTERN}/videos(?:\?([^#]+))?"
    example = "https://www.iwara.tv/profile/USERNAME/videos"

    def items(self):
        user, params = self._user_params()
        return self.items_video(self.api.videos(params), user)


class IwaraUserPlaylistsExtractor(IwaraExtractor):
    subcategory = "user-playlists"
    pattern = rf"{USER_PATTERN}/playlists(?:\?([^#]+))?"
    example = "https://www.iwara.tv/profile/USERNAME/playlists"

    def items(self):
        base = f"{self.root}/playlist/"

        for playlist in self.api.playlists(self._user_params()[1]):
            playlist["type"] = "playlist"
            playlist["_extractor"] = IwaraPlaylistExtractor
            url = f"{base}{playlist['id']}"
            yield Message.Queue, url, playlist


class IwaraFollowingExtractor(IwaraExtractor):
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following"
    example = "https://www.iwara.tv/profile/USERNAME/following"

    def items(self):
        uid = self.api.profile(self.groups[0])["user"]["id"]
        return self.items_user(self.api.user_following(uid), "user")


class IwaraFollowersExtractor(IwaraExtractor):
    subcategory = "followers"
    pattern = rf"{USER_PATTERN}/followers"
    example = "https://www.iwara.tv/profile/USERNAME/followers"

    def items(self):
        uid = self.api.profile(self.groups[0])["user"]["id"]
        return self.items_user(self.api.user_followers(uid), "follower")


class IwaraImageExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv image pages"""
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/image/([^/?#]+)"
    example = "https://www.iwara.tv/image/ID"

    def items(self):
        return self.items_image((self.api.image(self.groups[0]),))


class IwaraVideoExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv videos"""
    subcategory = "video"
    pattern = rf"{BASE_PATTERN}/video/([^/?#]+)"
    example = "https://www.iwara.tv/video/ID"

    def items(self):
        return self.items_video((self.api.video(self.groups[0]),))


class IwaraPlaylistExtractor(IwaraExtractor):
    """Extractor for individual iwara.tv playlist pages"""
    subcategory = "playlist"
    pattern = rf"{BASE_PATTERN}/playlist/([^/?#]+)"
    example = "https://www.iwara.tv/playlist/ID"

    def items(self):
        return self.items_video(self.api.playlist(self.groups[0]))


class IwaraFavoriteExtractor(IwaraExtractor):
    subcategory = "favorite"
    pattern = rf"{BASE_PATTERN}/favorites(?:/(image|video)s)?"
    example = "https://www.iwara.tv/favorites/videos"

    def items(self):
        type = self.groups[0] or "vidoo"
        return self.items_by_type(type, self.api.favorites(type))


class IwaraSearchExtractor(IwaraExtractor):
    """Extractor for iwara.tv search pages"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search\?([^#]+)"
    example = "https://www.iwara.tv/search?query=QUERY&type=TYPE"

    def items(self):
        params = text.parse_query(self.groups[0])
        type = params.get("type")
        self.kwdict["search_tags"] = query = params.get("query")
        return self.items_by_type(type, self.api.search(type, query))


class IwaraTagExtractor(IwaraExtractor):
    """Extractor for iwara.tv tag search"""
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}/(image|video)s(?:\?([^#]+))?"
    example = "https://www.iwara.tv/videos?tags=TAGS"

    def items(self):
        type, qs = self.groups
        params = text.parse_query(qs)
        self.kwdict["search_tags"] = params.get("tags")
        return self.items_by_type(type, self.api.media(type, params))


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

    def video(self, video_id):
        endpoint = f"/video/{video_id}"
        return self._call(endpoint)

    def playlist(self, playlist_id):
        endpoint = f"/playlist/{playlist_id}"
        return self._pagination(endpoint)

    def detail(self, media):
        endpoint = f"/{media['type']}/{media['id']}"
        return self._call(endpoint)

    def images(self, params):
        endpoint = "/images"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def videos(self, params):
        endpoint = "/videos"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def playlists(self, params):
        endpoint = "/playlists"
        return self._pagination(endpoint, params)

    def media(self, type, params):
        endpoint = f"/{type}s"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def favorites(self, type):
        if not self.username:
            raise exception.AuthRequired(
                "username & password", "your favorites")
        endpoint = f"/favorites/{type}s"
        return self._pagination(endpoint)

    def search(self, type, query):
        endpoint = "/search"
        params = {"type": type, "query": query}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def profile(self, username):
        endpoint = f"/profile/{username}"
        return self._call(endpoint)

    def user_following(self, user_id):
        endpoint = f"/user/{user_id}/following"
        return self._pagination(endpoint)

    def user_followers(self, user_id):
        endpoint = f"/user/{user_id}/followers"
        return self._pagination(endpoint)

    def source(self, file_url):
        base, _, query = file_url.partition("?")
        if not (expires := text.extr(query, "expires=", "&")):
            return ()
        file_id = base.rpartition("/")[2]
        sha_postfix = "5nFp9kmbNnHdAFhaqMvt"
        sha_key = f"{file_id}_{expires}_{sha_postfix}"
        hash = hashlib.sha1(sha_key.encode()).hexdigest()
        headers = {"X-Version": hash, **self.headers}
        return self.extractor.request_json(file_url, headers=headers)

    def authenticate(self):
        self.headers["Authorization"] = self._authenticate_impl(self.username)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, username):
        refresh_token = _refresh_token_cache(username)
        if refresh_token is None:
            self.extractor.log.info("Logging in as %s", username)

            url = f"{self.root}/user/login"
            json = {
                "email"   : username,
                "password": self.password
            }
            data = self.extractor.request_json(
                url, method="POST", headers=self.headers, json=json,
                fatal=False)

            if not (refresh_token := data.get("token")):
                self.extractor.log.debug(data)
                raise exception.AuthenticationError(data.get("message"))
            _refresh_token_cache.update(username, refresh_token)

        self.extractor.log.info("Refreshing access token for %s", username)

        url = f"{self.root}/user/token"
        headers = {"Authorization": f"Bearer {refresh_token}", **self.headers}
        data = self.extractor.request_json(
            url, method="POST", headers=headers, fatal=False)

        if not (access_token := data.get("accessToken")):
            self.extractor.log.debug(data)
            raise exception.AuthenticationError(data.get("message"))
        return f"Bearer {access_token}"

    def _call(self, endpoint, params=None, headers=None):
        if headers is None:
            headers = self.headers

        url = self.root + endpoint
        self.authenticate()
        return self.extractor.request_json(url, params=params, headers=headers)

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


@cache(maxage=28*86400, keyarg=0)
def _refresh_token_cache(username):
    return None
