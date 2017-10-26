# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// URLs"""

import mimetypes
from .common import DownloaderBase
from .. import util


class Downloader(DownloaderBase):
    scheme = "http"

    def __init__(self, session, output):
        DownloaderBase.__init__(self, session, output)
        self.response = None
        self.retries = self.config("retries", 5)
        self.timeout = self.config("timeout", 30)
        self.verify = self.config("verify", True)

    def connect(self, url, offset):
        headers = {}
        if offset:
            headers["Range"] = "bytes={}-".format(offset)

        self.response = self.session.request(
            "GET", url, stream=True, headers=headers, allow_redirects=True,
            timeout=self.timeout, verify=self.verify)

        code = self.response.status_code
        if code == 200:
            offset = 0
            size = self.response.headers.get("Content-Length")
        elif code == 206:
            size = self.response.headers["Content-Range"].rpartition("/")[2]
        elif code == 416:
            # file is already complete
            return -1, 0
        else:
            self.response.raise_for_status()

        return offset, util.safe_int(size)

    def receive(self, file):
        for data in self.response.iter_content(16384):
            file.write(data)

    def reset(self):
        if self.response:
            self.response.close()
        self.response = None

    def get_extension(self):
        mtype = self.response.headers.get("Content-Type", "image/jpeg")
        mtype = mtype.partition(";")[0]
        exts = mimetypes.guess_all_extensions(mtype, strict=False)
        if exts:
            exts.sort()
            return exts[-1][1:]
        self.log.warning(
            "No filename extension found for MIME type '%s'", mtype)
        return "txt"
