# -*- coding: utf-8 -*-

# Copyright 2017-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Utility functions and classes"""

import re
import os
import sys
import json
import random
import sqlite3
import binascii
import datetime
import functools
import itertools
import urllib.parse
from http.cookiejar import Cookie
from . import text, exception


def bencode(num, alphabet="0123456789"):
    """Encode an integer into a base-N encoded string"""
    data = ""
    base = len(alphabet)
    while num:
        num, remainder = divmod(num, base)
        data = alphabet[remainder] + data
    return data


def bdecode(data, alphabet="0123456789"):
    """Decode a base-N encoded string ( N = len(alphabet) )"""
    num = 0
    base = len(alphabet)
    for c in data:
        num *= base
        num += alphabet.index(c)
    return num


def advance(iterable, num):
    """"Advance 'iterable' by 'num' steps"""
    iterator = iter(iterable)
    next(itertools.islice(iterator, num, num), None)
    return iterator


def unique(iterable):
    """Yield unique elements from 'iterable' while preserving order"""
    seen = set()
    add = seen.add
    for element in iterable:
        if element not in seen:
            add(element)
            yield element


def unique_sequence(iterable):
    """Yield sequentially unique elements from 'iterable'"""
    last = None
    for element in iterable:
        if element != last:
            last = element
            yield element


def raises(cls):
    """Returns a function that raises 'cls' as exception"""
    def wrap(*args):
        raise cls(*args)
    return wrap


def identity(x):
    """Returns its argument"""
    return x


def noop():
    """Does nothing"""


def generate_token(size=16):
    """Generate a random token with hexadecimal digits"""
    data = random.getrandbits(size * 8).to_bytes(size, "big")
    return binascii.hexlify(data).decode()


