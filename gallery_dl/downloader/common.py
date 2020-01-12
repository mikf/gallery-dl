# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os
import logging
from .. import config, util


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""

    def __init__(self, extractor, output):
        self.session = extractor.session
        self.out = output
        self.part = self.config("part", True)
        self.partdir = self.config("part-directory")

        self.log = logging.getLogger("downloader." + self.scheme)
        self.log.job = extractor.log.job
        self.log.extractor = extractor

        if self.partdir:
            self.partdir = util.expand_path(self.partdir)
            os.makedirs(self.partdir, exist_ok=True)

    def config(self, key, default=None):
        """Interpolate downloader config value for 'key'"""
        return config.interpolate(("downloader", self.scheme), key, default)

    def download(self, url, pathfmt):
        """Write data from 'url' into the file specified by 'pathfmt'"""
