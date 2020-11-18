# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Common classes and constants used by postprocessor modules."""


class PostProcessor():
    """Base class for postprocessors"""

    def __init__(self, job):
        name = self.__class__.__name__[:-2].lower()
        self.log = job.get_logger("postprocessor." + name)

    def __repr__(self):
        return self.__class__.__name__