def format_value(value, suffixes="kMGTPEZY"):
    value = format(value)
    value_len = len(value)
    index = value_len - 4
    if index >= 0:
        offset = (value_len - 1) % 3 + 1
        return (value[:offset] + "." + value[offset:offset+2] +
                suffixes[index // 3])
    return value


def combine_dict(a, b):
    """Recursively combine the contents of 'b' into 'a'"""
    for key, value in b.items():
        if key in a and isinstance(value, dict) and isinstance(a[key], dict):
            combine_dict(a[key], value)
        else:
            a[key] = value
    return a


def transform_dict(a, func):
    """Recursively apply 'func' to all values in 'a'"""
    for key, value in a.items():
        if isinstance(value, dict):
            transform_dict(value, func)
        else:
            a[key] = func(value)


def filter_dict(a):
    """Return a copy of 'a' without "private" entries"""
    return {k: v for k, v in a.items() if k[0] != "_"}


def delete_items(obj, keys):
    """Remove all 'keys' from 'obj'"""
    for key in keys:
        if key in obj:
            del obj[key]


def enumerate_reversed(iterable, start=0, length=None):
    """Enumerate 'iterable' and return its elements in reverse order"""
    start -= 1
    if length is None:
        length = len(iterable)
    return zip(
        range(length - start, start, -1),
        reversed(iterable),
    )


def number_to_string(value, numbers=(int, float)):
    """Convert numbers (int, float) to string; Return everything else as is."""
    return str(value) if value.__class__ in numbers else value


def to_string(value):
    """str() with "better" defaults"""
    if not value:
        return ""
    if value.__class__ is list:
        try:
            return ", ".join(value)
        except Exception:
            return ", ".join(map(str, value))
    return str(value)


def to_timestamp(dt):
    """Convert naive datetime to UTC timestamp string"""
    try:
        return str((dt - EPOCH) // SECOND)
    except Exception:
        return ""


def dump_json(obj, fp=sys.stdout, ensure_ascii=True, indent=4):
    """Serialize 'obj' as JSON and write it to 'fp'"""
    json.dump(
        obj, fp,
        ensure_ascii=ensure_ascii,
        indent=indent,
        default=str,
        sort_keys=True,
    )
    fp.write("\n")


def dump_response(response, fp, *,
                  headers=False, content=True, hide_auth=True):
    """Write the contents of 'response' into a file-like object"""

    if headers:
        request = response.request
        req_headers = request.headers.copy()
        res_headers = response.headers.copy()
        outfmt = """\
{request.method} {request.url}
Status: {response.status_code} {response.reason}

Request Headers
---------------
{request_headers}

Response Headers
----------------
{response_headers}
"""
        if hide_auth:
            authorization = req_headers.get("Authorization")
            if authorization:
                atype, sep, _ = authorization.partition(" ")
                req_headers["Authorization"] = atype + " ***" if sep else "***"

            cookie = req_headers.get("Cookie")
            if cookie:
                req_headers["Cookie"] = ";".join(
                    c.partition("=")[0] + "=***"
                    for c in cookie.split(";")
                )

            set_cookie = res_headers.get("Set-Cookie")
            if set_cookie:
                res_headers["Set-Cookie"] = re.sub(
                    r"(^|, )([^ =]+)=[^,;]*", r"\1\2=***", set_cookie,
                )

        fp.write(outfmt.format(
            request=request,
            response=response,
            request_headers="\n".join(
                name + ": " + value
                for name, value in req_headers.items()
            ),
            response_headers="\n".join(
                name + ": " + value
                for name, value in res_headers.items()
            ),
        ).encode())

    if content:
        if headers:
            fp.write(b"\nContent\n-------\n")
        fp.write(response.content)


def expand_path(path):
    """Expand environment variables and tildes (~)"""
    if not path:
        return path
    if not isinstance(path, str):
        path = os.path.join(*path)
    return os.path.expandvars(os.path.expanduser(path))


def remove_file(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def remove_directory(path):
    try:
        os.rmdir(path)
    except OSError:
        pass


def load_cookiestxt(fp):
    """Parse a Netscape cookies.txt file and return a list of its Cookies"""
    cookies = []

    for line in fp:

        line = line.lstrip()
        # strip '#HttpOnly_'
        if line.startswith("#HttpOnly_"):
            line = line[10:]
        # ignore empty lines and comments
        if not line or line[0] in ("#", "$"):
            continue
        # strip trailing '\n'
        if line[-1] == "\n":
            line = line[:-1]

        domain, domain_specified, path, secure, expires, name, value = \
            line.split("\t")
        if not name:
            name = value
            value = None

        cookies.append(Cookie(
            0, name, value,
            None, False,
            domain,
            domain_specified == "TRUE",
            domain.startswith("."),
            path, False,
            secure == "TRUE",
            None if expires == "0" or not expires else expires,
            False, None, None, {},
        ))

    return cookies


def save_cookiestxt(fp, cookies):
    """Write 'cookies' in Netscape cookies.txt format to 'fp'"""
    fp.write("# Netscape HTTP Cookie File\n\n")

    for cookie in cookies:
        if cookie.value is None:
            name = ""
            value = cookie.name
        else:
            name = cookie.name
            value = cookie.value

        fp.write("\t".join((
            cookie.domain,
            "TRUE" if cookie.domain.startswith(".") else "FALSE",
            cookie.path,
            "TRUE" if cookie.secure else "FALSE",
            "0" if cookie.expires is None else str(cookie.expires),
            name,
            value,
        )) + "\n")


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
    "bg": "Bulgarian",
    "ca": "Catalan",
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
    "ja": "Japanese",
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


class UniversalNone():
    """None-style object that supports more operations than None itself"""
    __slots__ = ()

    def __getattribute__(self, _):
        return self

    def __getitem__(self, _):
        return self

    @staticmethod
    def __bool__():
        return False

    @staticmethod
    def __str__():
        return "None"

    __repr__ = __str__


NONE = UniversalNone()
EPOCH = datetime.datetime(1970, 1, 1)
SECOND = datetime.timedelta(0, 1)
WINDOWS = (os.name == "nt")
SENTINEL = object()
SPECIAL_EXTRACTORS = {"oauth", "recursive", "test"}
GLOBALS = {
    "parse_int": text.parse_int,
    "urlsplit" : urllib.parse.urlsplit,
    "datetime" : datetime.datetime,
    "abort"    : raises(exception.StopExtraction),
    "terminate": raises(exception.TerminateExtraction),
    "re"       : re,
}


def compile_expression(expr, name="<expr>", globals=GLOBALS):
    code_object = compile(expr, name, "eval")
    return functools.partial(eval, code_object, globals)


def build_duration_func(duration, min=0.0):
    if not duration:
        return None

    try:
        lower, upper = duration
    except TypeError:
        pass
    else:
        return functools.partial(
            random.uniform,
            lower if lower > min else min,
            upper if upper > min else min,
        )

    return functools.partial(identity, duration if duration > min else min)


def build_predicate(predicates):
    if not predicates:
        return lambda url, kwdict: True
    elif len(predicates) == 1:
        return predicates[0]
    return functools.partial(chain_predicates, predicates)


def chain_predicates(predicates, url, kwdict):
    for pred in predicates:
        if not pred(url, kwdict):
            return False
    return True


class RangePredicate():
    """Predicate; True if the current index is in the given range"""
    def __init__(self, rangespec):
        self.ranges = self.optimize_range(self.parse_range(rangespec))
        self.index = 0

        if self.ranges:
            self.lower, self.upper = self.ranges[0][0], self.ranges[-1][1]
        else:
            self.lower, self.upper = 0, 0

    def __call__(self, url, _):
        self.index += 1

        if self.index > self.upper:
            raise exception.StopExtraction()

        for lower, upper in self.ranges:
            if lower <= self.index <= upper:
                return True
        return False

    @staticmethod
    def parse_range(rangespec):
        """Parse an integer range string and return the resulting ranges

        Examples:
            parse_range("-2,4,6-8,10-") -> [(1,2), (4,4), (6,8), (10,INTMAX)]
            parse_range(" - 3 , 4-  4, 2-6") -> [(1,3), (4,4), (2,6)]
        """
        ranges = []

        for group in rangespec.split(","):
            if not group:
                continue
            first, sep, last = group.partition("-")
            if not sep:
                beg = end = int(first)
            else:
                beg = int(first) if first.strip() else 1
                end = int(last) if last.strip() else sys.maxsize
            ranges.append((beg, end) if beg <= end else (end, beg))

        return ranges

    @staticmethod
    def optimize_range(ranges):
        """Simplify/Combine a parsed list of ranges

        Examples:
            optimize_range([(2,4), (4,6), (5,8)]) -> [(2,8)]
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


class UniquePredicate():
    """Predicate; True if given URL has not been encountered before"""
    def __init__(self):
        self.urls = set()

    def __call__(self, url, _):
        if url.startswith("text:"):
            return True
        if url not in self.urls:
            self.urls.add(url)
            return True
        return False


class FilterPredicate():
    """Predicate; True if evaluating the given expression returns True"""

    def __init__(self, expr, target="image"):
        name = "<{} filter>".format(target)
        self.expr = compile_expression(expr, name)

    def __call__(self, _, kwdict):
        try:
            return self.expr(kwdict)
        except exception.GalleryDLException:
            raise
        except Exception as exc:
            raise exception.FilterError(exc)


class ExtendedUrl():
    """URL with attached config key-value pairs"""
    def __init__(self, url, gconf, lconf):
        self.value, self.gconfig, self.lconfig = url, gconf, lconf

    def __str__(self):
        return self.value


class DownloadArchive():

    def __init__(self, path, extractor):
        con = sqlite3.connect(path, timeout=60, check_same_thread=False)
        con.isolation_level = None
        self.close = con.close
        self.cursor = con.cursor()

        try:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS archive "
                                "(entry PRIMARY KEY) WITHOUT ROWID")
        except sqlite3.OperationalError:
            # fallback for missing WITHOUT ROWID support (#553)
            self.cursor.execute("CREATE TABLE IF NOT EXISTS archive "
                                "(entry PRIMARY KEY)")
        self.keygen = (
            extractor.config("archive-prefix", extractor.category) +
            extractor.config("archive-format", extractor.archive_fmt)
        ).format_map

    def check(self, kwdict):
        """Return True if the item described by 'kwdict' exists in archive"""
        key = kwdict["_archive_key"] = self.keygen(kwdict)
        self.cursor.execute(
            "SELECT 1 FROM archive WHERE entry=? LIMIT 1", (key,))
        return self.cursor.fetchone()

    def add(self, kwdict):
        """Add item described by 'kwdict' to archive"""
        key = kwdict.get("_archive_key") or self.keygen(kwdict)
        self.cursor.execute(
            "INSERT OR IGNORE INTO archive VALUES (?)", (key,))
