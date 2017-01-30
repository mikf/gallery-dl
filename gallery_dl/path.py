# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
from . import config, text


class PathFormat():

    def __init__(self, extractor):
        key = ["extractor", extractor.category]
        if extractor.subcategory:
            key.append(extractor.subcategory)
        self.filename_fmt = config.interpolate(
            key + ["filename_fmt"], default=extractor.filename_fmt
        )
        self.directory_fmt = config.interpolate(
            key + ["directory_fmt"], default=extractor.directory_fmt
        )
        self.has_extension = False
        self.keywords = {}
        self.directory = self.realdirectory = ""
        self.path = self.realpath = ""

    def open(self):
        """Open file ta 'realpath' and return a corresponding file object"""
        return open(self.realpath, "wb")

    def exists(self):
        """Return True if 'path' is complete and referse to an existing path"""
        if self.has_extension:
            return os.path.exists(self.realpath)
        return False

    def set_directory(self, keywords):
        """Build directory path and create it if necessary"""
        segments = [
            text.clean_path(segment.format_map(keywords).strip())
            for segment in self.directory_fmt
        ]
        self.directory = os.path.join(
            self.get_base_directory(),
            *segments
        )
        self.realdirectory = self.adjust_path(self.directory)
        os.makedirs(self.realdirectory, exist_ok=True)

    def set_keywords(self, keywords):
        """Set filename keywords"""
        self.keywords = keywords
        self.has_extension = bool(keywords.get("extension"))
        if self.has_extension:
            self.build_path()

    def set_extension(self, extension):
        """Set the 'extension' keyword"""
        self.has_extension = True
        self.keywords["extension"] = extension
        self.build_path()

    def build_path(self, sep=os.path.sep):
        """Use filename-keywords and directory to build a full path"""
        filename = text.clean_path(self.filename_fmt.format_map(self.keywords))
        self.path = self.directory + sep + filename
        self.realpath = self.realdirectory + sep + filename

    @staticmethod
    def get_base_directory():
        """Return the base-destination-directory for downloads"""
        bdir = config.get(("base-directory",), default=(".", "gallery-dl"))
        if not isinstance(bdir, str):
            bdir = os.path.join(*bdir)
        return os.path.expanduser(os.path.expandvars(bdir))

    @staticmethod
    def adjust_path(path):
        """Enable longer-than-260-character paths on windows"""
        return "\\\\?\\" + os.path.abspath(path) if os.name == "nt" else path
