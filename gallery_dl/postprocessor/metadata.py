# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to JSON files"""

from .common import PostProcessor
from .. import util
import json


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
            self.write(file, pathfmt)

    def _write_custom(self, file, pathfmt):
        output = self.formatter.format_map(pathfmt.keywords)
        file.write(output)

    def _write_tags(self, file, pathfmt):
        kwds = pathfmt.keywords
        tags = kwds.get("tags") or kwds.get("tag_string")

        if not tags:
            return

        if not isinstance(tags, list):
            for separator in (" :: ", ", ", " "):
                taglist = tags.split(separator)
                if len(taglist) >= len(tags) / 16:
                    break
            tags = taglist

        file.write("\n".join(tags))
        file.write("\n")

    def _write_json(self, file, pathfmt):
        json.dump(
            pathfmt.keywords,
            file,
            sort_keys=True,
            indent=self.indent,
            ensure_ascii=self.ascii,
        )


__postprocessor__ = MetadataPP
