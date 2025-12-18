# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Filesystem path handling"""

import os
import shutil
import functools
from . import util, formatter, exception

WINDOWS = util.WINDOWS
EXTENSION_MAP = {
    "jpeg": "jpg",
    "jpe" : "jpg",
    "jfif": "jpg",
    "jif" : "jpg",
    "jfi" : "jpg",
}


class PathFormat():

    def __init__(self, extractor):
        config = extractor.config
        kwdefault = config("keywords-default")
        if kwdefault is None:
            kwdefault = util.NONE

        self.filename_conditions = self.directory_conditions = None

        filename_fmt = config("filename")
        try:
            if filename_fmt is None:
                filename_fmt = extractor.filename_fmt
            elif isinstance(filename_fmt, dict):
                self.filename_conditions = [
                    (util.compile_filter(expr),
                     formatter.parse(fmt, kwdefault).format_map)
                    for expr, fmt in filename_fmt.items() if expr
                ]
                filename_fmt = filename_fmt.get("", extractor.filename_fmt)

            self.filename_formatter = formatter.parse(
                filename_fmt, kwdefault).format_map
        except Exception as exc:
            raise exception.FilenameFormatError(exc)

        directory_fmt = config("directory")
        try:
            if directory_fmt is None:
                directory_fmt = extractor.directory_fmt
            elif isinstance(directory_fmt, dict):
                self.directory_conditions = [
                    (util.compile_filter(expr), [
                        formatter.parse(fmt, kwdefault).format_map
                        for fmt in fmts
                    ])
                    for expr, fmts in directory_fmt.items() if expr
                ]
                directory_fmt = directory_fmt.get("", extractor.directory_fmt)

            self.directory_formatters = [
                formatter.parse(dirfmt, kwdefault).format_map
                for dirfmt in directory_fmt
            ]
        except Exception as exc:
            raise exception.DirectoryFormatError(exc)

        self.kwdict = {}
        self.delete = False
        self.prefix = ""
        self.filename = ""
        self.extension = ""
        self.directory = ""
        self.realdirectory = ""
        self.path = ""
        self.realpath = ""
        self.temppath = ""

        extension_map = config("extension-map")
        if extension_map is None:
            extension_map = EXTENSION_MAP
        self.extension_map = extension_map.get

        restrict = config("path-restrict", "auto")
        replace = config("path-replace", "_")
        conv = config("path-convert")
        if restrict == "auto":
            restrict = "\\\\|/<>:\"?*" if WINDOWS else "/"
        elif restrict == "unix":
            restrict = "/"
        elif restrict == "windows":
            restrict = "\\\\|/<>:\"?*"
        elif restrict == "ascii":
            restrict = "^0-9A-Za-z_."
        elif restrict == "ascii+":
            restrict = "^0-9@-[\\]-{ #-)+-.;=!}~"
        self.clean_segment = _build_cleanfunc(restrict, replace, conv)

        remove = config("path-remove", "\x00-\x1f\x7f")
        self.clean_path = _build_cleanfunc(remove, "")

        strip = config("path-strip", "auto")
        if strip == "auto":
            strip = ". " if WINDOWS else ""
        elif strip == "unix":
            strip = ""
        elif strip == "windows":
            strip = ". "
        self.strip = strip

        if WINDOWS:
            self.extended = config("path-extended", True)

        self.basedirectory_conditions = None
        basedir = extractor._parentdir
        if not basedir:
            basedir = config("base-directory")
            if basedir is None:
                basedir = self.clean_path(f".{os.sep}gallery-dl{os.sep}")
            elif basedir:
                if isinstance(basedir, dict):
                    self.basedirectory_conditions = conds = []
                    for expr, bdir in basedir.items():
                        if not expr:
                            basedir = bdir
                            continue
                        conds.append((util.compile_filter(expr),
                                      self._prepare_basedirectory(bdir)))
                basedir = self._prepare_basedirectory(basedir)
        self.basedirectory = basedir

    def _prepare_basedirectory(self, basedir):
        basedir = util.expand_path(basedir)
        if os.altsep and os.altsep in basedir:
            basedir = basedir.replace(os.altsep, os.sep)
        if basedir[-1] != os.sep:
            basedir += os.sep
        return self.clean_path(basedir)

    def __str__(self):
        return self.realpath

    def open(self, mode="wb"):
        """Open file and return a corresponding file object"""
        try:
            return open(self.temppath, mode)
        except FileNotFoundError:
            if "r" in mode:
                # '.part' file no longer exists
                return util.NullContext()
            os.makedirs(self.realdirectory)
            return open(self.temppath, mode)

    def exists(self):
        """Return True if the file exists on disk"""
        if self.extension:
            try:
                os.lstat(self.realpath)  # raises OSError if file doesn't exist
                return self.check_file()
            except OSError:
                pass
        return False

    def check_file(self):
        return True

    def _enum_file(self):
        num = 1
        try:
            while True:
                prefix = format(num) + "."
                self.kwdict["extension"] = prefix + self.extension
                self.build_path()
                os.lstat(self.realpath)  # raises OSError if file doesn't exist
                num += 1
        except OSError:
            pass
        self.prefix = prefix
        return False

    def set_directory(self, kwdict):
        """Build directory path and create it if necessary"""
        self.kwdict = kwdict

        if self.basedirectory_conditions is None:
            basedir = self.basedirectory
        else:
            for condition, basedir in self.basedirectory_conditions:
                if condition(kwdict):
                    break
            else:
                basedir = self.basedirectory

        if segments := self.build_directory(kwdict):
            self.directory = directory = \
                f"{basedir}{self.clean_path(os.sep.join(segments))}{os.sep}"
        else:
            self.directory = directory = basedir

        if WINDOWS and self.extended:
            directory = self._extended_path(directory)
        self.realdirectory = directory

    def _extended_path(self, path):
        # Enable longer-than-260-character paths
        path = os.path.abspath(path)
        if not path.startswith("\\\\"):
            path = "\\\\?\\" + path
        elif not path.startswith("\\\\?\\"):
            path = "\\\\?\\UNC\\" + path[2:]

        # abspath() in Python 3.7+ removes trailing path separators (#402)
        if path[-1] != os.sep:
            return path + os.sep
        return path

    def set_filename(self, kwdict):
        """Set general filename data"""
        self.kwdict = kwdict
        self.filename = self.temppath = self.prefix = ""

        ext = kwdict["extension"]
        kwdict["extension"] = self.extension = self.extension_map(ext, ext)

    def set_extension(self, extension, real=True):
        """Set filename extension"""
        self.extension = extension = self.extension_map(extension, extension)
        self.kwdict["extension"] = self.prefix + extension

    def fix_extension(self, _=None):
        """Fix filenames without a given filename extension"""
        try:
            if not self.extension:
                self.kwdict["extension"] = \
                    self.prefix + self.extension_map("", "")
                self.build_path()
                if self.path[-1] == ".":
                    self.path = self.path[:-1]
                    self.temppath = self.realpath = self.realpath[:-1]
            elif not self.temppath:
                self.build_path()
        except exception.GalleryDLException:
            raise
        except Exception:
            self.path = self.directory + "?"
            self.realpath = self.temppath = self.realdirectory + "?"
        return True

    def build_filename(self, kwdict):
        """Apply 'kwdict' to filename format string"""
        try:
            if self.filename_conditions is None:
                fmt = self.filename_formatter
            else:
                for condition, fmt in self.filename_conditions:
                    if condition(kwdict):
                        break
                else:
                    fmt = self.filename_formatter
            return self.clean_path(self.clean_segment(fmt(kwdict)))
        except Exception as exc:
            raise exception.FilenameFormatError(exc)

    def build_directory(self, kwdict):
        """Apply 'kwdict' to directory format strings"""
        try:
            if self.directory_conditions is None:
                formatters = self.directory_formatters
            else:
                for condition, formatters in self.directory_conditions:
                    if condition(kwdict):
                        break
                else:
                    formatters = self.directory_formatters

            segments = []
            strip = self.strip
            for fmt in formatters:
                segment = fmt(kwdict)
                if segment.__class__ is str:
                    segment = segment.strip()
                    if strip and segment not in {".", ".."}:
                        segment = segment.rstrip(strip)
                    if segment:
                        segments.append(self.clean_segment(segment))
                else:  # assume list
                    for segment in segment:
                        segment = segment.strip()
                        if strip and segment not in {".", ".."}:
                            segment = segment.rstrip(strip)
                        if segment:
                            segments.append(self.clean_segment(segment))
            return segments
        except Exception as exc:
            raise exception.DirectoryFormatError(exc)

    def build_path(self):
        """Combine directory and filename to full paths"""
        self.filename = filename = self.build_filename(self.kwdict)
        self.path = self.directory + filename
        self.realpath = self.realdirectory + filename
        if not self.temppath:
            self.temppath = self.realpath

    def part_enable(self, part_directory=None):
        """Enable .part file usage"""
        if self.extension:
            self.temppath += ".part"
        else:
            self.kwdict["extension"] = self.prefix + self.extension_map(
                "part", "part")
            self.build_path()

        if part_directory is not None:
            if isinstance(part_directory, list):
                for condition, part_directory in part_directory:
                    if condition(self.kwdict):
                        break
                else:
                    return

            self.temppath = os.path.join(
                part_directory,
                os.path.basename(self.temppath),
            )

    def part_size(self):
        """Return size of .part file"""
        try:
            return os.stat(self.temppath).st_size
        except OSError:
            pass
        return 0

    def set_mtime(self, path=None):
        if (mtime := (self.kwdict.get("_mtime_meta") or
                      self.kwdict.get("_mtime_http"))):
            util.set_mtime(self.realpath if path is None else path, mtime)

    def finalize(self):
        """Move tempfile to its target location"""
        if self.delete:
            self.delete = False
            os.unlink(self.temppath)
            return

        if self.temppath != self.realpath:
            # Move temp file to its actual location
            while True:
                try:
                    os.replace(self.temppath, self.realpath)
                except FileNotFoundError:
                    try:
                        # delayed directory creation
                        os.makedirs(self.realdirectory)
                    except FileExistsError:
                        # file at self.temppath does not exist
                        return False
                    continue
                except OSError:
                    # move across different filesystems
                    try:
                        shutil.copyfile(self.temppath, self.realpath)
                    except FileNotFoundError:
                        try:
                            os.makedirs(self.realdirectory)
                        except FileExistsError:
                            return False
                        shutil.copyfile(self.temppath, self.realpath)
                    os.unlink(self.temppath)
                break

        self.set_mtime()


def _build_convertfunc(func, conv):
    if len(conv) <= 1:
        conv = formatter._CONVERSIONS[conv]
        return lambda x: conv(func(x))

    def convert_many(x):
        x = func(x)
        for conv in convs:
            x = conv(x)
        return x
    convs = [formatter._CONVERSIONS[c] for c in conv]
    return convert_many


def _build_cleanfunc(chars, repl, conv=None):
    if not chars:
        func = util.identity
    elif isinstance(chars, dict):
        if 0 not in chars:
            chars = _process_repl_dict(chars)
            chars[0] = None

        def func(x):
            return x.translate(table)
        table = str.maketrans(chars)
    elif len(chars) == 1:
        def func(x):
            return x.replace(chars, repl)
    else:
        func = functools.partial(util.re(f"[{chars}]").sub, repl)
    return _build_convertfunc(func, conv) if conv else func


def _process_repl_dict(chars):
    # can't modify 'chars' while *directly* iterating over its keys
    for char in [c for c in chars if len(c) > 1]:
        if len(char) == 3 and char[1] == "-":
            citer = range(ord(char[0]), ord(char[2])+1)
        else:
            citer = char

        repl = chars.pop(char)
        for c in citer:
            chars[c] = repl

    return chars
