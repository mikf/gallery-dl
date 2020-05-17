# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to JSON files"""

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
            self.contentfmt = util.Formatter(cfmt).format_map
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
            self.metadir = directory.rstrip(sep) + os.sep

        extfmt = options.get("extension-format")
        if extfmt:
            self._filename = self._filename_custom
            self.extfmt = util.Formatter(extfmt).format_map
        else:
            self.extension = options.get("extension", ext)

        if options.get("bypost"):
            self.run_metadata, self.run = self.run, self.run_metadata

    def run(self, pathfmt):
        path = self._directory(pathfmt) + self._filename(pathfmt)
        with open(path, "w", encoding="utf-8") as file:
            self.write(file, pathfmt.kwdict)

    def _directory(self, pathfmt):
        return pathfmt.realdirectory

    def _directory_custom(self, pathfmt):
        directory = os.path.join(pathfmt.realdirectory, self.metadir)
        os.makedirs(directory, exist_ok=True)
        return directory

    def _filename(self, pathfmt):
        return pathfmt.filename + "." + self.extension

    def _filename_custom(self, pathfmt):
        kwdict = pathfmt.kwdict
        ext = kwdict["extension"]
        kwdict["extension"] = pathfmt.extension
        kwdict["extension"] = pathfmt.prefix + self.extfmt(kwdict)
        filename = pathfmt.build_filename()
        kwdict["extension"] = ext
        return filename

    def _write_custom(self, file, kwdict):
        file.write(self.contentfmt(kwdict))

    def _write_tags(self, file, kwdict):
        tags = kwdict.get("tags") or kwdict.get("tag_string")

        if not tags:
            return

        if not isinstance(tags, list):
            taglist = tags.split(", ")
            if len(taglist) < len(tags) / 16:
                taglist = tags.split(" ")
            tags = taglist

        file.write("\n".join(tags))
        file.write("\n")

    def _write_json(self, file, kwdict):
        util.dump_json(util.filter_dict(kwdict), file, self.ascii, self.indent)


__postprocessor__ = MetadataPP
