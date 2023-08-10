# -*- coding: utf-8 -*-

# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Store files in ZIP archives"""

from .common import PostProcessor
from .. import util
import zipfile
import os


class ZipPP(PostProcessor):

    COMPRESSION_ALGORITHMS = {
        "store": zipfile.ZIP_STORED,
        "zip"  : zipfile.ZIP_DEFLATED,
        "bzip2": zipfile.ZIP_BZIP2,
        "lzma" : zipfile.ZIP_LZMA,
    }

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.delete = not options.get("keep-files", False)
        self.files = options.get("files")
        ext = "." + options.get("extension", "zip")
        algorithm = options.get("compression", "store")
        if algorithm not in self.COMPRESSION_ALGORITHMS:
            self.log.warning(
                "unknown compression algorithm '%s'; falling back to 'store'",
                algorithm)
            algorithm = "store"

        self.zfile = None
        self.path = job.pathfmt.realdirectory[:-1]
        self.args = (self.path + ext, "a",
                     self.COMPRESSION_ALGORITHMS[algorithm], True)

        job.register_hooks({
            "file": (self.write_safe if options.get("mode") == "safe" else
                     self.write_fast),
        }, options)
        job.hooks["finalize"].append(self.finalize)

    def open(self):
        try:
            return zipfile.ZipFile(*self.args)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.path))
            return zipfile.ZipFile(*self.args)

    def write(self, pathfmt, zfile):
        # 'NameToInfo' is not officially documented, but it's available
        # for all supported Python versions and using it directly is a lot
        # faster than calling getinfo()
        if self.files:
            self.write_extra(pathfmt, zfile, self.files)
            self.files = None
        if pathfmt.filename not in zfile.NameToInfo:
            zfile.write(pathfmt.temppath, pathfmt.filename)
            pathfmt.delete = self.delete

    def write_fast(self, pathfmt):
        if self.zfile is None:
            self.zfile = self.open()
        self.write(pathfmt, self.zfile)

    def write_safe(self, pathfmt):
        with self.open() as zfile:
            self.write(pathfmt, zfile)

    def write_extra(self, pathfmt, zfile, files):
        for path in map(util.expand_path, files):
            if not os.path.isabs(path):
                path = os.path.join(pathfmt.realdirectory, path)
            try:
                zfile.write(path, os.path.basename(path))
            except OSError as exc:
                self.log.warning(
                    "Unable to write %s to %s", path, zfile.filename)
                self.log.debug("%s: %s", exc, exc.__class__.__name__)
                pass
            else:
                if self.delete:
                    util.remove_file(path)

    def finalize(self, pathfmt):
        if self.zfile:
            self.zfile.close()

        if self.delete:
            util.remove_directory(self.path)

            if self.zfile and not self.zfile.NameToInfo:
                # remove empty zip archive
                util.remove_file(self.zfile.filename)


__postprocessor__ = ZipPP
