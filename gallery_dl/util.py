# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions and classes"""

import os
import sys
from . import config, text, exception


def parse_range(rangespec):
    """Parse an integer range string and return the resulting ranges

    Examples
        parse_range("-2,4,6-8,10-")      -> [(1,2), (4,4), (6,8), (10,INTMAX)]
        parse_range(" - 3 , 4-  4, 2-6") -> [(1,3), (4,4), (2,6)]
    """
    ranges = []

    for group in rangespec.split(","):
        parts = group.split("-", maxsplit=1)
        try:
            if len(parts) == 1:
                beg = int(parts[0])
                end = beg
            else:
                beg = int(parts[0]) if parts[0].strip() else 1
                end = int(parts[1]) if parts[1].strip() else sys.maxsize
            ranges.append((beg, end) if beg <= end else (end, beg))
        except ValueError:
            pass

    return ranges


def optimize_range(ranges):
    """Simplify/Combine a parsed list of ranges

    Examples
        optimize_range([(2,4), (4,6), (5,8)])         -> [(2,8)]
        optimize_range([(1,1), (2,2), (3,6), (8,9))]) -> [(1,6), (8-9)]
    """
    if len(ranges) <= 1:
        return ranges

    ranges.sort()
    riter = iter(ranges)
    result = []

    beg, end = next(riter)
    for lower, upper in riter:
        if lower > end+1:
            result.append((beg, end))
            beg, end = lower, upper
        elif upper > end:
            end = upper
    result.append((beg, end))
    return result


def code_to_language(code, default="English"):
    """Map an ISO 639-1 language code to its actual name"""
    return codes.get(code.lower(), default)


def language_to_code(lang, default="en"):
    """Map a language name to its ISO 639-1 code"""
    lang = lang.capitalize()
    for code, language in codes.items():
        if language == lang:
            return code
    return default


codes = {
    "ar": "Arabic",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "jp": "Japanese",
    "ko": "Korean",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "zh": "Chinese",
}


class RangePredicate():
    """Predicate; is True if the current index is in the given range"""
    def __init__(self, rangespec):
        self.ranges = optimize_range(parse_range(rangespec))
        self.index = 0
        if self.ranges:
            self.lower, self.upper = self.ranges[0][0], self.ranges[-1][1]
        else:
            self.lower, self.upper = 0, 0

    def __bool__(self):
        self.index += 1

        if self.index > self.upper:
            raise exception.StopExtraction()

        for lower, upper in self.ranges:
            if lower <= self.index <= upper:
                return True
        return False


class PathFormat():

    def __init__(self, extractor):
        key = ["extractor", extractor.category]
        if extractor.subcategory:
            key.append(extractor.subcategory)
        self.filename_fmt = config.interpolate(
            key + ["filename"], default=extractor.filename_fmt
        )
        self.directory_fmt = config.interpolate(
            key + ["directory"], default=extractor.directory_fmt
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
