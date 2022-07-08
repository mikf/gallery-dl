# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Use metadata as file modification time"""

from .common import PostProcessor
from .. import text, util, formatter
from datetime import datetime


class MtimePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        value = options.get("value")
        if value:
            self._get = formatter.parse(value, None, util.identity).format_map
        else:
            key = options.get("key", "date")
            self._get = lambda kwdict: kwdict.get(key)

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

    def run(self, pathfmt):
        mtime = self._get(pathfmt.kwdict)
        pathfmt.kwdict["_mtime"] = (
            util.datetime_to_timestamp(mtime)
            if isinstance(mtime, datetime) else
            text.parse_int(mtime)
        )


__postprocessor__ = MtimePP
