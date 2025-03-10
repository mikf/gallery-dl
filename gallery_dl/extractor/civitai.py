# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.civitai.com/"""

from .common import Extractor, Message
from .. import text, util, exception
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
    archive_fmt = "{file[uuid]|uuid}"
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

        metadata = self.config("metadata")
        if metadata:
            if isinstance(metadata, str):
                metadata = metadata.split(",")
            elif not isinstance(metadata, (list, tuple)):
                metadata = ("generation",)
            self._meta_generation = ("generation" in metadata)
        else:
            self._meta_generation = False

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
                if self._meta_generation:
                    image["generation"] = self.api.image_generationdata(
                        image["id"])
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
            parts = url.rsplit("/", 3)
            image["uuid"] = parts[1]
            parts[2] = self._image_quality
            return "/".join(parts)
        image["uuid"] = url

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
            if self._meta_generation:
                file["generation"] = self.api.image_generationdata(file["id"])
            yield data

    def _parse_query(self, value):
        return text.parse_query_list(
            value, {"tags", "reactions", "baseModels", "tools", "techniques",
                    "types", "fileFormats"})


class CivitaiModelExtractor(CivitaiExtractor):
    subcategory = "model"
    directory_fmt = ("{category}", "{user[username]}",
                     "{model[id]}{model[name]:? //}",
                     "{version[id]}{version[name]:? //}")
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
        files = []

        for num, file in enumerate(version["files"], 1):
            file["uuid"] = "model-{}-{}-{}".format(
                model["id"], version["id"], file["id"])
            files.append({
                "num"      : num,
                "file"     : file,
                "filename" : file["name"],
                "extension": "bin",
                "url"      : file.get("downloadUrl") or
                             "{}/api/download/models/{}".format(
                                 self.root, version["id"]),
                "_http_headers" : {
                    "Authorization": self.api.headers.get("Authorization")},
                "_http_validate": self._validate_file_model,
            })

        return files

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


class CivitaiTagExtractor(CivitaiExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tag/([^/?&#]+)"
    example = "https://civitai.com/tag/TAG"

    def models(self):
        tag = text.unquote(self.groups[0])
        return self.api.models_tag(tag)


class CivitaiSearchExtractor(CivitaiExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/models\?([^#]+)"
    example = "https://civitai.com/search/models?query=QUERY"

    def models(self):
        params = text.parse_query(self.groups[0])
        return self.api.models(params)


class CivitaiModelsExtractor(CivitaiExtractor):
    subcategory = "models"
    pattern = BASE_PATTERN + r"/models(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/models"

    def models(self):
        params = text.parse_query(self.groups[0])
        return self.api.models(params)


class CivitaiImagesExtractor(CivitaiExtractor):
    subcategory = "images"
    pattern = BASE_PATTERN + r"/images(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/images"

    def images(self):
        params = text.parse_query(self.groups[0])
        return self.api.images(params)


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
            (CivitaiUserVideosExtractor, base + "videos"),
        ), ("user-models", "user-posts"))


class CivitaiUserModelsExtractor(CivitaiExtractor):
    subcategory = "user-models"
    pattern = USER_PATTERN + r"/models/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/models"

    def models(self):
        user, query = self.groups
        params = self._parse_query(query)
        params["username"] = text.unquote(user)
        return self.api.models(params)


class CivitaiUserPostsExtractor(CivitaiExtractor):
    subcategory = "user-posts"
    directory_fmt = ("{category}", "{username|user[username]}", "posts",
                     "{post[id]}{post[title]:? //}")
    pattern = USER_PATTERN + r"/posts/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/posts"

    def posts(self):
        user, query = self.groups
        params = self._parse_query(query)
        params["username"] = text.unquote(user)
        return self.api.posts(params)


class CivitaiUserImagesExtractor(CivitaiExtractor):
    subcategory = "user-images"
    pattern = USER_PATTERN + r"/images/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/images"

    def __init__(self, match):
        self.params = self._parse_query(match.group(2))
        if self.params.get("section") == "reactions":
            self.subcategory = "reactions"
            self.images = self.images_reactions
        CivitaiExtractor.__init__(self, match)

    def images(self):
        params = self.params
        params["username"] = text.unquote(self.groups[0])
        return self.api.images(params)

    def images_reactions(self):
        if "Authorization" not in self.api.headers and \
                not self.cookies.get(
                "__Secure-civitai-token", domain=".civitai.com"):
            raise exception.AuthorizationError("api-key or cookies required")

        params = self.params
        params["authed"] = True
        params["useIndex"] = False
        if "reactions" not in params:
            params["reactions"] = ("Like", "Dislike", "Heart", "Laugh", "Cry")
        return self.api.images(params)


class CivitaiUserVideosExtractor(CivitaiExtractor):
    subcategory = "user-videos"
    directory_fmt = ("{category}", "{username|user[username]}", "videos")
    pattern = USER_PATTERN + r"/videos/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/videos"

    def images(self):
        self._image_ext = "mp4"

        user, query = self.groups
        params = self._parse_query(query)
        params["types"] = ["video"]
        params["username"] = text.unquote(user)
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

    def models_tag(self, tag):
        return self.models({"tag": tag})

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
    """Interface for the Civitai tRPC API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api/trpc/"
        self.headers = {
            "content-type"    : "application/json",
            "x-client-version": "5.0.542",
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

    def image_generationdata(self, image_id):
        endpoint = "image.getGenerationData"
        params = {"id": int(image_id)}
        return self._call(endpoint, params)

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

        params = self._type_params(params)
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

    def models_tag(self, tag):
        return self.models({"tagname": tag})

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
        """Combine 'params_user' with 'params_default'"""
        params_default.update(params_user)
        return params_default

    def _type_params(self, params):
        """Convert 'params' values to expected types"""
        types = {
            "tags"          : int,
            "tools"         : int,
            "techniques"    : int,
            "modelId"       : int,
            "modelVersionId": int,
            "remixesOnly"   : _bool,
            "nonRemixesOnly": _bool,
            "withMeta"      : _bool,
            "fromPlatform"  : _bool,
            "supportsGeneration": _bool,
        }

        for name, value in params.items():
            if name not in types:
                continue
            elif isinstance(value, str):
                params[name] = types[name](value)
            elif isinstance(value, list):
                type = types[name]
                params[name] = [type(item) for item in value]
        return params


def _bool(value):
    return True if value == "true" else False
