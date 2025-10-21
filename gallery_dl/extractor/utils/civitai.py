# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import util
from ...cache import memcache
import time


def _bool(value):
    return value == "true"


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
