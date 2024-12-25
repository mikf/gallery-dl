# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Filesystem path handling"""

import os
import re
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
                self.build_filename = self.build_filename_conditional
                filename_fmt = filename_fmt.get("", extractor.filename_fmt)

            self.filename_formatter = formatter.parse(
                filename_fmt, kwdefault).format_map
        except Exception as exc:
            raise exception.FilenameFormatError(exc)

        directory_fmt = config("directory")
        self.directory_conditions = ()
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
                self.build_directory = self.build_directory_conditional
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
        self.clean_segment = self._build_cleanfunc(restrict, replace)

        remove = config("path-remove", "\x00-\x1f\x7f")
        self.clean_path = self._build_cleanfunc(remove, "")

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

        basedir = extractor._parentdir
        if not basedir:
            basedir = config("base-directory")
            sep = os.sep
            if basedir is None:
                basedir = "." + sep + "gallery-dl" + sep
            elif basedir:
                basedir = util.expand_path(basedir)
                altsep = os.altsep
                if altsep and altsep in basedir:
                    basedir = basedir.replace(altsep, sep)
                if basedir[-1] != sep:
                    basedir += sep
            basedir = self.clean_path(basedir)
        self.basedirectory = basedir

    @staticmethod
    def _build_cleanfunc(chars, repl):
        if not chars:
            return util.identity
        elif isinstance(chars, dict):
            def func(x, table=str.maketrans(chars)):
                return x.translate(table)
        elif len(chars) == 1:
            def func(x, c=chars, r=repl):
                return x.replace(c, r)
        else:
            return functools.partial(
                re.compile("[" + chars + "]").sub, repl)
        return func

    def open(self, mode="wb"):
        """Open file and return a corresponding file object"""
        try:
            return open(self.temppath, mode)
        except FileNotFoundError:
            os.makedirs(self.realdirectory)
            return open(self.temppath, mode)

    def exists(self):
        """Return True if the file exists on disk"""
        if self.extension and os.path.exists(self.realpath):
            return self.check_file()
        return False

    @staticmethod
    def check_file():
        return True

    def _enum_file(self):
        num = 1
        try:
            while True:
                prefix = format(num) + "."
                self.kwdict["extension"] = prefix + self.extension
                self.build_path()
                os.stat(self.realpath)  # raises OSError if file doesn't exist
                num += 1
        except OSError:
            pass
        self.prefix = prefix
        return False

    def set_directory(self, kwdict):
        """Build directory path and create it if necessary"""
        self.kwdict = kwdict

        segments = self.build_directory(kwdict)
        if segments:
            self.directory = directory = self.basedirectory + self.clean_path(
                os.sep.join(segments) + os.sep)
        else:
            self.directory = directory = self.basedirectory

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
            return self.clean_path(self.clean_segment(
                self.filename_formatter(kwdict)))
        except Exception as exc:
            raise exception.FilenameFormatError(exc)

    def build_filename_conditional(self, kwdict):
        try:
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
        segments = []
        append = segments.append
        strip = self.strip

        try:
            for fmt in self.directory_formatters:
                segment = fmt(kwdict).strip()
                if strip and segment != "..":
                    # remove trailing dots and spaces (#647)
                    segment = segment.rstrip(strip)
                if segment:
                    append(self.clean_segment(segment))
            return segments
        except Exception as exc:
            raise exception.DirectoryFormatError(exc)

    def build_directory_conditional(self, kwdict):
        segments = []
        append = segments.append
        strip = self.strip

        try:
            for condition, formatters in self.directory_conditions:
                if condition(kwdict):
                    break
            else:
                formatters = self.directory_formatters
            for fmt in formatters:
                segment = fmt(kwdict).strip()
                if strip and segment != "..":
                    segment = segment.rstrip(strip)
                if segment:
                    append(self.clean_segment(segment))
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
        if part_directory:
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
                    # delayed directory creation
                    os.makedirs(self.realdirectory)
                    continue
                except OSError:
                    # move across different filesystems
                    try:
                        shutil.copyfile(self.temppath, self.realpath)
                    except FileNotFoundError:
                        os.makedirs(self.realdirectory)
                        shutil.copyfile(self.temppath, self.realpath)
                    os.unlink(self.temppath)
                break

        mtime = self.kwdict.get("_mtime")
        if mtime:
            util.set_mtime(self.realpath, mtime)
