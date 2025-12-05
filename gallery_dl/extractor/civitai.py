# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.civitai.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import memcache
import itertools
import time

BASE_PATTERN = r"(?:https?://)?civitai\.com"
USER_PATTERN = rf"{BASE_PATTERN}/user/([^/?#]+)"


class CivitaiExtractor(Extractor):
    """Base class for civitai extractors"""
    category = "civitai"
    root = "https://civitai.com"
    directory_fmt = ("{category}", "{user[username]}", "images")
    filename_fmt = "{file[id]}.{extension}"
    archive_fmt = "{file[uuid]}"
    request_interval = (0.5, 1.5)

    def _init(self):
        if self.config("api") == "rest":
            self.log.debug("Using REST API")
            self.api = CivitaiRestAPI(self)
        else:
            self.log.debug("Using tRPC API")
            self.api = CivitaiTrpcAPI(self)

        if quality := self.config("quality"):
            if not isinstance(quality, str):
                quality = ",".join(quality)
            self._image_quality = quality
            self._image_ext = ("png" if quality == "original=true" else "jpg")
        else:
            self._image_quality = "original=true"
            self._image_ext = "png"

        if quality_video := self.config("quality-videos"):
            if not isinstance(quality_video, str):
                quality_video = ",".join(quality_video)
            if quality_video[0] == "+":
                quality_video = (self._image_quality + "," +
                                 quality_video.lstrip("+,"))
            self._video_quality = quality_video
        elif quality_video is not None and quality:
            self._video_quality = self._image_quality
        else:
            self._video_quality = "quality=100"
        self._video_ext = "webm"

        if metadata := self.config("metadata"):
            if isinstance(metadata, str):
                metadata = metadata.split(",")
            elif not isinstance(metadata, (list, tuple)):
                metadata = {"generation", "version", "post", "tags"}
            self._meta_generation = ("generation" in metadata)
            self._meta_version = ("version" in metadata)
            self._meta_post = ("post" in metadata)
            self._meta_tags = ("tags" in metadata)
        else:
            self._meta_generation = self._meta_version = self._meta_post = \
                self._meta_tags = False

    def items(self):
        if models := self.models():
            data = {"_extractor": CivitaiModelExtractor}
            for model in models:
                url = f"{self.root}/models/{model['id']}"
                yield Message.Queue, url, data
            return

        if posts := self.posts():
            for post in posts:

                if "images" in post:
                    images = post["images"]
                else:
                    images = self.api.images_post(post["id"])

                post = self.api.post(post["id"])
                post["date"] = self.parse_datetime_iso(post["publishedAt"])
                data = {
                    "post": post,
                    "user": post.pop("user"),
                }
                if self._meta_version:
                    data["model"], data["version"] = \
                        self._extract_meta_version(post)

                yield Message.Directory, "", data
                for file in self._image_results(images):
                    file.update(data)
                    yield Message.Url, file["url"], file
            return

        if images := self.images():
            for file in images:

                data = {
                    "file": file,
                    "user": file.pop("user"),
                }

                if self._meta_generation:
                    data["generation"] = self._extract_meta_generation(file)
                if self._meta_tags:
                    data["tags"] = self._extract_meta_tags(file)
                if self._meta_version:
                    data["model"], data["version"] = \
                        self._extract_meta_version(file, False)
                    if "post" in file:
                        data["post"] = file.pop("post")
                if self._meta_post and "post" not in data:
                    data["post"] = post = self._extract_meta_post(file)
                    if post:
                        post.pop("user", None)
                file["date"] = self.parse_datetime_iso(file["createdAt"])

                data["url"] = url = self._url(file)
                text.nameext_from_url(url, data)
                if not data["extension"]:
                    data["extension"] = (
                        self._video_ext if file.get("type") == "video" else
                        self._image_ext)
                yield Message.Directory, "", data
                yield Message.Url, url, data
            return

    def models(self):
        return ()

    def posts(self):
        return ()

    def images(self):
        return ()

    def _url(self, image):
        url = image["url"]
        video = image.get("type") == "video"
        quality = self._video_quality if video else self._image_quality

        if "/" in url:
            parts = url.rsplit("/", 3)
            image["uuid"] = parts[1]
            parts[2] = quality
            return "/".join(parts)

        image["uuid"] = url
        name = image.get("name")
        if not name:
            if mime := image.get("mimeType"):
                name = f"{image.get('id')}.{mime.rpartition('/')[2]}"
            else:
                ext = self._video_ext if video else self._image_ext
                name = f"{image.get('id')}.{ext}"
        return (f"https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA"
                f"/{url}/{quality}/{name}")

    def _image_results(self, images):
        for num, file in enumerate(images, 1):
            data = text.nameext_from_url(file["url"], {
                "num" : num,
                "file": file,
                "url" : self._url(file),
            })
            if not data["extension"]:
                data["extension"] = (
                    self._video_ext if file.get("type") == "video" else
                    self._image_ext)
            if "id" not in file and data["filename"].isdecimal():
                file["id"] = text.parse_int(data["filename"])
            if "date" not in file:
                file["date"] = self.parse_datetime_iso(file["createdAt"])
            if self._meta_generation:
                file["generation"] = self._extract_meta_generation(file)
            if self._meta_tags:
                file["tags"] = self._extract_meta_tags(file)
            yield data

    def _image_reactions(self):
        self._require_auth()

        params = self.params
        params["authed"] = True
        params["useIndex"] = False
        if "reactions" not in params:
            params["reactions"] = ("Like", "Dislike", "Heart", "Laugh", "Cry")
        return self.api.images(params)

    def _require_auth(self):
        if "Authorization" not in self.api.headers and \
                not self.cookies.get(
                "__Secure-civitai-token", domain=".civitai.com"):
            raise exception.AuthRequired(("api-key", "authenticated cookies"))

    def _parse_query(self, value):
        return text.parse_query_list(
            value, {"tags", "reactions", "baseModels", "tools", "techniques",
                    "types", "fileFormats"})

    def _extract_meta_generation(self, image):
        try:
            return self.api.image_generationdata(image["id"])
        except Exception as exc:
            return self.log.traceback(exc)

    def _extract_meta_post(self, image):
        try:
            post = self.api.post(image["postId"])
            post["date"] = self.parse_datetime_iso(post["publishedAt"])
            return post
        except Exception as exc:
            return self.log.traceback(exc)

    def _extract_meta_tags(self, image):
        try:
            return self.api.tag_getvotabletags(image["id"])
        except Exception as exc:
            return self.log.traceback(exc)

    def _extract_meta_version(self, item, is_post=True):
        try:
            if version_id := self._extract_version_id(item, is_post):
                version = self.api.model_version(version_id).copy()
                return version.pop("model", None), version
        except Exception as exc:
            self.log.traceback(exc)
        return None, None

    def _extract_version_id(self, item, is_post=True):
        if version_id := item.get("modelVersionId"):
            return version_id
        if version_ids := item.get("modelVersionIds"):
            return version_ids[0]
        if version_ids := item.get("modelVersionIdsManual"):
            return version_ids[0]

        if is_post:
            return None

        item["post"] = post = self.api.post(item["postId"])
        post.pop("user", None)
        return self._extract_version_id(post)


