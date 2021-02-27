# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to external files"""

from .common import PostProcessor
from .. import util
import os


class MetadataPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        mode = options.get("mode", "json")
        if mode == "custom":
            self.write = self._write_custom
            cfmt = options.get("content-format") or options.get("format")
            if isinstance(cfmt, list):
                cfmt = "\n".join(cfmt) + "\n"
            self._content_fmt = util.Formatter(cfmt).format_map
            ext = "txt"
        elif mode == "tags":
            self.write = self._write_tags
            ext = "txt"
        else:
            self.write = self._write_json
            self.indent = options.get("indent", 4)
            self.ascii = options.get("ascii", False)
            ext = "json"

        directory = options.get("directory")
        if directory:
            self._directory = self._directory_custom
            sep = os.sep + (os.altsep or "")
            self._metadir = util.expand_path(directory).rstrip(sep) + os.sep

        filename = options.get("filename")
        extfmt = options.get("extension-format")
        if filename:
            self._filename = self._filename_custom
            self._filename_fmt = util.Formatter(filename).format_map
        elif extfmt:
            self._filename = self._filename_extfmt
            self._extension_fmt = util.Formatter(extfmt).format_map
        else:
            self.extension = options.get("extension", ext)

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        for event in events:
            job.hooks[event].append(self.run)

    def run(self, pathfmt):
        directory = self._directory(pathfmt)
        path = directory + self._filename(pathfmt)

        try:
            with open(path, "w", encoding="utf-8") as fp:
                self.write(fp, pathfmt.kwdict)
        except FileNotFoundError:
            os.makedirs(directory, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fp:
                self.write(fp, pathfmt.kwdict)

    def _directory(self, pathfmt):
        return pathfmt.realdirectory

    def _directory_custom(self, pathfmt):
        return os.path.join(pathfmt.realdirectory, self._metadir)

    def _filename(self, pathfmt):
        return (pathfmt.filename or "metadata") + "." + self.extension

    def _filename_custom(self, pathfmt):
        return pathfmt.clean_path(pathfmt.clean_segment(
            self._filename_fmt(pathfmt.kwdict)))

    def _filename_extfmt(self, pathfmt):
        kwdict = pathfmt.kwdict
        ext = kwdict.get("extension")
        kwdict["extension"] = pathfmt.extension
        kwdict["extension"] = pathfmt.prefix + self._extension_fmt(kwdict)
        filename = pathfmt.build_filename()
        kwdict["extension"] = ext
        return filename

    def _write_custom(self, fp, kwdict):
        fp.write(self._content_fmt(kwdict))

    def _write_tags(self, fp, kwdict):
        tags = kwdict.get("tags") or kwdict.get("tag_string")

        if not tags:
            return

        if not isinstance(tags, list):
            taglist = tags.split(", ")
            if len(taglist) < len(tags) / 16:
                taglist = tags.split(" ")
            tags = taglist

        fp.write("\n".join(tags) + "\n")

    def _write_json(self, fp, kwdict):
        util.dump_json(util.filter_dict(kwdict), fp, self.ascii, self.indent)


__postprocessor__ = MetadataPP
