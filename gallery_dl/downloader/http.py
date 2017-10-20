# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// URLs"""

import time
import requests.exceptions as rexcepts
import mimetypes
import logging
from .common import BasicDownloader
from .. import config, util

log = logging.getLogger("http")


class Downloader(BasicDownloader):

    retries = config.interpolate(("downloader", "http", "retries",), 5)
    timeout = config.interpolate(("downloader", "http", "timeout",), 30)
    verify = config.interpolate(("downloader", "http", "verify",), True)

    def __init__(self, session, output):
        BasicDownloader.__init__(self)
        self.session = session
        self.out = output

    def download_impl(self, url, pathfmt):
        partial = False
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
                    url, stream=True, timeout=self.timeout, verify=self.verify,
                )
            except (rexcepts.ConnectionError, rexcepts.Timeout) as exception:
                msg = exception
                continue
            except (rexcepts.RequestException, UnicodeError) as exception:
                msg = exception
                break

            # reject error-status-codes
            if response.status_code not in (200, 206):
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

            #
            if partial and "Content-Range" in response.headers:
                size = response.headers["Content-Range"].rpartition("/")[2]
            else:
                size = response.headers.get("Content-Length")
            size = util.safe_int(size)

            # everything ok -- proceed to download
            self.out.start(pathfmt.path)
            self.downloading = True
            try:
                with pathfmt.open() as file:
                    for data in response.iter_content(16384):
                        file.write(data)
                    if size and file.tell() != size:
                        msg = "filesize mismatch ({} != {})".format(
                            file.tell(), size)
                        continue
            except rexcepts.RequestException as exception:
                msg = exception
                response.close()
                continue
            self.downloading = False
            self.out.success(pathfmt.path, tries)
            return

        # output for unrecoverable errors
        self.out.error(pathfmt.path, msg, tries, 0)
