# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Collection of functions that work in strings/text"""

import re
import html.parser
import urllib.parse
import platform

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

def extract(txt, begin, end, pos=0):
    try:
        first = txt.index(begin, pos) + len(begin)
        last = txt.index(end, first)
        return txt[first:last], last+len(end)
    except ValueError:
        return None, pos

def extract_all(txt, begin, end, pos=0):
    try:
        first = txt.index(begin, pos)
        last = txt.index(end, first + len(begin)) + len(end)
        return txt[first:last], last
    except ValueError:
        return None, pos

if platform.system() == "Windows":
    clean_path = clean_path_windows
else:
    clean_path = clean_path_posix

unquote = urllib.parse.unquote

unescape = html.parser.HTMLParser().unescape
