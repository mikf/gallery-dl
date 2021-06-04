# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Use metadata as file modification time"""

from .common import PostProcessor
from ..text import parse_int


class MtimePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.key = options.get("key", "date")
        job.register_hooks({"file": self.run}, options)

    def run(self, pathfmt):
        mtime = pathfmt.kwdict.get(self.key)
        ts = getattr(mtime, "timestamp", None)
        pathfmt.kwdict["_mtime"] = ts() if ts else parse_int(mtime)


__postprocessor__ = MtimePP
