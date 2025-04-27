# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Trigger directory format string evaluation"""

from .common import PostProcessor


class DirectoryPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        events = options.get("event")
        if events is None:
            events = ("prepare",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

    def run(self, pathfmt):
        pathfmt.set_directory(pathfmt.kwdict)


__postprocessor__ = DirectoryPP
