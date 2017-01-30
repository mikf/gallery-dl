# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http:// and https:// urls"""

import time
import requests
import mimetypes
from .common import BasicDownloader


class Downloader(BasicDownloader):

    def __init__(self, output):
        BasicDownloader.__init__(self)
        self.session = requests.session()
        self.out = output

    def download_impl(self, url, pathfmt):
        tries = 0
        while True:
            # try to connect to remote source
            try:
                response = self.session.get(url, stream=True, verify=True)
            except requests.exceptions.ConnectionError as exptn:
                tries += 1
                self.out.error(pathfmt.path, exptn, tries, self.max_tries)
                time.sleep(1)
                if tries == self.max_tries:
                    return tries
                continue

            # reject error-status-codes
            if response.status_code != requests.codes.ok:
                tries += 1
                self.out.error(pathfmt.path, 'HTTP status "{} {}"'.format(
                    response.status_code, response.reason),
                    tries, self.max_tries
                )
                if response.status_code == 404:
                    return self.max_tries
                time.sleep(1)
                if tries == self.max_tries:
                    return tries
                continue

            # everything ok -- proceed to download
            break

        if not pathfmt.has_extension:
            # set 'extension' keyword from Content-Type header
            mtype = response.headers.get("Content-Type", "image/jpeg")
            extensions = mimetypes.guess_all_extensions(mtype, strict=False)
            extensions.sort()
            pathfmt.set_extension(extensions[-1][1:])
            if pathfmt.exists():
                self.out.skip(pathfmt.path)
                response.close()
                return

        self.out.start(pathfmt.path)
        self.downloading = True
        with pathfmt.open() as file:
            for data in response.iter_content(16384):
                file.write(data)
        self.downloading = False
        self.out.success(pathfmt.path, tries)

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
