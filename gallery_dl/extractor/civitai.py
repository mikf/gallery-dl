# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.civitai.com/"""

from .common import Extractor, Message
from .. import text, util
import itertools
import time

BASE_PATTERN = r"(?:https?://)?civitai\.com"
USER_PATTERN = BASE_PATTERN + r"/user/([^/?#]+)"


class CivitaiExtractor(Extractor):
    """Base class for civitai extractors"""
    category = "civitai"
    root = "https://civitai.com"
    directory_fmt = ("{category}", "{username|user[username]}", "images")
    filename_fmt = "{file[id]|id|filename}.{extension}"
    archive_fmt = "{file[hash]|hash}"
    request_interval = (0.5, 1.5)

    def _init(self):
        if self.config("api") == "rest":
            self.log.debug("Using REST API")
            self.api = CivitaiRestAPI(self)
        else:
            self.log.debug("Using tRPC API")
            self.api = CivitaiTrpcAPI(self)

        quality = self.config("quality")
        if quality:
            if not isinstance(quality, str):
                quality = ",".join(quality)
            self._image_quality = quality
            self._image_ext = ("png" if quality == "original=true" else "jpg")
        else:
            self._image_quality = "original=true"
            self._image_ext = "png"

    def items(self):
        models = self.models()
        if models:
            data = {"_extractor": CivitaiModelExtractor}
            for model in models:
                url = "{}/models/{}".format(self.root, model["id"])
                yield Message.Queue, url, data
            return

        posts = self.posts()
        if posts:
            for post in posts:

                if "images" in post:
                    images = post["images"]
                else:
                    images = self.api.images_post(post["id"])

                post = self.api.post(post["id"])
                post["date"] = text.parse_datetime(
                    post["publishedAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                data = {
                    "post": post,
                    "user": post["user"],
                }
                del post["user"]

                yield Message.Directory, data
                for file in self._image_results(images):
                    file.update(data)
                    yield Message.Url, file["url"], file
            return

        images = self.images()
        if images:
            for image in images:
                url = self._url(image)
                image["date"] = text.parse_datetime(
                    image["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                text.nameext_from_url(url, image)
                image["extension"] = self._image_ext
                yield Message.Directory, image
                yield Message.Url, url, image
            return

    def models(self):
        return ()

    def posts(self):
        return ()

    def images(self):
        return ()

    def _url(self, image):
        url = image["url"]
        if "/" in url:
            parts = url.rsplit("/", 2)
            parts[1] = self._image_quality
            return "/".join(parts)

        name = image.get("name")
        if not name:
            mime = image.get("mimeType") or self._image_ext
            name = "{}.{}".format(image.get("id"), mime.rpartition("/")[2])
        return (
            "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/{}/{}/{}".format(
                url, self._image_quality, name)
        )

    def _image_results(self, images):
        for num, file in enumerate(images, 1):
            data = text.nameext_from_url(file["url"], {
                "num" : num,
                "file": file,
                "url" : self._url(file),
            })
            if not data["extension"]:
                data["extension"] = self._image_ext
            if "id" not in file and data["filename"].isdecimal():
                file["id"] = text.parse_int(data["filename"])
            yield data


class CivitaiModelExtractor(CivitaiExtractor):
    subcategory = "model"
    directory_fmt = ("{category}", "{user[username]}",
                     "{model[id]}{model[name]:? //}",
                     "{version[id]}{version[name]:? //}")
    filename_fmt = "{file[id]}.{extension}"
    archive_fmt = "{file[hash]}"
    pattern = BASE_PATTERN + r"/models/(\d+)(?:/?\?modelVersionId=(\d+))?"
    example = "https://civitai.com/models/12345/TITLE"

    def items(self):
        model_id, version_id = self.groups
        model = self.api.model(model_id)

        if "user" in model:
            user = model["user"]
            del model["user"]
        else:
            user = model["creator"]
            del model["creator"]
        versions = model["modelVersions"]
        del model["modelVersions"]

        if version_id:
            version_id = int(version_id)
            for version in versions:
                if version["id"] == version_id:
                    break
            else:
                version = self.api.model_version(version_id)
            versions = (version,)

        for version in versions:
            version["date"] = text.parse_datetime(
                version["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")

            data = {
                "model"  : model,
                "version": version,
                "user"   : user,
            }

            yield Message.Directory, data
            for file in self._extract_files(model, version, user):
                file.update(data)
                yield Message.Url, file["url"], file

    def _extract_files(self, model, version, user):
        filetypes = self.config("files")
        if filetypes is None:
            return self._extract_files_image(model, version, user)

        generators = {
            "model"   : self._extract_files_model,
            "image"   : self._extract_files_image,
            "gallery" : self._extract_files_gallery,
            "gallerie": self._extract_files_gallery,
        }
        if isinstance(filetypes, str):
            filetypes = filetypes.split(",")

        return itertools.chain.from_iterable(
            generators[ft.rstrip("s")](model, version, user)
            for ft in filetypes
        )

    def _extract_files_model(self, model, version, user):
        return [
            {
                "num"      : num,
                "file"     : file,
                "filename" : file["name"],
                "extension": "bin",
                "url"      : file["downloadUrl"],
                "_http_headers" : {
                    "Authorization": self.api.headers.get("Authorization")},
                "_http_validate": self._validate_file_model,
            }
            for num, file in enumerate(version["files"], 1)
        ]

    def _extract_files_image(self, model, version, user):
        if "images" in version:
            images = version["images"]
        else:
            params = {
                "modelVersionId": version["id"],
                "prioritizedUserIds": [user["id"]],
                "period": "AllTime",
                "sort": "Most Reactions",
                "limit": 20,
                "pending": True,
            }
            images = self.api.images(params, defaults=False)

        return self._image_results(images)

    def _extract_files_gallery(self, model, version, user):
        images = self.api.images_gallery(model, version, user)
        return self._image_results(images)

    def _validate_file_model(self, response):
        if response.headers.get("Content-Type", "").startswith("text/html"):
            alert = text.extr(
                response.text, 'mantine-Alert-message">', "</div></div></div>")
            if alert:
                msg = "\"{}\" - 'api-key' required".format(
                    text.remove_html(alert))
            else:
                msg = "'api-key' required to download this file"
            self.log.warning(msg)
            return False
        return True


class CivitaiImageExtractor(CivitaiExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/images/(\d+)"
    example = "https://civitai.com/images/12345"

    def images(self):
        return self.api.image(self.groups[0])


class CivitaiPostExtractor(CivitaiExtractor):
    subcategory = "post"
    directory_fmt = ("{category}", "{username|user[username]}", "posts",
                     "{post[id]}{post[title]:? //}")
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    example = "https://civitai.com/posts/12345"

    def posts(self):
        return ({"id": int(self.groups[0])},)


class CivitaiTagModelsExtractor(CivitaiExtractor):
    subcategory = "tag-models"
    pattern = BASE_PATTERN + r"/(?:tag/|models\?tag=)([^/?&#]+)"
    example = "https://civitai.com/tag/TAG"

    def models(self):
        tag = text.unquote(self.groups[0])
        return self.api.models({"tag": tag})


class CivitaiTagImagesExtractor(CivitaiExtractor):
    subcategory = "tag-images"
    pattern = BASE_PATTERN + r"/images\?tags=([^&#]+)"
    example = "https://civitai.com/images?tags=12345"

    def images(self):
        tag = text.unquote(self.groups[0])
        return self.api.images({"tag": tag})


class CivitaiSearchExtractor(CivitaiExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/models\?([^#]+)"
    example = "https://civitai.com/search/models?query=QUERY"

    def models(self):
        params = text.parse_query(self.groups[0])
        return self.api.models(params)


class CivitaiUserExtractor(CivitaiExtractor):
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://civitai.com/user/USER"

    def initialize(self):
        pass

    def items(self):
        base = "{}/user/{}/".format(self.root, self.groups[0])
        return self._dispatch_extractors((
            (CivitaiUserModelsExtractor, base + "models"),
            (CivitaiUserPostsExtractor , base + "posts"),
            (CivitaiUserImagesExtractor, base + "images"),
        ), ("user-models", "user-posts"))


class CivitaiUserModelsExtractor(CivitaiExtractor):
    subcategory = "user-models"
    pattern = USER_PATTERN + r"/models/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/models"

    def models(self):
        params = text.parse_query(self.groups[1])
        params["username"] = text.unquote(self.groups[0])
        return self.api.models(params)


class CivitaiUserPostsExtractor(CivitaiExtractor):
    subcategory = "user-posts"
    directory_fmt = ("{category}", "{username|user[username]}", "posts",
                     "{post[id]}{post[title]:? //}")
    pattern = USER_PATTERN + r"/posts/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/posts"

    def posts(self):
        params = text.parse_query(self.groups[1])
        params["username"] = text.unquote(self.groups[0])
        return self.api.posts(params)


class CivitaiUserImagesExtractor(CivitaiExtractor):
    subcategory = "user-images"
    pattern = USER_PATTERN + r"/images/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/images"

    def images(self):
        params = text.parse_query(self.groups[1])
        params["username"] = text.unquote(self.groups[0])
        return self.api.images(params)


class CivitaiRestAPI():
    """Interface for the Civitai Public REST API

    https://developer.civitai.com/docs/api/public-rest
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"
        self.headers = {"Content-Type": "application/json"}

        api_key = extractor.config("api-key")
        if api_key:
            extractor.log.debug("Using api_key authentication")
            self.headers["Authorization"] = "Bearer " + api_key

        nsfw = extractor.config("nsfw")
        if nsfw is None or nsfw is True:
            nsfw = "X"
        elif not nsfw:
            nsfw = "Safe"
        self.nsfw = nsfw

    def image(self, image_id):
        return self.images({
            "imageId": image_id,
        })

    def images(self, params):
        endpoint = "/v1/images"
        if "nsfw" not in params:
            params["nsfw"] = self.nsfw
        return self._pagination(endpoint, params)

    def images_gallery(self, model, version, user):
        return self.images({
            "modelId"       : model["id"],
            "modelVersionId": version["id"],
        })

    def model(self, model_id):
        endpoint = "/v1/models/{}".format(model_id)
        return self._call(endpoint)

    def model_version(self, model_version_id):
        endpoint = "/v1/model-versions/{}".format(model_version_id)
        return self._call(endpoint)

    def models(self, params):
        return self._pagination("/v1/models", params)

    def _call(self, endpoint, params=None):
        if endpoint[0] == "/":
            url = self.root + endpoint
        else:
            url = endpoint

        response = self.extractor.request(
            url, params=params, headers=self.headers)
        return response.json()

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            yield from data["items"]

            try:
                endpoint = data["metadata"]["nextPage"]
            except KeyError:
                return
            params = None


class CivitaiTrpcAPI():
    """Interface for the Civitai TRPC API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api/trpc/"
        self.headers = {
            "content-type"    : "application/json",
            "x-client-version": "5.0.146",
            "x-client-date"   : "",
            "x-client"        : "web",
            "x-fingerprint"   : "undefined",
        }
        api_key = extractor.config("api-key")
        if api_key:
            extractor.log.debug("Using api_key authentication")
            self.headers["Authorization"] = "Bearer " + api_key

        nsfw = extractor.config("nsfw")
        if nsfw is None or nsfw is True:
            nsfw = 31
        elif not nsfw:
            nsfw = 1
        self.nsfw = nsfw

    def image(self, image_id):
        endpoint = "image.get"
        params = {"id": int(image_id)}
        return (self._call(endpoint, params),)

    def images(self, params, defaults=True):
        endpoint = "image.getInfinite"

        if defaults:
            params = self._merge_params(params, {
                "useIndex"     : True,
                "period"       : "AllTime",
                "sort"         : "Newest",
                "types"        : ["image"],
                "withMeta"     : False,  # Metadata Only
                "fromPlatform" : False,  # Made On-Site
                "browsingLevel": self.nsfw,
                "include"      : ["cosmetics"],
            })

        return self._pagination(endpoint, params)

    def images_gallery(self, model, version, user):
        endpoint = "image.getImagesAsPostsInfinite"
        params = {
            "period"        : "AllTime",
            "sort"          : "Newest",
            "modelVersionId": version["id"],
            "modelId"       : model["id"],
            "hidden"        : False,
            "limit"         : 50,
            "browsingLevel" : self.nsfw,
        }

        for post in self._pagination(endpoint, params):
            yield from post["images"]

    def images_post(self, post_id):
        params = {
            "postId" : int(post_id),
            "pending": True,
        }
        return self.images(params)

    def model(self, model_id):
        endpoint = "model.getById"
        params = {"id": int(model_id)}
        return self._call(endpoint, params)

    def model_version(self, model_version_id):
        endpoint = "modelVersion.getById"
        params = {"id": int(model_version_id)}
        return self._call(endpoint, params)

    def models(self, params, defaults=True):
        endpoint = "model.getAll"

        if defaults:
            params = self._merge_params(params, {
                "period"       : "AllTime",
                "periodMode"   : "published",
                "sort"         : "Newest",
                "pending"      : False,
                "hidden"       : False,
                "followed"     : False,
                "earlyAccess"  : False,
                "fromPlatform" : False,
                "supportsGeneration": False,
                "browsingLevel": self.nsfw,
            })

        return self._pagination(endpoint, params)

    def post(self, post_id):
        endpoint = "post.get"
        params = {"id": int(post_id)}
        return self._call(endpoint, params)

    def posts(self, params, defaults=True):
        endpoint = "post.getInfinite"
        meta = {"cursor": ("Date",)}

        if defaults:
            params = self._merge_params(params, {
                "browsingLevel": self.nsfw,
                "period"       : "AllTime",
                "periodMode"   : "published",
                "sort"         : "Newest",
                "followed"     : False,
                "draftOnly"    : False,
                "pending"      : True,
                "include"      : ["cosmetics"],
            })

        return self._pagination(endpoint, params, meta)

    def user(self, username):
        endpoint = "user.getCreator"
        params = {"username": username}
        return (self._call(endpoint, params),)

    def _call(self, endpoint, params, meta=None):
        url = self.root + endpoint
        headers = self.headers

        if meta:
            input = {"json": params, "meta": {"values": meta}}
        else:
            input = {"json": params}

        params = {"input": util.json_dumps(input)}
        headers["x-client-date"] = str(int(time.time() * 1000))
        response = self.extractor.request(url, params=params, headers=headers)

        return response.json()["result"]["data"]["json"]

    def _pagination(self, endpoint, params, meta=None):
        if "cursor" not in params:
            params["cursor"] = None
            meta_ = {"cursor": ("undefined",)}

        while True:
            data = self._call(endpoint, params, meta_)
            yield from data["items"]

            try:
                if not data["nextCursor"]:
                    return
            except KeyError:
                return

            params["cursor"] = data["nextCursor"]
            meta_ = meta

    def _merge_params(self, params_user, params_default):
        params_default.update(params_user)
        return params_default
