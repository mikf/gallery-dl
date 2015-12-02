# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os

class BasicDownloader():
    """Base class for downloader modules"""

    max_tries = 5

    def download(self, url, path):
        """Download the resource at 'url' and write it to a file given by 'path'"""
        with open(path, "wb") as file:
            try:
                return self.download_impl(url, file)
            except:
                #remove file if download failed
                file.close()
                os.unlink(path)
                raise

    def download_impl(self, url, file_handle):
        """Actual implementaion of the download process"""
        pass
