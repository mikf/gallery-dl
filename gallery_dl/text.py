# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of functions that work on strings/text"""

import re
import html
import datetime
import urllib.parse

HTML_RE = re.compile("<[^>]+>")


def remove_html(txt, repl=" ", sep=" "):
    """Remove html-tags from a string"""
    try:
        txt = HTML_RE.sub(repl, txt)
    except TypeError:
        return ""
    if sep:
        return sep.join(txt.split())
    return txt.strip()


def split_html(txt):
    """Split input string by HTML tags"""
    try:
        return [
            unescape(x).strip()
            for x in HTML_RE.split(txt)
            if x and not x.isspace()
        ]
    except TypeError:
        return []


def ensure_http_scheme(url, scheme="https://"):
    """Prepend 'scheme' to 'url' if it doesn't have one"""
    if url and not url.startswith(("https://", "http://")):
        return scheme + url.lstrip("/:")
    return url


def filename_from_url(url):
    """Extract the last part of an URL to use as a filename"""
    try:
        return url.partition("?")[0].rpartition("/")[2]
    except (TypeError, AttributeError):
        return ""


def ext_from_url(url):
    """Extract the filename extension of an URL"""
    name, _, ext = filename_from_url(url).rpartition(".")
    return ext.lower() if name else ""


def nameext_from_url(url, data=None):
    """Extract the last part of an URL and fill 'data' accordingly"""
    if data is None:
        data = {}

    filename = unquote(filename_from_url(url))
    name, _, ext = filename.rpartition(".")
    if name and len(ext) <= 16:
        data["filename"], data["extension"] = name, ext.lower()
    else:
        data["filename"], data["extension"] = filename, ""

    return data


def extract(txt, begin, end, pos=0):
    """Extract the text between 'begin' and 'end' from 'txt'

    Args:
        txt: String to search in
        begin: First string to be searched for
        end: Second string to be searched for after 'begin'
        pos: Starting position for searches in 'txt'

    Returns:
        The string between the two search-strings 'begin' and 'end' beginning
        with position 'pos' in 'txt' as well as the position after 'end'.

        If at least one of 'begin' or 'end' is not found, None and the original
        value of 'pos' is returned

    Examples:
        extract("abcde", "b", "d")    -> "c" , 4
        extract("abcde", "b", "d", 3) -> None, 3
    """
    try:
        first = txt.index(begin, pos) + len(begin)
        last = txt.index(end, first)
        return txt[first:last], last+len(end)
    except (ValueError, TypeError, AttributeError):
        return None, pos


def rextract(txt, begin, end, pos=-1):
    try:
        lbeg = len(begin)
        first = txt.rindex(begin, 0, pos)
        last = txt.index(end, first + lbeg)
        return txt[first + lbeg:last], first
    except (ValueError, TypeError, AttributeError):
        return None, pos


def extract_all(txt, rules, pos=0, values=None):
    """Calls extract for each rule and returns the result in a dict"""
    if values is None:
        values = {}
    for key, begin, end in rules:
        result, pos = extract(txt, begin, end, pos)
        if key:
            values[key] = result
    return values, pos


def extract_iter(txt, begin, end, pos=0):
    """Yield values that would be returned by repeated calls of extract()"""
    index = txt.index
    lbeg = len(begin)
    lend = len(end)
    try:
        while True:
            first = index(begin, pos) + lbeg
            last = index(end, first)
            pos = last + lend
            yield txt[first:last]
    except (ValueError, TypeError, AttributeError):
        return


def extract_from(txt, pos=0, default=""):
    """Returns a function object that extracts from 'txt'"""
    def extr(begin, end, index=txt.index, txt=txt):
        nonlocal pos
        try:
            first = index(begin, pos) + len(begin)
            last = index(end, first)
            pos = last + len(end)
            return txt[first:last]
        except (ValueError, TypeError, AttributeError):
            return default
    return extr


def parse_unicode_escapes(txt):
    """Convert JSON Unicode escapes in 'txt' into actual characters"""
    if "\\u" in txt:
        return re.sub(r"\\u([0-9a-fA-F]{4})", _hex_to_char, txt)
    return txt


def _hex_to_char(match):
    return chr(int(match.group(1), 16))


def parse_bytes(value, default=0, suffixes="bkmgtp"):
    """Convert a bytes-amount ("500k", "2.5M", ...) to int"""
    try:
        last = value[-1].lower()
    except (TypeError, KeyError, IndexError):
        return default

    if last in suffixes:
        mul = 1024 ** suffixes.index(last)
        value = value[:-1]
    else:
        mul = 1

    try:
        return round(float(value) * mul)
    except ValueError:
        return default


def parse_int(value, default=0):
    """Convert 'value' to int"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_float(value, default=0.0):
    """Convert 'value' to float"""
    if not value:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_query(qs):
    """Parse a query string into key-value pairs"""
    result = {}
    try:
        for key, value in urllib.parse.parse_qsl(qs):
            if key not in result:
                result[key] = value
    except AttributeError:
        pass
    return result


def parse_timestamp(ts, default=None):
    """Create a datetime object from a unix timestamp"""
    try:
        return datetime.datetime.utcfromtimestamp(int(ts))
    except (TypeError, ValueError, OverflowError):
        return default


def parse_datetime(date_string, format="%Y-%m-%dT%H:%M:%S%z", utcoffset=0):
    """Create a datetime object by parsing 'date_string'"""
    try:
        if format.endswith("%z") and date_string[-3] == ":":
            # workaround for Python < 3.7: +00:00 -> +0000
            ds = date_string[:-3] + date_string[-2:]
        else:
            ds = date_string
        d = datetime.datetime.strptime(ds, format)
        o = d.utcoffset()
        if o is not None:
            # convert to naive UTC
            d = d.replace(tzinfo=None, microsecond=0) - o
        else:
            if d.microsecond:
                d = d.replace(microsecond=0)
            if utcoffset:
                # apply manual UTC offset
                d += datetime.timedelta(0, utcoffset * -3600)
        return d
    except (TypeError, IndexError, KeyError):
        return None
    except (ValueError, OverflowError):
        return date_string


urljoin = urllib.parse.urljoin

quote = urllib.parse.quote
unquote = urllib.parse.unquote

escape = html.escape
unescape = html.unescape
