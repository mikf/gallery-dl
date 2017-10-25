# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions and classes"""

import re
import os
import sys
import hmac
import time
import base64
import random
import shutil
import string
import _string
import hashlib
import datetime
import urllib.parse
from . import text, exception


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
        optimize_range([(1,1), (2,2), (3,6), (8,9))]) -> [(1,6), (8,9)]
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


def bdecode(data, alphabet="0123456789"):
    """Decode a base-N encoded string ( N = len(alphabet) )"""
    num = 0
    base = len(alphabet)
    for c in data:
        num *= base
        num += alphabet.index(c)
    return num


def combine_dict(a, b):
    """Recursively combine the contents of b into a"""
    for key, value in b.items():
        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
        else:
            a[key] = value
    return a


def safe_int(value, default=0):
    """Safely convert value to integer"""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def expand_path(path):
    """Expand environment variables and tildes (~)"""
    if not path:
        return path
    return os.path.expandvars(os.path.expanduser(path))


def code_to_language(code, default=None):
    """Map an ISO 639-1 language code to its actual name"""
    return CODES.get((code or "").lower(), default)


def language_to_code(lang, default=None):
    """Map a language name to its ISO 639-1 code"""
    if lang is None:
        return default
    lang = lang.capitalize()
    for code, language in CODES.items():
        if language == lang:
            return code
    return default


