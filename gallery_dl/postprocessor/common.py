# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by postprocessor modules."""

from . import log


class PostProcessor():
    """Base class for postprocessors"""
    log = log

    def prepare(self, pathfmt):
        """ """

    def run(self, pathfmt):
        """Execute the postprocessor for a file"""

    def finalize(self):
        """Cleanup"""
