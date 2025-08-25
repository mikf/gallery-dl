# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann (kinda)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Use metadata as directory modification time"""

from .common import PostProcessor
from .. import text, util, formatter
from datetime import datetime
import os


class DirmtimePP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        if value := options.get("value"):
            self._get = formatter.parse(value, None, util.identity).format_map
        else:
            key = options.get("key", "date")
            self._get = lambda kwdict: kwdict.get(key)

        events = options.get("event")
        if events is None:
            events = ("post",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

        self._directories_processed = set()

    def run(self, pathfmt):
        mtime = self._get(pathfmt.kwdict)
        if mtime is None:
            return

        directory = pathfmt.realdirectory

        if directory in self._directories_processed:
            return
        self._directories_processed.add(directory)

        if not os.path.exists(directory):
            return

        if isinstance(mtime, datetime):
            timestamp = util.datetime_to_timestamp(mtime)
        else:
            timestamp = text.parse_int(mtime)

        if timestamp is not None:
            self.log.debug("Setting directory mtime: %s", directory)
            util.set_mtime(directory, timestamp)


__postprocessor__ = DirmtimePP