class CivitaiModelExtractor(CivitaiExtractor):
    subcategory = "model"
    directory_fmt = ("{category}", "{user[username]}",
                     "{model[id]}{model[name]:? //}",
                     "{version[id]}{version[name]:? //}")
    pattern = rf"{BASE_PATTERN}/models/(\d+)(?:/?\?modelVersionId=(\d+))?"
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
            version["date"] = self.parse_datetime_iso(version["createdAt"])

            data = {
                "model"  : model,
                "version": version,
                "user"   : user,
            }

            yield Message.Directory, "", data
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
            name, sep, ext = file["name"].rpartition(".")
            if not sep:
                name = ext
                ext = "bin"
            file["uuid"] = f"model-{model['id']}-{version['id']}-{file['id']}"
            files.append({
                "num"      : num,
                "file"     : file,
                "filename" : name,
                "extension": ext,
                "url"      : (
                    file.get("downloadUrl") or
                    f"{self.root}/api/download/models/{version['id']}"),
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
                "prioritizedUserIds": (user["id"],),
                "period" : self.api._param_period(),
                "sort"   : self.api._param_sort(),
                "limit"  : 20,
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
                msg = f"\"{text.remove_html(alert)}\" - 'api-key' required"
            else:
                msg = "'api-key' required to download this file"
            self.log.warning(msg)
            return False
        return True


class CivitaiImageExtractor(CivitaiExtractor):
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/images/(\d+)"
    example = "https://civitai.com/images/12345"

    def images(self):
        return self.api.image(self.groups[0])


class CivitaiCollectionExtractor(CivitaiExtractor):
    subcategory = "collection"
    directory_fmt = ("{category}", "{user_collection[username]}",
                     "collections", "{collection[id]}{collection[name]:? //}")
    pattern = rf"{BASE_PATTERN}/collections/(\d+)"
    example = "https://civitai.com/collections/12345"

    def images(self):
        cid = int(self.groups[0])
        self.kwdict["collection"] = col = self.api.collection(cid)
        self.kwdict["user_collection"] = col.pop("user", None)

        params = {
            "collectionId"  : cid,
            "period"        : self.api._param_period(),
            "sort"          : self.api._param_sort(),
            "browsingLevel" : self.api.nsfw,
            "include"       : ("cosmetics",),
        }
        return self.api.images(params, defaults=False)


class CivitaiPostExtractor(CivitaiExtractor):
    subcategory = "post"
    directory_fmt = ("{category}", "{username|user[username]}", "posts",
                     "{post[id]}{post[title]:? //}")
    pattern = rf"{BASE_PATTERN}/posts/(\d+)"
    example = "https://civitai.com/posts/12345"

    def posts(self):
        return ({"id": int(self.groups[0])},)


class CivitaiTagExtractor(CivitaiExtractor):
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}/tag/([^/?&#]+)"
    example = "https://civitai.com/tag/TAG"

    def models(self):
        tag = text.unquote(self.groups[0])
        return self.api.models_tag(tag)


class CivitaiSearchModelsExtractor(CivitaiExtractor):
    subcategory = "search-models"
    pattern = rf"{BASE_PATTERN}/search/models\?([^#]+)"
    example = "https://civitai.com/search/models?query=QUERY"

    def models(self):
        params = self._parse_query(self.groups[0])
        return CivitaiSearchAPI(self).search_models(
            params.get("query"), params.get("sortBy"), self.api.nsfw)


class CivitaiSearchImagesExtractor(CivitaiExtractor):
    subcategory = "search-images"
    pattern = rf"{BASE_PATTERN}/search/images\?([^#]+)"
    example = "https://civitai.com/search/images?query=QUERY"

    def images(self):
        params = self._parse_query(self.groups[0])
        return CivitaiSearchAPI(self).search_images(
            params.get("query"), params.get("sortBy"), self.api.nsfw)


class CivitaiModelsExtractor(CivitaiExtractor):
    subcategory = "models"
    pattern = rf"{BASE_PATTERN}/models(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/models"

    def models(self):
        params = self._parse_query(self.groups[0])
        return self.api.models(params)


class CivitaiImagesExtractor(CivitaiExtractor):
    subcategory = "images"
    pattern = rf"{BASE_PATTERN}/images(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/images"

    def images(self):
        params = self._parse_query(self.groups[0])
        params["types"] = ("image",)
        return self.api.images(params)


class CivitaiVideosExtractor(CivitaiExtractor):
    subcategory = "videos"
    pattern = rf"{BASE_PATTERN}/videos(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/videos"

    def images(self):
        params = self._parse_query(self.groups[0])
        params["types"] = ("video",)
        return self.api.images(params)


class CivitaiPostsExtractor(CivitaiExtractor):
    subcategory = "posts"
    pattern = rf"{BASE_PATTERN}/posts(?:/?\?([^#]+))?(?:$|#)"
    example = "https://civitai.com/posts"

    def posts(self):
        params = self._parse_query(self.groups[0])
        return self.api.posts(params)


class CivitaiUserExtractor(Dispatch, CivitaiExtractor):
    pattern = rf"{USER_PATTERN}/?(?:$|\?|#)"
    example = "https://civitai.com/user/USER"

    def items(self):
        base = f"{self.root}/user/{self.groups[0]}/"
        return self._dispatch_extractors((
            (CivitaiUserModelsExtractor, base + "models"),
            (CivitaiUserPostsExtractor , base + "posts"),
            (CivitaiUserImagesExtractor, base + "images"),
            (CivitaiUserVideosExtractor, base + "videos"),
            (CivitaiUserCollectionsExtractor, base + "collections"),
        ), ("user-images", "user-videos"))


class CivitaiUserModelsExtractor(CivitaiExtractor):
    subcategory = "user-models"
    pattern = rf"{USER_PATTERN}/models/?(?:\?([^#]+))?"
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
    pattern = rf"{USER_PATTERN}/posts/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/posts"

    def posts(self):
        user, query = self.groups
        params = self._parse_query(query)
        params["username"] = text.unquote(user)
        return self.api.posts(params)


class CivitaiUserImagesExtractor(CivitaiExtractor):
    subcategory = "user-images"
    pattern = rf"{USER_PATTERN}/images/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/images"

    def __init__(self, match):
        user, query = match.groups()
        self.params = self._parse_query(query)
        self.params["types"] = ("image",)
        if self.params.get("section") == "reactions":
            self.subcategory = "reactions-images"
            self.images = self._image_reactions
        else:
            self.params["username"] = text.unquote(user)
        CivitaiExtractor.__init__(self, match)

    def images(self):
        return self.api.images(self.params)


class CivitaiUserVideosExtractor(CivitaiExtractor):
    subcategory = "user-videos"
    directory_fmt = ("{category}", "{username|user[username]}", "videos")
    pattern = rf"{USER_PATTERN}/videos/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/videos"

    def __init__(self, match):
        user, query = match.groups()
        self.params = self._parse_query(query)
        self.params["types"] = ("video",)
        if self.params.get("section") == "reactions":
            self.subcategory = "reactions-videos"
            self.images = self._image_reactions
        else:
            self.params["username"] = text.unquote(user)
        CivitaiExtractor.__init__(self, match)

    images = CivitaiUserImagesExtractor.images


class CivitaiUserCollectionsExtractor(CivitaiExtractor):
    subcategory = "user-collections"
    pattern = rf"{USER_PATTERN}/collections/?(?:\?([^#]+))?"
    example = "https://civitai.com/user/USER/collections"

    def items(self):
        user, query = self.groups
        params = self._parse_query(query)
        params["userId"] = self.api.user(text.unquote(user))[0]["id"]

        base = f"{self.root}/collections/"
        for collection in self.api.collections(params):
            collection["_extractor"] = CivitaiCollectionExtractor
            yield Message.Queue, f"{base}{collection['id']}", collection


class CivitaiGeneratedExtractor(CivitaiExtractor):
    """Extractor for your generated files feed"""
    subcategory = "generated"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "generated")
    pattern = rf"{BASE_PATTERN}/generate"
    example = "https://civitai.com/generate"

    def items(self):
        self._require_auth()

        for gen in self.api.orchestrator_queryGeneratedImages():
            gen["date"] = self.parse_datetime_iso(gen["createdAt"])
            yield Message.Directory, "", gen
            for step in gen.pop("steps", ()):
                for image in step.pop("images", ()):
                    data = {"file": image, **step, **gen}
                    url = image["url"]
                    yield Message.Url, url, text.nameext_from_url(url, data)


class CivitaiRestAPI():
    """Interface for the Civitai Public REST API

    https://developer.civitai.com/docs/api/public-rest
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"
        self.headers = {"Content-Type": "application/json"}

        if api_key := extractor.config("api-key"):
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
        endpoint = f"/v1/models/{model_id}"
        return self._call(endpoint)

    @memcache(keyarg=1)
    def model_version(self, model_version_id):
        endpoint = f"/v1/model-versions/{model_version_id}"
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
            "x-client-version": "5.0.954",
            "x-client-date"   : "",
            "x-client"        : "web",
            "x-fingerprint"   : "undefined",
        }
        if api_key := extractor.config("api-key"):
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
                "period"       : self._param_period(),
                "sort"         : self._param_sort(),
                "withMeta"     : False,  # Metadata Only
                "fromPlatform" : False,  # Made On-Site
                "browsingLevel": self.nsfw,
                "include"      : ("cosmetics",),
            })

        params = self._type_params(params)
        return self._pagination(endpoint, params)

    def images_gallery(self, model, version, user):
        endpoint = "image.getImagesAsPostsInfinite"
        params = {
            "period"        : self._param_period(),
            "sort"          : self._param_sort(),
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

    @memcache(keyarg=1)
    def model_version(self, model_version_id):
        endpoint = "modelVersion.getById"
        params = {"id": int(model_version_id)}
        return self._call(endpoint, params)

    def models(self, params, defaults=True):
        endpoint = "model.getAll"

        if defaults:
            params = self._merge_params(params, {
                "period"       : self._param_period(),
                "periodMode"   : "published",
                "sort"         : self._param_sort(),
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
                "period"       : self._param_period(),
                "periodMode"   : "published",
                "sort"         : self._param_sort(),
                "followed"     : False,
                "draftOnly"    : False,
                "pending"      : True,
                "include"      : ("cosmetics",),
            })

        params = self._type_params(params)
        return self._pagination(endpoint, params, meta,
                                user=("username" in params))

    def collection(self, collection_id):
        endpoint = "collection.getById"
        params = {"id": int(collection_id)}
        return self._call(endpoint, params)["collection"]

    def collections(self, params, defaults=True):
        endpoint = "collection.getInfinite"

        if defaults:
            params = self._merge_params(params, {
                "browsingLevel": self.nsfw,
                "sort"         : self._param_sort(),
            })

        params = self._type_params(params)
        return self._pagination(endpoint, params)

    def tag_getvotabletags(self, image_id):
        endpoint = "tag.getVotableTags"
        params = {"id": int(image_id), "type": "image"}
        return self._call(endpoint, params)

    def user(self, username):
        endpoint = "user.getCreator"
        params = {"username": username}
        return (self._call(endpoint, params),)

    def orchestrator_queryGeneratedImages(self):
        endpoint = "orchestrator.queryGeneratedImages"
        params = {
            "ascending": True if self._param_sort() == "Oldest" else False,
            "tags"     : ("gen",),
            "authed"   : True,
        }
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params, meta=None):
        url = self.root + endpoint
        headers = self.headers

        if meta:
            input = {"json": params, "meta": {"values": meta}}
        else:
            input = {"json": params}

        params = {"input": util.json_dumps(input)}
        headers["x-client-date"] = str(int(time.time() * 1000))
        return self.extractor.request_json(
            url, params=params, headers=headers)["result"]["data"]["json"]

    def _pagination(self, endpoint, params, meta=None, user=False):
        if "cursor" not in params:
            params["cursor"] = None
            meta_ = {"cursor": ("undefined",)}

        data = self._call(endpoint, params, meta_)
        if user and data["items"] and \
                data["items"][0]["user"]["username"] != params["username"]:
            return ()

        while True:
            yield from data["items"]

            try:
                if not data["nextCursor"]:
                    return
            except KeyError:
                return

            params["cursor"] = data["nextCursor"]
            meta_ = meta
            data = self._call(endpoint, params, meta_)

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

    def _param_period(self):
        if period := self.extractor.config("period"):
            return period
        return "AllTime"

    def _param_sort(self):
        if sort := self.extractor.config("sort"):
            s = sort[0].lower()
            if s in "drn":
                return "Newest"
            if s in "ao":
                return "Oldest"
            return sort
        return "Newest"


def _bool(value):
    return value == "true"


class CivitaiSearchAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = "https://search-new.civitai.com"

        if auth := extractor.config("token"):
            if " " not in auth:
                auth = f"Bearer {auth}"
        else:
            auth = ("Bearer 8c46eb2508e21db1e9828a97968d"
                    "91ab1ca1caa5f70a00e88a2ba1e286603b61")

        self.headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "X-Meilisearch-Client": "Meilisearch instant-meilisearch (v0.13.5)"
                                    " ; Meilisearch JavaScript (v0.34.0)",
            "Origin": extractor.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=4",
        }

    def search(self, query, type, facets, nsfw=31):
        endpoint = "/multi-search"

        query = {
            "q"       : query,
            "indexUid": type,
            "facets"  : facets,
            "attributesToHighlight": (),
            "highlightPreTag" : "__ais-highlight__",
            "highlightPostTag": "__/ais-highlight__",
            "limit" : 51,
            "offset": 0,
            "filter": (self._generate_filter(nsfw),),
        }

        return self._pagination(endpoint, query)

    def search_models(self, query, type=None, nsfw=31):
        facets = (
            "category.name",
            "checkpointType",
            "fileFormats",
            "lastVersionAtUnix",
            "tags.name",
            "type",
            "user.username",
            "version.baseModel",
        )
        return self.search(query, type or "models_v9", facets, nsfw)

    def search_images(self, query, type=None, nsfw=31):
        facets = (
            "aspectRatio",
            "baseModel",
            "createdAtUnix",
            "tagNames",
            "techniqueNames",
            "toolNames",
            "type",
            "user.username",
        )
        return self.search(query, type or "images_v6", facets, nsfw)

    def _call(self, endpoint, query):
        url = self.root + endpoint
        params = util.json_dumps({"queries": (query,)})

        data = self.extractor.request_json(
            url, method="POST", headers=self.headers, data=params)

        return data["results"][0]

    def _pagination(self, endpoint, query):
        limit = query["limit"] - 1
        threshold = limit // 2

        while True:
            data = self._call(endpoint, query)

            items = data["hits"]
            yield from items

            if len(items) < threshold:
                return
            query["offset"] += limit

    def _generate_filter(self, level):
        fltr = []

        if level & 1:
            fltr.append("1")
        if level & 2:
            fltr.append("2")
        if level & 4:
            fltr.append("4")
        if level & 8:
            fltr.append("8")
        if level & 16:
            fltr.append("16")

        if not fltr:
            return "()"
        return "(nsfwLevel=" + " OR nsfwLevel=".join(fltr) + ")"
