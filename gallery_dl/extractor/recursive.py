# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Recursive extractor"""

from .common import Extractor, Message
import requests
import re


class RecursiveExtractor(Extractor):
    """Extractor that fetches URLs from a remote or local source"""
    category = "recursive"
    pattern = r"r(?:ecursive)?:"
    test = ("recursive:https://pastebin.com/raw/FLwrCYsT", {
        "url": "eee86d65c346361b818e8f4b2b307d9429f136a2",
    })

    def items(self):
        self.session.mount("file://", FileAdapter())
        page = self.request(self.url.partition(":")[2]).text
        del self.session.adapters["file://"]

        for match in re.finditer(r"https?://[^\s\"']+", page):
            yield Message.Queue, match.group(0), {}


class FileAdapter(requests.adapters.BaseAdapter):
    """Requests adapter for local files"""

    def send(self, request, **kwargs):
        response = requests.Response()
        try:
            response.raw = open(request.url[7:], "rb")
        except OSError:
            import io
            response.raw = io.BytesIO()
            response.status_code = requests.codes.bad_request
        else:
            response.raw.release_conn = response.raw.close
            response.status_code = requests.codes.ok
        return response

    def close(self):
        pass
