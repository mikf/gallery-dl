# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
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

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        mapping = options.get("mapping", self.DEFAULT_MAPPING)

        self.mapping = {
            ext: directory
            for directory, exts in mapping.items()
            for ext in exts
        }

        job.hooks["prepare"].append(self.prepare)
        job.hooks["file"].append(self.move)

    def prepare(self, pathfmt):
        ext = pathfmt.extension
        if ext in self.mapping:
            # set initial paths to enable download skips
            self._build_paths(pathfmt, self.mapping[ext])

    def move(self, pathfmt):
        ext = pathfmt.extension
        if ext in self.mapping:
            # rebuild paths in case the filename extension changed
            path = self._build_paths(pathfmt, self.mapping[ext])
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def _build_paths(pathfmt, extra):
        path = pathfmt.realdirectory + extra
        pathfmt.realpath = path + os.sep + pathfmt.filename
        pathfmt.path = pathfmt.directory + extra + os.sep + pathfmt.filename
        return path


__postprocessor__ = ClassifyPP
