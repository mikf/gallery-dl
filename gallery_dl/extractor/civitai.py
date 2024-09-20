# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.civitai.com/"""

from .common import Extractor, Message
from .. import text
import itertools
import re

BASE_PATTERN = r"(?:https?://)?civitai\.com"


class CivitaiExtractor(Extractor):
    """Base class for civitai extractors"""
    category = "civitai"
    root = "https://civitai.com"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.api = CivitaiAPI(self)

    def items(self):
        data = {"_extractor": CivitaiModelExtractor}
        for model in self.models():
            url = "{}/models/{}".format(self.root, model["id"])
            yield Message.Queue, url, data


class CivitaiModelExtractor(CivitaiExtractor):
    subcategory = "model"
    directory_fmt = ("{category}", "{user[username]}",
                     "{model[id]}{model[name]:? //}",
                     "{version[id]}{version[name]:? //}")
    archive_fmt = "{file[hash]}"
    pattern = BASE_PATTERN + r"/models/(\d+)(?:/?\?modelVersionId=(\d+))?"
    example = "https://civitai.com/models/12345/TITLE"

    def items(self):
        model_id, version_id = self.groups
        self._sub = re.compile(r"/width=\d*/").sub

        model = self.api.model(model_id)
        creator = model["creator"]
        versions = model["modelVersions"]
        del model["creator"]
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
                "user"   : creator,
            }

            yield Message.Directory, data
            for file in self._extract_files(model, version):
                file.update(data)
                yield Message.Url, file["url"], file

    def _extract_files(self, model, version):
        filetypes = self.config("files")
        if filetypes is None:
            return self._extract_files_image(model, version)

        generators = {
            "model"   : self._extract_files_model,
            "image"   : self._extract_files_image,
            "gallery" : self._extract_files_gallery,
            "gallerie": self._extract_files_gallery,
        }
        if isinstance(filetypes, str):
            filetypes = filetypes.split(",")

        return itertools.chain.from_iterable(
            generators[ft.rstrip("s")](model, version)
            for ft in filetypes
        )

    def _extract_files_model(self, model, version):
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

    def _extract_files_image(self, model, version):
        return [
            text.nameext_from_url(file["url"], {
                "num" : num,
                "file": file,
                "url" : self._sub("/w/", file["url"]),
            })
            for num, file in enumerate(version["images"], 1)
        ]

    def _extract_files_gallery(self, model, version):
        params = {
            "modelId"       : model["id"],
            "modelVersionId": version["id"],
        }

        for num, file in enumerate(self.api.images(params), 1):
            yield text.nameext_from_url(file["url"], {
                "num" : num,
                "file": file,
                "url" : self._sub("/w/", file["url"]),
            })

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


class CivitaiTagExtractor(CivitaiExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tag/([^?/#]+)"
    example = "https://civitai.com/tag/TAG"

    def models(self):
        tag = text.unquote(self.groups[0])
        return self.api.models({"tag": tag})


class CivitaiSearchExtractor(CivitaiExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/models\?([^#]+)"
    example = "https://civitai.com/search/models?query=QUERY"

    def models(self):
        params = text.parse_query(self.groups[0])
        return self.api.models(params)


class CivitaiUserExtractor(CivitaiExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)(?:/models)?/?(?:$|\?|#)"
    example = "https://civitai.com/user/USER/models"

    def models(self):
        params = {"username": text.unquote(self.groups[0])}
        return self.api.models(params)


class CivitaiAPI():
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

    def images(self, params):
        endpoint = "/v1/images"
        return self._pagination(endpoint, params)

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
