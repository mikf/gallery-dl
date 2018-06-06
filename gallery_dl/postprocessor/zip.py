# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Add files to ZIP archives"""

from .common import PostProcessor
import zipfile


class ZipPP(PostProcessor):

    COMPRESSION_ALGORITHMS = {
        "store": zipfile.ZIP_STORED,
        "zip": zipfile.ZIP_DEFLATED,
        "bzip2": zipfile.ZIP_BZIP2,
        "lzma": zipfile.ZIP_LZMA,
    }

    def __init__(self, options):
        PostProcessor.__init__(self)
        self.ext = "." + options.get("extension", "zip")

        algorithm = options.get("compression", "store")
        if algorithm not in self.COMPRESSION_ALGORITHMS:
            algorithm = "store"
        self.compression = self.COMPRESSION_ALGORITHMS[algorithm]

    def run(self, pathfmt):
        archive = pathfmt.realdirectory + self.ext
        with zipfile.ZipFile(archive, "a", self.compression, True) as zfile:
            zfile.write(pathfmt.temppath, pathfmt.filename)


__postprocessor__ = ZipPP
