# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os

class BasicDownloader():
    """Base class for downlaoder modules"""

    max_tries = 5

    def download(self, url, path):
        """Download the resource at 'url' and write it to a file given by 'path'"""
        with open(path, "wb") as file:
            try:
                return self.download_impl(url, file)
            except:
                # make sure to remove file if download failed
                os.unlink(path)
                raise

    def download_impl(self, url, file_handle):
        """Actual implementaion of the download process"""
        pass

    @staticmethod
    def print_error(file, error, tries, max_tries=5):
        """Print a message indicating an error during download"""
        if tries == 1 and hasattr(file, "name"):
            print("\r\033[1;31m", file.name, sep="")
        print("\033[0;31m[Error]\033[0m ", error, " (", tries, "/", max_tries, ")", sep="")
