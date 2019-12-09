# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to JSON files"""

from .common import PostProcessor
from .. import util

class Metadata_bypostPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)

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

        extfmt = options.get("extension-format")
        if extfmt:
            self.path = self._path_format
            self.extfmt = util.Formatter(extfmt).format_map
        else:
            self.path = self._path_append
            self.extension = options.get("extension", ext)

    def prepare(self, pathfmt):
        with open(self.path(pathfmt), "w", encoding="utf-8") as file:
            self.write(file, pathfmt.kwdict)

    def _path_append(self, pathfmt):
        return "{}.{}".format(pathfmt.realpath, self.extension)

    def _path_format(self, pathfmt):
        kwdict = pathfmt.kwdict
        ext = kwdict["extension"]
        kwdict["extension"] = pathfmt.extension
        kwdict["extension"] = pathfmt.prefix + self.extfmt(kwdict)
        path = pathfmt.realdirectory + pathfmt.build_filename()
        kwdict["extension"] = ext
        return path

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


__postprocessor__ = Metadata_bypostPP
