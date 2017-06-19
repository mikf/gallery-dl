# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// urls"""

import time
import requests
import requests.exceptions as rexcepts
import mimetypes
import logging
from .common import BasicDownloader
from .. import config

log = logging.getLogger("http")


class Downloader(BasicDownloader):

    retries = config.interpolate(("downloader", "http", "retries",), 5)
    timeout = config.interpolate(("downloader", "http", "timeout",), None)

    def __init__(self, output):
        BasicDownloader.__init__(self)
        self.session = requests.session()
        self.out = output

    def download_impl(self, url, pathfmt):
        tries = 0
        msg = ""
        while True:
            tries += 1
            if tries > 1:
                self.out.error(pathfmt.path, msg, tries-1, self.retries)
                if tries > self.retries:
                    return
                time.sleep(1)

            # try to connect to remote source
            try:
                response = self.session.get(
                    url, stream=True, timeout=self.timeout
                )
            except (rexcepts.ConnectionError, rexcepts.Timeout) as exception:
                msg = exception
                continue
            except (rexcepts.RequestException, UnicodeError) as exception:
                msg = exception
                break

            # reject error-status-codes
            if response.status_code != 200:
                msg = 'HTTP status "{} {}"'.format(
                    response.status_code, response.reason
                )
                response.close()
                if response.status_code == 404:
                    break
                continue

            if not pathfmt.has_extension:
                # set 'extension' keyword from Content-Type header
                mtype = response.headers.get("Content-Type", "image/jpeg")
                mtype = mtype.partition(";")[0]
                exts = mimetypes.guess_all_extensions(mtype, strict=False)
                if exts:
                    exts.sort()
                    pathfmt.set_extension(exts[-1][1:])
                else:
                    log.warning("No file extension found for MIME type '%s'",
                                mtype)
                    pathfmt.set_extension("txt")
                if pathfmt.exists():
                    self.out.skip(pathfmt.path)
                    response.close()
                    return

            # everything ok -- proceed to download
            self.out.start(pathfmt.path)
            self.downloading = True
            try:
                with pathfmt.open() as file:
                    for data in response.iter_content(16384):
                        file.write(data)
            except rexcepts.RequestException as exception:
                msg = exception
                response.close()
                continue
            self.downloading = False
            self.out.success(pathfmt.path, tries)
            return

        # output for unrecoverable errors
        self.out.error(pathfmt.path, msg, tries, 0)

    def set_headers(self, headers):
        """Set headers for http requests"""
        self.set_dict(self.session.headers, headers)

    def set_cookies(self, cookies):
        """Set cookies for http requests"""
        self.set_dict(self.session.cookies, cookies)

    @staticmethod
    def set_dict(dest, src):
        """Copy the contents of dictionary 'src' to 'dest'"""
        dest.clear()
        dest.update(src)
