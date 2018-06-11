# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Store files in ZIP archives"""

from .common import PostProcessor
import zipfile
import os


class ZipPP(PostProcessor):

    COMPRESSION_ALGORITHMS = {
        "store": zipfile.ZIP_STORED,
        "zip": zipfile.ZIP_DEFLATED,
        "bzip2": zipfile.ZIP_BZIP2,
        "lzma": zipfile.ZIP_LZMA,
    }

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)
        self.delete = not options.get("keep-files", False)
        self.ext = "." + options.get("extension", "zip")
        algorithm = options.get("compression", "store")
        if algorithm not in self.COMPRESSION_ALGORITHMS:
            self.log.warning(
                "unknown compression algorithm '%s'; falling back to 'store'",
                algorithm)
            algorithm = "store"

        self.path = pathfmt.realdirectory
        self.zfile = zipfile.ZipFile(
            self.path + self.ext, "a",
            self.COMPRESSION_ALGORITHMS[algorithm], True)

    def run(self, pathfmt):
        # 'NameToInfo' is not officially documented, but it's available
        # for all supported Python versions and using it directly is a lot
        # better than calling getinfo()
        if pathfmt.filename not in self.zfile.NameToInfo:
            self.zfile.write(pathfmt.temppath, pathfmt.filename)
            pathfmt.delete = self.delete

    def finalize(self):
        self.zfile.close()

        if self.delete:
            try:
                os.rmdir(self.path)
            except OSError:
                pass


__postprocessor__ = ZipPP
