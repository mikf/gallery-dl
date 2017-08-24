# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of functions that work in strings/text"""

import sys
import re
import os.path
import html
import urllib.parse


INVALID_XML_CHARS = (1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 14, 15, 16, 17, 18,
                     19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)


def clean_xml(xmldata, repl=""):
    """Replace/Remove invalid control characters in XML data"""
    for char in INVALID_XML_CHARS:
        char = chr(char)
        if char in xmldata:
            xmldata = xmldata.replace(char, repl)
    return xmldata


def remove_html(text):
    """Remove html-tags from a string"""
    return " ".join(re.sub("<[^>]+?>", " ", text).split())


def filename_from_url(url):
    """Extract the last part of an url to use as a filename"""
    try:
        path = urllib.parse.urlparse(url).path
        pos = path.rindex("/")
        return path[pos+1:]
    except ValueError:
        return url


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
        return path


def clean_path_posix(path):
    """Remove illegal characters from a path-segment (Posix)"""
    try:
        return path.replace("/", "_")
    except AttributeError:
        return path


def shorten_path(path, limit=255, encoding=sys.getfilesystemencoding()):
    """Shorten a path segment to at most 'limit' bytes"""
    return (path.encode(encoding)[:limit]).decode(encoding, "ignore")


def shorten_filename(fname, limit=255, encoding=sys.getfilesystemencoding()):
    """Shorten filename to at most 'limit' bytes while preserving extension"""
    name, extension = os.path.splitext(fname)
    bext = extension.encode(encoding)
    bname = name.encode(encoding)[:limit-len(bext)]
    return bname.decode(encoding, "ignore") + extension


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
    except ValueError:
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


def parse_query(qs):
    """Parse a query string into key-value pairs"""
    return {key: vlist[0] for key, vlist in urllib.parse.parse_qs(qs).items()}


if os.name == "nt":
    clean_path = clean_path_windows
else:
    clean_path = clean_path_posix

unquote = urllib.parse.unquote
escape = html.escape

try:
    unescape = html.unescape
except AttributeError:
    import html.parser
    unescape = html.parser.HTMLParser().unescape
