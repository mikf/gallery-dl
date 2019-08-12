# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to JSON files"""

from .common import PostProcessor
from .. import util


class MetadataPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)

        mode = options.get("mode", "json")
        ext = "txt"

        if mode == "custom":
            self.write = self._write_custom
            self.formatter = util.Formatter(options.get("format"))
        elif mode == "tags":
            self.write = self._write_tags
        else:
            self.write = self._write_json
            self.indent = options.get("indent", 4)
            self.ascii = options.get("ascii", False)
            ext = "json"

        self.extension = options.get("extension", ext)

    def run(self, pathfmt):
        path = "{}.{}".format(pathfmt.realpath, self.extension)
        with open(path, "w", encoding="utf-8") as file:
            self.write(file, pathfmt.kwdict)

    def _write_custom(self, file, kwdict):
        output = self.formatter.format_map(kwdict)
        file.write(output)

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
        util.dump_json(kwdict, file, self.ascii, self.indent)


__postprocessor__ = MetadataPP