CODES = {
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

SPECIAL_EXTRACTORS = ("oauth", "recursive", "test")


def build_predicate(predicates):
    if not predicates:
        return lambda url, kwds: True
    elif len(predicates) == 1:
        return predicates[0]
    else:
        return ChainPredicate(predicates)


class RangePredicate():
    """Predicate; True if the current index is in the given range"""
    def __init__(self, ranges):
        self.ranges = ranges
        self.index = 0
        if self.ranges:
            self.lower, self.upper = self.ranges[0][0], self.ranges[-1][1]
        else:
            self.lower, self.upper = 0, 0

    def __call__(self, url, kwds):
        self.index += 1

        if self.index > self.upper:
            raise exception.StopExtraction()

        for lower, upper in self.ranges:
            if lower <= self.index <= upper:
                return True
        return False


class UniquePredicate():
    """Predicate; True if given URL has not been encountered before"""
    def __init__(self):
        self.urls = set()

    def __call__(self, url, kwds):
        if url not in self.urls:
            self.urls.add(url)
            return True
        return False


class FilterPredicate():
    """Predicate; True if evaluating the given expression returns True"""
    globalsdict = {
        "safe_int": safe_int,
        "urlsplit": urllib.parse.urlsplit,
        "datetime": datetime.datetime,
        "re": re,
    }

    def __init__(self, codeobj):
        self.codeobj = codeobj

    def __call__(self, url, kwds):
        try:
            return eval(self.codeobj, self.globalsdict, kwds)
        except Exception as exc:
            raise exception.FilterError(exc)


class ChainPredicate():
    """Predicate; True if all of its predicates return True"""
    def __init__(self, predicates):
        self.predicates = predicates

    def __call__(self, url, kwds):
        for pred in self.predicates:
            if not pred(url, kwds):
                return False
        return True


class Formatter():
    """Custom, trimmed-down version of string.Formatter

    This string formatter implementation is a mostly performance-optimized
    variant of the original string.Formatter class. Unnecessary features have
    been removed (positional arguments, unused argument check) and new
    formatting options have been added.

    Extra Conversions:
    - "l": calls str.lower on the target value
    - "u": calls str.upper
    - "c": calls str.capitalize
    - "C": calls string.capwords
    - Example: {f!l} -> "example"; {f!u} -> "EXAMPLE"

    Extra Format Specifiers:
    - "?<before>/<after>/":
        Adds <before> and <after> to the actual value if it evaluates to True.
        Otherwise the whole replacement field becomes an empty string.
        Example: {f:?-+/+-/} -> "-+Example+-" (if "f" contains "Example")
                             -> ""            (if "f" is None, 0, "")
    """
    conversions = {
        "l": str.lower,
        "u": str.upper,
        "c": str.capitalize,
        "C": string.capwords,
        "s": str,
        "r": repr,
        "a": ascii,
    }

    def vformat(self, format_string, kwargs):
        """Apply 'kwargs' to the initial format_string and return its result"""
        result = []
        append = result.append

        for literal_text, field_name, format_spec, conversion in \
                _string.formatter_parser(format_string):

            if literal_text:
                append(literal_text)

            if field_name:
                obj = self.get_field(field_name, kwargs)
                if conversion:
                    obj = self.conversions[conversion](obj)
                if format_spec:
                    format_spec = format_spec.format_map(kwargs)
                    obj = self.format_field(obj, format_spec)
                else:
                    obj = str(obj)
                append(obj)

        return "".join(result)

    @staticmethod
    def format_field(value, format_spec):
        """Format 'value' according to 'format_spec'"""
        if format_spec[0] == "?":
            if not value:
                return ""
            before, after, format_spec = format_spec.split("/", 2)
            return before[1:] + format(value, format_spec) + after
        return format(value, format_spec)

    @staticmethod
    def get_field(field_name, kwargs):
        """Return value called 'field_name' from 'kwargs'"""
        first, rest = _string.formatter_field_name_split(field_name)

        obj = kwargs[first]
        for is_attr, i in rest:
            if is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj[i]

        return obj


class PathFormat():

    def __init__(self, extractor):
        self.filename_fmt = extractor.config(
            "filename", extractor.filename_fmt)
        self.directory_fmt = extractor.config(
            "directory", extractor.directory_fmt)
        self.formatter = Formatter()

        self.has_extension = False
        self.keywords = {}
        self.directory = self.realdirectory = ""
        self.path = self.realpath = self.partpath = ""

        bdir = extractor.config("base-directory", (".", "gallery-dl"))
        if not isinstance(bdir, str):
            bdir = os.path.join(*bdir)
        self.basedirectory = expand_path(bdir)

        skipmode = extractor.config("skip", True)
        if skipmode == "abort":
            self.exists = self._exists_abort
        elif skipmode == "exit":
            self.exists = self._exists_exit
        elif not skipmode:
            self.exists = lambda: False

    def open(self, mode="wb"):
        """Open file and return a corresponding file object"""
        return open(self.partpath or self.realpath, mode)

    def exists(self):
        """Return True if 'path' is complete and refers to an existing path"""
        if self.has_extension:
            return os.path.exists(self.realpath)
        return False

    def set_directory(self, keywords):
        """Build directory path and create it if necessary"""
        try:
            segments = [
                text.clean_path(
                    self.formatter.vformat(segment, keywords).strip())
                for segment in self.directory_fmt
            ]
        except Exception as exc:
            raise exception.FormatError(exc, "directory")

        self.directory = os.path.join(
            self.basedirectory,
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

    def set_extension(self, extension, real=True):
        """Set the 'extension' keyword"""
        self.has_extension = real
        self.keywords["extension"] = extension
        self.build_path()

    def build_path(self, sep=os.path.sep):
        """Use filename-keywords and directory to build a full path"""
        try:
            filename = text.clean_path(
                self.formatter.vformat(self.filename_fmt, self.keywords))
        except Exception as exc:
            raise exception.FormatError(exc, "filename")

        filename = sep + filename
        self.path = self.directory + filename
        self.realpath = self.realdirectory + filename

    def part_enable(self, part_directory=None):
        """Enable .part file usage"""
        if self.has_extension:
            self.partpath = self.realpath + ".part"
        else:
            self.set_extension("part", False)
            self.partpath = self.realpath
        if part_directory:
            self.partpath = os.path.join(
                part_directory,
                os.path.basename(self.partpath),
            )

    def part_size(self):
        """Return size of .part file"""
        if self.partpath:
            try:
                return os.stat(self.partpath).st_size
            except OSError:
                pass
        return 0

    def part_move(self):
        """Rename .part file to its actual filename"""
        try:
            os.rename(self.partpath, self.realpath)
            return
        except OSError:
            pass
        shutil.copyfile(self.partpath, self.realpath)
        os.unlink(self.partpath)

    def _exists_abort(self):
        if self.has_extension and os.path.exists(self.realpath):
            raise exception.StopExtraction()
        return False

    def _exists_exit(self):
        if self.has_extension and os.path.exists(self.realpath):
            exit()
        return False

    @staticmethod
    def adjust_path(path):
        """Enable longer-than-260-character paths on windows"""
        return "\\\\?\\" + os.path.abspath(path) if os.name == "nt" else path


class OAuthSession():
    """Minimal wrapper for requests.session objects to support OAuth 1.0"""
    def __init__(self, session, consumer_key, consumer_secret,
                 token=None, token_secret=None):
        self.session = session
        self.consumer_secret = consumer_secret
        self.token_secret = token_secret or ""
        self.params = {}
        self.params["oauth_consumer_key"] = consumer_key
        self.params["oauth_token"] = token
        self.params["oauth_signature_method"] = "HMAC-SHA1"
        self.params["oauth_version"] = "1.0"

    def get(self, url, params):
        params.update(self.params)
        params["oauth_nonce"] = self.nonce(16)
        params["oauth_timestamp"] = int(time.time())
        params["oauth_signature"] = self.signature(url, params)
        return self.session.get(url, params=params)

    def signature(self, url, params):
        """Generate 'oauth_signature' value"""
        query = urllib.parse.urlencode(sorted(params.items()))
        message = self.concat("GET", url, query).encode()
        key = self.concat(self.consumer_secret, self.token_secret).encode()
        signature = hmac.new(key, message, hashlib.sha1).digest()
        return base64.b64encode(signature).decode()

    @staticmethod
    def concat(*args):
        return "&".join(urllib.parse.quote(item, "") for item in args)

    @staticmethod
    def nonce(N, alphabet=string.ascii_letters):
        return "".join(random.choice(alphabet) for _ in range(N))
