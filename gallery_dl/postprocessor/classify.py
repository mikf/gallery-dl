# -*- coding: utf-8 -*-

# Copyright 2018-2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Categorize files by file extension"""

from .common import PostProcessor
import os


class ClassifyPP(PostProcessor):

    DEFAULT_MAPPING = {
        "Pictures" : ("jpg", "jpeg", "png", "gif", "bmp", "svg", "webp",
                      "avif", "heic", "heif", "ico", "psd"),
        "Video"    : ("flv", "ogv", "avi", "mp4", "mpg", "mpeg", "3gp", "mkv",
                      "webm", "vob", "wmv", "m4v", "mov"),
        "Music"    : ("mp3", "aac", "flac", "ogg", "wma", "m4a", "wav"),
        "Archives" : ("zip", "rar", "7z", "tar", "gz", "bz2"),
        "Documents": ("txt", "pdf"),
    }

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.directory = self.realdirectory = ""

        mapping = options.get("mapping", self.DEFAULT_MAPPING)
        self.mapping = {
            ext: directory
            for directory, exts in mapping.items()
            for ext in exts
        }

        job.register_hooks({
            "post"   : self.initialize,
            "prepare": self.prepare,
        }, options)

    def initialize(self, pathfmt):
        # store base directory paths
        self.directory = pathfmt.directory
        self.realdirectory = pathfmt.realdirectory

    def prepare(self, pathfmt):
        # extend directory paths depending on file extension
        ext = pathfmt.extension
        if ext in self.mapping:
            extra = self.mapping[ext] + os.sep
            pathfmt.directory = self.directory + extra
            pathfmt.realdirectory = self.realdirectory + extra


__postprocessor__ = ClassifyPP
