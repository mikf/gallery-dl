# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of functions that work in strings/text"""

import re
import html
import os.path
import urllib.parse


INVALID_XML_CHARS = (
    "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07",
    "\x08", "\x0b", "\x0c", "\x0e", "\x0f", "\x10", "\x11", "\x12",
    "\x13", "\x14", "\x15", "\x16", "\x17", "\x18", "\x19", "\x1a",
    "\x1b", "\x1c", "\x1d", "\x1e", "\x1f",
)


def clean_xml(xmldata, repl=""):
    """Replace/Remove invalid control characters in 'xmldata'"""
    if not isinstance(xmldata, str):
        try:
            xmldata = "".join(xmldata)
        except TypeError:
            return ""
    for char in INVALID_XML_CHARS:
        if char in xmldata:
            xmldata = xmldata.replace(char, repl)
    return xmldata


def remove_html(txt):
    """Remove html-tags from a string"""
    try:
        return " ".join(re.sub("<[^>]+>", " ", txt).split())
    except TypeError:
        return ""


def split_html(txt, sep=None):
    """Split input string by html-tags"""
    try:
        return [
            x for x in re.split("<[^>]+>", txt)
            if x and not x.isspace()
        ]
    except TypeError:
        return []


def filename_from_url(url):
    """Extract the last part of an url to use as a filename"""
    try:
        return urllib.parse.urlsplit(url).path.rpartition("/")[2]
    except (TypeError, AttributeError):
        return ""


def nameext_from_url(url, data=None):
    """Extract the last part of an url and fill 'data' accordingly"""
    if data is None:
        data = {}
    data["filename"] = unquote(filename_from_url(url))
    data["name"], ext = os.path.splitext(data["filename"])
    data["extension"] = ext[1:].lower()
    return data


def clean_path_windows(path):
    """Remove illegal characters from a path-segment (Windows)"""
    try:
        return re.sub(r'[<>:"\\/|?*]', "_", path)
    except TypeError:
        return ""


def clean_path_posix(path):
    """Remove illegal characters from a path-segment (Posix)"""
    try:
        return path.replace("/", "_")
    except AttributeError:
        return ""


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
    """Yield all values obtained by repeated calls to text.extract"""
    while True:
        value, pos = extract(txt, begin, end, pos)
        if value is None:
            return
        yield value


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


if os.name == "nt":
    clean_path = clean_path_windows
else:
    clean_path = clean_path_posix

urljoin = urllib.parse.urljoin
unquote = urllib.parse.unquote
escape = html.escape

try:
    unescape = html.unescape
except AttributeError:
    import html.parser
    unescape = html.parser.HTMLParser().unescape
