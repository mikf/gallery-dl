# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module for http urls"""

import time
import requests
from .common import BasicDownloader

class Downloader(BasicDownloader):

    def __init__(self, printer):
        BasicDownloader.__init__(self)
        self.session = requests.session()
        self.printer = printer

    def download_impl(self, url, file):
        tries = 0
        while True:
            # try to connect to remote source
            try:
                response = self.session.get(url, stream=True, verify=True)
            except requests.exceptions.ConnectionError as exptn:
                tries += 1
                self.printer.error(file, exptn, tries, self.max_tries)
                time.sleep(1)
                if tries == self.max_tries:
                    raise
                continue

            # reject error-status-codes
            if response.status_code != requests.codes.ok:
                tries += 1
                self.printer.error(file, 'HTTP status "{} {}"'.format(
                    response.status_code, response.reason), tries, self.max_tries)
                if response.status_code == 404:
                    return self.max_tries
                time.sleep(1)
                if tries == self.max_tries:
                    response.raise_for_status()
                continue

            # everything ok -- proceed to download
            break

        for data in response.iter_content(16384):
            file.write(data)
        return tries

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

