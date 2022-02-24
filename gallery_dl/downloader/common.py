# -*- coding: utf-8 -*-

# Copyright 2014-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by downloader modules."""

import os
from .. import config, util


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""

    def __init__(self, job):
        extr = job.extractor

        self.options = options = config.build_module_options_dict(
            extr, "downloader", self.scheme)
        self.config = cfg = options.get

        self.out = job.out
        self.log = job.get_logger("downloader." + self.scheme)
        self.session = extr.session

        self.part = cfg("part", True)
        if partdir := cfg("part-directory"):
            self.partdir = util.expand_path(partdir)
            os.makedirs(self.partdir, exist_ok=True)
        else:
            self.partdir = None

    def download(self, url, pathfmt):
        """Write data from 'url' into the file specified by 'pathfmt'"""
