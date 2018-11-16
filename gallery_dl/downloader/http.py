# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// URLs"""

import time
import mimetypes
from requests.exceptions import ConnectionError, Timeout
from .common import DownloaderBase
from .. import text, exception


class HttpDownloader(DownloaderBase):
    scheme = "http"

    def __init__(self, extractor, output):
        DownloaderBase.__init__(self, extractor, output)
        self.response = None
        self.retries = self.config("retries", extractor._retries)
        self.timeout = self.config("timeout", extractor._timeout)
        self.verify = self.config("verify", extractor._verify)
        self.rate = self.config("rate")
        self.chunk_size = 16384

        if self.rate:
            self.rate = text.parse_bytes(self.rate)
            if not self.rate:
                self.log.warning("Invalid rate limit specified")
            elif self.rate < self.chunk_size:
                self.chunk_size = self.rate

    def connect(self, url, offset):
        headers = {}
        if offset:
            headers["Range"] = "bytes={}-".format(offset)

        try:
            self.response = self.session.request(
                "GET", url, stream=True, headers=headers, allow_redirects=True,
                timeout=self.timeout, verify=self.verify)
        except (ConnectionError, Timeout) as exc:
            raise exception.DownloadRetry(exc)

        code = self.response.status_code
        if code == 200:  # OK
            offset = 0
            size = self.response.headers.get("Content-Length")
        elif code == 206:  # Partial Content
            size = self.response.headers["Content-Range"].rpartition("/")[2]
        elif code == 416:  # Requested Range Not Satisfiable
            raise exception.DownloadComplete()
        elif code == 429 or 500 <= code < 600:  # Server Error
            raise exception.DownloadRetry(
                "{} Server Error: {} for url: {}".format(
                    code, self.response.reason, url))
        else:
            self.response.raise_for_status()

        return offset, text.parse_int(size)

    def receive(self, file):
        if self.rate:
            total = 0            # total amount of bytes received
            start = time.time()  # start time

        for data in self.response.iter_content(self.chunk_size):
            file.write(data)

            if self.rate:
                total += len(data)
                expected = total / self.rate  # expected elapsed time
                delta = time.time() - start   # actual elapsed time since start
                if delta < expected:
                    # sleep if less time passed than expected
                    time.sleep(expected - delta)

    def reset(self):
        if self.response:
            self.response.close()
        self.response = None

    def get_extension(self):
        mtype = self.response.headers.get("Content-Type", "image/jpeg")
        mtype = mtype.partition(";")[0]

        if mtype in MIMETYPE_MAP:
            return MIMETYPE_MAP[mtype]

        exts = mimetypes.guess_all_extensions(mtype, strict=False)
        if exts:
            exts.sort()
            return exts[-1][1:]

        self.log.warning(
            "No filename extension found for MIME type '%s'", mtype)
        return "txt"


MIMETYPE_MAP = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/bmp": "bmp",
    "image/webp": "webp",
    "image/svg+xml": "svg",

    "video/webm": "webm",
    "video/ogg": "ogg",
    "video/mp4": "mp4",

    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",

    "application/ogg": "ogg",
    "application/octet-stream": "bin",
}


__downloader__ = HttpDownloader
