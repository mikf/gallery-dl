# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Categorize files by file extension"""

from .common import PostProcessor
import os


class ClassifyPP(PostProcessor):

    DEFAULT_MAPPING = {
        "Music" : ("mp3", "aac", "flac", "ogg", "wma", "m4a", "wav"),
        "Video" : ("flv", "ogv", "avi", "mp4", "mpg", "mpeg", "3gp", "mkv",
                   "webm", "vob", "wmv"),
        "Pictures" : ("jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"),
        "Archives" : ("zip", "rar", "7z", "tar", "gz", "bz2"),
    }

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)
        mapping = options.get("mapping", self.DEFAULT_MAPPING)

        self.mapping = {
            ext: directory
            for directory, exts in mapping.items()
            for ext in exts
        }

    def run(self, pathfmt):
        ext = pathfmt.keywords["extension"]

        if ext in self.mapping:
            path = pathfmt.realdirectory + os.sep + self.mapping[ext]
            pathfmt.realpath = path + os.sep + pathfmt.filename
            os.makedirs(path, exist_ok=True)


__postprocessor__ = ClassifyPP
