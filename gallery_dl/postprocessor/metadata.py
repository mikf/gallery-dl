# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Write metadata to JSON files"""

from .common import PostProcessor
import json


class MetadataPP(PostProcessor):

    def __init__(self, pathfmt, options):
        PostProcessor.__init__(self)
        self.indent = options.get("indent", 4)
        self.ascii = options.get("ascii", False)

    def run(self, pathfmt):
        with open(pathfmt.realpath + ".json", "w") as file:
            json.dump(
                pathfmt.keywords,
                file,
                sort_keys=True,
                indent=self.indent,
                ensure_ascii=self.ascii,
            )


__postprocessor__ = MetadataPP
