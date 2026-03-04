# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Trigger actions"""

from .common import PostProcessor
from .. import actions


class ActionsPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)
        self.action = actions.parse(options.get("mode") or
                                    options.get("action"))
        self.args = {
            "job"  : job,
            "log"  : job.extractor.log,
            "level": 0,
        }
        events = options.get("event")
        if events is None:
            events = ("prepare",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

    def run(self, pathfmt):
        self.action({**pathfmt.kwdict, **self.args})


__postprocessor__ = ActionsPP
